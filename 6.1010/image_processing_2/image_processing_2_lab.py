#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing 2
"""

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
import os

# import typing  # optional import
import random
from PIL import Image


# COPY THE FUNCTIONS THAT YOU IMPLEMENTED IN IMAGE PROCESSING PART 1 BELOW!
def get_pixel(image, row, col):
    """
    Retrieves the value of a specified pixel.

    Args
    image: the original input image, presented in a row-major list
    row: the row of the desired pixel
    col: the column of the desired pixel

    Returns: the pixel value
    """
    get_width = image["width"]  # creating variable to store width
    return image["pixels"][row * get_width + col]  # corrected indexing from col, row
    # Explanation of new indexing: since image["pixels"] is row major,
    # it means that row x will begin after x * width values. To account
    # for the column, once in row x, add the column number.


def set_pixel(image, row, col, color):
    """
    Sets the value of a specific pixel.

    Args
    image: the original input image, presented in a row-major list
    row: the row of the desired pixel
    col: the column of the desired pixel

    Returns: the pixel with its value updated
    """
    set_width = image["width"]  # creating variable to store width
    image["pixels"][row * set_width + col] = color  # corrected indexing from row, col


def apply_per_pixel(image, func):
    """
    Applies a function to every pixel of an image.

    Args
    image: the original input image
    func: the function to be applied to all pixels

    Returns: a new image with all of its pixels modified by func
    """
    height = image["height"]
    width = image["width"]  # declaring variables for convenience
    result = {
        "height": height,
        "width": width,  # typo - "widht" instead of "width"
        "pixels": [0]
        * (height * width),  # intialized list of proper size instead of empty list
    }
    for row in range(
        height
    ):  # corrected from col in height - height measures number of ROWS
        for col in range(
            width
        ):  # corrected from row in width - width measures number of COLS
            color = get_pixel(
                image, row, col
            )  # corrected from (image, col, row) for parameter consistency
            new_color = func(color)
            set_pixel(result, row, col, new_color)  # was initially outside inner loop
    return result


def inverted(image):
    """
    Takes an image and inverts each pixel by subtracting its value
    from 255.

    Args
    image: the original input image

    Returns: an inverted version of the original image
    """
    return apply_per_pixel(
        image, lambda color: 255 - color
    )  # should be 255 instead of 256 to invert correctly


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel is represented by a dictionary containing two keys:
    {
        "size": an int indicating the size (i.e. 3 for a 3x3 kernel, 5 for a 5x5, etc)
        "values": a list of the values of the kernel in row major order
    }

    Args
    image: the original input image
    kernel: the kernel that is to be applies to the image
    boundary_behavior: desired boundary behavior ("zero", "extend", or "wrap")

    Returns: a new image with the kernel applied
    """

    def get_pixel_check_boundary(
        image, row, col
    ):  # function to check if pixel is within
        # boundary and return correct value for out-of-bounds pixels
        if boundary_behavior == "zero":
            if (
                row < 0 or row >= height or col < 0 or col >= width
            ):  # check if out of bounds
                return 0
            else:
                return get_pixel(image, row, col)  # if not out of bounds, return pixel

        elif boundary_behavior == "extend":
            row = max(
                0, min(row, height - 1)
            )  # min statement: sets row/col to height/width if it is greater than height/width
            col = max(
                0, min(col, width - 1)
            )  # max statement: sets row/col to 0 if it's less than 0
            return get_pixel(image, row, col)

        elif boundary_behavior == "wrap":
            row = (
                row % height
            )  # mod function returns row/col if row/col is less than height/width
            col = (
                col % width
            )  # and if row/col is greater than height/width, returns row/col landed on after wrapping
            return get_pixel(image, row, col)

        else:
            return None  # return None if boundary type is invalid

    def apply_kernel_to_pixel(
        frame, row, col, kernel, result, new_color
    ):  # helper function to apply kernel to each pixel

        for kernel_row in range(
            -frame, frame + 1
        ):  # iterating through kernel as applied to an origin
            for kernel_col in range(-frame, frame + 1):
                im_kern_row = row + kernel_row
                im_kern_col = col + kernel_col
                kernel_val = kernel["values"][
                    (kernel_row + frame) * kernel_size + (kernel_col + frame)
                ]  # retrieving correct value from kernel
                new_color += kernel_val * get_pixel_check_boundary(
                    image, im_kern_row, im_kern_col
                )  # multiplying value of kernel by appropriate pixel
        set_pixel(result, row, col, new_color)

    height = image["height"]
    width = image["width"]
    result = {  # creates new image as to not modify original
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    frame = (
        kernel["size"] // 2
    )  # creates a "frame", aka how much a kernel radiates from its origin
    kernel_size = kernel["size"]

    for row in range(height):  # iterating through image
        for col in range(width):
            new_color = 0
            apply_kernel_to_pixel(frame, row, col, kernel, result, new_color)

    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.

    Args
    image: input image

    Returns: a rounded and clipped version of the image
    """
    for i in range(len(image["pixels"])):  # iterating through all pixels
        if image["pixels"][i] > 255:  # clipping if higher than 255 or lower than 0
            image["pixels"][i] = 255
        elif image["pixels"][i] < 0:
            image["pixels"][i] = 0
        else:
            image["pixels"][i] = round(image["pixels"][i])  # rounding
    return image


def box_blur(n):
    """
    Given a dimension, n, create a box blur kernel:
    a square kernel whose values are all equal and add up to 1

    Args
    n: size of the square box blur kernel

    Returns: a box blur kernel of size n
    """
    val = 1 / (n * n)
    kernel = {"size": n, "values": [val] * (n * n)}
    return kernel


def sharpen_kernel(n):
    """
    First creates a box blur kernel, then creates an appropriate
    sharpening kernel.

    Sharpening equation: S_r,c = 2I_r,c - B_r,c

    To create an appropriate kernel for this, one should multiply
    the original image by a factor of 2. This can be done using the
    identity kernel - a square kernel with 1 at the center and zeroes
    everywhere else. This can be multiplied by 2. An example
    3x3 kernel would look like:
            [0, 0, 0,
             0, 2, 0,
             0, 0, 0]
    One would then subtract the blur kernel from this. Again, using 3x3:
            [0, 0, 0,     [-1/9, -1/9, -1/9         [-1/9, -1/9, -1/9,
             0, 2, 0,  -   -1/9, -1/9, -1/9    =     -1/9, 17/9, -1/9,
             0, 0, 0]      -1/9, -1/9, -1/9]         -1/9, -1/9, -1/9]
    This final product is the appropriate sharpening kernel.

    Args
    n: size of the square sharpening kernel

    Returns: a sharpening kernel calculated as described above
    """
    kernel = box_blur(n)  # creating blur kernel

    unsharpened = {
        "size": kernel["size"],
        "values": [
            -i for i in kernel["values"]
        ],  # making every value of blur kernel negative
    }

    center = n // 2

    unsharpened["values"][center * n + center] += 2  # adding 2 to the center value

    return unsharpened


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Args
    image: original input image
    kernel_size: size of square blur box kernel

    Returns: blurred image
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    blur_kernel = box_blur(kernel_size)

    # then compute the correlation of the input image with that kernel
    result = correlate(image, blur_kernel, "extend")

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(result)


def sharpened(image, kernel_size):
    """
    Return a new image representing the result of applying sharpening, or
    unsharp masking, a manipulation represented by the equation
                    S_r,c = 2I_r,c - B_r,c
    In which I is the original image and B is the image after a box blur
    has been applied. This function takes in the original image and the
    kernel size of the blur as input and outputs a new "sharpened" image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Args
    image: original input image
    kernel_size: size of square sharpening kernel

    Returns: sharpened image
    """
    kernel = sharpen_kernel(kernel_size)  # creating appropriate kernel
    result = correlate(image, kernel, "extend")  # computing correlation
    return round_and_clip_image(result)  # rounding/clipping result


def edges(image):
    """
    Return a new image representing the result of applying the Sobel
    operator filter. Two kernels, K_1 and K_2, are applied to the original
    imagine via correlate (using the extend behavior), giving O_1 and O_2.

    Each pixel of the output of this function, O, is the square root of
    the sum of squares of corresponding pixels in O_1 and O_2.

    This operation detects and highlights the edges of the original image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Args
    image: original input image

    Returns: image with Sobel operator filter applied
    """
    k_x = {"size": 3, "values": [-1, 0, 1, -2, 0, 2, -1, 0, 1]}

    k_y = {"size": 3, "values": [-1, -2, -1, 0, 0, 0, 1, 2, 1]}

    o_x = correlate(image, k_x, "extend")  # correlating image by both k_x and k_y
    o_y = correlate(image, k_y, "extend")

    height = image["height"]
    width = image["width"]
    result = {  # creating new dictionary as to not mutate original image
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    for row in range(height):  # iterating through image
        for col in range(width):
            o_x_pix = get_pixel(o_x, row, col)
            o_y_pix = get_pixel(o_y, row, col)
            set_pixel(result, row, col, round((o_x_pix**2 + o_y_pix**2) ** (0.5)))

    return round_and_clip_image(result)


# HELPER FUNCTIONS


def get_indiv_color(image, rgb_index):
    """
    Given a color image, extract the values of just
    one of the three colors (red, green, blue) represented.

    Arguments:
    image: input color image
    rgb_index: 0 for red, 1, for green, 2 for blue

    Returns:
    a greyscale image containing the values only of
    the specified color
    """
    height = image["height"]
    width = image["width"]
    result = {  # creating new dictionary as to not mutate original image
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    for row in range(height):  # iterating through image
        for col in range(width):
            # setting pixel to be the value of individual color by indexing tuple
            set_pixel(result, row, col, image["pixels"][row * width + col][rgb_index])

    return result


def recombine_colors(red, green, blue):
    """
    Given a three greyscale images representing each
    of the three colors (red, green, blue) return a combined
    color image with rgb values given in tuples

    Arguments:
    red: greyscale image containing red values
    green: greyscale image containing green values
    blue: greyscale image containing blue values

    Returns:
    a color image containing rgb values
    """
    height = red["height"]
    width = red["width"]
    result = {  # creating new dictionary as to not mutate original image
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    for row in range(height):  # iterating through image
        for col in range(width):
            # setting pixel to be a tuple containing red, green, and blue values
            set_pixel(
                result,
                row,
                col,
                (
                    red["pixels"][row * width + col],
                    green["pixels"][row * width + col],
                    blue["pixels"][row * width + col],
                ),
            )

    return result


# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def color_filter(image):

        # separating color image into individual greyscale
        # images and applying filter to each
        red = filt(get_indiv_color(image, 0))
        green = filt(get_indiv_color(image, 1))
        blue = filt(get_indiv_color(image, 2))
        # recombining filtered greyscale images into color image
        result = recombine_colors(red, green, blue)

        return result

    return color_filter


def make_blur_filter(kernel_size):
    """
    Given the desired kernel size, return a blur filter
    that only requires "image" as input and applies
    a kernel of the desired size to the image.

    Arguments:
    kernel_size: desired size of kernel

    Returns:
    A new blur filter requiring only an image as a parameter
    """

    def new_blur(image):
        return blurred(image, kernel_size)

    return new_blur


def make_sharpen_filter(kernel_size):
    """
    Given the desired kernel size, return a sharpen filter
    that only requires "image" as input and applies
    a kernel of the desired size to the image.

    Arguments:
    kernel_size: desired size of kernel

    Returns:
    A new sharpen filter requiring only an image as a parameter
    """

    def new_sharpen(image):
        return sharpened(image, kernel_size)

    return new_sharpen


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def cascade_filt(image):
        # intialize current to be the image
        current = image
        for filter in filters:
            # loop through list of filters and apply each to current
            current = filter(current)
        return current

    return cascade_filt


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """

    # make copy of input image to not modify original
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],
    }

    for _ in range(ncols):
        # recalculate greyscale image based on current result
        grey = greyscale_image_from_color_image(result)
        # recalculate energy map based on current greyscale image
        energy = compute_energy(grey)
        # recalculate cumulative energy map
        cem = cumulative_energy_map(energy)
        # find the minimum energy seam
        seam = minimum_energy_seam(cem)
        # remove the seam from the current result
        result = image_without_seam(result, seam)

    return result


