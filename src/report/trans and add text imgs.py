import PIL
from PIL import Image


input_path = '../../experiments/busgan/exp2/figures/epoch_10_validation.png'
output_img = '../../figures/exp/wl1gan.png'

in_img = Image.open(input_path)
in_img = in_img.rotate(90)

for i in range(3):
    for j in range(3):
        sample = in_img.crop(box=(i*256, j*256, (i+1)*256, (j+1)*256)).rotate(-90)
        in_img.paste(sample, box=(i*256, j*256))

#in_img.show()
in_img.save(output_img)
print('deb')
