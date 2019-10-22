from pathlib import Path
import matplotlib.pyplot as plt
from skimage.util import invert
from skimage.filters import try_all_threshold
from skimage import io
from skimage.color import rgb2gray, gray2rgb
from skimage.morphology import skeletonize
from skimage.morphology import skeletonize
from skimage import data
import matplotlib.pyplot as plt
from skimage.util import invert
from skimage.filters import try_all_threshold
from skimage import io
from skimage.color import rgb2gray
import numpy as np
import networkx as nx
from itertools import combinations
from itertools import product
from postman_problems.solver import cpp
from matplotlib import cm, colors
import math
import pandas as pd
from staticmap import px_to_coords
from PIL import Image

in_dir = '../../output/skeleton masks/'
out_file = '../../figures/exp/extvalsamples.png'

img_paths = [filepath for filepath in Path(in_dir).glob('*.png')]

nb_samples = 6
final_image = Image.new("RGB", (nb_samples*256, 3*256))
for i, img_path in enumerate(img_paths[:nb_samples]):
    img = io.imread(str(img_path))
    mask_image = img[:, 512:768, :]
    mask_image = rgb2gray(mask_image)
    mask_image[mask_image <= 0.5] = 0
    mask_image[mask_image > 0.5] = 1

    h, w = 256, 256

    G = nx.MultiGraph()
    # nodes is [(0,0), (0,1), (0,2), ..., (w, h - 1), (w, h)]
    nodes = list(product(range(w), range(h)))
    G.add_nodes_from(nodes)
    # Must do G.add_edges_from([((0, 0), (1, 1)),((0, 0), (0, 1),...)])
    # In numpy the first dimension is rows
    # Add edges between white colored neighbouring pixels
    edges = []
    for y in range(0, h):
        for x in range(0, w):
            if x != w - 1:
                if mask_image[y][x] == 0 and mask_image[y][x + 1] == 0:
                    edges.append(
                        ((x, y), (x + 1, y)))
            if y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x] == 0:
                    edges.append(
                        ((x, y), (x, y + 1)))
            # South-east diag
            if x != w - 1 and y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x + 1] == 0:
                    edges.append(((x, y), (x + 1, y + 1)))
            # South-west diag
            if x != 0 and y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x - 1] == 0:
                    edges.append(((x, y), (x - 1, y + 1)))
    # Add the weight for the cpp
    G.add_edges_from(edges)
    G.remove_nodes_from(list(nx.isolates(G)))
    # Get largest connected component
    G = max(nx.connected_component_subgraphs(G), key=len)
    img_np = np.ones((256, 256))
    img_np[[p[1] for p in G.nodes], [p[0] for p in G.nodes]] = 0
    img_np = gray2rgb(img_np) * 255
    img[:, 512:768, :] = img_np
    im = Image.fromarray(img)

    for j in range(3):
        sample = im.crop(box=(j * 256, 0, (j + 1) * 256, 256))
        k=0
        if j == 1:
            k = 2
        elif j == 2:
            k = 1
        final_image.paste(sample, box=(i * 256, k * 256))

final_image.save(out_file)
print('deb')
