#!/usr/bin/env python3

import math
from types import NoneType

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    return image['pixels'][y*image['width']+x]


def advanced_get_pixel(image, x, y, b_behavior):
    '''
    Apply different methods for getting pixels and account for edge behavior

    Parameters:
    *image (dict): contains height, width, and list of pixels for the image
    *x (int): x location of the pixel on image
    *y (int): y location of the pixel on image

    Returns:
    A pixel value (int) at the location (x, y)
    '''
    width = image['width']
    height = image['height']

    #converts from 2d indices to a list of indices
    index = y*width+x

    #any thing outside of the range is black
    if b_behavior == "zero":
        if x < 0 or y < 0:
            return 0
        if x >= width or y >= height:
            return 0
    
    elif b_behavior == "extend":
        #whenever x and y is negative, then use the block at 0 indice
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        #whenever more than bound, use the edge row and col
        if x >= width:
            x = width-1
        if y >= height:
            y = height-1
        index = y*width+x
   
    elif b_behavior == "wrap":
        #keep adding to negative numbers until positive
        while x < 0:
            x+=width
        while y < 0:
            y+=height

        #use mod operator
        if x >= width:
            x = x%width
        if y >=height:
            y = y%height
        index = y*width+x
    else:
        pass
    
    return image['pixels'][index]
    


def set_pixel(image, x, y, c):
    image['pixels'][y*image['width']+x] = c
    


