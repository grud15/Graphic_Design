"""
The objective of this code is to take any image and give it a hand-drawn, graphic design look.

To do this, the code identifies the RGB values (aka colors) for every pixel in the image and determines the most
common RGB values. Then, the code re-identifies RGB values for every pixel and this time, the
code assigns a previously determined common color to the pixel based on which common color is closest
to the RGB value of that pixel.

Once the edit is applied, a side-by-side picture of the original and new image is shown.
"""

from simpleimage import SimpleImage
from statistics import mode, StatisticsError

DEFAULT_IMAGE = 'images/emily.jpg'

# Constants for edit: RECOLOR1 10, 40, 0.05

"""
The larger this constant, the more colors similar to main color are removed from list_of_all_colors.
This creates a shorter, more diversified list of main colors (on RGB scale 0-255)
"""
RGB_ERROR_RANGE = 10

"""
The larger this constant, the more pixels are converted to a main color similar to it.
"""
RGB_BIG_ERROR_RANGE = 40

"""
The larger this constant, the more hues of main color are removed from list_of_all_colors.
 This creates a shorter, more diversified list of main colors (on RGB scale 0-255)
"""
RATIO_ERROR_RANGE = 0.05


def main():
    file = get_file()

    original = SimpleImage(file)
    original.show()

    list_of_main_colors = find_main_colors(original)
    gd = edit(original, list_of_main_colors)
    gd.show()

    original = SimpleImage(file)
    final = before_after(original, gd)
    final.show()


def find_main_colors(original):
    list_of_all_colors = []
    list_of_main_colors = []
    for pixel in original:
        r = pixel.red
        g = pixel.green
        b = pixel.blue
        data_point = (r, g, b)
        list_of_all_colors.append(data_point)
    while True:
        try:
            # To get main color, find the most occurring RGB value (mode) in list of all colors
            main_color = mode(list_of_all_colors)
            list_of_main_colors.append(main_color)
            # Update list of all colors to exclude the most occurring color
            list_of_all_colors = [data_point for data_point in list_of_all_colors if data_point != main_color]
            # Update list of all colors to exclude colors near the most occurring color
            list_of_all_colors = [data_point for data_point in list_of_all_colors if
                                  not_near_main_color_1(data_point, main_color)]
            # Update list of all colors to exclude colors with similar hues of the most occurring color
            list_of_all_colors = [data_point for data_point in list_of_all_colors if
                                  not_near_main_color_2(data_point, main_color)]
        except StatisticsError:  # When there is no more mode in the list of all colors, break the loop
            break
    return list_of_main_colors  # We have the main colors in the image!


# The r, g, AND b values of a pixel had to fall outside a given range to remain in list of all colors
def not_near_main_color_1(data_point, main_color):
    if (data_point[0] < main_color[0] - RGB_ERROR_RANGE) or (data_point[0] > main_color[0] + RGB_ERROR_RANGE):
        if (data_point[1] < main_color[1] - RGB_ERROR_RANGE) or (data_point[1] > main_color[1] + RGB_ERROR_RANGE):
            if (data_point[2] < main_color[2] - RGB_ERROR_RANGE) or (data_point[2] > main_color[2] + RGB_ERROR_RANGE):
                return True


# The r, g, AND b ratios of a pixel had to fall outside a given range to remain in list of all colors
# If the ratios of two colors are similar, they merely differ in hue i.e. darker (1, 2, 1) & lighter (20, 43, 22)
def not_near_main_color_2(data_point, main_color):
    sum_data_point = (data_point[0] + data_point[1] + data_point[2]) + .01
    data_point_ratio = (data_point[0] / sum_data_point, data_point[1] / sum_data_point, data_point[2] / sum_data_point)
    sum_main_color = (main_color[0] + main_color[1] + main_color[2]) + .01
    main_color_ratio = (main_color[0] / sum_main_color, main_color[1] / sum_main_color, main_color[2] / sum_main_color)
    if (data_point_ratio[0] <= main_color_ratio[0] - RATIO_ERROR_RANGE) or \
            (data_point_ratio[0] >= main_color_ratio[0] + RATIO_ERROR_RANGE):
        if (data_point_ratio[0] <= main_color_ratio[0] - RATIO_ERROR_RANGE) or \
                (data_point_ratio[0] >= main_color_ratio[0] + RATIO_ERROR_RANGE):
            if (data_point_ratio[0] <= main_color_ratio[0] - RATIO_ERROR_RANGE) or \
                    (data_point_ratio[0] >= main_color_ratio[0] + RATIO_ERROR_RANGE):
                return True


def edit(original, list_of_main_colors):
    done = assign_main_colors(original, list_of_main_colors)
    return done


def assign_main_colors(original, list_of_main_colors):
    # Take the list of main colors and put them into a dictionary so they can be accessed
    num_of_colors = len(list_of_main_colors)
    color_dict = dict()
    for i in range(num_of_colors):
        color_dict["color " + str(i + 1)] = list_of_main_colors[i]
    print(color_dict)
    # Again, find RGB values for every pixel. This time, replace pixel with closest main color
    for pixel in original:
        r = pixel.red
        g = pixel.green
        b = pixel.blue
        data_point = (r, g, b)
        recolor1(data_point, color_dict, pixel)
    return original


# If r, g, AND b values fall between specified range for a main color, change that pixel to the main color
# Will run through main colors until there is a match for all values
# Range constant is relatively large so that every pixel is replaced by main color
def recolor1(data_point, color_dict, pixel):
    for k in color_dict:
        if (color_dict[k])[0] - RGB_BIG_ERROR_RANGE < data_point[0] < (color_dict[k])[0] + RGB_BIG_ERROR_RANGE:
            if (color_dict[k])[1] - RGB_BIG_ERROR_RANGE < data_point[1] < (color_dict[k])[1] + RGB_BIG_ERROR_RANGE:
                if (color_dict[k])[2] - RGB_BIG_ERROR_RANGE < data_point[2] < (color_dict[k])[2] + RGB_BIG_ERROR_RANGE:
                    pixel.red = (color_dict[k])[0]
                    pixel.green = (color_dict[k])[1]
                    pixel.blue = (color_dict[k])[2]

# Creates a side-by-side picture of the original and new image
def before_after(original, gd):
    width = original.width
    height = original.height
    sbs_image = SimpleImage.blank(2 * width, height)
    for y in range(height):
        for x in range(width):
            before = original.get_pixel(x, y)
            sbs_image.set_pixel(x, y, before)
            after = gd.get_pixel(x, y)
            sbs_image.set_pixel((width + x), y, after)
    return sbs_image


# Read image file path from user, or use the default file
def get_file():
    filename = input('Enter image file (or press enter for default): ')
    if filename == '':
        filename = DEFAULT_IMAGE
    return filename


if __name__ == '__main__':
    main()
