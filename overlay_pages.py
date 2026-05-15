import time

from alttester import By
from alttester import AltKeyCode

from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException
)


class OverlayPage(BasePage):

    def __init__(self, altdriver, appium_driver):
        BasePage.__init__(self, altdriver, appium_driver)

    @property
    def resume_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'Resume', timeout=2)

    @property
    def main_menu_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'Exit', timeout=2)

    @property
    def title(self):
        return self.altdriver.wait_for_object(By.PATH, '//Game/PauseMenu/Text', timeout=2)

    def is_displayed(self):
        return self.resume_button and self.main_menu_button and self.title

    def press_resume(self):
        self.resume_button.tap()

    def press_main_menu(self):
        self.main_menu_button.tap()

    def header_failure(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//Lives/Header", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def sub_header_failure(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text (TMP)", timeout=600)
        text_button = ad_button.get_text()
        return text_button

    def sub_header_new(self):
        ad_button = self.altdriver.find_objects(By.NAME, "Text (TMP)", )
        text_button = ad_button[2].get_text()
        return text_button

    def heart_amount(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//Amount/Text", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def item1_amount(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//ItemWithAmount-Store-Bundle(Clone)/Body/Amount/Text",
                                                   timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def item2_amount(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//ItemWithAmount-Store-Bundle(Clone)[1]/Body/Amount/Text",
                                                   timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def item3_amount(self):
        ad_button = self.altdriver.wait_for_object(By.PATH, "//ItemWithAmount-Store-Bundle(Clone)[2]/Body/Amount/Text",
                                                   timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def last_chance_header(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "HeaderText", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def button_fail_close(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, "Button-Close", timeout=3)
            if button:
                button.tap()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_Play_Rv(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-PlayOnRV", timeout=50)
        button.click()

    def button_Play_soft(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-PlayOnSoft", timeout=50)
        button.click()

    def btn_setting(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-Settings", timeout=50)
        button.click()

    def btn_bank_currency(self):
        button = self.altdriver.wait_for_object(By.NAME, "bank_Currency", timeout=50)
        button.click()

    def btn_vip(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-VIP', timeout=50)
        button.click()

    def btn_vip_freeTrial(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-FreeTrial', timeout=5)
        return button

    def btn_store_purchase(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-StorePurchase', timeout=5)
        return button

    def btn_store_purchase_rv(self):
        button = self.altdriver.find_objects(By.NAME, 'Button-StorePurchase')
        return button[0]

    def btn_store_purchase_free(self):
        button = self.altdriver.wait_for_object(By.PATH,
                                                '//Cell_Content/Cell-Shop-HalfHeight(Clone)/Body/Button-StorePurchase',
                                                timeout=50)
        button.click()

    def click_native_element_agree(self):
        retries = 2
        element_clicked = False
        wait = WebDriverWait(self.appium_driver, 30)  # use self.driver from BasePage

        while retries > 0 and not element_clicked:
            try:
                # Wait until the frame (content) element is visible
                frame = wait.until(EC.visibility_of_element_located((SeleniumBy.ID, "android:id/content")))

                if frame.is_displayed():
                    #frame.click()
                    print("✅ Frame clicked.")

                    try:
                        # Wait briefly before checking for consent
                        time.sleep(6)
                        consent_button = self.appium_driver.find_element(SeleniumBy.XPATH, "//*[@text='Agree']")
                        consent_button.click()
                        print("✅ Agree button clicked.")
                    except (TimeoutException, NoSuchElementException):
                        print("⚠️ Agree button not found. Proceeding to next step.")
                        return

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

    def click_native_element_buy(self):
        retries = 2
        element_clicked = False
        wait = WebDriverWait(self.appium_driver, 20)  # use self.driver from BasePage

        while retries > 0 and not element_clicked:
            try:
                # Wait until the frame (content) element is visible
                frame = wait.until(EC.visibility_of_element_located((SeleniumBy.ID, "android:id/content")))

                if frame.is_displayed():

                    try:
                        # Wait briefly before checking for consent
                        time.sleep(6)
                        consent_button = self.appium_driver.find_element(SeleniumBy.XPATH, "//*[@text='1-tap buy']")
                        consent_button.click()
                        print("✅ buy clicked.")
                    except (TimeoutException, NoSuchElementException):
                        print("⚠️ buy button not found. Proceeding to next step.")
                        return

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

    def click_native_element_subscribe(self):
        retries = 2
        element_clicked = False
        wait = WebDriverWait(self.appium_driver, 20)  # use self.driver from BasePage

        while retries > 0 and not element_clicked:
            try:
                # Wait until the frame (content) element is visible
                frame = wait.until(EC.visibility_of_element_located((SeleniumBy.ID, "android:id/content")))

                if frame.is_displayed():
                    #frame.click()
                    print("✅ Frame clicked.")

                    try:
                        # Wait briefly before checking for consent
                        time.sleep(6)
                        consent_button = self.appium_driver.find_element(SeleniumBy.XPATH, "//*[@text='Subscribe']")
                        consent_button.click()
                        print("✅ buy clicked.")
                    except (TimeoutException, NoSuchElementException):
                        print("⚠️ buy button not found. Proceeding to next step.")
                        return

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

    def btn_daily_reward(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Widget-HomeDailyReward', timeout=50)
        button.click()

    def btn_reward_claim(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Claim', timeout=50)
        button.click()

    def btn_reward_claim_again(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.wait_for_object(By.NAME, 'Button-ClaimAgain')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_reward_claim_puzzels(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.wait_for_object(By.NAME, 'Button-Claim')

            # If any are found, return True
            button.click()

        except Exception:
            # If none found, return False
            return False

    def btn_reward_claim_close(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.NAME, "Button-ClosePopup", timeout=2)
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_reward_Try_it(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, "Try it!")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_reward_spin_wheel(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Widget-HomeSpinWheel', timeout=50)
        button.click()

    def btn_free_spin(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-SpinWheel', timeout=50)
        button.click()

    def btn_free_spin_close(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Exit', timeout=50)
        button.click()

    def text_double_bundle(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-StarterPack!", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def is_notification_displayed(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Widget-Notification")

            # If any are found, return True
            return len(buttons) > 0

        except Exception:
            # If none found, return False
            return False

    def text_Title(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Title", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def text_Sub_Title(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Title (1)", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def btn_RV_Reward(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Rewards')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def profile(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Widget-PlayerProfileSmall', timeout=50)
        button.click()

    def profile_edit(self, text_to_enter):
        # Click the Edit button
        time.sleep(2)
        button = self.altdriver.wait_for_object(By.NAME, 'Widget-PlayerProfileLong', timeout=50)
        button.click()
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Edit', timeout=50)
        button.click()
        time.sleep(4)
        # Wait for the input field to appear (replace with your field name in Unity)
        input_field = self.altdriver.wait_for_object(By.NAME, 'Text-InputField', timeout=50)
        time.sleep(2)
        # Enter text into the field
        input_field.set_text(text_to_enter)
        time.sleep(2)
        # Press Enter key
        self.altdriver.press_key(AltKeyCode.Return)

    def profile_pic(self):
        buttons = self.altdriver.find_objects(By.NAME, 'Button-AvatarPick(Clone)')
        if len(buttons) >= 2:
            buttons[1].click()  # index 1 = 2nd element
        else:
            raise Exception("Less than 2 AvatarPick buttons found")

    def coin_count(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "ItemGroup", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def coin_count_lvl2_1(self):
        self.altdriver.wait_for_object(By.NAME, "ItemAmount", timeout=30)
        ad_button = self.altdriver.find_objects(By.NAME, "ItemAmount")
        text_button = ad_button[0].get_text()
        return text_button

    def coin_count_lvl2_2(self):
        self.altdriver.wait_for_object(By.NAME, "ItemAmount", timeout=30)
        ad_button = self.altdriver.find_objects(By.NAME, "ItemAmount")
        text_button = ad_button[1].get_text()
        return text_button

    def coin_count_lvl2_3(self):
        self.altdriver.wait_for_object(By.NAME, "ItemAmount", timeout=30)
        ad_button = self.altdriver.find_objects(By.NAME, "ItemAmount")
        text_button = ad_button[2].get_text()
        return text_button

    def starterPack(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "HeaderText", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def text_starter_pack_icons_1(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Body/Amount/Text")
        text_button = ad_button[0].get_text()
        return text_button

    def text_starter_pack_icons_2(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Body/Amount/Text")
        text_button = ad_button[1].get_text()
        return text_button

    def text_starter_pack_icons_3(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Body/Amount/Text")
        text_button = ad_button[2].get_text()
        return text_button

    def text_starter_pack_icons_4(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Body/Amount/Text")
        text_button = ad_button[3].get_text()
        return text_button

    def text_starter_pack_icons_5(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Body/Amount/Text")
        text_button = ad_button[4].get_text()
        return text_button

    def text_description(self):
        ad_button = self.altdriver.find_object(By.NAME, "Description")
        text_button = ad_button.get_text()
        return text_button

    def click_skin_scroll(self):
        print("scrolling")
        # Find the scroll view
        scroll_view = self.altdriver.wait_for_object(By.NAME, "ScrollView", timeout=15)

        # Get screen position (tuple)
        x, y = scroll_view.get_screen_position()
        print(f"ScrollView position: x={x}, y={y}")

        # Perform scroll
        # Python SDK scroll expects (x, y) tuple and speed integer
        self.altdriver.scroll(x, -2000)  # negative = scroll up

    def btn_RV_skin(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Group-Ads')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_store_skin(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'ItemWithAmount-Store-Horizontal-Purchase(Clone)')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_store_click(self):
        button = self.altdriver.find_objects(By.NAME, 'Button-SkinsPurchase')
        button[4].click()

    def btn_Queens_event_play(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Start', timeout=50)
        button.click()

    def text_event_1(self):
        ad_button = self.altdriver.find_objects(By.NAME, "Text-Info")
        text_button = ad_button[0].get_text()
        return text_button

    def text_event_2(self):
        ad_button = self.altdriver.find_objects(By.NAME, "Text-Info")
        text_button = ad_button[1].get_text()
        return text_button

    def text_event_3(self):
        ad_button = self.altdriver.find_objects(By.NAME, "Text-Info")
        text_button = ad_button[2].get_text()
        return text_button

    def btn_Queens_event(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-QueensEvent")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_event_info(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Info")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_leaderboard(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Leaderboard', timeout=50)
        button.click()

    def btn_leaderboard_pencil(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-EditPlayerName', timeout=50)
        button.click()

    def btn_settings(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Settings', timeout=50)
        button.click()

    def btn_toggle_music(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Toggle-Music', timeout=50)
        button.click()

    def btn_toggle_sound(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Toggle-Sound', timeout=50)
        button.click()

    def btn_toggle_haptic(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Toggle-Haptic', timeout=50)
        button.click()

    def btn_toggle_autox(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Toggle-Accessibility', timeout=50)
        button.click()

    def btn_quit(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-Quit', timeout=50)
        button.click()

    def btn_feedback(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Button-Feedback')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_subscription(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Button-Restore')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_privacy(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Button-PrivacyPolicy')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def adPreferences(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Button-AdPreferences')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def terms(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Button-TermsAndCondidionss')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def build(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'BuildNumber')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def userId(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'UserID')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def btn_click_privacy(self):
        button = self.altdriver.find_object(By.NAME, 'Button-PrivacyPolicy')
        button.click()

    def text_event_time(self):
        ad_button = self.altdriver.find_object(By.NAME, "TimeText")
        text_button = ad_button.get_text()
        return text_button

    def text_rewards_gems(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Amount/Text")
        text_button = ad_button[0].get_text()
        return text_button

    def text_rewards_coins(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Amount/Text")
        text_button = ad_button[1].get_text()
        return text_button

    def text_rewards_coins_hard(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Amount/Text")
        text_button = ad_button[2].get_text()
        return text_button

    def text_rewards_puzzel(self):
        ad_button = self.altdriver.find_objects(By.PATH, "//Amount/Text")
        text_button = ad_button[1].get_text()
        return text_button

    def btn_daily_challenge(self):
        button = self.altdriver.find_object(By.NAME, 'Button-HomeDailyChallenge')
        button.click()

    def btn_reward_close(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-PopupClose', timeout=50)
        button.click()

    def btn_navigation_jigsaw(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-NavigationBar-Jigsaws', timeout=50)
        button.click()

    def btn_play_daily_challenge(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-DailyChallenge', timeout=50)
        button.click()

    def btn_play_daily_challenge_rv(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Button-DailyChallengeRV', timeout=90)
        button.click()

    def btn_arrow_daily_challenge(self):
        button = self.altdriver.find_object(By.NAME, 'Button-Prev-Month')
        button.click()

    def btn_arrow_daily_challenge_1(self):
        button = self.altdriver.find_object(By.NAME, 'Button-Next-Month')
        button.click()

    def btn_challenge_info(self):
        button = self.altdriver.find_object(By.NAME, 'Button-Info')
        button.click()

    def btn_trophies(self):
        button = self.altdriver.find_object(By.NAME, 'Button-TrophyCollection')
        button.click()

    def notif_daily_challenge(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Notif')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def text_daily_challenge(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Text-BeatLevelsToWinPrizes')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def txt_privacy(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'PrivacyPolicy')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def text_Beating(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Beating", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def btn_vip_timer(self):

        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Widget-VIPTimer')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def text_very_hard(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Difficulty", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def text_widget_timer(self):
        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'Widget-VIPEventTimer')

            # If any are found, return True
            return button is not None

        except Exception:
            # If none found, return False
            return False

    def text_discount_vip(self):
        try:
            # Try to find all notification buttons
            button = self.altdriver.find_object(By.NAME, 'VIP-DiscountOffer')

            # If any are found, return True
            return button

        except Exception:
            # If none found, return False
            return False

    def button_tryItForFree(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-TryForFree')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_vip(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-VIP')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_continue(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Continue")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def is_RV_Reward_displayed(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Button-RVReward")

            # If any are found, return True
            return len(buttons) > 0

        except Exception:
            # If none found, return False
            return False

    def btn_rating(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "3")
            if button:
                button.click()
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("rating button not available, continuing without click.")

    def btn_rating_no_thanks(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, "No thanks")
            if button:
                button.click()
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("rating button not available, continuing without click.")

    def btn_rating_confirm(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.wait_for_object(By.TEXT, "Confirm Rating", timeout=3)
            if button:
                button.click()
                button.click()
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("rating button not available, continuing without click.")

    def button_winStreak(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Widget-HomeStreak')

            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def msg_treasure_Event(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, 'Grand Prize Claimed!')
            if button:
                return button
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def msg_treasure_Event_success(self):
        button = self.altdriver.find_object(By.NAME, 'Button-Awesome')
        button.click()

    def click_puzzel_tab(self):
        partial_name = 'Generator for 01_'
        element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
        element.click()

    def msg_puzzel_Event(self):
        text = self.altdriver.wait_for_object(By.NAME, 'Text-GrandPrize', timeout=15)
        return text

    def text_vip(self):
        text = self.altdriver.wait_for_object(By.NAME, 'Text-VIP', timeout=15)

    def text_club(self):
        text = self.altdriver.wait_for_object(By.NAME, 'Text-Club', timeout=15)
        return text

    def day_streak_day(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Text-DayNumber', timeout=5)
        return btn

    def day_streak_counter(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Text-DayStreak', timeout=5)
        return btn

    def day_streak_badges1(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge01', timeout=5)
        return btn

    def day_streak_badges2(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge02', timeout=50)
        return btn

    def day_streak_badges3(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge03', timeout=50)
        return btn

    def day_streak_badges4(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge04', timeout=50)
        return btn

    def day_streak_badges5(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge05', timeout=50)
        return btn

    def day_streak_badges6(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge06', timeout=50)
        return btn

    def day_streak_badges7(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge07', timeout=50)
        return btn

    def day_streak_badges8(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge08', timeout=50)
        return btn

    def day_streak_badges9(self):
        btn = self.altdriver.wait_for_object(By.NAME, 'Cell-AchievementBadge09', timeout=50)
        return btn

    def day_streak_player_stat1(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat/Text-Number', timeout=50)
        return btn.get_text()

    def day_streak_player_stat2(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat (1)/Text-Number', timeout=50)
        return btn.get_text()

    def day_streak_player_stat3(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat (2)/Text-Number', timeout=50)
        return btn.get_text()

    def day_streak_player_stat1_value(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat/Text -Value', timeout=50)
        return btn.get_text()

    def day_streak_player_stat2_value(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat (1)/Text -Value', timeout=50)
        return btn.get_text()

    def day_streak_player_stat3_value(self):
        btn = self.altdriver.wait_for_object(By.PATH, '//Cell-PlayerStat (2)/Text -Value', timeout=50)
        return btn.get_text()

    def tab_banners(self):
        button = self.altdriver.wait_for_object(By.NAME, 'Tab-Banners', timeout=50)
        button.click()

    def button_banner_pick_1(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Button-ProfileBackgroundPick(Clone)")

            # If any are found, return True
            buttons[0].click()

        except Exception:
            # If none found, return False
            return False

    def button_banner_pick_2(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Button-ProfileBackgroundPick(Clone)")

            # If any are found, return True
            buttons[1].click()

        except Exception:
            # If none found, return False
            return False

    def button_banner_pick_3(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Button-ProfileBackgroundPick(Clone)")

            # If any are found, return True
            buttons[2].click()

        except Exception:
            # If none found, return False
            return False

    def is_RoundText(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "TournamentHeader")

            # If any are found, return True
            return True

        except Exception:
            # If none found, return False
            return False

    def is_Timer(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Widget-Timer")

            # If any are found, return True
            return True

        except Exception:
            # If none found, return False
            return False

    def click_native_rating(self):
        retries = 2
        element_clicked = False
        wait = WebDriverWait(self.appium_driver, 20)  # use self.driver from BasePage

        while retries > 0 and not element_clicked:
            try:
                # Wait until the frame (content) element is visible
                frame = wait.until(EC.visibility_of_element_located((SeleniumBy.XPATH, "//*[@name='Not Now']")))

                if frame.is_displayed():

                    try:
                        # Wait briefly before checking for consent
                        time.sleep(6)
                        consent_button = self.appium_driver.find_element(SeleniumBy.XPATH, "//*[@name='Not Now']")
                        consent_button.click()
                        print("✅ buy clicked.")
                    except (TimeoutException, NoSuchElementException):
                        print("⚠️ buy button not found. Proceeding to next step.")
                        return

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

    def is_text_finished(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_object(By.NAME, "Text-YouFinished")

            # If any are found, return True
            return buttons

        except Exception:
            # If none found, return False
            return False

    def is_text_position(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_object(By.NAME, "Text-Position")

            # If any are found, return True
            return buttons

        except Exception:
            # If none found, return False
            return False

    def is_best_Results(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Text-Best")

            # If any are found, return True
            return len(buttons) > 0

        except Exception:
            # If none found, return False
            return False

    def is_rank(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Text-Rank")

            # If any are found, return True
            return len(buttons) > 0

        except Exception:
            # If none found, return False
            return False

    def is_panel_reduce_time(self):
        try:
            # Try to find all notification buttons
            buttons = self.altdriver.find_objects(By.NAME, "Panel-ReduceTime")

            # If any are found, return True
            return len(buttons) > 0

        except Exception:
            # If none found, return False
            return False

    def rating_confirm_btn(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Confirm")
            if button:
                button.click()
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def button_AutoX(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, 'Button-BuyAutoX')

            if button:
                button.click()
                print("AutoX  button clicked.")
            else:
                print("AutoX button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("AutoX button not available, continuing without click.")

    def widget_Queens_event(self):

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

    def widget_NoThanks(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, "NO THANKS!")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def finished_seasons(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Dropdown")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def puzzel_free(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, "Free")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def text_count(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Text-Count")
            if button:
                return button
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def text_header(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Text-Header")
            if button:
                return button
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def unlock_level(self):
        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-DailyChallengeIAP")
            if button:
                return button
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_accept(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Accept")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def tab_legends(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Tab-Legends")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_collect(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "ContinueButton")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_pet_1(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Widget-PetViewerWindow-FirstSelection")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_pet_1_select(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Select")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_pet_equip(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.NAME, "Button-Equip")
            if button:
                button.click()
                print("Booster claim button clicked.")
            else:
                print("Booster claim button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("Booster claim button not available, continuing without click.")

    def btn_noThanks(self):

        try:
            # Try to find the button with a short wait
            button = self.altdriver.find_object(By.TEXT, "No thanks!")
            if button:
                button.click()
                print("rating button clicked.")
            else:
                print("rating button not found, skipping.")
        except Exception:
            # If not found, just continue
            print("rating button not available, continuing without click.")

    def tab_leaderboard(self):
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
