import logging
import os
import re
import time

from alttester import By, AltException, NotFoundException
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class StartPage(BasePage):
    def __init__(self, altdriver, appium_driver):
        BasePage.__init__(self, altdriver, appium_driver)

    def load(self):
        self.altdriver.load_scene('Start')

    @property
    def start_button(self):
        return self.altdriver.find_object(By.NAME, 'StartButton')

    @property
    def start_text(self):
        return self.altdriver.find_object(By.NAME, 'StartText')

    @property
    def logo_image(self):
        return self.altdriver.find_object(By.NAME, 'LogoImage')

    @property
    def unity_url_button(self):
        return self.altdriver.find_object(By.NAME, 'UnityURLButton')

    def is_displayed(self):
        return self.start_button \
            and self.start_text \
            and self.logo_image \
            and self.unity_url_button

    def press_start(self):
        self.start_button.tap()

    def get_start_button_text(self):
        return self.start_text.get_text()

    def get_status_with_appium_driver(self):
        # example method for using appium in code
        return self.appium_driver.get_status()

    def click_Consent(self, timeout=500, retries=3):
        """
        Click a native element (frame/content) and optionally a consent button if present.

        Args:
            driver: Appium driver instance
            timeout: seconds to wait for element visibility
            retries: number of retries if stale element or timeout occurs
        """
        element_clicked = False

        while retries > 0 and not element_clicked:
            try:
                wait = WebDriverWait(self.appium_driver, timeout)
                # Wait for the frame element to be visible
                frame = wait.until(EC.visibility_of_element_located((AppiumBy.ID, "android:id/content")))

                if frame.is_displayed():
                    frame.click()
                    print("✅ Frame clicked.")

                    # Wait briefly for the consent button to appear
                    time.sleep(20)
                    try:
                        consent_button = self.appium_driver.find_element(AppiumBy.XPATH, "//*[@content-desc='Consent']")
                        consent_button.click()
                        print("✅ Consent button clicked.")
                    except (TimeoutException, NoSuchElementException):
                        print("⚠️ Consent button not found. Proceeding...")

                    element_clicked = True

                else:
                    print("⚠️ Frame is not displayed. Exiting function.")
                    return

            except StaleElementReferenceException:
                retries -= 1
                print(f"⚠️ Encountered a stale element. Retrying... Attempts left: {retries}")

            except TimeoutException:
                retries -= 1
                print(f"⚠️ Element not found within timeout. Retrying... Attempts left: {retries}")

            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                break

        if retries <= 0 and not element_clicked:
            print("❌ Failed to click the element after all retries.")

    def click_Consent_IOS(self):
        wait = WebDriverWait(self.appium_driver, 1000)
        consent_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//*[@name='Consent']"))
        )
        consent_button.click()

    '''
    def click_GDPR(self):
        path = "//ButtonGroup/AcceptButton"
        #path = "AcceptButton"
        try:
            print(f"🔍 Locating GDPR AcceptButton at {path}")
            btn = self.altdriver.wait_for_object(By.PATH, path, timeout=400)

            # 1) Tap at its world coordinates
            x_f, y_f, _ = btn.get_world_position()
            x, y = int(x_f), int(y_f)
            print(f"🧭 Tapping at ({x}, {y})…")
            self.altdriver.click((x, y))

            # 2) Wait for the Unity pause notification
            print("⏸️ Waiting for applicationPausedNotification…")
            start = time.time()
            while time.time() - start < 5:
                if self.altdriver.get_last_notification() == "applicationPausedNotification":
                    print("✅ Detected applicationPausedNotification (Unity paused).")
                    break
                time.sleep(0.2)
            else:
                print("⚠️ No pause notification — assuming tap still worked.")

            # 3) Now hand off to Appium without touching AltTester again
            print("Switching to NATIVE_APP context for native dialog…")
            self.appium_driver.switch_to.context("NATIVE_APP")

        except Exception as e:
            # If AltTester disconnects here, we assume tap succeeded
            print(f"⚠️ click_GDPR raised {type(e).__name__}: {e}")
            print("Assuming GDPR tap succeeded since native dialog should follow.")
            self.appium_driver.switch_to.context("NATIVE_APP")

    '''

    def click_GDPR(self, retries=5, wait_between_attempts=5,
                   AltObjectNotFoundException=None):  # Increased default retries
        """
        Attempts to find and click the GDPR Accept button using AltTester,
        with a retry mechanism for transient disconnections or object not found.
        """
        gdpr_button_locator_path = "//ButtonGroup/AcceptButton/Body"  # AltTester path locator

        for attempt in range(1, retries + 1):
            logging.info(
                f"click_GDPR: Attempt {attempt}/{retries}: Locating GDPR AcceptButton at {gdpr_button_locator_path}")

            # Print context handles for debugging, but use logging for cleaner output
            logging.debug(
                f"click_GDPR: Before AltTester operation, Appium context handles: {self.appium_driver.contexts}")

            try:
                # AltTester's wait_for_object handles its own timeout.
                # The timeout here is for AltTester's internal wait.
                gdpr_button = self.altdriver.wait_for_object(
                    By.PATH, gdpr_button_locator_path, timeout=30  # Use a reasonable AltTester timeout
                )

                logging.info(f"click_GDPR: Found GDPR AcceptButton on attempt {attempt}. Clicking...")
                gdpr_button.click()
                logging.info("click_GDPR: Successfully clicked GDPR AcceptButton.")

                # Print context handles after click for debugging
                logging.debug(
                    f"click_GDPR: After AltTester operation, Appium context handles: {self.appium_driver.contexts}")
                return  # Exit successfully

            except AltException as e:  # Catch general AltTester exceptions, including connection issues (4002)
                logging.warning(f"click_GDPR: AltTester exception on attempt {attempt}: {e}")
                if "closed the connection or unexpectedly disconnected" in str(e):
                    logging.info("click_GDPR: App disconnected. Attempting to restart game and reconnect AltTester.")
                    # This is where you might trigger a full game restart and AltTester reconnection
                    # You would need access to package_name and main_activity here.
                    # For example, if these are class variables in TestBase:
                    # self.restart_game(TestBase._app_package, TestBase._android_app_activity)
                    # time.sleep(5) # Give app time to restart
                    # self.altdriver = TestBase.connect_to_alttester_with_retries(
                    #     cls=TestBase, # Pass TestBase class
                    #     game_package_name=TestBase._app_package,
                    #     game_main_activity=TestBase._android_app_activity,
                    #     max_retries=3, # Fewer retries for in-test reconnect
                    #     retry_delay_seconds=5
                    # )
                    # if self.altdriver is None:
                    #     logging.error("click_GDPR: Failed to reconnect AltTester after app restart attempt.")
                    #     raise # Re-raise if reconnection fails
            except Exception as e:  # Catch any other unexpected errors
                logging.error(f"click_GDPR: An unexpected error occurred on attempt {attempt}: {e}")

            if attempt < retries:
                logging.info(f"click_GDPR: Waiting {wait_between_attempts} seconds before retrying...")
                time.sleep(wait_between_attempts)
            else:
                logging.error(f"click_GDPR: Failed to click GDPR AcceptButton after {retries} attempts.")
                raise  # Re-raise the last exception if all retries fail

    '''
    def click_Allow(self, retries=3, delay=2):

        self.appium_driver.switch_to.context("NATIVE_APP")
        print("Current context:", self.appium_driver.current_context)

        for attempt in range(1, retries + 1):
            try:
                print(f"🟡 Attempt {attempt} to click 'Allow' button...")
                wait = WebDriverWait(self.appium_driver, 50)  # Shorter wait each retry
                allow_button = wait.until(
                    EC.element_to_be_clickable((AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button"))
                )
                allow_button.click()
                print("✅ 'Allow' button clicked.")
                return
            except (TimeoutException, WebDriverException) as e:
                print(f"⚠️ Attempt {attempt} failed: {str(e)}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    print("❌ Failed to click 'Allow' button after multiple attempts.")
                    raise
    '''

    def click_Allow(self):
        wait = WebDriverWait(self.appium_driver, 5000)  # shorter wait
        try:
            allow_button = wait.until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.android.permissioncontroller:id/permission_allow_button"))
            )
            if allow_button.is_displayed():
                allow_button.click()
                print("Clicked Allow button.")
        except TimeoutException:
            # Button not found or not clickable, continue silently
            print("Allow button not displayed, continuing...")

    def click_debug_menu(self):
        gdpr_button = self.altdriver.wait_for_object(By.NAME,
                                                     "BTN_DebugMenu",
                                                     timeout=20)
        # gdpr_button = self.altdriver.wait_for_object(By.PATH,
        # "/DebugMenuPanelSettings(Clone)/DebugMenu-container/UnityEngine.UIElements.Button",
        # timeout=2000)


        gdpr_button.click()

    def click_Ad(self):
        scroll_view = self.altdriver.wait_for_object(By.NAME, "optionsScrollView", timeout=15)

        # Get the screen position of the object
        position = scroll_view.get_screen_position()

        # Perform tap at that position
        self.altdriver.tap(position)

        # Perform scroll (negative speed = upward, positive = downward)
        self.altdriver.scroll(-15, 3)
        time.sleep(5)

        ad_button = self.altdriver.wait_for_object(By.NAME, "BTN_HomeScreen_Ads", timeout=15)
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        #  "/DebugMenuPanelSettings/DebugMenuManager-container/optionsTabMainVisual/holder/mainSafeArea/optionsContainerRoot/optionsScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/optionsListView/UnityEngine.UIElements.Button[13]",
        #  timeout=500)
        #ad_button = self.altdriver.wait_for_object(By.NAME,"BTN_HomeScreen_Ads",
        # timeout=500)
        ad_button.click()

    def click_General(self):
        scroll_view = self.altdriver.wait_for_object(By.NAME, "optionsScrollView", timeout=15)

        # Get the screen position of the object
        position = scroll_view.get_screen_position()

        # Perform tap at that position
        self.altdriver.tap(position)

        # Perform scroll (negative speed = upward, positive = downward)
        self.altdriver.scroll(-24, 3)
        time.sleep(5)

        ad_button = self.altdriver.wait_for_object(By.NAME, "BTN_HomeScreen_General", timeout=15)
        # ad_button = self.altdriver.wait_for_object(By.PATH,
        #  "/DebugMenuPanelSettings/DebugMenuManager-container/optionsTabMainVisual/holder/mainSafeArea/optionsContainerRoot/optionsScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/optionsListView/UnityEngine.UIElements.Button[13]",
        #  timeout=500)
        # ad_button = self.altdriver.wait_for_object(By.NAME,"BTN_HomeScreen_Ads",
        # timeout=500)
        ad_button.click()

    def click_toggle_Ad(self):
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        # "//UnityEngine.UIElements.Foldout/unity-content/KWDebug.Utils.VisualElements.SlideToggle[1]",
        # timeout=300)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "TOGGLE_AdsDebugPage_TestRewardNoCallback",
                                                   timeout=300)
        ad_button.click()

    def click_toggle_Video(self):
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        #"//UnityEngine.UIElements.Foldout/unity-content/KWDebug.Utils.VisualElements.SlideToggle[2]",
        # timeout=300)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "TOGGLE_AdsDebugPage_TestInterstitialNoCallback",
                                                   timeout=30)
        ad_button.click()

    def click_toggle_Interstitial_Video(self):
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        # "//UnityEngine.UIElements.Foldout/unity-content/KWDebug.Utils.VisualElements.SlideToggle[3]",
        #timeout=300)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "TOGGLE_AdsDebugPage_InterstitialAdsBlock",
                                                   timeout=30)
        ad_button.click()

    def click_toggle_Reward_Video(self):
        # ad_button = self.altdriver.wait_for_object(By.PATH,
        # "//UnityEngine.UIElements.Foldout/unity-content/KWDebug.Utils.VisualElements.SlideToggle[3]",
        # timeout=300)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "TOGGLE_AdsDebugPage_RewardVideoAdsBlock",
                                                   timeout=30)
        ad_button.click()

    def click_btn_Back(self):
        time.sleep(5)
        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, "BTN_DebugPageBase_Back", timeout=20)
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def click_game_btn(self):
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        # "/DebugMenuPanelSettings/DebugMenuManager-container/optionsTabMainVisual/holder/mainSafeArea/optionsContainerRoot/optionsScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/optionsListView/UnityEngine.UIElements.Button[3]",
        #  timeout=2500)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "BTN_HomeScreen_Queens",
                                                   timeout=25)
        ad_button.click()
        ad_button.click()

    def enter_level(self, text):
        time.sleep(7)
        text = str(text)
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        # "//UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.TextField/unity-text-input/UnityEngine.UIElements.TextElement",
        # timeout=1500)
        # ad_button = self.altdriver.wait_for_object(By.PATH,
        #   "//unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.TextField/unity-text-input/UnityEngine.UIElements.TextElement",
        # timeout=1500)
        ad_button = self.altdriver.wait_for_object(By.NAME, "level_textBox", timeout=20)
        #ad_button = self.altdriver.find_object(By.NAME,"level_textBox")

        #ad_button.clic#k()

        #ad_button.set_text(ad_button.get_text()[:-1])
        time.sleep(4)
        ad_button.set_text(text)
        #ad_button.set_text(ad_button.get_text() + c)

        # Clear field by simulating backspaces
        #current_text = ad_button.get_text()
        #for _ in current_text:
        #ad_button.set_text(ad_button.get_text()[:-1])
        #ad_button.set_text("")
        #time.sleep(2)

        # Type each digit manually
        #for c in str(text):
        #ad_button.set_text(ad_button.get_text() + c)
        #time.sleep(3)

        print(f"DEBUG enter_level(): value after typing = {ad_button.get_text()}")

    def click_jump_level(self):

        scroll_view = self.altdriver.wait_for_object(By.NAME, "optionsScrollView", timeout=15)

        # Get the screen position of the object
        position = scroll_view.get_screen_position()

        # Perform tap at that position
        self.altdriver.tap(position)

        # Perform scroll (negative speed = upward, positive = downward)
        self.altdriver.scroll(-3, 3)
        #ad_button = self.altdriver.wait_for_object(By.TEXT, "Jump To Level", timeout=15)
        ad_button = self.altdriver.wait_for_object(By.PATH, "/DebugMenuPanelSettings/CONTAINER_HomeScreen_DebugMenu/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/CONTAINER_DebugPageBase_Root/UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.Button[7]", timeout=15)
        ad_button.click()

    def click_give_money(self):
        #ad_button = self.altdriver.wait_for_object(By.TEXT, "Give Money", timeout=15)
        ad_button = self.altdriver.wait_for_object(By.PATH, "/DebugMenuPanelSettings/CONTAINER_HomeScreen_DebugMenu/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/CONTAINER_DebugPageBase_Root/UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.Button[1]", timeout=15)
        ad_button.click()

    def click_clear_prefs(self):
        #ad_button = self.altdriver.wait_for_object(By.TEXT, "Clear Player Prefs", timeout=15)
        ad_button = self.altdriver.wait_for_object(By.PATH, "/DebugMenuPanelSettings/CONTAINER_HomeScreen_DebugMenu/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/CONTAINER_DebugPageBase_Root/UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.Button[4]", timeout=15)
        ad_button.click()

    def disable_control(self):
        button = self.altdriver.wait_for_object(By.PATH,
                                                '/DebugMenuPanelSettings/DebugMenuManager-container/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/UnityEngine.UIElements.VisualElement/UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.Button[3]',
                                                timeout=50)
        button.click()

    def click_level1_btn(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "BTN_LEVEL_1", timeout=10)
        ad_button.click()

    def click_btn_clear(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Booster-Clear", timeout=10)
        ad_button.click()

    def click_tutorial(self):
        #tutorial = self.altdriver.wait_for_object(By.NAME, "PopUp-Tutorial-SchemeA(Clone)",timeout=300)
        #tutorial.click()
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Next", timeout=30)
        ad_button.tap()

    def click_gotIt(self):
        time.sleep(1)
        # tutorial = self.altdriver.wait_for_object(By.NAME, "PopUp-Tutorial-SchemeA(Clone)",timeout=300)
        # tutorial.click()
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-GotIt", timeout=30)
        ad_button.tap()

    def click_back(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Back", timeout=30)
        ad_button.tap()

    def instruction1(self):
        time.sleep(2)
        try:
            ad_button = self.altdriver.find_object(By.NAME, "Instruction1")
            text_button = ad_button.get_text()
            return text_button
        except NotFoundException:
            return False

    def instruction2(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.NAME, "Instruction2")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def instruction3(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.NAME, "Instruction3")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def instruction4(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.NAME, "Instruction4")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def btn_next(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Continue", timeout=30)
        ad_button.tap()

    def btn_cell(self):
        time.sleep(2)
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-0-1", timeout=20)
        time.sleep(3)
        ad_button.click()
        ad_button.click()

    def popup_text(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.NAME, "Text ")
        text_button = ad_button.get_text()
        #ad_button.click()
        return text_button

    def place_queen_text(self):
        time.sleep(2)
        ad_button = self.altdriver.wait_for_object(By.PATH, "//TextBoxSmall-TapAgainToMark/Contents/Text ", timeout=20)
        text_button = ad_button.get_text()
        #ad_button.click()
        return text_button

    def EachColourOneQueenText(self):
        time.sleep(4)
        ad_button = self.altdriver.wait_for_object_object(By.PATH, "//TextBox-EachColourOneQueen/Contents/Text",
                                                          timeout=20)
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def queensCannotTouchText(self):
        time.sleep(4)
        ad_button = self.altdriver.wait_for_object(By.PATH, "//TextBox-QueensCantTouchQueens/Contents/Text",
                                                   timeout=20)
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def tapOnceSpacesRuleOutText(self):
        time.sleep(4)
        ad_button = self.altdriver.find_object(By.PATH, "//TextBox-TapOnceSpacesRuleOut/Contents/Text ")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def cantBeInRowsText(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.PATH, "//TextBox-CantBeInRows/Contents/Text")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def figureOutLastQueen(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.PATH, "//TextBox-FigureOutLastQueen/Contents/Text")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def needHintText(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.PATH, "//TextBoxSmall-NeedHint/Contents/Text")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def lastQueen(self):
        time.sleep(2)
        ad_button = self.altdriver.find_object(By.PATH, "//TextBoxSmall-OnlySpaceLeft/Contents/Text")
        text_button = ad_button.get_text()
        # ad_button.click()
        return text_button

    def click_cell_1(self):
        time.sleep(50)
        #control_pad_path = "/Canvas/KwaleeCanvas/Screen-Game(Clone)/Control Pad"
        control_pad_path = 'Background-Grey'
        button_continue_path = "Button-Continue"
        time.sleep(5)
        control_pad = self.altdriver.find_objects(By.NAME, control_pad_path)
        control_pad[0].click()
        control_pad1 = self.altdriver.wait_for_object(By.NAME, control_pad_path, timeout=20)

        control_pad1.click()

        button_continue = self.altdriver.wait_for_object(By.NAME, button_continue_path, timeout=20)

        button_continue.click()

        control_pad2 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad2.click()

        control_pad3 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad3.click()

        control_pad4 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad4.click()

        control_pad5 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad5.click()

        control_pad6 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad6.click()

        control_pad7 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad7.click()

        control_pad8 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad8.click()

        control_pad9 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad9.click()

        control_pad10 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad10.click()

        control_pad11 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad11.click()

        control_pad12 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad12.click()

        control_pad13 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad13.click()

        control_pad14 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad14.click()

        control_pad15 = self.altdriver.wait_for_object(By.PATH, control_pad_path, timeout=20)

        control_pad15.click()

    def click_cell_2(self):
        ad_button = self.altdriver.find_object(By.NAME, "Control Pad")
        ad_button.click()
        ad_button.click()

    def click_cell_3(self):
        ad_button = self.altdriver.find_object(By.NAME, "Control Pad")
        ad_button.click()
        ad_button.click()

    def level_complete(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Next", timeout=30)
        ad_button.click()

    def click_Privacy(self, retries=1, wait_between_attempts=5,
                      AltObjectNotFoundException=None):  # Increased default retries
        """
        Attempts to find and click the GDPR Accept button using AltTester,
        with a retry mechanism for transient disconnections or object not found.
        """
        gdpr_button_locator_path = "PrivacyPolicyButton"  # AltTester path locator

        for attempt in range(1, retries + 1):
            logging.info(
                f"click_GDPR: Attempt {attempt}/{retries}: Locating GDPR AcceptButton at {gdpr_button_locator_path}")

            # Print context handles for debugging, but use logging for cleaner output
            logging.debug(
                f"click_GDPR: Before AltTester operation, Appium context handles: {self.appium_driver.contexts}")

            try:
                # AltTester's wait_for_object handles its own timeout.
                # The timeout here is for AltTester's internal wait.
                gdpr_button = self.altdriver.wait_for_object(
                    By.NAME, gdpr_button_locator_path, timeout=70  # Use a reasonable AltTester timeout
                )

                logging.info(f"click_privacy: Found GDPR AcceptButton on attempt {attempt}. Clicking...")
                gdpr_button.click()
                logging.info("click_privacy: Successfully clicked GDPR AcceptButton.")

                # Print context handles after click for debugging
                logging.debug(
                    f"click_privacy: After AltTester operation, Appium context handles: {self.appium_driver.contexts}")
                return  # Exit successfully

            except AltException as e:  # Catch general AltTester exceptions, including connection issues (4002)
                logging.warning(f"click_GDPR: AltTester exception on attempt {attempt}: {e}")
                if "closed the connection or unexpectedly disconnected" in str(e):
                    logging.info("click_GDPR: App disconnected. Attempting to restart game and reconnect AltTester.")
                    # This is where you might trigger a full game restart and AltTester reconnection
                    # You would need access to package_name and main_activity here.
                    # For example, if these are class variables in TestBase:
                    # self.restart_game(TestBase._app_package, TestBase._android_app_activity)
                    # time.sleep(5) # Give app time to restart
                    # self.altdriver = TestBase.connect_to_alttester_with_retries(
                    #     cls=TestBase, # Pass TestBase class
                    #     game_package_name=TestBase._app_package,
                    #     game_main_activity=TestBase._android_app_activity,
                    #     max_retries=3, # Fewer retries for in-test reconnect
                    #     retry_delay_seconds=5
                    # )
                    # if self.altdriver is None:
                    #     logging.error("click_GDPR: Failed to reconnect AltTester after app restart attempt.")
                    #     raise # Re-raise if reconnection fails
            except Exception as e:  # Catch any other unexpected errors
                logging.error(f"click_privacy: An unexpected error occurred on attempt {attempt}: {e}")

            if attempt < retries:
                logging.info(f"click_privacy: Waiting {wait_between_attempts} seconds before retrying...")
                time.sleep(wait_between_attempts)
            else:
                logging.error(f"click_privacy: Failed to click GDPR AcceptButton after {retries} attempts.")
                raise

    def click_Terms(self, retries=1, wait_between_attempts=5,
                    AltObjectNotFoundException=None):  # Increased default retries
        """
        Attempts to find and click the GDPR Accept button using AltTester,
        with a retry mechanism for transient disconnections or object not found.
        """
        gdpr_button_locator_path = "TermsOfServiceButton"  # AltTester path locator

        for attempt in range(1, retries + 1):
            logging.info(
                f"click_GDPR: Attempt {attempt}/{retries}: Locating GDPR AcceptButton at {gdpr_button_locator_path}")

            # Print context handles for debugging, but use logging for cleaner output
            logging.debug(
                f"click_GDPR: Before AltTester operation, Appium context handles: {self.appium_driver.contexts}")

            try:
                # AltTester's wait_for_object handles its own timeout.
                # The timeout here is for AltTester's internal wait.
                gdpr_button = self.altdriver.wait_for_object(
                    By.NAME, gdpr_button_locator_path, timeout=70  # Use a reasonable AltTester timeout
                )

                logging.info(f"click_GDPR: Found GDPR AcceptButton on attempt {attempt}. Clicking...")
                gdpr_button.click()
                logging.info("click_GDPR: Successfully clicked GDPR AcceptButton.")

                # Print context handles after click for debugging
                logging.debug(
                    f"click_GDPR: After AltTester operation, Appium context handles: {self.appium_driver.contexts}")
                return  # Exit successfully

            except AltException as e:  # Catch general AltTester exceptions, including connection issues (4002)
                logging.warning(f"click_GDPR: AltTester exception on attempt {attempt}: {e}")
                if "closed the connection or unexpectedly disconnected" in str(e):
                    logging.info("click_GDPR: App disconnected. Attempting to restart game and reconnect AltTester.")
                    # This is where you might trigger a full game restart and AltTester reconnection
                    # You would need access to package_name and main_activity here.
                    # For example, if these are class variables in TestBase:
                    # self.restart_game(TestBase._app_package, TestBase._android_app_activity)
                    # time.sleep(5) # Give app time to restart
                    # self.altdriver = TestBase.connect_to_alttester_with_retries(
                    #     cls=TestBase, # Pass TestBase class
                    #     game_package_name=TestBase._app_package,
                    #     game_main_activity=TestBase._android_app_activity,
                    #     max_retries=3, # Fewer retries for in-test reconnect
                    #     retry_delay_seconds=5
                    # )
                    # if self.altdriver is None:
                    #     logging.error("click_GDPR: Failed to reconnect AltTester after app restart attempt.")
                    #     raise # Re-raise if reconnection fails
            except Exception as e:  # Catch any other unexpected errors
                logging.error(f"click_GDPR: An unexpected error occurred on attempt {attempt}: {e}")

            if attempt < retries:
                logging.info(f"click_GDPR: Waiting {wait_between_attempts} seconds before retrying...")
                time.sleep(wait_between_attempts)
            else:
                logging.error(f"click_GDPR: Failed to click GDPR AcceptButton after {retries} attempts.")
                raise

    def btn_cell_all(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-1-1", timeout=30)
        ad_button.click()
        ad_button1 = self.altdriver.wait_for_object(By.NAME, "Grid-4-1", timeout=30)
        ad_button1.click()
        ad_button2 = self.altdriver.wait_for_object(By.NAME, "Grid-5-1", timeout=30)
        ad_button2.click()

    def btn_cell_all_next(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-2-1", timeout=30)

        ad_button.click()
        ad_button1 = self.altdriver.wait_for_object(By.NAME, "Grid-3-1", timeout=30)

        ad_button1.click()
        ad_button2 = self.altdriver.wait_for_object(By.NAME, "Grid-8-1", timeout=30)

        ad_button2.click()

    def btn_cell_all_next1(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-9-1", timeout=30)
        time.sleep(3)
        ad_button.click()
        ad_button.click()

    def hint_icon(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Booster-Hint", timeout=30)
        time.sleep(3)
        ad_button.click()

    def btn_cell_all_next2(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-7-1", timeout=30)
        time.sleep(3)
        ad_button.click()
        ad_button.click()

    def queens_grid(self):
        print(">>> Entered queens_grid()", flush=True)
        try:
            # Wait for the element to appear (up to 15 seconds)
            self.altdriver.wait_for_object_which_contains(By.NAME, "queensGrid", timeout=15)

            queens_elements = self.altdriver.find_object_which_contains(By.NAME, "queensGrid")
            if queens_elements is None:
                print("queensGrid not found")
                return []

            print(f"Found {queens_elements} queensGrid elements")
            queens_name = queens_elements.name
            queens_list = queens_name.split(":")[1].strip("[]").split(",")
            print(queens_list)
            return queens_list
        except Exception as e:
            print(f"Exception in queens_grid: {e}", flush=True)
            return []

    def color_grid(self):
        print(">>> Entered color_grid()", flush=True)
        try:
            # Wait up to 15 seconds for the element
            self.altdriver.wait_for_object_which_contains(By.NAME, "gridColor", timeout=15)

            color_elements = self.altdriver.find_object_which_contains(By.NAME, "gridColor")
            if color_elements is None:
                print("gridColor not found", flush=True)
                return []

            print(f"Found {color_elements} gridColor elements", flush=True)
            grid_color_name = color_elements.name
            grid_color_list = grid_color_name.split(":")[1].strip("[]").split(",")
            print(grid_color_list, flush=True)
            return grid_color_list
        except Exception as e:
            print(f"Exception in color_grid: {e}", flush=True)
            return []

    def grid_size(self):
        try:
            print(">>> Entered grid_size()")
            size = self.altdriver.find_object_which_contains(By.NAME, "x*y")
            if size is None:
                print("Grid size element not found")
                return None
            print(f"Found {size} grid size element")
            size_text = size.name.split("-")[1]  # extract part after '-'
            x, y = map(int, size_text.split("*"))
            print(f"Grid size: x={x}, y={y}")
            return x, y
        except Exception as e:
            print(f"Exception in grid_size: {e}")
            return None

    def grid_size_daily_challenge(self):
        try:
            print(">>> Entered grid_size()")
            size = self.altdriver.find_object_which_contains(By.NAME, "daily_x*y")
            if size is None:
                print("Grid size element not found")
                return None
            print(f"Found {size} grid size element")
            size_text = size.name.split("-")[1]  # extract part after '-'
            x, y = map(int, size_text.split("*"))
            print(f"Grid size: x={x}, y={y}")
            return x, y
        except Exception as e:
            print(f"Exception in grid_size: {e}")
            return None

    def queens_grid_daily_challenge(self):
        print(">>> Entered queens_grid()", flush=True)
        try:
            # Wait for the element to appear (up to 15 seconds)
            self.altdriver.wait_for_object_which_contains(By.NAME, "daily_queensGrid", timeout=15)

            queens_elements = self.altdriver.find_object_which_contains(By.NAME, "daily_queensGrid")
            if queens_elements is None:
                print("queensGrid not found")
                return []

            print(f"Found {queens_elements} queensGrid elements")
            queens_name = queens_elements.name
            queens_list = queens_name.split(":")[1].strip("[]").split(",")
            print(queens_list)
            return queens_list
        except Exception as e:
            print(f"Exception in queens_grid: {e}", flush=True)
            return []

    def color_grid_daily_challenge(self):
        print(">>> Entered color_grid()", flush=True)
        try:
            # Wait up to 15 seconds for the element
            self.altdriver.wait_for_object_which_contains(By.NAME, "daily_gridColor", timeout=15)

            color_elements = self.altdriver.find_object_which_contains(By.NAME, "daily_gridColor")
            if color_elements is None:
                print("gridColor not found", flush=True)
                return []

            print(f"Found {color_elements} gridColor elements", flush=True)
            grid_color_name = color_elements.name
            grid_color_list = grid_color_name.split(":")[1].strip("[]").split(",")
            print(grid_color_list, flush=True)
            return grid_color_list
        except Exception as e:
            print(f"Exception in color_grid: {e}", flush=True)
            return []

    def color_grid_daily_challenge_iap1(self):
        print(">>> Entered color_grid_daily_challenge()", flush=True)
        try:
            # Wait for at least one matching element
            self.altdriver.wait_for_object_which_contains(By.NAME, "daily_gridColor", timeout=15)

            # Get all elements whose name contains 'daily_gridColor'
            color_elements = self.altdriver.find_objects(By.PATH, "//daily_gridColor")

            if len(color_elements) < 2:
                print(f"⚠️ Found only {len(color_elements)} 'daily_gridColor' elements.", flush=True)
                return []

            # Get the 2nd one
            second_color_element = color_elements[1]
            print(f"✅ Found second daily_gridColor element: {second_color_element.name}", flush=True)

            # Parse color list
            if ":" in second_color_element.name:
                grid_color_list = second_color_element.name.split(":")[1].strip("[]").split(",")
            else:
                print(f"⚠️ Unexpected format for grid color name: {second_color_element.name}", flush=True)
                return []

            print(f"🎨 Extracted grid colors: {grid_color_list}", flush=True)
            return grid_color_list

        except Exception as e:
            print(f"❌ Exception in color_grid_daily_challenge: {e}", flush=True)
            return []

    def level_id(self):
        try:
            print(">>> levelid")
            id = self.altdriver.find_object_which_contains(By.NAME, "levelid:")
            if id is None:
                print("level id element not found")
                return None
            print(f"Found {id} level id element")
            size_text = id.name.split(":")[1]  # extract part after '-'

            return size_text
        except Exception as e:
            print(f"Exception in grid_size: {e}")
            return None

    def btn_level_2(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_2', timeout=50)
        button.click()

    def btn_level_4(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_4', timeout=50)
        button.click()

    def btn_level_5(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_5', timeout=50)
        button.click()

    def btn_level_6(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_6', timeout=50)
        button.click()

    def btn_level_7(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_7', timeout=50)
        button.click()

    def btn_level_8(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_8', timeout=50)
        button.click()

    def btn_level_30(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_30', timeout=50)
        button.click()

    def btn_level_75(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_75', timeout=50)
        button.click()

    def btn_level_151(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_151', timeout=50)
        button.click()

    def btn_level_154(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_154', timeout=500)
        button.click()

    def btn_level_159(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_159', timeout=50)
        button.click()

    def btn_level_160(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_160', timeout=50)
        button.click()

    def btn_level_161(self):
        button = self.altdriver.wait_for_object(By.NAME, 'BTN_LEVEL_161', timeout=50)
        button.click()

    def booster_claim(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-Text", timeout=30)
        button.click()

    def vip_claim(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-Claim", timeout=30)
        button.click()

    def booster_queen(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-Booster-Queen", timeout=80)
        button.tap()

    def cell_12(self):
        button = self.altdriver.wait_for_object(By.NAME, "Grid-12-1", timeout=50)
        button.tap()
        button.tap()

    def cell_10(self):
        button = self.altdriver.wait_for_object(By.NAME, "Grid-10-1", timeout=50)
        button.click()
        button.click()

    def cell_09(self):
        button = self.altdriver.wait_for_object(By.NAME, "Grid-9-1", timeout=50)
        button.click()
        button.click()

    def cell_0(self):
        button = self.altdriver.wait_for_object(By.NAME, "Grid-0-1", timeout=50)
        button.click()
        button.click()

    def cell_15(self):
        button = self.altdriver.wait_for_object(By.NAME, "Grid-15-1", timeout=50)
        button.click()
        button.click()

    def booster_text(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//SpeechBubble/Panel/Text", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def click_balancy_btn(self):
        scroll_view = self.altdriver.wait_for_object(By.NAME, "optionsScrollView", timeout=15)

        # Get the screen position of the object
        position = scroll_view.get_screen_position()

        # Perform tap at that position
        self.altdriver.tap(position)

        # Perform scroll (negative speed = upward, positive = downward)
        self.altdriver.scroll(-10, 3)
        time.sleep(5)
        ad_button = self.altdriver.wait_for_object(By.NAME,
                                                   "BTN_HomeScreen_Balancy",
                                                   timeout=25)
        ad_button.click()

    def click_force_delete(self):
        #button = self.altdriver.wait_for_object(By.TEXT, "Force Delete Player (needs reboot)", timeout=50)
        button=self.altdriver.wait_for_object(By.PATH, "/DebugMenuPanelSettings/CONTAINER_HomeScreen_DebugMenu/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/CONTAINER_DebugPageBase_Root/UnityEngine.UIElements.Button[1]", timeout=50)
        button.click()

    def button_skins(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-Skins", timeout=30)
        button.click()

    def tab_queens(self):
        button = self.altdriver.wait_for_object(By.NAME, "Tab-Queen", timeout=30)
        button.click()

    def tab_colors(self):
        button = self.altdriver.wait_for_object(By.NAME, "Tab-Queen (1)", timeout=30)
        button.click()

    def cell_queen(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Cell-QueenSkin(Clone)[Skin_A]")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def cell_heart_notification(self):
        button = self.altdriver.wait_for_object(By.NAME, "Widget-Notification", timeout=30)
        button.click()

    def cell_event(self):
        button = self.altdriver.wait_for_object(By.NAME, "Cell-QueenEventSkin(Clone)", timeout=30)
        button.click()

    def cell_vip(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Cell-QueenVIPSkin(Clone)[Skin_E]")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def text_free_skin(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "IAP-Text (2)", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def skin_preview(self):
        button = self.altdriver.wait_for_object(By.NAME, "PreviewContainer", timeout=30)
        button.click()

    def cell_hearts(self):
        button = self.altdriver.wait_for_object(By.NAME, "Cell-QueenVIPSkin(Clone)", timeout=30)
        button.click()

    def treasure_event(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Widget-HomeScreen-QueensTreasureEvent")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def booster_claim_play(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Text")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def booster_queen_play(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Booster-Queen")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_booster_close_play(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-ClosePopup")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_fail_close_play(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, "Button-Close",timeout=20)
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_queens_event__play(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Start')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_navigation_jigsaw_play(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NavigationBar-Jigsaws')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_play_game_hard(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Play-Hard')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_play_game_very_hard(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Play-VeryHard')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_play_game_level(self, level):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            partial_name = f"LEVEL {level}"
            print(partial_name)  # color part is dynamic
            element = self.altdriver.find_object(By.NAME, 'Text-LevelX')
            element.click()

            print("play claim button clicked.")

        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")

    def btn_play_game(self):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            button = self.altdriver.find_object(By.NAME, 'Button-Play')

            if button:
                button.click()

                print("play claim button clicked.")
            else:
                print("play button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")

    def home_button_game(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Home')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def home_button_text(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, 'Home')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_fail_close_game(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Close')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def puzzel_hand_game(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'FTUE-Hand')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def puzzel_tab_game(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NavigationBar-Jigsaws')

            if button:
                button.click()
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def home_button_popup_puzzel(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Claim')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_reward_close_game(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, 'Button-PopupClose',timeout=2)

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_reward_No_Thanks(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NoThanks')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def home_tab_gamePlay(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NavigationBar-Home')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def win_game(self):
        button = self.altdriver.wait_for_object(By.TEXT, "Win Level", timeout=60)
        button.click()

    def get_install_id(self):
        time.sleep(2)
        try:
            ad_button = self.altdriver.wait_for_object(By.NAME, "LBL_InstallId",timeout=2)
            text_button = ad_button.get_text()
            return text_button
        except NotFoundException:
            return False

    def extract_install_id(self, text):
        if not text:  # catches None and False
            return None

        # Ensure it's a string
        text = str(text).strip()

        # Strip leading/trailing quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        # Regex to capture content inside <color=white>...</color>
        match = re.search(r"<color=white>(.*?)</color>", text)
        if match:
            return match.group(1).strip()

        return None

    def btn_2x_rv(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, 'Button-RVReward', timeout=30)

            if button:
                button.click()
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def x2_Applied(self):
        time.sleep(2)
        try:
            ad_button = self.altdriver.find_object(By.NAME, "Widget-x2Applied")

            return ad_button
        except NotFoundException:
            return False

    def is_element_present_expert_play(self):
        try:
            return self.altdriver.find_object(By.NAME, 'Button-Play-ExpertMode') is not None
        except Exception:
            return False

    def btn_play_expert(self):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            button = self.altdriver.find_object(By.NAME, 'Button-Play-ExpertMode')

            if button:
                button.click()

                print("play claim button clicked.")
            else:
                print("play button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")

    def btn_play_expert_try_for_free(self):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            button = self.altdriver.find_object(By.NAME, 'Button-TryFree')

            if button:
                button.click()

                print("play claim button clicked.")
            else:
                print("play button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")


    def btn_cell_expert_ftue(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Grid-44-1", timeout=30)
        ad_button.click()
        ad_button.click()
        ad_button1 = self.altdriver.wait_for_object(By.NAME, "Grid-35-1", timeout=30)
        ad_button1.click()
        ad_button2 = self.altdriver.wait_for_object(By.NAME, "Grid-43-1", timeout=30)
        ad_button2.click()
        ad_button3 = self.altdriver.wait_for_object(By.NAME, "Grid-51-1", timeout=30)
        ad_button3.click()
        ad_button4 = self.altdriver.wait_for_object(By.NAME, "Grid-36-1", timeout=3)
        ad_button4.click()
        ad_button5 = self.altdriver.wait_for_object(By.NAME, "Grid-52-1", timeout=3)
        ad_button5.click()
        ad_button5 = self.altdriver.wait_for_object(By.NAME, "Grid-37-1", timeout=3)
        ad_button5.click()
        ad_button6 = self.altdriver.wait_for_object(By.NAME, "Grid-45-1", timeout=3)
        ad_button6.click()
        ad_button7 = self.altdriver.wait_for_object(By.NAME, "Grid-53-1", timeout=3)
        ad_button7.click()
        ad_button8 = self.altdriver.wait_for_object(By.NAME, "Grid-44-1", timeout=3)
        ad_button8.click()
        ad_button8.click()
        ad_button9 = self.altdriver.wait_for_object(By.NAME, "Grid-59-1", timeout=3)
        ad_button9.click()
        ad_button10 = self.altdriver.wait_for_object(By.NAME, "Grid-4-1", timeout=3)
        ad_button10.click()
        ad_button11 = self.altdriver.wait_for_object(By.NAME, "Grid-4-1", timeout=3)
        ad_button11.click()
        ad_button12 = self.altdriver.wait_for_object(By.NAME, "Grid-12-1", timeout=3)
        ad_button12.click()
        ad_button13 = self.altdriver.wait_for_object(By.NAME, "Grid-20-1", timeout=3)
        ad_button13.click()
        ad_button14 = self.altdriver.wait_for_object(By.NAME, "Grid-28-1", timeout=3)
        ad_button14.click()
        ad_button15 = self.altdriver.wait_for_object(By.NAME, "Grid-46-1", timeout=3)
        ad_button15.click()
        ad_button15.click()
        ad_button16 = self.altdriver.wait_for_object(By.NAME, "Grid-62-1", timeout=3)
        ad_button16.click()
        ad_button16.click()
        ad_button17 = self.altdriver.wait_for_object(By.NAME, "Grid-34-1", timeout=3)
        ad_button17.click()
        ad_button17.click()
        ad_button18 = self.altdriver.wait_for_object(By.NAME, "Grid-50-1", timeout=3)
        ad_button18.click()
        ad_button18.click()
        ad_button19 = self.altdriver.wait_for_object(By.NAME, "Grid-32-1", timeout=3)
        ad_button19.click()
        ad_button19.click()
        ad_button20 = self.altdriver.wait_for_object(By.NAME, "Grid-48-1", timeout=3)
        ad_button20.click()
        ad_button20.click()
        ad_button21 = self.altdriver.wait_for_object(By.NAME, "Grid-17-1", timeout=3)
        ad_button21.click()
        ad_button21.click()
        ad_button22 = self.altdriver.wait_for_object(By.NAME, "Grid-19-1", timeout=3)
        ad_button22.click()
        ad_button22.click()
        ad_button23 = self.altdriver.wait_for_object(By.NAME, "Grid-13-1", timeout=3)
        ad_button23.click()
        ad_button23.click()
        ad_button24 = self.altdriver.wait_for_object(By.NAME, "Grid-29-1", timeout=3)
        ad_button24.click()
        ad_button24.click()
        ad_button25 = self.altdriver.wait_for_object(By.NAME, "Grid-15-1", timeout=3)
        ad_button25.click()
        ad_button25.click()
        ad_button26 = self.altdriver.wait_for_object(By.NAME, "Grid-31-1", timeout=3)
        ad_button26.click()
        ad_button26.click()
        ad_button27 = self.altdriver.wait_for_object(By.NAME, "Grid-3-1", timeout=3)
        ad_button27.click()
        ad_button27.click()
        ad_button28 = self.altdriver.wait_for_object(By.NAME, "Grid-1-1", timeout=3)
        ad_button28.click()
        ad_button28.click()

    def btn_play_expert_buy(self):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            button = self.altdriver.find_object(By.NAME, 'Button-Play-ExpertModeBuy')

            if button:
                button.click()

                print("play claim button clicked.")
            else:
                print("play button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")


    def btn_play_expert_next(self):

        try:
            time.sleep(2)
            # Try to find the button with a short wait
            #button = self.altdriver.find_objects(By.PATH, "//SubScreen-Home/PlayButtons/Button-Play", timeout=300)

            button = self.altdriver.find_object(By.NAME, 'Button-Play-ExpertModeNext')

            if button:
                button.click()

                print("play claim button clicked.")
            else:
                print("play button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("play button not available, continuing without click.")

    def enter_expert_level(self, text):
        time.sleep(7)
        text = str(text)
        #ad_button = self.altdriver.wait_for_object(By.PATH,
        # "//UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.TextField/unity-text-input/UnityEngine.UIElements.TextElement",
        # timeout=1500)
        # ad_button = self.altdriver.wait_for_object(By.PATH,
        #   "//unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.TextField/unity-text-input/UnityEngine.UIElements.TextElement",
        # timeout=1500)
        ad_button = self.altdriver.wait_for_object(By.NAME, "expertLevel_textBox", timeout=20)
        #ad_button = self.altdriver.find_object(By.NAME,"level_textBox")

        #ad_button.clic#k()

        #ad_button.set_text(ad_button.get_text()[:-1])
        time.sleep(4)
        ad_button.set_text(text)
        #ad_button.set_text(ad_button.get_text() + c)

        # Clear field by simulating backspaces
        #current_text = ad_button.get_text()
        #for _ in current_text:
        #ad_button.set_text(ad_button.get_text()[:-1])
        #ad_button.set_text("")
        #time.sleep(2)

        # Type each digit manually
        #for c in str(text):
        #ad_button.set_text(ad_button.get_text() + c)
        #time.sleep(3)

        print(f"DEBUG enter_level(): value after typing = {ad_button.get_text()}")

    def click_jump_expert_level(self):

        scroll_view = self.altdriver.wait_for_object(By.NAME, "optionsTabMainVisual", timeout=15)

        # Get the screen position of the object
        position = scroll_view.get_screen_position()

        # Perform tap at that position
        self.altdriver.tap(position)

        # Perform scroll (negative speed = upward, positive = downward)
        self.altdriver.scroll(-4, 3)
        #ad_button = self.altdriver.wait_for_object(By.TEXT, "Jump To Expert Level", timeout=15)
        ad_button = self.altdriver.wait_for_object(By.PATH, "/DebugMenuPanelSettings/CONTAINER_HomeScreen_DebugMenu/optionsTabMainVisual/holder/mainSafeArea/pagesContainerRoot/pagesContainer/CONTAINER_DebugPageBase_Root/UnityEngine.UIElements.ScrollView/unity-content-and-vertical-scroll-container/unity-content-viewport/unity-content-container/elementsContainer/UnityEngine.UIElements.Button[8]", timeout=15)
        ad_button.click()

    def btn_play_locked(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Locked')

            if button:
                return button
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def grid_size_expert(self):
        try:
            print(">>> Entered grid_size()")
            size = self.altdriver.find_object_which_contains(By.NAME, "expert_x*y")
            if size is None:
                print("Grid size element not found")
                return None
            print(f"Found {size} grid size element")
            size_text = size.name.split("-")[1]  # extract part after '-'
            x, y = map(int, size_text.split("*"))
            print(f"Grid size: x={x}, y={y}")
            return x, y
        except Exception as e:
            print(f"Exception in grid_size: {e}")
            return None

    def queens_grid_expert(self):
        print(">>> Entered queens_grid()", flush=True)
        try:
            # Wait for the element to appear (up to 15 seconds)
            self.altdriver.wait_for_object_which_contains(By.NAME, "expert_queensGrid", timeout=15)

            queens_elements = self.altdriver.find_object_which_contains(By.NAME, "expert_queensGrid")
            if queens_elements is None:
                print("queensGrid not found")
                return []

            print(f"Found {queens_elements} queensGrid elements")
            queens_name = queens_elements.name
            queens_list = queens_name.split(":")[1].strip("[]").split(",")
            print(queens_list)
            return queens_list
        except Exception as e:
            print(f"Exception in queens_grid: {e}", flush=True)
            return []

    def color_grid_expert(self):
        print(">>> Entered color_grid()", flush=True)
        try:
            # Wait up to 15 seconds for the element
            self.altdriver.wait_for_object_which_contains(By.NAME, "expert_gridColor", timeout=15)

            color_elements = self.altdriver.find_object_which_contains(By.NAME, "expert_gridColor")
            if color_elements is None:
                print("gridColor not found", flush=True)
                return []

            print(f"Found {color_elements} gridColor elements", flush=True)
            grid_color_name = color_elements.name
            grid_color_list = grid_color_name.split(":")[1].strip("[]").split(",")
            print(grid_color_list, flush=True)
            return grid_color_list
        except Exception as e:
            print(f"Exception in color_grid: {e}", flush=True)
            return []

    def btn_navigation_pet(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NavigationBar-Pets')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_navigation_leader_board(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-NavigationBar-Leaderboard')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_challenge(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-Challenge')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

