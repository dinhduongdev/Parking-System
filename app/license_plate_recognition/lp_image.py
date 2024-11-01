from PIL import Image
import cv2
import torch
import math
import function.utils_rotate as utils_rotate
from IPython.display import display
import os
import time
import argparse
import function.helper as helper

# Set up argument parser to get the input image path from command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image")
args = ap.parse_args()

# Load YOLO models for license plate detection and OCR
yolo_LP_detect = torch.hub.load(
    "yolov5",
    "custom",
    path="model/LP_detector_nano_61.pt",
    force_reload=True,
    source="local",
)
yolo_license_plate = torch.hub.load(
    "yolov5",
    "custom",
    path="model/LP_ocr_nano_62.pt",
    force_reload=True,
    source="local",
)
yolo_license_plate.conf = 0.7  # Set confidence threshold for OCR model

# Read the input image using OpenCV
img = cv2.imread(args.image)

# Detect license plates in the image
plates = yolo_LP_detect(img, size=640)

# Convert detection results to a list of bounding boxes
list_plates = plates.pandas().xyxy[0].values.tolist()
list_read_plates = set()  # Set to store unique license plates

# If no plates are detected, try to read the plate directly from the image
if len(list_plates) == 0:
    lp = helper.read_plate(yolo_license_plate, img)
    if lp != "unknown":
        # Annotate the image with the detected license plate
        cv2.putText(img, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        list_read_plates.add(lp)
else:
    # Iterate over detected plates
    for plate in list_plates:
        flag = 0
        x = int(plate[0])  # xmin
        y = int(plate[1])  # ymin
        w = int(plate[2] - plate[0])  # xmax - xmin
        h = int(plate[3] - plate[1])  # ymax - ymin
        crop_img = img[y : y + h, x : x + w]  # Crop the detected plate from the image
        # Draw a rectangle around the detected plate
        cv2.rectangle(
            img,
            (int(plate[0]), int(plate[1])),
            (int(plate[2]), int(plate[3])),
            color=(0, 0, 225),
            thickness=2,
        )
        # Save the cropped image and read it back
        cv2.imwrite("crop.jpg", crop_img)
        rc_image = cv2.imread("crop.jpg")
        lp = ""
        # Try to read the plate with different deskewing parameters
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(
                    yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct)
                )
                print(lp)
                if lp != "unknown":
                    list_read_plates.add(lp)
                    # Annotate the image with the detected license plate
                    cv2.putText(
                        img,
                        lp,
                        (int(plate[0]), int(plate[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (36, 255, 12),
                        2,
                    )
                    flag = 1
                    break
            if flag == 1:
                break

# Display the final image with annotations
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.imshow("frame", img)
cv2.resizeWindow("frame", 800, 600)
cv2.waitKey()
cv2.destroyAllWindows()
