from PIL import Image
from pathlib import Path

input_dir = '../../output/unet thresholds/imgs/'
output_path = '../../figures/exp/thresimgs.png'

img_paths = [img for img in Path(input_dir).glob('*.png')]
sorted(img_paths, key=lambda img_path: float(img_paths[0].name.rsplit('_')[1].rsplit('.', 1)[0]))
img_paths = img_paths[::-1]
img_paths = img_paths[3::2]
nb_rows = 4
nb_cols = len(img_paths) + 2

f_img = Image.new("RGB", (256*nb_cols, 256*nb_rows))

for i, img_path in enumerate(img_paths):
    img = Image.open(img_path)
    for j in range(nb_rows):
        if i == 1:
                x_img = img.crop((j*256, 0, (j+1)*256, 256))
                f_img.paste(x_img, (0, j*256))

                y_img = img.crop((j*256, 256, (j+1)*256, 256*2))
                f_img.paste(y_img, (256, j*256))

        y_pred_img = img.crop((j*256, 256*2, (j+1)*256, 256*3))
        f_img.paste(y_pred_img, ((i+2)*256, j*256))

f_img.save(output_path)
