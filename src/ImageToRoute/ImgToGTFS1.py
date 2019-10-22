from itertools import combinations
from itertools import product

import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

img_path = 'D:/Google Drive/UoE/Thesis/output/routes/1.jpg'
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
_, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY_INV)
#
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

h, w = img.shape[:2]


def img_to_graph(img):
    h, w = img.shape[:2]

    G = nx.MultiGraph()
    # nodes is [(0,0), (0,1), (0,2), ..., (255,254), (255,255)]
    nodes = list(product(range(w), range(h)))
    G.add_nodes_from(nodes)
    # Must do G.add_edges_from([((0, 0), (1, 1)),((0, 0), (0, 1),...)])
    # In numpy the first dimension is rows
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

    G.add_edges_from(edges)

    return G


G = img_to_graph(img)


# Remove unnecessery diagonials
nodes = list(G.nodes())
cliques = list(nx.find_cliques(G))
for clique in cliques:
    if len(clique) > 2:
        cl_edges = list(combinations(clique, 2))
        # For each edge in the clique
        for cl_edge in cl_edges:
            # If they have diff x and y they are a diagonal
            if (cl_edge[0][0] != cl_edge[1][0] and
                    cl_edge[0][1] != cl_edge[1][1]):
                if G.has_edge(*cl_edge):
                    G.remove_edge(*cl_edge)

# Remove left edge of squares
for node in nodes:
    x, y = node
    if x != w - 1 and y != h - 1:
        # Check if node is top left corner of square
        if (G.has_edge((x, y), (x + 1, y)) and
                G.has_edge((x, y), (x, y + 1)) and
                G.has_edge((x, y + 1), (x + 1, y + 1)) and
                G.has_edge((x + 1, y), (x + 1, y + 1))):
            G.remove_edge((x, y), (x, y + 1))

edge_removed = True
while edge_removed:
    # # Remove edges from nodes with degree 1
    edge_removed = False
    for node in nodes:
        if G.degree[node] == 1:
            edge = list(G.edges(node))
            # edge surely has degree 1
            G.remove_edges_from(edge)
            edge_removed = True


def graph_to_img(G):
    w = max(G.nodes, key=lambda x: x[0])[0] + 1
    h = max(G.nodes, key=lambda x: x[1])[1] + 1
    img = np.zeros((h, w))

    for node, deg in G.degree():
        if deg > 0:
            x, y = node
            img[y, x] = 255

    return img

from postman_problems.solver import cpp

for e in list(G.edges()):
    G.remove_edge(*e)
    G.add_edge(*e, distance=1, id=str(e))

G.remove_nodes_from(list(nx.isolates(G)))
c, g = cpp(G)
edgelist = [(e1, e2) for e1, e2, _, _ in c]

#TODO: somehow avoid the last stop being too close to the first one?
stops = [n1 for n1, n2 in edgelist[::60]]

# pos is {(0,0): (0,255), (0,1): (0,254), (0,2): (0,253), ...,
# (255,254): (255,1), (255,255): (255,0)}
# Need to reverse order of y in the positions since img has origin top left
# and pyplot has origin bottom left
# nodes = list(G.nodes())
# poses = [(x, 255-y) for x,y in nodes]
# pos = dict(zip(nodes, poses))#list(product(range(w), range(h)[::-1]))))
# nx.draw_networkx(G, pos=pos, with_labels=False, node_size=1, node_color='w', width=2)
# nx.draw_networkx(G, pos=pos, edgelist=c, with_labels=False, node_size=1, node_color='w', edge_color ='r', width=2)
# #plt.show()
# import sys
# sys.path.insert(0,'C:\\Program Files (x86)\\Graphviz2.38\\bin')
# from postman_problems import viz
# viz.make_circuit_images(c, G, '../../output/path')
# viz.make_circuit_video('../../output/path', 'asd')
print('deb')
