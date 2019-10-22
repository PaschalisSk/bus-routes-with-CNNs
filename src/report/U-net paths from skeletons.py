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

imgs_info = pd.read_csv('../../data/route_imgs_256/imgs_info.csv')
in_dir = '../../output/skeleton masks/'
out_path = '../../output/paths from skeletons/'

img_paths = [filepath for filepath in Path(in_dir).glob('*.png')]
paths_list_coords = []
paths_list_coords.append(['img', 'stops sequence (lon, lat)'])
paths_list_px = []
paths_list_px.append(['img', 'stops sequence (x, y)'])

for i, img_path in enumerate(img_paths, 1):
    img_name = img_path.name
    paths_list_coords.append([img_name])
    paths_list_px.append([img_name])
    img_info = imgs_info.loc[imgs_info['img'] == img_name.rsplit('.')[0] + '.jpg']
    img_path = str(img_path)

    img = io.imread(img_path)
    mask_image = img[:, 512:768, :]
    mask_image = rgb2gray(mask_image)
    mask_image[mask_image <= 0.5] = 0
    mask_image[mask_image > 0.5] = 1

    center = (img_info['center_lon'].values[0], img_info['center_lat'].values[0])
    zoom = img_info['zoom'].values[0]
    lon1, lat1 = px_to_coords((0, 0), 256, 256, 15, center, tile_size=64)
    lon2, lat2 = px_to_coords((0, 1), 256, 256, 15, center, tile_size=64)
    s_dist = distance((lat1, lon1), (lat2, lon2))
    lon1, lat1 = px_to_coords((0, 0), 256, 256, 15, center, tile_size=64)
    lon2, lat2 = px_to_coords((1, 1), 256, 256, 15, center, tile_size=64)
    d_dist = distance((lat1, lon1), (lat2, lon2))

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
                        ((x, y), (x + 1, y), {'distance': s_dist, 'id': ' '}))
            if y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x] == 0:
                    edges.append(
                        ((x, y), (x, y + 1), {'distance': s_dist, 'id': ' '}))
            # South-east diag
            if x != w - 1 and y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x + 1] == 0:
                    edges.append(((x, y), (x + 1, y + 1),
                                  {'distance': d_dist, 'id': ' '}))
            # South-west diag
            if x != 0 and y != h - 1:
                if mask_image[y][x] == 0 and mask_image[y + 1][x - 1] == 0:
                    edges.append(((x, y), (x - 1, y + 1),
                                  {'distance': d_dist, 'id': ' '}))
    # Add the weight for the cpp
    G.add_edges_from(edges)
    G.remove_nodes_from(list(nx.isolates(G)))
    # Get largest connected component
    G = max(nx.connected_component_subgraphs(G), key=len)

    # ### -------TEST ---
    # nodes = list(G.nodes())
    # poses = [(x, 255 - y) for x, y in nodes]
    # pos = dict(zip(nodes, poses))
    # ax = plt.axes(aspect='equal')
    # nx.draw_networkx(G, pos=pos, ax=ax,
    #                  with_labels=False, nodelist=[], node_size=15,
    #                  edge_color='black', width=2)
    # plt.show()
    # ### -- END TEST --
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

    stops_nodes_coords = [px_to_coords(point, 256, 256, zoom, center, tile_size=64) for point in stops_nodes]
    paths_list_coords[i].extend(stops_nodes_coords)
    paths_list_px[i].extend(stops_nodes)
    print(img_name)
    # ### -------TEST ---
    nodes = list(G.nodes())
    poses = [(x, 255 - y) for x, y in nodes]
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
    norm = colors.Normalize(vmin=0, vmax=N)
    sm = plt.cm.ScalarMappable(cmap=edge_color, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ticks=[0, N])
    cbar.ax.set_yticklabels([r'Start', r'Finish'])
    plt.ylim(0, 256)
    plt.xlim(0, 256)
    ax.legend(['Bus stop'], handletextpad=0.1)
    plt.show()
    # ### -- END TEST --

# with open(out_path + 'paths_list_coords.csv', 'w') as f:
#     f.writelines('\t'.join(str(j) for j in i) + '\n' for i in paths_list_coords)
#
# with open(out_path + 'paths_list_px.csv', 'w') as f:
#     f.writelines('\t'.join(str(j) for j in i) + '\n' for i in paths_list_px)
