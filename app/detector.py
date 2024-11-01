import torch
import cv2
from app.license_plate_recognition.function.helper import read_plate
from app.license_plate_recognition.function.utils_rotate import deskew
from collections import Counter

detector_nano_path = "app/license_plate_recognition/model/LP_detector_nano_61.pt"
ocr_nano_path = "app/license_plate_recognition/model/LP_ocr_nano_62.pt"
detector_path = "app/license_plate_recognition/model/LP_detector.pt"
ocr_path = "app/license_plate_recognition/model/LP_ocr.pt"


def is_valid_plate(plate: str) -> bool:
    if plate == "unknown":
        return False
    length = len(plate)
    if length < 7 or length > 9:
        return False
    if not plate[:2].isnumeric():
        return False
    if not plate[2].isalpha():
        return False
    if not plate[-4:].isnumeric() and not plate[-5:].isnumeric():
        return False
    return True


class YOLODetector:
    def __init__(self):
        # Load YOLO models for license plate detection and OCR
        self.yolo_LP_detect = torch.hub.load(
            "app\\license_plate_recognition\\yolov5",
            "custom",
            path=detector_nano_path,
            force_reload=True,
            source="local",
        )
        self.yolo_license_plate = torch.hub.load(
            "app\\license_plate_recognition\\yolov5",
            "custom",
            path=ocr_path,
            force_reload=True,
            source="local",
        )
        self.yolo_license_plate.conf = 0.60  # Set confidence threshold for OCR model

    def detect_plates(self, img):
        plates = self.yolo_LP_detect(img)
        return plates.pandas().xyxy[0].values.tolist()

    def read_from_deskew(self, crop_img):
        plates = []
        flag = 0
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = read_plate(self.yolo_license_plate, deskew(crop_img, cc, ct))
                lp = lp.replace("-", "")
                if is_valid_plate(lp):
                    plates.append(lp)
                    flag = 1
                    break
            if flag == 1:
                break
        return plates


detector = YOLODetector()


def most_common_plate(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]


def detect_and_read_plate(img):
    """Return the first plate strings if it's valid"""
    plates = detector.detect_plates(img)

    for plate in plates:
        crop_img = get_crop_image(img, plate)
        try:
            plate_arr = detector.read_from_deskew(crop_img)
            if len(plate_arr) > 0:
                return plate_arr
        except Exception as e:
            print(e)
    return []


def get_crop_image(img, plate):
    x = int(plate[0])  # xmin
    y = int(plate[1])  # ymin
    w = int(plate[2] - plate[0])  # xmax - xmin
    h = int(plate[3] - plate[1])  # ymax - ymin
    return img[y : y + h, x : x + w]
