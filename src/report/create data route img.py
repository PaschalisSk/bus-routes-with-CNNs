from PIL import Image

im = Image.open('../../figures/misc/routeroadimgs/1.jpg')
route = im.crop((0, 0, 256, 256))
road = im.crop((256, 0, 512, 256))

route_trnsp = route.convert("RGBA")
datas = route_trnsp.getdata()

newData = []
for item in datas:
    if item[0] < 220 and item[1] < 220 and item[2] < 220:
        newData.append((255, 255, 0, 255))
    else:
        newData.append((255, 255, 255, 0))
route_trnsp.putdata(newData)

bg = road.copy()
bg.paste(route_trnsp, (0, 0), route_trnsp)
route.save('../../figures/misc/routeroadimgs/route.png')
road.save('../../figures/misc/routeroadimgs/road.png')
bg.save('../../figures/misc/routeroadimgs/comb.png')
print('deb')
