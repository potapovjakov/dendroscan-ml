from CLIPFilter_2 import CLIPFilter
from classes import filters, translations, latin_names 
from PIL import Image

model = CLIPFilter("../models/mobileclip_s1.pt", filters, translations, latin_names)

img = Image.open(r"/home/potapovya/pictures/listvennica_crop.png").convert("RGB")
print(model.process(img))
