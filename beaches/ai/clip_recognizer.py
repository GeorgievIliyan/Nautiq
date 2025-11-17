from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import threading

device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None
_processor = None
_lock = threading.Lock()

def get_clip_match(image_path_or_obj, text_prompt: str):
    global _model, _processor

    if _model is None or _processor is None:
        with _lock:
            if _model is None or _processor is None:
                _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
                _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                print("[INFO] CLIP model loaded successfully.")

    if isinstance(image_path_or_obj, str):
        image = Image.open(image_path_or_obj)
    else:
        image = image_path_or_obj

    text_prompts = [
        text_prompt,
        "an unrelated image",
        "a random object",
        "a blank photo"
    ]

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