import cv2
from queue import Queue
from threading import Event, Thread
import numpy as np
import time
from app.detector import detect_and_read_plate, most_common_plate
from abc import ABC, abstractmethod
import requests
import json

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

    def retry(self):
        for _ in range(Stream.MAX_TRY):
            self.cap = cv2.VideoCapture(self.url)
            if self.cap.isOpened():
                self.is_available = True
                break
            self.is_available = False
            print("Stream not available, retrying...")
            time.sleep(Stream.TRY_TIMEOUT)


class Camera(ABC):
    TIME_TO_PASS = 5
    MAX_TRY = 1

    def __init__(self, url, title, delay=0.5):
        self.__camera = Stream(url, delay)
        self.__frame_queue = Queue(maxsize=1)
        self.__event = Event()
        self.img = self.__camera.capture()
        self.title = title
        self.is_running = False
        self.display_thread = Thread(target=self.display, daemon=True)
        self.process_thread = Thread(target=self.process, daemon=True)
        self.label = ""

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

    @property
    def delay_ms(self):
        return int(self.delay * 1000)

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
                self.retry_stream()
                if not self.is_available:
                    self.stop()
                    break
                continue

            elif self.__frame_queue.full():
                self.__frame_queue.get()
            self.__frame_queue.put(self.img)

            time.sleep(self.delay)
        self.__event.set()
        self.__camera.release()

    def retry_stream(self):
        self.__camera.retry()

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
        self.detected_plates = ""

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
                self.detected_plates = ""
                self.label = ""
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
                self.label = self.detected_plates
                print(
                    f"({self.title}) Detected plates: {self.detected_plates} {curr_plates}"
                )

                # Check if the plate is registered
                # If registered, user's balance is enough open the gate and sleep for 5 seconds, request for create qr code
                user = CameraIn.get_user_of_plate(self.detected_plates)
                if user is None:
                    self.label += f"\n(User not found)"
                    print("User not found")
                elif user["balance"] < 10:
                    self.label += f"\n{user['username']} doesn't have enough money. Balance: {user['balance']}"
                    with open("log/checkin.txt", "a") as f:
                        f.write(
                            f"[{time.strftime('%d/%m/%Y, %H:%M:%S')}]: {user['username']} {self.detected_plates} doesn't have enough money.\n\n"
                        )
                else:
                    self.event.set()
                    CameraIn.create_qr_code(user["username"])
                    self.label += (
                        f'{user["username"]} {self.detected_plates} Check in success'
                    )
                    # Write logs
                    with open("log/checkin.txt", "a") as f:
                        f.write(
                            f"[{time.strftime('%d/%m/%Y, %H:%M:%S')}]: {user['username']} {self.detected_plates}\n\n"
                        )
                curr_plates.clear()

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


class CameraQR(Camera):
    def __init__(self, url, title, delay=0.5, shared_qr_data=None):
        super().__init__(url, title, delay)
        self.detector = cv2.QRCodeDetector()
        self.shared_qr_data = shared_qr_data

    def process(self):
        while self.is_running:
            if self.event.is_set():
                time.sleep(self.delay)
                continue
            # Get the frame from the queue
            try:
                img = self.frame_queue.get(timeout=Camera.TIME_TO_PASS + 2)
            except:
                print(f"No frame received {self.title}")
                continue
            print("Detecting...", self.title)

            data, bbox, _ = self.detector.detectAndDecode(img)
            if data:
                parts = data.split()
                username = parts[0].split(":")[1]
                uuid = parts[1].split(":")[1]
                print(f"================{username} {uuid}===============")
                self.shared_qr_data["qr_data"] = requests.get(
                    f"http://localhost:5000/get_qr_data?uuid={uuid}&username={username}"
                ).json()
                self.label = json.dumps(self.shared_qr_data["qr_data"], indent=2)
                print(f"QR detected: {self.shared_qr_data['qr_data']}")


class CameraOut(Camera):
    def __init__(self, url, title, delay=0.5, shared_qr_data=None):
        super().__init__(url, title, delay)
        self.shared_qr_data = shared_qr_data

    def process(self):
        """
        This only detects only when the qrcode is detected
        1. Detect the license plate
        2. Check if the license plate is match with the user's plate of the qr code
        4. If true, open the gate and sleep for 5 seconds, post the check out time to the server
        5. Repeat the process
        """
        curr_plates = []
        while self.is_running:
            if self.event.is_set():
                self.event.clear()
                time.sleep(Camera.TIME_TO_PASS)
                self.detected_plates = ""
                self.label = ""
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
                self.label = self.detected_plates
                print(
                    f"({self.title}) Detected plates: {self.detected_plates} {curr_plates}"
                )

                # Check if the license plate is match with the user's plate of the qr code
                # If match, open the gate and sleep for 5 seconds, post the check out time to the server
                if (
                    self.detected_plates
                    != self.shared_qr_data["qr_data"]["license_plate"]
                ):
                    self.label += f"\n(License plate does not match)"
                    print("License plate does not match")
                # Check if the user already checked out
                elif self.shared_qr_data["qr_data"]["checkout_date"] != "":
                    self.label += f"\nThis QR has been used!!!"
                    with open("log/checkout.txt", "a") as f:
                        f.write(
                            f"QR: {self.shared_qr_data['qr_data']['uuid']} has been used!!!\n\n"
                        )
                else:
                    self.event.set()
                    self.label += f"Check out success"
                    response = requests.post(
                        "http://localhost:5000/checkout",
                        json={
                            "username": self.shared_qr_data["qr_data"]["username"],
                            "uuid": self.shared_qr_data["qr_data"]["uuid"],
                        },
                    )
                    print(f"{response.status_code} {response.text}")
                    # Write logs
                    with open("log/checkout.txt", "a") as f:
                        f.write(
                            f"[{time.strftime('%d/%m/%Y, %H:%M:%S')}]: {self.shared_qr_data['qr_data']['username']} {self.detected_plates}\nQR: {self.shared_qr_data['qr_data']['uuid']}\n\n"
                        )
                curr_plates.clear()
