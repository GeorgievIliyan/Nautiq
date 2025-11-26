from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", use_fast=True)

def get_clip_match(image_path, text_prompts, unrelated_prompt="unrelated object", threshold=0.25):

    if isinstance(image_path, str):
        image = Image.open(image_path).convert("RGB")
    else:
        image = Image.open(image_path).convert("RGB")

    if isinstance(text_prompts, str):
        text_prompts = [text_prompts]
    elif not isinstance(text_prompts, (list, tuple)):
        raise ValueError("text_prompts must be a string or list/tuple of strings")
    text_prompts = [str(t) for t in text_prompts]

    all_prompts = text_prompts + [unrelated_prompt]

    inputs = processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        image_embeds = outputs.image_embeds / outputs.image_embeds.norm(p=2, dim=-1, keepdim=True)
        text_embeds = outputs.text_embeds / outputs.text_embeds.norm(p=2, dim=-1, keepdim=True)

        scores = (image_embeds @ text_embeds.T).squeeze(0)
        print("📝 Raw scores:", scores)
        scores = scores.cpu().tolist()
        print("📝 Scores as list:", scores)

    main_scores = scores[:-1]
    unrelated_score = scores[-1]
    all_scores = {text_prompts[i]: float(main_scores[i]) for i in range(len(text_prompts))}
    all_scores[unrelated_prompt] = float(unrelated_score)
    print("📝 All scores:", all_scores)

    best_idx = main_scores.index(max(main_scores))
    best_prompt = text_prompts[best_idx]
    confidence = main_scores[best_idx]

    if unrelated_score > threshold:
        print(f"⚠️ Unrelated prompt score {unrelated_score:.4f} > {threshold}, lowering confidence.")
        confidence = min(confidence, threshold)

    print(f"✅ Best match: '{best_prompt}' with confidence {confidence:.4f}")
    return best_prompt, float(confidence), all_scores