import os
import sys
import json
import pickle
import requests

from time import time
from requests.auth import HTTPBasicAuth

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from gi.repository import GLib


class TogglIndicator(object):
    def __init__(self):
        self.ind = appindicator.Indicator.new(
            "toggl-indicator",
            os.path.abspath("toggl.png"),
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.current_task = {}
        self.duration = 0
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)
        self.API_URLS = {
            "stop_task": "https://www.toggl.com/api/v8/time_entries/%s/stop",
            "new_task": "https://www.toggl.com/api/v8/time_entries/start",
            "current_task": "https://www.toggl.com/api/v8/time_entries/current"
        }
        self.prefs_path = os.path.join(os.getenv("HOME"), ".toggle_prefs")

    def open_preferences(self, widget=None):
        builder = Gtk.Builder()
        builder.add_from_file("toggl_ui.glade")
        window = builder.get_object("prefs")
        builder.connect_signals(UIHandler(self, window))
        window.show_all()

    def read_prefs(self):
        try:
            prefs_file = open(self.prefs_path)
        except IOError:
            self.open_preferences()
            return

        prefs = pickle.load(prefs_file)
        self.auth = HTTPBasicAuth(prefs.get("APITOKEN"), 'api_token')
        return prefs

    def save_prefs(self, apitoken):
        prefs = {"APITOKEN": apitoken}
        pickle.dump(prefs, open(self.prefs_path, 'a'))
        self.main()

    def get_current_task(self):
        task = requests.get(
            self.API_URLS["current_task"], auth=self.auth, timeout=120).json()
        task_data = task.get("data", {})
        if self.current_task and not task_data:
            self.duration = 0
            self.current_task = {}
        if task_data:
            self.current_task = task_data
            self.duration = time() + self.current_task.get("duration", time())
        return True

    def start_tracking(self, widget):
        builder = Gtk.Builder()
        builder.add_from_file("toggl_ui.glade")
        window = builder.get_object("new_task_dialog")
        builder.connect_signals(UIHandler(self, window))
        window.show_all()

    def stop_current_task(self, widget):
        requests.put(
             self.API_URLS["stop_task"] % self.current_task.get("id"),
             auth=self.auth, timeout=120)
        self.duration = 0
        self.current_task = {}
        return True

    def set_task(self, title):
        data = {
            "time_entry": {"description": title, "created_with": "myclient"}}
        requests.post(
            self.API_URLS["new_task"], auth=self.auth, data=json.dumps(data))
        self.get_current_task()
        self.render_indicator_logo()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        self.start_item = Gtk.MenuItem("Start")
        self.start_item.connect("activate", self.start_tracking)
        self.start_item.show()
        self.menu.append(self.start_item)

        self.prefs = Gtk.MenuItem("Preferences")
        self.prefs.connect("activate", self.open_preferences)
        self.prefs.show()
        self.menu.append(self.prefs)

        self.stop = Gtk.MenuItem("Stop task")
        self.stop.connect("activate", self.stop_current_task)
        self.stop.show()
        self.menu.append(self.stop)

        self.quit_item = Gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.prefs = self.read_prefs()
        self.get_current_task()
        GLib.timeout_add(1000, self.render_indicator_logo)
        GLib.timeout_add(360000, self.get_current_task)

    def render_indicator_logo(self):
        self.duration += 1
        hours = int(self.duration/3600)
        mins = int(self.duration/60) - hours*60
        seconds = int(self.duration) - mins*60 - hours*3600
        title = self.current_task.get("description", "Idle time")
        self.ind.set_label(
            " {}: {:02}:{:02}:{:02}".format(title, hours, mins, seconds),
            "toggl")
        return True

    def quit(self, widget):
        sys.exit(0)


class UIHandler(object):
    def __init__(self, indicator, window):
        self.indicator = indicator
        self.window = window

    def start(self, entry):
        self.indicator.set_task(title=entry.get_text())
        self.window.destroy()

    def save_prefs(self, entry):
        self.indicator.save_prefs(entry.get_text())
        self.window.destroy()


if __name__ == "__main__":
    indicator = TogglIndicator()
    indicator.main()

    Gtk.main()
