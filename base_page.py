import os
import sys
import time

sys.path.append(os.path.dirname(__file__))


class BasePage:
    def __init__(self, altdriver, appium_driver):
        self.altdriver = altdriver
        self.appium_driver = appium_driver

    def sleep(self):
        time.sleep(0.6)
