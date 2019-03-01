def scale_points(width, height, point, final_unit):
    # if the image is not square there is a proble,
    if width != height:
        print('conversion in distance_converter will not be accurate because the width and height of the image are not the same')


    mapdim = 816000 / 2
    cm_to_pix = height / mapdim

    pix_to_cm = mapdim / height


    if final_unit == 'cm':
        return point * pix_to_cm
    elif final_unit == 'pixels':
        return point * cm_to_pix



# x, y , radius
if __name__ == '__main__':
    width, height = 2000, 2000
    points = [
        [400, 819, 60], #alpha
        [648,571,63], # ha tinh
        [655, 461, 27], # ha tinh docks
        [603,1274,64], # ruins
        [448, 1256, 57], # runis docks
        [425,1428, 115], # tambang
        [568, 1646, 59], # na khard
        [728, 1765, 51], # sahmee
        [870,1856, 49], # sahmee docks
        [1170, 1855, 57], # ban tai
        [1168,1694,46], # camp charlie
        [936, 1342, 63], # pai nan
        [965, 947, 88], # boot camp
        [1090, 484, 53] ,#  tat mek
        [1148, 357,58] ,# kaho
        [1239,682,79], # paradise
        [1536, 404, 121] ,# mong nai
        [1700, 768,68] ,# camp bravo
        [1729, 1110, 57], # lakawi
        [1328, 1240, 168], # quarry
        [1697, 1393, 74], # kampong
        [1635, 1719, 49], #  docks
        [1305, 1512, 93], # cave
        [1591, 921, 42], # bravo warehouse
    ]


    newpoints = []
    for row in points:
        newrow = []
        for point in row:
            newrow.append(scale_points(width, height, point, 'cm'))
        newpoints.append(newrow)
    
    for item in newpoints:
        print('[ %s, %s, %s,' % (item[0], item[1], item[2]))
