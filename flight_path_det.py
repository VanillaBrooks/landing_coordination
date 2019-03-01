import pprint, pymysql, time
from PIL import Image

class PlanePath():
    def __init__(self, path_to_image):
        left, upper, right, lower = 420, 0, 1500, 1080
        self.path = path_to_image
        self.image = Image.open(self.path).crop((left, upper, right, lower))
        self.image.convert('RGB')

    def find_flight_path(self):
        self.width, self.height = self.image.size
        self.pixel = self.image.load()

        self.pixel_list = []
        for w in range(self.width):
            for h in range(self.height):
                
                color_values = self.pixel[w, h]
                if len(color_values) ==4:
                    r, g, b, alpha = color_values
                else:
                    r, g, b = color_values
                if r > 150 and g < 30 and b < 30:
                    self.pixel[w, h] = (0, 0, 0)
                    self.pixel_list.append((w, h))

        self.image.save(self.path)
    def plane_slope(self):
        xcord, ycord = list(zip(*self.pixel_list))
        pixel_x1 = min(xcord)
        pixel_x2 = max(xcord)

        possibley = [[], []]
        for x, y in self.pixel_list:
            if x == pixel_x1:
                possibley[0].append(y)
            elif x == pixel_x2:
                possibley[1].append(y)

        pixel_y1 = min(possibley[0])
        pixel_y2 = min(possibley[1])

        self.x1, self.y1 = self.scale_points(pixel_x1,pixel_y1, 'cm')
        self.x2, self.y2 = self.scale_points(pixel_x2,pixel_y2, 'cm')

        self.slope = ((self.y1 - self.y2) / (self.x1 - self.x2))
        self.yintercept = (self.slope * (-1 * self.x1)) + self.y1
    def scale_points(self, xpoint, ypoint, final_unit):
        mapdim = 816000 / 2
        x_cm_to_pix = self.width / mapdim
        y_cm_to_pix = self.height / mapdim

        x_pix_to_cm = mapdim / self.width
        y_pix_to_cm = mapdim / self.height

        if final_unit == 'cm':
            return xpoint * x_pix_to_cm, ypoint * y_pix_to_cm
        elif final_unit == 'pixels':
            return xpoint * x_cm_to_pix, ypoint * y_cm_to_pix
