import cv2
from queue import Queue
from threading import Event, Thread
import numpy as np
import time
from app.detector import detect_and_read_plate, most_common_plate
from abc import ABC, abstractmethod
import requests

BLACK_IMG = np.zeros((480, 640, 3), dtype=np.uint8)


class Stream:
    MAX_TRY = 2
    TRY_TIMEOUT = 5

    def __init__(self, url, delay=0.1):
        self.url = url
        self.delay = delay
        for _ in range(Stream.MAX_TRY):
            self.cap = cv2.VideoCapture(url)
            if self.cap.isOpened():
                self.is_available = True
                break
            print("Stream not available, retrying...")
            time.sleep(Stream.TRY_TIMEOUT)
        else:
            self.is_available = False
            raise Exception("Stream not available")

    def capture(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        self.is_available = False
        return None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()


class Camera(ABC):
    TIME_TO_PASS = 5
    MAX_TRY = 2

    def __init__(self, url, title, delay=0.5):
        self.__camera = Stream(url, delay)
        self.__frame_queue = Queue(maxsize=1)
        self.__event = Event()
        self.detected_plates = ""
        self.img = self.__camera.capture()
        self.title = title
        self.is_running = False
        self.display_thread = Thread(target=self.display, daemon=True)
        self.process_thread = Thread(target=self.process, daemon=True)

    @property
    def frame_queue(self):
        return self.__frame_queue

    @property
    def event(self):
        return self.__event

    @property
    def is_available(self):
        return self.__camera.is_available

    @property
    def delay(self):
        return self.__camera.delay

    def display(self):
        # Keep capturing the frame and display it
        while self.is_running:
            # Sleep for 5 seconds if the event is set and then display again
            if self.__event.is_set():
                self.img = None
                self.__frame_queue.queue.clear()
                time.sleep(Camera.TIME_TO_PASS)
                continue

            self.img = self.__camera.capture()

            # The camera has been shut down suddenly
            if not self.is_available:
                self.stop()
                break
            elif self.__frame_queue.full():
                self.__frame_queue.get()
            self.__frame_queue.put(self.img)

            time.sleep(self.delay)
        self.__event.set()
        self.__camera.release()

    @abstractmethod
    def process(self):
        pass

    def stop(self):
        print(f"Shutting down {self.title}...")
        self.is_running = False
        self.__event.set()
        self.display_thread.join()
        self.process_thread.join()

    def pause(self):
        self.__event.set()

    def resume(self):
        self.__event.clear()

    def start(self):
        self.is_running = True
        self.display_thread.start()
        self.process_thread.start()


class CameraIn(Camera):

    def __init__(self, url, title, delay=0.5):
        super().__init__(url, title, delay)

    def process(self):
        """
        1. Detect the license plate
        2. Check if the license plate is registered
        3. If registered, check if the user's balance is enough
        4. If the balance is enough, open the gate and sleep for 5 seconds
        5. Request for creating a QR code
        6. Repeat the process
        """
        curr_plates = []
        while self.is_running:
            if self.event.is_set():
                self.event.clear()
                time.sleep(Camera.TIME_TO_PASS)
                continue
            # Get the frame from the queue
            try:
                img = self.frame_queue.get(timeout=Camera.TIME_TO_PASS + 2)
            except:
                print(f"No frame received {self.title}")
                continue
            print("Detecting...", self.title)
            curr_plates.extend(detect_and_read_plate(img))
            if len(curr_plates) == Camera.MAX_TRY:
                self.detected_plates = most_common_plate(curr_plates)
                print(
                    f"({self.title}) Detected plates: {self.detected_plates} {curr_plates}"
                )

                # Check if the plate is registered
                # If registered, user's balance is enough open the gate and sleep for 5 seconds, request for create qr code
                user = CameraIn.get_user_of_plate(self.detected_plates)
                if user is None:
                    print("User not found")
                elif user["balance"] < 10:
                    print("Insufficient balance")
                    break
                else:
                    self.event.set()
                    CameraIn.create_qr_code(user["username"])
                curr_plates.clear()

        self.stop()

    @staticmethod
    def get_user_of_plate(plate):
        response = requests.get(
            f"http://localhost:5000/camera_in?license_plate={plate}"
        )
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def create_qr_code(username, date=time.strftime("%d/%m/%Y, %H:%M:%S")):
        # Generate QR code
        response = requests.get(
            f"http://localhost:5000/generate_qr?username={username}&date={date}"
        )
        print(f"{response.status_code} {response.text}")

        # Deduct balance from the user's wallet
        response = requests.post(
            "http://localhost:5000/account/vallet",
            json={"username": username, "amount": -10},  # Send JSON payload
        )
        print(f"{response.status_code} {response.text}")


class CameraOut(Camera):
    def __init__(self, url, title, delay=0.5):
        super().__init__(url, title, delay)
        detector = cv2.QRCodeDetector()

    def process(self):
        """
        This only detects only when the qrcode is detected
        1. Detect the license plate
        2. Check if the license plate is match with the user's plate of the qr code
        3. If match, open the gate and sleep for 5 seconds, post the check out time to the server
        4. Repeat the process
        """
        curr_plates = []
        while self.is_running:
            if self.__event.is_set():
                time.sleep(Camera.TIME_TO_PASS)
                continue
            # Get the frame from the queue
            try:
                img = self.__frame_queue.get(timeout=Camera.TIME_TO_PASS + 3)
            except:
                print(f"No frame received {self.title}. Shut down...")
                break
            print("Detecting...", self.title)
            curr_plates.extend(detect_and_read_plate(img))
            if len(curr_plates) == Camera.MAX_TRY:
                self.detected_plates = most_common_plate(curr_plates)
                print(
                    f"({self.title}) Detected plates: {self.detected_plates} {curr_plates}"
                )
                curr_plates.clear()

                # Check if the plate is registered
                # If registered, user's balance is enough open the gate and sleep for 5 seconds, request for create qr code
                user = CameraIn.get_user_of_plate(self.detected_plates)
                if user is None:
                    print("User not found")
                elif user["balance"] < 10:
                    print("Insufficient balance")
                else:
                    self.__event.set()
                    CameraIn.create_qr_code(user["username"])

        self.stop()


class CameraQR(Camera):
    def __init__(self, url, title, delay=0.5):
        super().__init__(url, title, delay)

    def process(self):
        curr_plates = []
        while self.is_running:
            if self.__event.is_set():
                time.sleep(Camera.TIME_TO_PASS)
                continue
            # Get the frame from the queue
            try:
                img = self.__frame_queue.get(timeout=Camera.TIME_TO_PASS + 3)
            except:
                print(f"No frame received {self.title}. Shut down...")
                break
            print("Detecting...", self.title)
            curr_plates.extend(detect_and_read_plate(img))
            if len(curr_plates) == Camera.MAX_TRY:
                self.detected_plates = most_common_plate(curr_plates)
                print(
                    f"({self.title}) Detected plates: {self.detected_plates} {curr_plates}"
                )
                curr_plates.clear()

                # Check if the plate is registered
                # If registered, user's balance is enough open the gate and sleep for 5 seconds, request for create qr code
                user = CameraIn.get_user_of_plate(self.detected_plates)
                if user is None:
                    print("User not found")
                elif user["balance"] < 10:
                    print("Insufficient balance")
                else:
                    self.__event.set()
                    CameraIn.create_qr_code(user["username"])

        self.stop()
