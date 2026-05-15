import os
import subprocess
import sys
import time
import unittest
import logging
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC
from typing import Union, Dict
import allure
import pytest
from alttester import AltDriver, AltReversePortForwarding, AltException

from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait

sys.path.append(os.path.dirname(__file__))


class TestBase(unittest.TestCase):
    platform = None
    _app_package: str = None
    _android_app_activity: str = None
    _ios_bundle_id: str = None

    @staticmethod
    def read_config_properties(file_path: str) -> Dict[str, str]:
        config = {}
        logging.info(f"read_config_properties: Attempting to open file: '{file_path}'")
        if not os.path.exists(file_path):
            logging.error(f"read_config_properties: Error: Properties file not found at '{file_path}'")
            return config
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('!'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                    elif ':' in line:
                        key, value = line.split(':', 1)
                    else:
                        logging.warning(f"read_config_properties: Skipping malformed line: '{line}'")
                        continue
                    config[key.strip()] = value.strip()
            logging.info(f"read_config_properties: Successfully read {len(config)} entries from '{file_path}'.")
            sys.stdout.write(f"DEBUG: read_config_properties: Successfully read config. Content: {config}\n")
        except Exception as e:
            logging.error(f"read_config_properties: Error reading properties file '{file_path}': {e}")
        return config

    @classmethod
    def setUpClass(cls):

        root_dir = (Path(__file__).resolve().parent.parent)
        config_file_path = root_dir / "config.properties"

        # Read the configuration
        app_config = TestBase.read_config_properties(str(config_file_path))

        if not app_config:
            raise RuntimeError(
                f"Failed to load app configuration from '{config_file_path}'. Cannot proceed with tests."
            )

        # Determine platform
        cls.platform = os.getenv("APPIUM_PLATFORM", app_config.get("platformName", "android")).lower()
        print(f"Running on {cls.platform}")

        cls.options = AppiumOptions()

        if cls.platform == "android":

            # ANDROID capabilities
            cls.options.platform_name = "Android"

            cls.options.set_capability(
                "appium:app",
                os.getenv("APPIUM_APPFILE", str(app_config.get("app", "application.apk")))
            )

            cls.options.automation_name = os.getenv("APPIUM_AUTOMATION",
                                                    app_config.get("automationName", "UiAutomator2"))
            cls._app_package = app_config.get("app.package")
            cls._android_app_activity = app_config.get("android_app_activity")

            cls.options.set_capability("appium:appPackage", app_config.get("app.package"))
            cls.options.set_capability("appium:appActivity", app_config.get("android_app_activity"))
            cls.options.set_capability("appium:newCommandTimeout", 15000)
            cls.options.set_capability("enableMultiWindows", True)
            cls.options.set_capability("autoAcceptAlerts", True)
            cls.options.set_capability("autoDismissAlerts", True)
            cls.options.set_capability("appium:autoGrantPermissions", True)
            cls.options.set_capability("appium:adbExecTimeout", 30000)

        elif cls.platform == "ios":
            # IOS capabilities
            cls.options.platform_name = "iOS"
            cls.options.automation_name = "XCUITest"
            cls._ios_bundle_id = app_config.get("app.appBundleId")
            udid = cls.get_udid_from_ip()
            cls.options.set_capability("udid", udid)
            print(f"✅ Using UDID: {udid}")
            cls.options.set_capability("appium:app",
                                       os.getenv("APPIUM_APPFILE", str(app_config.get("app", "application.ipa"))))
            cls.options.set_capability("appium:bundleId", app_config.get("app.appBundleId"))
            cls.options.set_capability("appium:newCommandTimeout", 35000)
            cls.options.set_capability("autoAcceptAlerts", True)
            cls.options.set_capability("autoDismissAlerts", True)
            cls.options.set_capability("appium:autoGrantPermissions", True)
            cls.options.set_capability("enableMultiWindows", True)
            cls.options.set_capability("appium:permissions",
                                       f'{{ "{app_config.get("app.appBundleId")}": {{"location": "always", "notifications": "yes"}} }}')
            cls.options.set_capability("appium:preventWDAAttachments", True)
            cls.options.set_capability("appium:waitForIdleTimeout", 0)
            cls.options.set_capability("allowInvisibleElements", True)
            cls.options.set_capability("deviceScreenSize", "full")
            cls.options.set_capability("showXcodeLog", True)
            cls.options.set_capability("wdaLocalPort", 8100)
            cls.options.set_capability("wdaLaunchTimeout", 120000)
            cls.options.set_capability("wdaConnectionTimeout", 120000)
            cls.options.set_capability("clearSystemFiles", True)
            cls.options.set_capability("webviewConnectTimeout", 120000)
            cls.options.set_capability("webviewConnectRetries", 60)
            cls.options.set_capability("includeSafariInWebviews", True)
            cls.options.set_capability("enableWebviewDetailsCollection", True)
            cls.options.set_capability("startIWDP", True)
            cls.options.set_capability("ios_webkit_debug_proxy", True)




        else:
            raise RuntimeError(f"Unsupported platform: {cls.platform}")

        # Start Appium driver
        cls.appium_driver = webdriver.Remote(
            os.getenv("APPIUM_URL", "http://localhost:4723"), options=cls.options)
        print("Appium driver started")
        # Reverse port forwarding only for Android
        if cls.platform == "android":
            time.sleep(10)
            cls.click_Consent()
        else:

            time.sleep(15)
            cls.click_Consent_IOS()

        cls.setup_reverse_port_forwarding()
        cls.altdriver = AltDriver("alttester.kwalee.com", 13000, "Queens Puzzle", True, 12000)
        #cls.altdriver = AltDriver("alttester.kwalee.com", 13000, "__default__", True, 12000)

        time.sleep(15)

    def setUp(self):
        """
        Make altdriver instance-level so pytest hooks can access it.
        unittest creates a new instance per test, so we copy the class-level driver.
        """
        self.altdriver = self.__class__.altdriver
        self.appium_driver = self.__class__.appium_driver

    @classmethod
    def setup_reverse_port_forwarding(cls):
        try:
            AltReversePortForwarding.remove_reverse_port_forwarding_android()
        except:
            print("No adb forward was present")
        if cls.platform == 'android':
            AltReversePortForwarding.reverse_port_forwarding_android()
            print("Port forwarded (Android).")
        else:
            print("Reverse port forwarding is available only for Android")

    @classmethod
    def tearDownClass(cls):
        try:
            AltReversePortForwarding.remove_reverse_port_forwarding_android()
            print("Reverse port forwarding removed")
        except:
            print("No adb forward was present")

            # --- FIX ---
        if hasattr(cls, "altdriver") and cls.altdriver:
            try:
                cls.altdriver.stop()
                print("AltDriver stopped")
            except Exception as e:
                print(f"Failed to stop AltDriver: {e}")
        else:
            print("AltDriver was never initialized at class level → skipping stop()")
        cls.appium_driver.quit()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    @classmethod
    def get_udid_from_ip(cls):
        # 🔧 Implement your logic here (for example, parsing `idevice_id -l`)
        import subprocess
        try:
            result = subprocess.run(["idevice_id", "-l"], stdout=subprocess.PIPE, text=True, check=True)
            udids = result.stdout.strip().splitlines()
            if udids:
                return udids[0]  # take the first connected device
            else:
                raise RuntimeError("No iOS devices detected via idevice_id")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch UDID: {e}")

    @classmethod
    def connect_to_alttester_with_retries(
            cls,  # 'cls' is passed to allow calling class methods like setup_reverse_port_forwarding
            host: str = 'alttester.kwalee.com',
            port: int = 13000,
            max_retries: int = 4,
            retry_delay_seconds: int = 5
    ) -> (Union)[
        AltDriver, None]:  # Changed from AltDriver | None to Union[AltDriver, None] for Python 3.9 compatibility
        """
        Attempts to connect to the AltTester server with a retry mechanism,
        including reverse port forwarding setup before each attempt.

        Args:
            cls: The class instance or class itself that contains setup_reverse_port_forwarding.
            host (str): The hostname or IP address of the AltTester server.
            port (int): The port number of the AltTester server.
            max_retries (int): The maximum number of reconnection attempts.
            retry_delay_seconds (int): The delay in seconds between retry attempts.

        Returns:
            Union[AltDriver, None]: An AltDriver instance if connection is successful,
                                    otherwise None after exhausting retries.
        """
        altdriver_instance = None
        for attempt in range(1, max_retries + 1):
            logging.info(
                f"Attempt {attempt}/{max_retries}: Setting up reverse port forwarding and connecting to AltTester server at {host}:{port}...")
            try:
                # Call the class method for reverse port forwarding
                # Assuming setup_reverse_port_forwarding is a class method or accessible via 'cls'
                cls.setup_reverse_port_forwarding()
                time.sleep(10)  # Wait for 10 seconds after setting up forwarding as requested

                # Initialize AltDriver connection
                # Using "__default__", True, 50000 as per your example
                #altdriver_instance = AltDriver(host, port, "Queens Puzzle", True, 50000)
                altdriver_instance = AltDriver(host, port, "__default__", True, 50000)

                logging.info(f"Successfully connected to AltTester on attempt {attempt}.")
                return altdriver_instance
            except (AltException) as e:
                error_message = str(e)
                if "No app connected that has the given tags." in error_message:
                    logging.error(
                        f"AltTester server reports 'No app connected with tags' on attempt {attempt}. "
                        f"Please ensure your AltTester-enabled game is running on the device/emulator "
                        f"and configured with the correct tags ('__default__'). Error: {error_message}"
                    )
                else:
                    logging.warning(f"Connection failed on attempt {attempt}: {e}")

                if attempt < max_retries:
                    logging.info(f"Retrying in {retry_delay_seconds} seconds...")
                    time.sleep(retry_delay_seconds)
                else:
                    logging.error(f"Failed to connect to AltTester after {max_retries} attempts.")
            except Exception as e:
                # Catch any other unexpected exceptions during connection
                logging.error(f"An unexpected error occurred during connection on attempt {attempt}: {e}")
                if attempt < max_retries:
                    logging.info(f"Retrying in {retry_delay_seconds} seconds...")
                    time.sleep(retry_delay_seconds)
                else:
                    logging.error(
                        f"Failed to connect to AltTester after {max_retries} attempts due to an unexpected error.")
        return None

    @classmethod
    def restart_game(cls, package_name: str, activity: str):

        logging.info(f"restart_game: Received package_name='{package_name}', main_activity='{activity}'")
        if package_name is None or not isinstance(package_name, str) or not package_name.strip():
            logging.error("restart_game: Error: package_name is None, not a string, or empty.")
            raise ValueError(f"App package name is invalid: '{package_name}'. Cannot restart game.")
        if activity is None or not isinstance(activity, str) or not activity.strip():
            logging.error("restart_game: Error: main_activity is None, not a string, or empty.")
            raise ValueError(f"App main activity is invalid: '{activity}'. Cannot restart game.")

        logging.info(f"restart_game: Attempting to restart game: {package_name} with activity: {activity}")

        try:
            subprocess.run(["which", "adb"], check=True, capture_output=True)
            logging.info("restart_game: 'adb' command found in PATH.")
        except subprocess.CalledProcessError:
            logging.error(
                "restart_game: 'adb' command not found in PATH. Please ensure Android SDK Platform-Tools are installed and configured.")
            raise FileNotFoundError("ADB command not found.")
        except FileNotFoundError:
            logging.error("restart_game: 'which' command not found. Cannot verify adb path.")
            # Continue, but log the warning. This is less critical than adb itself.
        # --- END adb PATH check ---

        try:
            logging.info(f"restart_game: Running adb shell am force-stop {package_name}")
            # Ensure package_name is explicitly converted to string, though it should be if checks pass
            subprocess.run(["adb", "shell", "am", "force-stop", str(package_name)], check=True, capture_output=True)
            logging.info(f"restart_game: Force-stopped {package_name}. Waiting 2 seconds...")
            time.sleep(2)

            start_command = f"am start -n {package_name}/{activity}"
            logging.info(f"restart_game: Running adb shell {start_command}")
            # Ensure main_activity is explicitly converted to string
            subprocess.run(["adb", "shell", start_command], check=True, capture_output=True)
            logging.info(f"restart_game: Started {package_name}/{activity}.")
        except subprocess.CalledProcessError as e:
            logging.error(
                f"restart_game: ADB command failed (return code {e.returncode}): {e.cmd}. Stderr: {e.stderr.decode().strip()}. Stdout: {e.stdout.decode().strip()}")
            raise
        except FileNotFoundError:  # This should now be caught by our 'which adb' check, but good to keep
            logging.error("restart_game: ADB command not found. Ensure ADB is installed and in your PATH.")
            raise
        except Exception as e:
            logging.error(f"restart_game: An unexpected error occurred: {e}")
            raise

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            driver = item.funcargs.get("driver")
            if driver:
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, name="screenshot", attachment_type=allure.attachment_type.PNG)

    @classmethod
    def restart_ios_app_old(cls, bundle_id: str):
        logging.info(f"Restarting iOS app {bundle_id}")
        subprocess.run(["xcrun", "simctl", "terminate", "booted", bundle_id], check=True)
        subprocess.run(["xcrun", "simctl", "launch", "booted", bundle_id], check=True)
        logging.info(f"iOS app {bundle_id} restarted")

    @classmethod
    def restart_ios_app(cls, bundle_id: str):
        logging.info(f"Restarting iOS app on real device: {bundle_id}")
        try:
            cls.appium_driver.terminate_app(bundle_id)
            time.sleep(2)
            cls.appium_driver.activate_app(bundle_id)
            logging.info(f"✅ iOS app {bundle_id} restarted successfully.")
        except Exception as e:
            logging.error(f"Failed to restart iOS app: {e}")
            raise

    @classmethod
    def click_Consent(cls, timeout=15, retries=4):
        time.sleep(5)
        attempt = 1

        while attempt <= retries:
            print(f"🔄 Consent Click Attempt {attempt}/{retries}")

            try:
                wait = WebDriverWait(cls.appium_driver, timeout)

                # Focus / tap screen to trigger dialog if needed
                try:
                    frame = wait.until(EC.presence_of_element_located((AppiumBy.ID, "android:id/content")))
                    frame.click()
                    print("✅ Frame clicked.")
                except Exception:
                    print("⚠️ Frame not clickable this attempt. Continuing.")

                # Check for consent button
                try:
                    consent_button = cls.appium_driver.find_element(AppiumBy.XPATH, "//*[@content-desc='Consent']")
                    consent_button.click()
                    print("✅ Consent button clicked.")
                    return  # ✅ ONLY return after success
                except Exception:
                    print("⚠️ Consent not visible yet — retrying...")

            except Exception as e:
                print(f"❌ Unexpected error: {e}")

            attempt += 1
            time.sleep(2)

        print("❌ Consent did not appear after all retries.")

    @classmethod
    def click_Consent_IOS(cls):
        wait = WebDriverWait(cls.appium_driver, 1000)
        consent_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//*[@name='Consent']"))
        )
        consent_button.click()

    @classmethod
    def _get_appium_options(cls, reset_app: bool):
        """
        Returns AppiumOptions without reinstalling the app if reset_app=False
        """
        root_dir = (Path(__file__).resolve().parent.parent)
        config_file_path = root_dir / "config.properties"

        # Read the configuration
        app_config = TestBase.read_config_properties(str(config_file_path))

        options = AppiumOptions()

        if cls.platform == "android":
            options.platform_name = "Android"
            options.automation_name = os.getenv("APPIUM_AUTOMATION", "UiAutomator2")
            cls._app_package = app_config.get("app.package")
            cls._android_app_activity = app_config.get("android_app_activity")
            if reset_app:
                options.set_capability("appium:app",
                                       os.getenv("APPIUM_APPFILE", str(app_config.get("app", "application.apk"))))
                options.set_capability("appium:fullReset", True)
                options.set_capability("appium:noReset", False)
            else:
                options.set_capability("appium:fullReset", False)
                options.set_capability("appium:noReset", True)

            options.set_capability("appium:appPackage", app_config.get("app.package"))
            options.set_capability("appium:appActivity", app_config.get("android_app_activity"))
            options.set_capability("appium:newCommandTimeout", 15000)
            options.automation_name = os.getenv("APPIUM_AUTOMATION",
                                                app_config.get("automationName", "UiAutomator2"))

        # Add iOS capabilities if needed
        elif cls.platform == "ios":
            options.platform_name = "iOS"
            options.automation_name = "XCUITest"
            options.set_capability("appium:bundleId", app_config.get("app.appBundleId"))

        driver = webdriver.Remote(os.getenv("APPIUM_URL", "http://localhost:4723"), options=options)

        time.sleep(10)  # give it time to connect
        return driver


