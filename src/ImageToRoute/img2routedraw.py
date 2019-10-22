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
from staticmap import px_to_coords

params = {
    'backend': 'ps',
    #'text.latex.preamble': ['\usepackage{gensymb}'],
    'axes.labelsize': 14, # fontsize for x and y labels (was 10)
    'axes.titlesize': 14,
    'font.size': 14, # was 10
    'legend.fontsize': 14, # was 10
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'text.usetex': True,
    'font.family': 'serif'
}
plt.rcParams.update(params)

# https://gist.github.com/rochacbruno/2883505
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 * 1000# m

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

img_path = 'D:/Google Drive/UoE/Thesis/figures/meth/circleroute.png'
center = (9.807234000000001, 54.903877)
zoom = 15
lon1, lat1 = px_to_coords((0, 0), 256, 256, 15, center, tile_size=64)
lon2, lat2 = px_to_coords((0, 1), 256, 256, 15, center, tile_size=64)
s_dist = distance((lat1, lon1), (lat2, lon2))
lon1, lat1 = px_to_coords((0, 0), 256, 256, 15, center, tile_size=64)
lon2, lat2 = px_to_coords((1, 1), 256, 256, 15, center, tile_size=64)
d_dist = distance((lat1, lon1), (lat2, lon2))

img = io.imread(img_path)
img = rgb2gray(img)
img[img > 0.5] = 1
img[img <= 0.5] = 0
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
                edges.append(((x, y), (x + 1, y), {'distance': s_dist, 'id': ' '}))
        if y != h - 1:
            if img[y][x] == 255 and img[y + 1][x] == 255:
                edges.append(((x, y), (x, y + 1), {'distance': s_dist, 'id': ' '}))
        # South-east diag
        if x != w - 1 and y != h - 1:
            if img[y][x] == 255 and img[y + 1][x + 1] == 255:
                edges.append(((x, y), (x + 1, y + 1), {'distance': d_dist, 'id': ' '}))
        # South-west diag
        if x != 0 and y != h - 1:
            if img[y][x] == 255 and img[y + 1][x - 1] == 255:
                edges.append(((x, y), (x - 1, y + 1), {'distance': d_dist, 'id': ' '}))
# Add the weight for the cpp
G.add_edges_from(edges)
G.remove_nodes_from(list(nx.isolates(G)))
path, _ = cpp(G)
path = [(e1, e2) for e1, e2, _, _ in path]

## ADD STOPS
# Add start
stops_nodes = [path[0][0]]
dist = 0
for e in path:
    d = G.get_edge_data(e[0], e[1])[0]['distance']
    dist += d
    if dist >= 300:
        stops_nodes.append(e[1])
        dist = 0

# Remove last item if we are less than 150 from start
if dist < 150:
    stops_nodes = stops_nodes[:-1]
## --- ##
# pos is {(0,0): (0,255), (0,1): (0,254), (0,2): (0,253), ...,
# (255,254): (255,1), (255,255): (255,0)}
# Need to reverse order of y in the positions since img has origin top left
# and pyplot has origin bottom left
nodes = list(G.nodes())
poses = [(x, 255-y) for x,y in nodes]
pos = dict(zip(nodes, poses))
ax = plt.axes(aspect='equal')
N = len(path)
edge_color = cm.get_cmap('gnuplot')
color_list = edge_color(np.linspace(0, 1, N))
cmap_name = edge_color.name + str(N)
edge_color.from_list(cmap_name, color_list, N)
nx.draw_networkx(G, pos=pos, edgelist=path, edge_color=color_list, ax=ax,
                 with_labels=False, nodelist=stops_nodes, node_size=15,
                 node_color='black', width=2)
plt.axis('off')
norm = colors.Normalize(vmin=0,vmax=N)
sm = plt.cm.ScalarMappable(cmap=edge_color, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ticks=[0, N])
cbar.ax.set_yticklabels([r'Start', r'Finish'])
plt.ylim(35, 220)
plt.xlim(35, 220)
ax.legend(['Bus stop'], handletextpad=0.1)
# plt.legend(loc=2, handletextpad=0.1)
# plt.gca().get_legend().legendHandles[1].set_visible(False)
# plt.gca().get_legend().texts[1].set_visible(False)
#plt.show()
#plt.figure(figsize=(256/my_dpi, 256/my_dpi), dpi=my_dpi)
#plt.savefig('D:/Google Drive/UoE/Thesis/figures/meth/routegwstops.eps', bbox_inches='tight')
#plt.savefig('D:/Google Drive/UoE/Thesis/figures/meth/routegraph.png', bbox_inches='tight', dpi=66)
#io.imsave(out_path, img)
# io.imshow(img)
# plt.show()
#io.imsave('D:/Google Drive/UoE/Thesis/output/routes/1sk.jpg', skeleton, cmap=plt.cm.gray)
print('deb')
