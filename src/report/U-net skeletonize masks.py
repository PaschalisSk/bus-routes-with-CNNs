from pathlib import Path
import matplotlib.pyplot as plt
from skimage.util import invert
from skimage.filters import try_all_threshold
from skimage import io
from skimage.color import rgb2gray, gray2rgb
from skimage.morphology import skeletonize

in_dir = '../../output/mask imgs/'
out_dir = '../../output/skeleton masks/'

img_paths = [filepath for filepath in Path(in_dir).glob('*.png')]

for img_path in img_paths:
    img_name = img_path.name
    img_path = str(img_path)

    img = io.imread(img_path)
    mask_image = img[:, 512:768, :]
    mask_image = rgb2gray(mask_image)
    mask_image[mask_image <= 0.5] = 0
    mask_image[mask_image > 0.5] = 1
    mask_image = invert(mask_image)
    skeleton = skeletonize(mask_image)
    mask_image[skeleton] = 0
    mask_image[skeleton == False] = 255
    mask_image = gray2rgb(mask_image)
    img[:, 512:768, :] = mask_image
    io.imsave(out_dir + img_name, img)
    print(img_name)
