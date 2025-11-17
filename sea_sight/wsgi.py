from PIL import Image
from beaches.ai.clip_recognizer import get_clip_match

dummy_image = Image.new("L", (224, 224))
get_clip_match(dummy_image, "dummy")