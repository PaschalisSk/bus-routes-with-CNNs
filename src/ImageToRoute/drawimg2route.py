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

img_path = 'D:/Google Drive/UoE/Thesis/figures/meth/circleroute.png'
out_path = 'D:/Google Drive/UoE/Thesis/figures/meth/circlerouteskel.png'
img = io.imread(img_path)
img = rgb2gray(img)
img[img <= 0.5] = 0
img[img > 0.5] = 1
image = invert(img)
skeleton = skeletonize(image)
img[skeleton] = 255
img[skeleton == False] = 0

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
            if img[y][x] == 255 and img[y][x + 1] == 255:
                edges.append(((x, y), (x + 1, y)))
        if y != h - 1:
            if img[y][x] == 255 and img[y + 1][x] == 255:
                edges.append(((x, y), (x, y + 1)))
        # South-east diag
        if x != w - 1 and y != h - 1:
            if img[y][x] == 255 and img[y + 1][x + 1] == 255:
                edges.append(((x, y), (x + 1, y + 1)))
        # South-west diag
        if x != 0 and y != h - 1:
            if img[y][x] == 255 and img[y + 1][x - 1] == 255:
                edges.append(((x, y), (x - 1, y + 1)))
# Add the weight for the cpp
G.add_edges_from(edges, distance=1, id=' ')
G.remove_nodes_from(list(nx.isolates(G)))
# pos is {(0,0): (0,255), (0,1): (0,254), (0,2): (0,253), ...,
# (255,254): (255,1), (255,255): (255,0)}
# Need to reverse order of y in the positions since img has origin top left
# and pyplot has origin bottom left
nodes = list(G.nodes())
poses = [(x, 255-y) for x,y in nodes]
pos = dict(zip(nodes, poses))
ax = plt.axes(aspect='equal')
nx.draw_networkx(G, pos=pos, ax=ax, with_labels=False, nodelist=[], node_size=1, node_color='black', width=1)
#plt.show()
plt.axis('off')
plt.ylim(0, 255)
plt.xlim(0, 255)
my_dpi = 106
#plt.figure(figsize=(256/my_dpi, 256/my_dpi), dpi=my_dpi)
#plt.savefig('D:/Google Drive/UoE/Thesis/figures/meth/routegraph.pdf', bbox_inches='tight')
plt.savefig('D:/Google Drive/UoE/Thesis/figures/meth/circleroutegraph.png', bbox_inches='tight', dpi=66)
#io.imsave(out_path, img)
# io.imshow(img)
# plt.show()
#io.imsave('D:/Google Drive/UoE/Thesis/output/routes/1sk.jpg', skeleton, cmap=plt.cm.gray)
print('deb')
