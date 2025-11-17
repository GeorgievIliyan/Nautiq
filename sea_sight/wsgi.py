from PIL import Image
from beaches.ai.clip_recognizer import get_clip_match

dummy_image = Image.new("RGB", (1, 1))
get_clip_match(dummy_image, "dummy")