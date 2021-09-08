from PIL import Image
from plantcv import plantcv as pcv
import cv2
import numpy as np
import uuid
import os

class plantcv_interface:
    def prepare_image(filename):
        img = cv2.imread(filename)

        # Converts color to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, (36, 30, 30,), (86, 255, 255))

        imask = mask > 0

        green = np.zeros_like(img, np.uint8)

        green[imask] = img[imask]

        cv2.imwrite(filename, green)

    def info_image(filename):
        
        img, path, unused = pcv.readimage(filename = filename)

        # Converts image from RGB to HSV
        split_image = pcv.rgb2gray_hsv(rgb_img = img, channel = 's')

        # Creates a binary image based on light
        binary_image = pcv.threshold.binary(gray_img = split_image, threshold = 85, max_value = 255, object_type='light')

        # Applies a median blur filter
        blurred_image = pcv.median_blur(gray_img = binary_image, ksize = 5)

        # Applies a gaussian blur filter
        gaussian_img = pcv.gaussian_blur(img = binary_image, ksize = (5, 5), sigma_x = 0, sigma_y = None)

        # Converts image from RGB to LAB
        # https://plantcv.readthedocs.io/en/latest/rgb2lab/
        grayscale_img = pcv.rgb2gray_lab(rgb_img = img, channel = 'b')

        # Creates a binary image based on light
        binary_image2 = pcv.threshold.binary(gray_img = grayscale_img, threshold = 160, max_value = 255, object_type = 'light')

        # Logically OR two binary images together
        combined_binary_image = pcv.logical_or(bin_img1 = split_image, bin_img2 = binary_image2)

        # Applies binary mask to image
        masked_image = pcv.apply_mask(img = img, mask = combined_binary_image, mask_color = 'white')

        # Converts image from RGB to LAB
        mask1 = pcv.rgb2gray_lab(rgb_img = masked_image, channel = 'a')
        mask2 = pcv.rgb2gray_lab(rgb_img = masked_image, channel = 'b')

        # Creates a binary image based on light or dark
        binary_image3 = pcv.threshold.binary(gray_img = mask1, threshold = 115, max_value = 255, object_type = 'dark')
        binary_image4 = pcv.threshold.binary(gray_img = mask1, threshold = 135, max_value = 255, object_type = 'light')
        binary_image5 = pcv.threshold.binary(gray_img = mask2, threshold = 128, max_value = 255, object_type = 'light')

        # Logically OR three binary images together
        combined_binary_image2 = pcv.logical_or(bin_img1 = binary_image3, bin_img2 = binary_image5)
        combined_binary_image3 = pcv.logical_or(bin_img1 = binary_image4, bin_img2 = combined_binary_image2)

        # Filters out bright noise from an image
        filtered_image = pcv.opening(gray_img = combined_binary_image3)

        # Logically XOR two binary images together
        xor_image = pcv.logical_xor(bin_img1 = binary_image3, bin_img2 = binary_image5)

        # Identifies objects and fills objects that are less than specified size
        filled_image = pcv.fill(bin_img = combined_binary_image3, size = 200)

        # Filters out dark noise from an image
        filtered_image2 = pcv.closing(gray_img = filled_image)

        # Applies a binary mask to an image
        masked_image2 = pcv.apply_mask(img = masked_image, mask = filled_image, mask_color = 'white')

        # Find objects within the image
        objects, object_hierachy = pcv.find_objects(img = masked_image2, mask = filled_image)

        # Combine objects together
        grouped_object, image_mask = pcv.object_composition(img = masked_image2, contours = objects, hierarchy = object_hierachy)

        # Shape Analysis
        analysis_image = pcv.analyze_object(img = masked_image2, obj = grouped_object, mask = image_mask, label = 'default')

        pcv.analyze_color(rgb_img = masked_image2, mask = image_mask)

        url = os.getcwd() +'\\images\\' + str(uuid.uuid4()) + '.json'

        width = pcv.outputs.observations['default']['width']['value']
        height = pcv.outputs.observations['default']['height']['value']

        r = pcv.outputs.observations['default']['red_frequencies']['value']
        g = pcv.outputs.observations['default']['green_frequencies']['value']
        b = pcv.outputs.observations['default']['blue_frequencies']['value']


        color = {
            "r" : r,
            "g" : g,
            "b" : b
            }

        return_data = {
            "width" : width,
            "height" : height,
            "color" : color
            }

        #pcv.outputs.save_results(url, outformat = "json")

        pcv.outputs.clear()

        return return_data