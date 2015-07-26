# -*- coding: utf-8 -*-
import os
import sys
import pkg_resources

from time import time

from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from gi.repository import GLib

from ui_handlers import UIHandler
from utils import Settings, HTTPConnection


class TogglIndicator(object):

    def __init__(self, settings):
        logo_path = pkg_resources.resource_filename(__name__, 'toggl.png')
        self.ind = appindicator.Indicator.new(
            "toggl-indicator",
            os.path.abspath(logo_path),
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )

        self.current_task = {}
        # Duration of the current task
        self.duration = 0

        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)

        # Path to glade ui resources
        self.glade_path = pkg_resources\
            .resource_filename(__name__, 'toggl_ui.glade')

        self.settings = settings

    def apitoken_dialog(self, widget=None):
        """ Dialog responsible for gathering apitoken """
        builder = Gtk.Builder()
        builder.add_from_file(self.glade_path)
        window = builder.get_object("prefs")
        builder.connect_signals(UIHandler(self, window))
        window.show_all()

    def new_task_dialog(self, widget):
        """ Renders create new task window """
        builder = Gtk.Builder()
        builder.add_from_file(self.glade_path)
        window = builder.get_object("new_task_dialog")
        builder.connect_signals(UIHandler(self, window))
        window.show_all()

    def stop_current_task(self, widget):
        self.connection.stop_current_task(self.current_task.get("id"))
        self.duration = 0
        self.current_task = {}
        return True

    def set_task(self, title):
        self.connection.set_current_task(title)
        self.update()
        self.render_indicator_logo()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        self.start_item = Gtk.MenuItem("Start/Switch")
        self.start_item.connect("activate", self.new_task_dialog)
        self.start_item.show()
        self.menu.append(self.start_item)

        self.stop = Gtk.MenuItem("Stop task")
        self.stop.connect("activate", self.stop_current_task)
        self.stop.show()
        self.menu.append(self.stop)

        self.prefs = Gtk.MenuItem("Set/change api token")
        self.prefs.connect("activate", self.apitoken_dialog)
        self.prefs.show()
        self.menu.append(self.prefs)

        self.quit_item = Gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        settings = self.settings.read_settings()

        if not settings or not HTTPConnection\
                .check_token(settings.get("api_token")):
            self.set_label("Wrong API Token")
        else:
            self.connection = HTTPConnection(api_token=settings["api_token"])
            self.update()
            GLib.timeout_add(360000, self.update)
            GLib.timeout_add(1000, self.render_indicator_logo)

    def render_indicator_logo(self):
        self.duration += 1
        hours = int(self.duration/3600)
        mins = int(self.duration/60) - hours*60
        seconds = int(self.duration) - mins*60 - hours*3600

        title = self.current_task.get("description", "Idle time")
        self.set_label(
            u" {}: {:02}:{:02}:{:02}".format(title, hours, mins, seconds))
        return True

    def set_label(self, label):
        self.ind.set_label(label, "toggl")

    def update(self):
        task_data = self.connection.get_current_task()

        # Update logo, stopping rendering current task
        if self.current_task and not task_data:
            self.duration = 0
            self.current_task = {}
        # Update logo, showing task and it's duration
        if task_data:
            self.current_task = task_data
            self.duration = time() + self.current_task.get("duration", time())
        return True

    def quit(self, widget):
        sys.exit(0)


def main():
    indicator = TogglIndicator(settings=Settings())
    indicator.main()
    Gtk.main()

if __name__ == "__main__":
    main()
