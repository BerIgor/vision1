import numpy as np
import cv2
import sklearn.preprocessing
from hw4 import utils
from hw4 import style_transfer
from hw4 import texture_transfer


def pixel_move(image, image_lap, point):
    x, y = point

    d_section = utils.get_sub_image(image_lap, point, 1)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(d_section)  # the points returned are in r,c format

    r, c = max_loc
    r -= 1
    c -= 1

    r = y + r
    c = x + c

    return image[r, c, :]


def image_move(image):
    # grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # lap = cv2.Laplacian(grey, cv2.CV_64F)

    moved_image = image.copy()
    for i in range(30):
        grey = cv2.cvtColor(moved_image, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(grey, cv2.CV_64F)
        for x in range(1, image.shape[1] - 1):
            for y in range(1, image.shape[0] - 1):
                moved_image[y, x, :] = pixel_move(image, lap, (x, y))
        cv2.imwrite(utils.get_pwd() + '/our_results/image_move' + str(i) + '.jpg', moved_image)

    return


def calc_motion_mat(image):

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(grey, cv2.CV_64F)

    movement_mat = np.zeros((image.shape[0], image.shape[1], 2))
    for x in range(1, image.shape[1] - 1):
        for y in range(1, image.shape[0] - 1):
            d_section = utils.get_sub_image(lap, (x, y), 1)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(d_section)  # the points returned are in r,c format

            r, c = max_loc
            r -= 1
            c -= 1

            r = y + r
            c = x + c
            movement_mat[y, x, 0] = r
            movement_mat[y, x, 1] = c
    return movement_mat


def image_move2(image, motion_matrix):

    moved_image = image.copy()

    for x in range(1, image.shape[1] - 1):
        for y in range(1, image.shape[0] - 1):
            src_r = int(motion_matrix[y, x, 0])
            src_c = int(motion_matrix[y, x, 1])
            moved_image[y, x, :] = image[src_r, src_c, :]

    return moved_image


if __name__ == "__main__":

    full_frame_list = utils.get_all_frames(utils.get_pwd() + '/our_data/ariel.avi')
    full_frame_mask_list = utils.get_all_frames(utils.get_pwd() + '/our_data/mask.avi')

    rows, cols, _ = np.shape(full_frame_list[0])

    background = cv2.imread(utils.get_pwd() + '/our_data/starry_bg.jpg')
    background = cv2.resize(background, dsize=(cols, rows))  # TODO: is this good?
    texture = cv2.imread(utils.get_pwd() + '/our_data/style.jpg')

    motion_mat = calc_motion_mat(full_frame_list[0])

    new_frame_list = list()

    background_moved = background
    for i in range(min(len(full_frame_mask_list), len(full_frame_list))):

        # gather images
        background_moved = image_move2(background_moved, motion_mat)
        frame = full_frame_list[i]
        mask = full_frame_mask_list[i]

        _, mask = cv2.threshold(mask, 127, 1, cv2.THRESH_BINARY)

        var = cv2.Laplacian(frame, cv2.CV_64F).var()
        if var < 50:
            continue  # skip this frame

        # handle masking
        fg = np.multiply(mask, frame)
        mask_inv = 1 - mask
        bg = np.multiply(mask_inv, background_moved)

        new_frame = fg + bg
        new_frame_list.append(new_frame)

    utils.make_normal_video(utils.get_pwd() + '/our_results/combined.avi', new_frame_list)

    exit()
    background_resized = cv2.resize(background, dsize=(cols, rows))
    background_resized = background_resized / 255
    # background_resized = cv2.GaussianBlur(background_resized, ksize=(31, 31), sigmaY=0, sigmaX=0)

    texture_resized = cv2.resize(texture, dsize=(cols, rows))
    # texture_resized = cv2.GaussianBlur(texture_resized, ksize=(11, 11), sigmaX=0, sigmaY=0)
    texture_resized = texture_resized / 255
    texture_resized = np.clip(texture_resized, a_max=1.0, a_min=0.0)

    frame_resized = cv2.resize(frame, dsize=(cols, rows))
    # texture_resized = cv2.GaussianBlur(texture_resized, ksize=(11, 11), sigmaX=0, sigmaY=0)
    frame_resized = frame_resized / 255
    frame_resized = np.clip(frame_resized, a_max=1.0, a_min=0.0)
    # bg_path = utils.get_pwd() + '/our_data/starry_bg.jpg'
    # te_path = utils.get_pwd() + '/our_data/style.jpg'
    # tt = texture_transfer.TextureTransferTool(te_path, bg_path, 64, 64, 3, 0.3, 0.3, 0.8, 0.005, 0)
    # res = tt.start(utils.get_pwd() + '/res.jpg')

    res = style_transfer.transfer(background_resized, texture_resized)
    # utils.cvshow("orig", background)
    utils.cvshow("res", res)

    exit()




    counter = 0
    for frame in full_frame_list:
        var = cv2.Laplacian(frame, cv2.CV_64F).var()
        if var < 50:
            counter += 1

    print(counter)
    """
    frame = full_frame_list[0]
    face_template = cv2.imread(utils.get_pwd() + '/our_data/face_template.bmp')
    res = cv2.matchTemplate(frame, face_template, cv2.TM_SQDIFF_NORMED)
    utils.cvshow("res", res)
    """