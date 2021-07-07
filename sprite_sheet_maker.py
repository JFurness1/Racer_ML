from PIL import Image
from glob import glob
import os
from math import ceil

out_name = "car.png"
base_dir = "E:\Projects\Racer_ML\MakingCarSprites\Render"
ofile = os.path.join(base_dir, out_name)

if os.path.isfile(ofile):
    os.remove(ofile)

imgs = [Image.open(f) for f in sorted(glob(os.path.join(base_dir, "*.png"))) if f != out_name]

dims = imgs[0].size

wcount = 12
hcount = ceil(len(imgs)/wcount)

wsize = wcount*dims[0]
hsize = hcount*dims[1]

out =  Image.new("RGBA", (wsize, hsize))

for i, img in enumerate(imgs):
    x = i%wcount
    y = (hcount - i//wcount)-1
    out.paste(img, (x*dims[0], y*dims[1]))

out.save(os.path.join(base_dir, out_name), "PNG")
