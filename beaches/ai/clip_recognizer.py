from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None
_processor = None

def get_clip_match(image_path, text_prompt: str):
    """
    Compare an image with a text description using CLIP.
    Lazy-loads model and processor to avoid blocking server start.
    """
    global _model, _processor

    if _model is None or _processor is None:
        print("[INFO] Loading CLIP model for the first time...")
        _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        print("[INFO] CLIP model loaded.")

    text_prompts = [
        text_prompt,
        "an unrelated image",
        "a random object",
        "a blank photo"
    ]

    image = Image.open(image_path)
    inputs = _processor(text=text_prompts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = _model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)[0]

    best_idx = int(probs.argmax())
    best_prompt = text_prompts[best_idx]
    confidence = float(probs[best_idx])

    scores = {p: float(probs[i]) for i, p in enumerate(text_prompts)}

    return best_prompt, confidence, scores