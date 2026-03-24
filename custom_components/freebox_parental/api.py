import requests
import hashlib

class FreeboxAPI:
    def __init__(self, host, app_id):
        self.host = host
        self.app_id = app_id
        self.session_token = None
        self.app_token = None

    def login(self):
        challenge = requests.get(f"{self.host}/api/v8/login/").json()["result"]["challenge"]

        password = hashlib.sha1((challenge + self.app_token).encode()).hexdigest()

        session = requests.post(f"{self.host}/api/v8/login/session/", json={
            "app_id": self.app_id,
            "password": password
        }).json()

        self.session_token = session["result"]["session_token"]

    def request(self, method, path, data=None):
        return requests.request(
            method,
            f"{self.host}/api/v8{path}",
            headers={"X-Fbx-App-Auth": self.session_token},
            json=data,
            timeout=5
        ).json()

    def get_devices(self):
        return self.request("GET", "/lan/browser/pub/")

    def get_profiles(self):
        return self.request("GET", "/parental/profile/")

    def set_device(self, device_id, state):
        return self.request("PUT", f"/lan/browser/pub/{device_id}", {"active": state})

    def set_profile(self, profile_id, enable):
        week = (
            {d: [["00:00", "23:59"]] for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
            if enable else
            {d: [] for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]}
        )

        return self.request("PUT", f"/parental/profile/{profile_id}", {"week": week})