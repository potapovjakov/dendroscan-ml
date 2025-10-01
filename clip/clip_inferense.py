import io

from clip.CLIPFilter_2 import CLIPFilter
from clip.classes import filters, translations, latin_names
from PIL import Image

model = CLIPFilter("./models/mobileclip_s1.pt", filters, translations, latin_names)


def get_clip_predict(crop_bytes):
    img = Image.open(io.BytesIO(crop_bytes)).convert("RGB")
    result = model.process(img)
    return result
