import numpy as np
import math
import cv2


def changeContrast(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    # Apply affine transformation to the image using the rotation matrix
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def compute_skew(src_img, center_thres):
    # Check the number of dimensions in the source image
    if len(src_img.shape) == 3:
        h, w, _ = src_img.shape  # For color images
    elif len(src_img.shape) == 2:
        h, w = src_img.shape  # For grayscale images
    else:
        print("unsupported image type")  # Unsupported image type

    # Apply median blur to the source image
    img = cv2.medianBlur(src_img, 3)

    # Detect edges using the Canny edge detector
    edges = cv2.Canny(
        img, threshold1=30, threshold2=100, apertureSize=3, L2gradient=True
    )

    # Detect lines using the Hough Line Transform
    lines = cv2.HoughLinesP(
        edges, 1, math.pi / 180, 30, minLineLength=w / 1.5, maxLineGap=h / 3.0
    )

    # If no lines are detected, return a default skew angle of 1
    if lines is None:
        return 1

    # Initialize variables to find the minimum line position
    min_line = 100
    min_line_pos = 0

    # Iterate through the detected lines
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            # Calculate the center point of the line
            center_point = [((x1 + x2) / 2), ((y1 + y2) / 2)]

            # Apply center threshold if specified
            if center_thres == 1:
                if center_point[1] < 7:
                    continue

            # Update the minimum line position if the current line is closer to the top
            if center_point[1] < min_line:
                min_line = center_point[1]
                min_line_pos = i

    # Initialize variables to calculate the average angle
    angle = 0.0
    nlines = lines.size
    cnt = 0

    # Calculate the angle of the minimum line position
    for x1, y1, x2, y2 in lines[min_line_pos]:
        ang = np.arctan2(y2 - y1, x2 - x1)

        # Exclude extreme rotations
        if math.fabs(ang) <= 30:
            angle += ang
            cnt += 1

    # If no valid lines are found, return a default skew angle
    if cnt == 0:
        return 0.0
    return (angle / cnt) * 180 / math.pi


def deskew(src_img, change_cons, center_thres):
    if change_cons == 1:
        return rotate_image(
            src_img, compute_skew(changeContrast(src_img), center_thres)
        )
    else:
        return rotate_image(src_img, compute_skew(src_img, center_thres))
