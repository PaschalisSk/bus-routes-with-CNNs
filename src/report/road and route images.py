from pathlib import Path
import os
import staticmap as sm

IMG_WIDTH = 1024
IMG_HEIGHT = IMG_WIDTH
ZOOM = 15

#'https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png'
#'https://api.maptiler.com/maps/ac954d00-25c8-4a7a-8773-40afb4d17a18/256/{z}/{x}/{y}.jpg?key=3rAT6TUcA56m3Ge4l5Xk'
# for ZOOM in range(8, 16):
#     m = sm.StaticMap(IMG_WIDTH, IMG_HEIGHT, url_template='https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png')
#     center = (-3.187127, 55.944403)
#     img = m.render(ZOOM, center)
#     img.save('../../figures/misc/edinimgs/' + ('edin' + str(ZOOM) + '1024.png'))

min_lon, min_lat = sm.px_to_coords((0, IMG_HEIGHT),
                                   IMG_WIDTH, IMG_HEIGHT,
                                   ZOOM, (-3.187127, 55.944403))
max_lon, max_lat = sm.px_to_coords((IMG_WIDTH, 0),
                                   IMG_WIDTH, IMG_HEIGHT,
                                   ZOOM, (-3.187127, 55.944403))

print('deb')
