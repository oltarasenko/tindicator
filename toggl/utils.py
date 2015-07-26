import os
import json
import pickle
import requests
from requests.auth import HTTPBasicAuth


class HTTPConnection(object):

    HTTP_ENDPOINTS = {
       "stop_task": "https://www.toggl.com/api/v8/time_entries/%s/stop",
       "new_task": "https://www.toggl.com/api/v8/time_entries/start",
       "current_task": "https://www.toggl.com/api/v8/time_entries/current"
    }

    def __init__(self, api_token):
        self.auth = HTTPBasicAuth(api_token, "api_token")

    @staticmethod
    def check_token(api_token):
        try:
            resp = requests.get(
                HTTPConnection.HTTP_ENDPOINTS.get("current_task"),
                auth=HTTPBasicAuth(api_token, "api_token"), timeout=60)
        except requests.Timeout:
            return False
        if resp.status_code != 200:
            return False
        return True

    def get_current_task(self):
        task = requests.get(HTTPConnection.HTTP_ENDPOINTS["current_task"],
                            auth=self.auth, timeout=60).json()

        task_data = task.get("data", {})
        return task_data

    def set_current_task(self, title):
        data = {
            "time_entry": {"description": title, "created_with": "tindicator"}}
        requests.post(
            HTTPConnection.HTTP_ENDPOINTS["new_task"], auth=self.auth,
            data=json.dumps(data))
        return True

    def stop_current_task(self, task_id):
        requests.put(
            HTTPConnection.HTTP_ENDPOINTS["stop_task"] % task_id,
            auth=self.auth, timeout=120)
        return True


class Settings(object):

    def __init__(self, path=".toggle_prefs"):
        self.path = os.path.join(os.getenv("HOME"), path)

    def read_settings(self):
        try:
            prefs_file = open(self.path, 'r')
        except IOError:
            return False
        return pickle.load(prefs_file)

    def save_settings(self, api_token):
        settings = {"api_token": api_token}
        pickle.dump(settings, open(self.path, 'w'))
        return True
