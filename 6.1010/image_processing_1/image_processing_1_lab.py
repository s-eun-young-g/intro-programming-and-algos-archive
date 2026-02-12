#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math
import os
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


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


# HELPER FUNCTIONS


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


# FILTERS


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


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
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
    by the "mode" parameter.
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


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # print("Loading bluegill file...")
    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(bluegill), "inverted_bluegill.png")
    """
    pigbird_kernel = {
        "size": 13,
        "values": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
    print("Loading pigbird file...")
    pigbird = load_greyscale_image("test_images/pigbird.png")
    save_greyscale_image(correlate(pigbird, pigbird_kernel, "zero"), "correlated_pigbird_zero.png")
    save_greyscale_image(correlate(pigbird, pigbird_kernel, "extend"), "correlated_pigbird_extend.png")
    save_greyscale_image(correlate(pigbird, pigbird_kernel, "wrap"), "correlated_pigbird_wrap.png")
    """
    # centered_pixel = load_greyscale_image("test_images/centered_pixel.png")
    # print(f"height: {centered_pixel["height"]}, width: {centered_pixel["width"]}, pixels: {centered_pixel["pixels"]}")
    # print("Loading cat file...")
    # cat = load_greyscale_image("test_images/cat.png")
    # save_greyscale_image(blurred(cat, 13), "blurred_cat_extend.png")
    # print("Loading python file...")
    # python = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(python, 11), "sharpened_python.png")
    # print("Loading construct file...")
    construct = load_greyscale_image("test_images/construct.png")
    save_greyscale_image(edges(construct), "edges_construct.png")
    # edges_centered_pixel = edges(centered_pixel)
    # print(f"height: {edges_centered_pixel["height"]}, width: {edges_centered_pixel["width"]}, pixels: {edges_centered_pixel["pixels"]}")