def apply_per_pixel(image, func):
    '''
    Apply a function to change color of each pixel

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image

    *func: function for changing the color values

    Returns:
    A new dictionary after changing image according to the function
    '''
    #create new dictionary so old one is not modified
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [255]*(image['height']*image['width']),
    }
    for x in range(image['width']):
        for y in range(image['height']):
            #get pixel val and apply function
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    '''
    Invert the colors of the image (255-c)

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image

    Returns:
    A new dictionary after changing image according to the function
    '''
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    kernel (dict): contains two key/val pairs
        *'dimension' (int): side length of the kernel
        *'list_vals; (list): pixel vals for kernel from left to right, top to bottom in order
    """
    dimension = kernel['dimension']
    
    if boundary_behavior not in 'zeroextendwrap':
        return None
    def func(x, y):
        L_indices = []

        #get a list of indice locations next to position (x, y)
        distance_away = (int)((dimension-1)/2)
        for j in range(y-distance_away, y+distance_away+1):
            for i in range(x-distance_away, x+distance_away+1):
            
                L_indices.append((i,j))

        #get the pixel val at each of those locations 
        L_pixel = []
        for element in L_indices:
            L_pixel.append(advanced_get_pixel(image, element[0], element[1], boundary_behavior))
       
        #calculate the value using linear combination of kernel and pixel
        pixel_val = 0
        for i,j in zip(L_pixel, kernel['list_vals']):
            pixel_val += i*j
        return pixel_val
    
    #create a new image dictionary
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [255]*(image['height']*image['width']),
    }
    #pass in vals for updating the image
    for x in range(image['width']):
        for y in range(image['height']):
            newcolor = func(x, y)
            set_pixel(result, x, y, newcolor)
    return result


        


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    list_pixels = image['pixels']
    for i in range(len(list_pixels)):
        list_pixels[i] = round(list_pixels[i])
        if list_pixels[i] < 0:
            list_pixels[i] = 0
        if list_pixels[i] > 255:
            list_pixels[i] = 255
    
    return {'height': image['height'], 'width': image['width'], 'pixels': list_pixels}

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    def create_kernel(n):
        list_vals = [1/(n*n)]*n*n
        return {'dimension': n, 'list_vals': list_vals}
    image_copy = {'height': image['height'], 'width': image['width'], 'pixels': image['pixels'].copy()}
    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    result = correlate(image_copy, create_kernel(n), 'extend')

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(result)


def sharpened(image, n):
    '''
    Apply a sharpening effect to image with kernel size n 

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image
    * n (int): the size of the kernel

    Returns:
    A new dictionary after sharpening the image
    '''
    B_xy = blurred(image, n)['pixels']
    
    S_xy= []
    for i, j in zip(image['pixels'], B_xy):
        S_xy.append(2*i-j)

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': S_xy
    }
    return round_and_clip_image(result)

def edges(image):
    '''
    Apply a Sobel operator filter useful for detecting edges in images

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image

    Returns:
    A new image dictionary after applying the Sobel operator filter

    '''
    kx = {'dimension': 3, 'list_vals': [-1, 0, 1, -2, 0, 2, -1, 0, 1]}
    ky = {'dimension': 3, 'list_vals': [-1, -2, -1, 0, 0, 0, 1, 2, 1]}
    O_x = correlate(image, kx, "extend")
    O_y = correlate(image, ky, 'extend')
    
    result = []
    for i,j in zip(O_x['pixels'], O_y['pixels']):
        result.append(round((i**2+j**2)**(1/2)))
        
    O_xy = {'height': image['height'], 'width': image['width'], 'pixels': result}
    
    

    return round_and_clip_image(O_xy)

# COLOR FILTERS

def color_split(image):
    '''
    Split the color image RGB values into separate lists

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image

    Returns a tuple of lists for each R, G, and B value in a color image
    '''
    r_pixels = []
    g_pixels = []
    b_pixels = []
    red = {'height': image['height'], 'width': image['width'], 'pixels':r_pixels }
    green = {'height': image['height'], 'width': image['width'], 'pixels': g_pixels}
    blue = {'height': image['height'], 'width': image['width'], 'pixels': b_pixels}

    for element in image['pixels']:
        r_pixels.append(element[0])
        g_pixels.append(element[1])
        b_pixels.append(element[2])
    
    return (red, green, blue)

def color_combine(image, red, green, blue):
    '''
    Join the RGB value lists together to form a color RGB tuple list

    Parameters:
    * image (dict): contains height, width, and list of pixels for the image

    Returns a dictionary of the filtered image
    '''
    result = []
    for i, j, k in zip(red['pixels'], green['pixels'], blue['pixels']):
        result.append((i, j, k))
    return {'height': image['height'], 'width': image['width'], 'pixels': result}

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def new_filt(image):
        red, green, blue = color_split(image)
        red_result = filt(red)
        green_result = filt(green)
        blue_result = filt(blue)

        return color_combine(image, red_result, green_result, blue_result)
    return new_filt

def make_blur_filter(n):
    def blur(image):
        return blurred(image, n)
    return blur

def make_sharpen_filter(n):
    def sharpen(image):
        return sharpened(image, n)
    return sharpen

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter_cas(image):
        for filter in filters:
            image = filter(image)
        return image
    return filter_cas

#adjust the brightness of the image by value n
def filter_brightness(image, n):
    red, green, blue = color_split(image)
    colors = [red['pixels'], green['pixels'], blue['pixels']]
    
    for color in colors:
        for i in range(len(color)):
            color[i] = color[i]+ n

    return color_combine(image, red, green, blue)
    

    
    
# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    bluegill = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(bluegill), "inverted_bluegill.png")
    
    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # list_vals = [0]*13*13
    # list_vals[26] = 1
    # kernel = {'dimension': 13, 'list_vals': list_vals}
    # save_greyscale_image(correlate(pigbird, kernel, 'zero'), "pigbird_zero.png")
    # save_greyscale_image(correlate(pigbird, kernel, 'extend'), "pigbird_extend.png")
    # save_greyscale_image(correlate(pigbird, kernel, 'wrap'), "pigbird_wrap.png")
    # test_image = {'height': 2, 'width': 2, 'pixels': [-1, -2.3, 300, 255.5]}
    # print(round_and_clip_image(test_image))

    # cat = load_greyscale_image('test_images/cat.png')
    # save_greyscale_image(blurred(cat, 13), 'cat_blurred.png')
    # save_greyscale_image(blurred(cat, 13), 'cat_blurred_zero.png')
    # save_greyscale_image(blurred(cat, 13), 'cat_blurred_wrap.png')
    # print(load_greyscale_image("test_images/mushroom.png"))

    # python = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(python, 11), "python_sharpened.png")

    # construct = load_greyscale_image('test_images/construct.png')
    # save_greyscale_image(edges(construct), 'construct_edge.png')

    # im = load_greyscale_image('test_images/centered_pixel.png')
    # save_greyscale_image(edges(im), 'centered_pixel_edges.png')
    # print(edges(im))

    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # save_color_image(color_inverted(load_color_image('test_images/cat.png')), 'cat_color_inverted.png')

    # blur_filter = make_blur_filter(9)
    # save_color_image(blur_filter(load_color_image('test_images/python.png')), 'python_color_blurred.png')

    #sharpen_filter = make_sharpen_filter(7)
    #save_color_image(sharpen_filter(load_color_image('test_images/sparrowchick.png')), 'sparrowchick_color_blurred.png')

    # im = load_color_image('test_images/cat.png')
    # print(im)

    mushroom = load_color_image('test_images/mushroom.png')
    save_color_image(filter_brightness(mushroom, 100), 'mushroom_constrast_100.png')

    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    frog = load_color_image('test_images/frog.png')
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    save_color_image(filt(frog), 'frog_filter.png')