from itertools import combinations
from itertools import product

import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from postman_problems.solver import cpp
from staticmap import px_to_coords
import pandas as pd
import gtfstk


class Img2Stops:
    def __init__(self, img_path, center, zoom):
        self.img_path = img_path
        self.center = center
        self.zoom = zoom
        # Read img in grayscale format
        # Route is in black pixels
        self.img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        # Convert pixels in [0, 220] to white (255)
        # and [220, 255] to black (0)
        # Did this in order to compare with skeletonize, thinning of opencv
        _, self.img = cv2.threshold(self.img, 220, 255, cv2.THRESH_BINARY_INV)
        self.h, self.w = self.img.shape[:2]
        self.G = None
        self.path = None
        self.stops = None
        self.feed = None

    def build_graph(self):
        self.G = self._img2graph()
        self._remove_diagonials()
        self._remove_left_edges()
        self._remove_leafs()
        # Remove isolated nodes, i.e. black pixels
        self.G.remove_nodes_from(list(nx.isolates(self.G)))

    def build_path(self):
        if self.G is None:
            self.build_graph()

        self.path, _ = cpp(self.G)
        self.path = [(e1, e2) for e1, e2, _, _ in self.path]
        return self.path

    def build_stops(self, distance=50):
        if self.path is None:
            self.build_path()
        #TODO: do this better
        self.stops = [n1 for n1, n2 in self.path[::distance]]

        return self.stops

    def build_feed(self):
        if self.stops is None:
            self.build_stops()

        routes = pd.DataFrame({'route_id': [1],
                               'route_short_name': ['sample'],
                               'route_type': [3]})
        trips = pd.DataFrame({'route_id': [1],
                              'trip_id': [1],
                              'shape_id': [1]})
        shapes = pd.DataFrame()
        for i, edge in enumerate(self.path):
            lon, lat = px_to_coords(edge[0], self.w, self.h, self.zoom,
                                    self.center, tile_size=64)
            shapes = shapes.append({
                            'shape_id': 1,
                            'shape_pt_lat': lat,
                            'shape_pt_lon': lon,
                            'shape_pt_sequence': i
                        }, ignore_index=True)
        shapes['shape_id'] = pd.to_numeric(shapes['shape_id'],
                                           downcast='integer')
        shapes['shape_pt_sequence'] = pd.to_numeric(shapes['shape_pt_sequence'],
                                           downcast='integer')
        stop_times = pd.DataFrame()
        for i, _ in enumerate(self.stops):
            stop_times = stop_times.append({
                            'trip_id': 1,
                            'stop_id': i,
                            'stop_sequence': i
                        }, ignore_index=True)

        stop_times['trip_id'] = pd.to_numeric(stop_times['trip_id'],
                                           downcast='integer')
        stop_times['stop_id'] = pd.to_numeric(stop_times['stop_id'],
                                           downcast='integer')
        stop_times['stop_sequence'] = pd.to_numeric(stop_times['stop_sequence'],
                                           downcast='integer')

        stops = pd.DataFrame()
        for i, node in enumerate(self.stops):
            lon, lat = px_to_coords(node, self.w, self.h, self.zoom,
                                    self.center, tile_size=64)
            stops = stops.append({
                            'stop_id': int(i),
                            'stop_lat': lat,
                            'stop_lon': lon
                        }, ignore_index=True)
        stops['stop_id'] = pd.to_numeric(stops['stop_id'],
                                           downcast='integer')

        self.feed = gtfstk.feed.Feed(dist_units='km', routes=routes,
                                     trips=trips, shapes=shapes,
                                     stop_times=stop_times, stops=stops)
        return self.feed


    def _img2graph(self):
        h, w = self.img.shape[:2]

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
                    if self.img[y][x] == 255 and self.img[y][x + 1] == 255:
                        edges.append(((x, y), (x + 1, y)))
                if y != h - 1:
                    if self.img[y][x] == 255 and self.img[y + 1][x] == 255:
                        edges.append(((x, y), (x, y + 1)))
                # South-east diag
                if x != w - 1 and y != h - 1:
                    if self.img[y][x] == 255 and self.img[y + 1][x + 1] == 255:
                        edges.append(((x, y), (x + 1, y + 1)))
                # South-west diag
                if x != 0 and y != h - 1:
                    if self.img[y][x] == 255 and self.img[y + 1][x - 1] == 255:
                        edges.append(((x, y), (x - 1, y + 1)))
        # Add the weight for the cpp
        G.add_edges_from(edges, distance=1, id=' ')
        return G

    def get_image(self):
        img = np.zeros((self.h, self.w))

        for node, deg in self.G.degree():
            if deg > 0:
                x, y = node
                img[y, x] = 255

        return img

    def _remove_diagonials(self):
        cliques = list(nx.find_cliques(self.G))
        # For each clique which is a list of nodes
        for clique in cliques:
            # For each clique of size 3 or 4 (that's the max we can have)
            if len(clique) > 2:
                # Get all the edges of the clique
                cl_edges = list(combinations(clique, 2))
                for cl_edge in cl_edges:
                    # If they have diff x and y they are a diagonal
                    if (cl_edge[0][0] != cl_edge[1][0] and
                            cl_edge[0][1] != cl_edge[1][1]):
                        # Check if we haven't already removed that edge
                        # since a diagonial may exist both in a clique
                        # of size 3 as well as size 4
                        if self.G.has_edge(*cl_edge):
                            self.G.remove_edge(*cl_edge)

    def _remove_left_edges(self):
        nodes = list(list(self.G.nodes()))
        # Remove left edge of squares
        for node in nodes:
            x, y = node
            if x != self.w - 1 and y != self.h - 1:
                # Check if node is top left corner of square
                if (self.G.has_edge((x, y), (x + 1, y)) and
                        self.G.has_edge((x, y), (x, y + 1)) and
                        self.G.has_edge((x, y + 1), (x + 1, y + 1)) and
                        self.G.has_edge((x + 1, y), (x + 1, y + 1))):
                    self.G.remove_edge((x, y), (x, y + 1))

    def _remove_leafs(self):
        edge_removed = True
        nodes = list(list(self.G.nodes()))
        while edge_removed:
            # # Remove edges from nodes with degree 1
            edge_removed = False
            for node in nodes:
                if self.G.degree[node] == 1:
                    edge = list(self.G.edges(node))
                    # edge surely has degree 1
                    self.G.remove_edges_from(edge)
                    edge_removed = True


if __name__ == '__main__':
    img_path = 'D:/Google Drive/UoE/Thesis/output/routes/1.jpg'
    img2gtfs = Img2GTFS(img_path, (-86.820774, 33.5016975), 15)
    feed = img2gtfs.build_feed()
    from pathlib import Path
    gtfstk.feed.write_gtfs(feed, Path('D:/Google Drive/UoE/Thesis/output/gtfs/1.zip'))
    # -86.820774,33.5016975, 15
    # 33.52001788784879, -86.84274665625
    # 33.52001788784879, -86.84274665625
    # lon, lat = px_to_coords((0,0), 256, 256, 15, (-86.820774,33.5016975), tile_size=64)
    # print('deb')
