# -*- coding: utf-8 -*-


class UIHandler(object):
    """
    For now we're using one handler class for both UI windows
    """

    def __init__(self, indicator, window):
        self.indicator = indicator
        self.window = window

    def start(self, entry):
        self.indicator.set_task(title=entry.get_text())
        self.window.destroy()

    def save_prefs(self, entry):
        self.indicator.settings.save_settings(entry.get_text())
        self.indicator.main()
        self.window.destroy()
