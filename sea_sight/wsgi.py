import os
from django.core.wsgi import get_wsgi_application

try:
    import torch
    from beaches.ai.clip_recognizer import get_clip_match
    print("Preloading CLIP model at server startup...")
    get_clip_match.__globals__['_model'] = None
    get_clip_match.__globals__['_processor'] = None
except Exception as e:
    print(f"[WARNING] Failed to preload CLIP: {e}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sea_sight.settings")

application = get_wsgi_application()

try:
    from PIL import Image
    import io
    dummy_image = Image.new("RGB", (1, 1))
    get_clip_match(dummy_image, "dummy")
    print("CLIP preloaded successfully.")
except Exception as e:
    print(f"[WARNING] CLIP preloading call failed: {e}")