# Something of my own


def background_color_fun(image):
    """
    Given an images, modifies the "background" by randomizing
    the color of low energy pixels.

    Arguments:
    image: input color image

    Returns:
    A color image in which all background are assigned a random color
    """
    # initializing new result dictionary
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],
    }

    # converting color image to greyscale
    grey = greyscale_image_from_color_image(result)

    # computing energy map
    energy = compute_energy(grey)

    # finding average energy of image
    average_energy = sum(energy["pixels"]) / len(energy["pixels"])

    # establishing a cut off value for background pixels
    cutoff = round(average_energy * 0.5)

    # initializing background index set (note: used set instead of list for reduced complexity/run time)
    background_indices = set()

    # adding indices of all pixels under threshold to set
    for pix in range(len(energy["pixels"])):
        if energy["pixels"][pix] < cutoff:
            background_indices.add(pix)

    # getting individual colors
    red = get_indiv_color(result, 0)
    green = get_indiv_color(result, 1)
    blue = get_indiv_color(result, 2)

    # defining helper function to randomize color of greyscale input image
    def randomize_color(rgb):
        for pix in background_indices:
            rgb["pixels"][pix] = random.randint(0, 255)
        return rgb

    # applying filter to red, green, and blue channels and recombining
    result = recombine_colors(
        randomize_color(red), randomize_color(green), randomize_color(blue)
    )

    return result


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).

    Greyscale pixel values are given by 0.229 * red + 0.587 * green + 0.114 * blue

    Arguments:
    image: input image

    Returns:
    greyscale version of the image
    """

    height = image["height"]
    width = image["width"]
    result = {  # creating new dictionary as to not mutate original image
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    for row in range(height):  # iterating through image
        for col in range(width):
            # creating greyscale image by applying formula
            result["pixels"][row * width + col] = round(
                image["pixels"][row * width + col][0] * 0.299
                + image["pixels"][row * width + col][1] * 0.587
                + image["pixels"][row * width + col][2] * 0.114
            )

    return result


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function) greyscale image, computes a "cumulative energy map" as described
    in the lab 2 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    height = energy["height"]
    width = energy["width"]
    result = {  # creating new dictionary as to not mutate original image
        "height": height,
        "width": width,
        "pixels": [0] * (height * width),
    }

    for col in range(width):  # set top row of result to top row of energy
        result["pixels"][col] = energy["pixels"][col]

    for row in range(1, height):
        for col in range(width):
            if 0 < col < width - 1:  # check if pixel is on the border
                # if pixel is not, find min of pixel one up and to the left, straight up, and up and to the right
                min_cem = min(
                    result["pixels"][(row - 1) * width + (col - 1)],
                    result["pixels"][(row - 1) * width + col],
                    result["pixels"][(row - 1) * width + (col + 1)],
                )
            elif col == 0:
                # if pixel on left border, find min of pixel straight up, and up and to the right
                min_cem = min(
                    result["pixels"][(row - 1) * width + col],
                    result["pixels"][(row - 1) * width + (col + 1)],
                )
            else:
                # if pixel on right border, find min of pixel up and to the left and strauight up
                min_cem = min(
                    result["pixels"][(row - 1) * width + (col - 1)],
                    result["pixels"][(row - 1) * width + col],
                )
            # set pixel equal to the cumulation of the energy path
            result["pixels"][row * width + col] = (
                energy["pixels"][row * width + col] + min_cem
            )

    return result


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map dictionary, returns a list of the indices into
    the 'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    height = cem["height"]
    width = cem["width"]

    # find the column with the minimum cumulative energy in the last row
    min_col = 0
    last_row_start = width * (height - 1)
    min_value = cem["pixels"][last_row_start]

    for col in range(1, width):
        last_row_col = last_row_start + col
        current_value = cem["pixels"][last_row_col]
        if current_value < min_value:
            min_value = current_value
            min_col = col

    # initialize seam list with the index of the minimum value in the last row
    min_seam = [last_row_start + min_col]

    # trace min path from the bottom to the top
    for row in range(height - 1, 0, -1):
        adj_col_val = []
        if min_col > 0:
            adj_col_val.append(min_col - 1)
        adj_col_val.append(min_col)
        if min_col < width - 1:
            adj_col_val.append(min_col + 1)

        # initialize variables to store the minimum adjacent value and its col location
        min_adj_col = None
        min_adj_value = None

        # iterate over the adjacent columns
        for adj_col in adj_col_val:
            current_adj_value = cem["pixels"][(row - 1) * width + adj_col]
            if min_adj_value is None or current_adj_value < min_adj_value:
                min_adj_value = current_adj_value
                min_adj_col = adj_col

        # update min_col to the column of the minimum adjacent value
        min_col = min_adj_col
        # dd the index of the minimum adjacent pixel to the seam
        min_seam.append((row - 1) * width + min_col)

    # reverse the seam to have it from top to bottom
    min_seam.reverse()
    return min_seam


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.

    Arguments:
    image: input image
    seam: a list with the indeces of the pixel along the seam path

    Returns:
    an image with the seam removed
    """
    height = image["height"]
    width = image["width"]
    result = {
        "height": height,
        "width": width - 1,  # decrease the width by one to account for seam removed
        "pixels": [],
    }
    for row in range(height):
        start_of_row = row * width
        current_seam = seam[row]  # index of the pixel to be removed in current row
        # in each row, add every pixel of that row to the result image EXCEPT the pixel on the seam
        for col in range(width):
            current_index = start_of_row + col
            if current_index != current_seam:
                result["pixels"].append(image["pixels"][current_index])
    return result


# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES


def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for col, val in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"] - 1:
            out += "\n "
    print(out)


def print_color_values(image):
    """
    Given a color image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that RGB values will be rounded to the nearest int.
    """
    out = f"Color image with {image['height']} rows"
    out += f" and {image['width']} columns:\n"
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        for color in range(3):
            val = str(round(pixel[color]))
            space_vals.append((col, color, val))
            space_sizes[(col, color)] = max(len(val), space_sizes.get((col, color), 0))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for col, color, val in space_vals:
        space_val = val.center(space_sizes[(col, color)])
        if color == 0:
            out += f" ({space_val}"
        elif color == 1:
            out += f" {space_val} "
        else:
            out += f"{space_val})"
        if col == image["width"] - 1 and color == 2:
            out += "\n"
    print(out)


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


# if __name__ == "__main__":
# code in this block will only be run when you explicitly run your script,
# and not when the tests are being run.  this is a good place for
# generating images, etc.

# color_inverted = color_filter_from_greyscale_filter(inverted)
# inverted_color_cat = color_inverted(load_color_image("test_images/cat.png"))
# save_color_image(inverted_color_cat, "inverted_cat.png")

# blur_filter = make_blur_filter(9)
# color_blur = color_filter_from_greyscale_filter(blur_filter)
# blurred_python = color_blur(load_color_image("test_images/python.png"))
# save_color_image(blurred_python, "blurred_python.png")

# sharpen_filter = make_sharpen_filter(7)
# color_sharpen = color_filter_from_greyscale_filter(sharpen_filter)
# sharpened_sparrowchick = color_sharpen(load_color_image("test_images/sparrowchick.png"))
# save_color_image(sharpened_sparrowchick, "sharpened_sparrowchick.png")

# filter1 = color_filter_from_greyscale_filter(edges)
# filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
# filt = filter_cascade([filter1, filter1, filter2, filter1])
# cascade_frog = filt(load_color_image("test_images/frog.png"))
# save_color_image(cascade_frog, "cascade_frog.png")

# seam_twocats = seam_carving(load_color_image("test_images/twocats.png"), 100)
# save_color_image(seam_twocats, "seam_twocats.png")

# random_paris = background_color_fun(load_color_image("test_images/paris.png"))
# save_color_image(random_paris, "random_paris.png")
# image = load_color_image("test_images/flood_input.png")
# print(image["width"])
# # print(image["height"])
