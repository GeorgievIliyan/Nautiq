from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_clip_match(image_path, text_prompts):
    image = Image.open(image_path)
    inputs = processor(text=text_prompts, images=image, return_tensors="pt", padding=True)
    inputs = {k:v.to(device) for k,v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)[0]

    scores = {t: float(probs[i]) for i, t in enumerate(text_prompts)}
    best_idx = int(probs.argmax())
    best_prompt = text_prompts[best_idx]
    confidence = float(probs[best_idx])

    print(f"Logits: {logits_per_image}")
    print(f"Probabilities: {probs}")
    print(f"Best prompt: {best_prompt}")
    print(f"Confidence: {confidence}")

    return best_prompt, confidence, scores