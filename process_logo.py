"""
Run this after placing a new new_logo.png in this folder.
Removes the magenta (#FF00FF) chroma-key background precisely,
then generates the ICO and updates the web/ copy.
"""
from PIL import Image
import numpy as np

img = Image.open("new_logo.png").convert("RGBA")
data = np.array(img, dtype=np.float32)

r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

# Magenta = high R, low G, high B
magenta_mask = (r > 180) & (g < 80) & (b > 180)

data[magenta_mask, 3] = 0
result = Image.fromarray(data.astype(np.uint8))

result.save("new_logo.png")
result.save("web/new_logo.png")
result.save("readmi.ico", format="ICO",
            sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

print("Done: new_logo.png / web/new_logo.png / readmi.ico updated")
