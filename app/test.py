import requests
import time


def create_qr_code(username, date=time.strftime("%d/%m/%Y, %H:%M:%S")):
    response = requests.get(
        f"http://localhost:5000/generate_qr?username={username}&date={date}"
    )
    # charge the user
    response = requests.get(
        f"http://localhost:5000/account/vallet?username={username}&amount=10"
    )
    if response.status_code == 200:
        return response.json()
    return None


print(create_qr_code("huy"))
