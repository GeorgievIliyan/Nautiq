from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

_model = None
_processor = None

def get_clip_model():
    global _model, _processor
    if _model is None or _processor is None:
        _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return _model, _processor

def get_clip_match(image_path, text_prompts):
    
    model, processor = get_clip_model()

    if isinstance(image_path, str):
        image = Image.open(image_path).convert("RGB")
    elif isinstance(image_path, Image.Image):
        image = image_path
    else:
        raise ValueError("image_path must be a string path or PIL.Image object")

    inputs = processor(text=text_prompts, images=image, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        image_embeds = outputs.image_embeds
        text_embeds = outputs.text_embeds

        image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
        text_embeds = text_embeds / text_embeds.norm(p=2, dim=-1, keepdim=True)

        scores = (image_embeds @ text_embeds.T).squeeze(0)

    best_idx = scores.argmax().item()
    best_score = scores[best_idx].item()
    best_match = text_prompts[best_idx]

    all_scores = [(text_prompts[i], scores[i].item()) for i in range(len(text_prompts))]

    return {
        "best_match": best_match,
        "score": best_score,
        "all_scores": all_scores
    }