from PIL import Image
from beaches.ai.clip_recognizer import get_clip_match

dummy_image = Image.new("RGB", (224, 224), color=(128, 128, 128))
get_clip_match(dummy_image, "dummy")