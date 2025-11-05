import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
from . import models

load_dotenv()

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_clip_match(image_path, text_prompts):
    image = Image.open(image_path)
    inputs = processor(text=text_prompts, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    probs = outputs.logits_per_image.softmax(dim=1)[0]
    scores = {t: float(p) for t, p in zip(text_prompts, probs)}
    best = max(scores, key=scores.get)
    return best, scores[best], scores

def check_badges(profile):
    unlocked = []

    if profile.missions_completed >= 10:
        unlocked.append('Explorer')
    if profile.xp >= 1000:
        unlocked.append('Achiever')

    for title in unlocked:
        badge = models.Badge.objects.filter(title=title).first()
        if badge and not profile.badge_set.filter(id=badge.id).exists():
            profile.badge_set.add(badge)