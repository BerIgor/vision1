import cv2 as cv
import numpy as np
from hw3 import utils


def perform(frame_list):
    frames_with_features = list()
    indices = [0, 3, 5]
    frame_list = [frame_list[x] for x in indices]
    for frame in frame_list:
        features, frame_after_harris = harris_and_nms(frame, nms_window=35)
        frames_with_features.append(frame_after_harris)

    rframes = utils.rotate_frames(frames_with_features)
    stacked_frames = utils.hstack_frames(rframes, reverse=True)

    cv.imwrite(utils.get_pwd() + "/q2" + ".jpg", stacked_frames)


# input: image that was prepped for harris detection
def harris_detect(image):
    res = cv.cornerHarris(image, 5, 3, 0.04)
    return res


# input: image is an rgb image
def prep_image_for_harris(image):
    gray_image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    gray_image = np.float32(gray_image)
    return gray_image


def harris_and_nms(image, nms_window=30):
    """
    Extracts feature point from image using harris corner detector + non-maximum suppression
    :param image - image to find edges in
    :param nms_window - window size to perform non maximum suppression in
    :return: list of feature points (list of tuples of x,y coordinates)
    :return: The original image + the detected feature points (pixels) marked in red
    """

    # Find edges using Harris
    # print(image.shape)
    image_harris = harris_detect(prep_image_for_harris(image))
    # utils.cvshow("Harris", image_harris)

    # Set survivor nms points on image
    image_harris_nms = image.copy()
    harris_nms_mask, feature_points = non_maximum_suppression(image_harris, nms_window)
    image_harris_nms[harris_nms_mask == np.max(harris_nms_mask)] = [255, 255, 255] # Window size of 64 was tested to return roughly 100 points on our frame
    # utils.cvshow("result", image_harris_nms)

    return feature_points, image_harris_nms


def non_maximum_suppression_good(img, win_size):
    """
    Performs non-maximum suppression on the output of harris corner detector
    :param img - output of harris corner detector. grayscale image
    :param nms_window - window size to perform non maximum suppression in
    :return: A binary version of the original harris output with only the maximum points. Binary values are 0 and max(original img)
    :return: list of feature points that survived after nms
    """
    # slide a window across the image
    img_max = np.amax(img)
    suppressed_img = np.zeros(img.shape)
    max_points_list = []
    for row in range(0, img.shape[0], win_size):
        for col in range(0, img.shape[1], win_size):
            # Extract current window
            row_next = row + win_size if (row + win_size < img.shape[0]) else img.shape[0] - 1
            col_next = col + win_size if (col + win_size < img.shape[1]) else img.shape[1] - 1
            img_win = img[row:row_next, col:col_next]
            # NMS on window:
            win_max = np.amax(img_win)
            for win_row in range(img_win.shape[0]):
                for win_col in range(img_win.shape[1]):
                    if (img_win[win_row, win_col] == win_max):
                        img_win[win_row, win_col] = img_max
                        max_points_list.append([col+win_col, row+win_row]) # X - col, Y - row   << this is what we had
                        # max_points_list.append([row + win_row, col + win_col])  # X - col, Y - row
                    else:
                        img_win[win_row, win_col] = 0

            suppressed_img[row:row_next, col:col_next] = img_win

    return suppressed_img, max_points_list


def non_maximum_suppression(img, win_size):
    """
    Performs non-maximum suppression on the output of harris corner detector
    :param img - output of harris corner detector. gray scale image
    :param win_size - window size to perform non maximum suppression in
    :return: A binary version of the original harris output with only the maximum points. Binary values are 0 and max(original img)
    :return: list of feature points that survived after nms
    """
    # slide a window across the image
    img_max = np.amax(img)
    suppressed_img = np.zeros(img.shape)
    max_points_list = []
    max_values_list = list()
    for row in range(0, img.shape[0], win_size):
        for col in range(0, img.shape[1], win_size):
            # Extract current window
            row_next = row + win_size if (row + win_size < img.shape[0]) else img.shape[0] - 1
            col_next = col + win_size if (col + win_size < img.shape[1]) else img.shape[1] - 1
            img_win = img[row:row_next, col:col_next]
            # NMS on window:
            win_max = np.amax(img_win)
            for win_row in range(img_win.shape[0]):
                for win_col in range(img_win.shape[1]):
                    if img_win[win_row, win_col] == win_max:
                        max_points_list.append([col+win_col, row+win_row])  # X - col, Y - row   << this is what we had
                        max_values_list.append(img_win[win_row, win_col])
                        img_win[win_row, win_col] = img_max
                    else:
                        img_win[win_row, win_col] = 0

            suppressed_img[row:row_next, col:col_next] = img_win

    ind = np.argpartition(max_values_list, -100)[-200:]
    max_points_list = [max_points_list[i] for i in ind]

    return suppressed_img, max_points_list
