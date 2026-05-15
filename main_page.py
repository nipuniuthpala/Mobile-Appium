import time
from alttester import By
from pages.base_page import BasePage


class MainPage(BasePage):
    def __init__(self, altdriver, appium_driver):
        BasePage.__init__(self, altdriver, appium_driver)

    def load(self):
        self.altdriver.load_scene('Main')

    @property
    def store_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'StoreButton', timeout=2)

    @property
    def leader_board_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'OpenLeaderboard', timeout=2)

    @property
    def settings_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'SettingButton', timeout=2)

    @property
    def mission_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'MissionButton', timeout=2)

    @property
    def run_button(self):
        return self.altdriver.wait_for_object(By.NAME, 'StartButton', timeout=2)

    @property
    def run_button_text(self):
        return self.altdriver.wait_for_object(By.PATH, '//UICamera/Loadout/StartButton/Text', timeout=2)

    @property
    def character_name(self):
        return self.altdriver.wait_for_object(By.NAME, 'CharName', timeout=2)

    @property
    def theme_name(self):
        return self.altdriver.wait_for_object(By.NAME, 'ThemeZone', timeout=2)

    def is_displayed(self):
        return self.store_button \
            and self.leader_board_button \
            and self.settings_button \
            and self.mission_button \
            and self.run_button \
            and self.character_name \
            and self.theme_name

    def press_run(self):
        while self.run_button_text.get_text() != "Run!":
            time.sleep(0.1)

        self.run_button.t

    def btn_clear(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Booster-Clear", timeout=30)
        ad_button.click()

    def btn_hint(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Booster-Hint", timeout=30)
        ad_button.click()

    def btn_settings(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Settings", timeout=30)
        ad_button.click()

    def btn_shop(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-NavigationBar-Shop", timeout=30)
        ad_button.click()

    def booster_count(self):
        ad_button = self.altdriver.wait_for_object(By.PATH,
                                                   "/Canvas/KwaleeCanvas/Screen-Game(Clone)/BottomUI/Widget-BoosterBar/Bar_Footer/Button-Booster-Queen/Contents/Badge-Booster/Body/Text",
                                                   timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def hint_count(self):
        ad_button = self.altdriver.wait_for_object(By.PATH,
                                                   "/Canvas/KwaleeCanvas/Screen-Game(Clone)/BottomUI/Widget-BoosterBar/Bar_Footer/Button-Booster-Hint/Contents/Badge-Booster/Body/Text",
                                                   timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def header_1(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Colour", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def header_2(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Rows&Columns", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def header_3(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-CantTouch", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def btn_play(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Play", timeout=30)
        ad_button.click()

    def hint_apply(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Apply", timeout=30)
        ad_button.click()

    def hint_text(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-Hint", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def hint_type_text(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-HintType", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def btn_booster_plus(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Icon-Plus", timeout=30)
        ad_button.click()

    def booster_plus_text(self):
        ad_button = self.altdriver.wait_for_object(By.TEXT, "Queen Finder", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def booster_plus_description(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Text-BoosterDescription", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def btn_booster_buy(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Buy", timeout=30)
        ad_button.click()

    def btn_booster_buy_coins(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Buy-Coins", timeout=30)
        ad_button.click()

    def btn_booster_close(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-ClosePopup", timeout=30)
        ad_button.click()

    def bank_currency(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "bank_Currency", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def bank_currency_text(self):
        time.sleep(2)
        ad_button = self.altdriver.wait_for_object(By.PATH, "//bank_Currency/Body/Amount/Text", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def hint_booster(self):
        ad_button = self.altdriver.wait_for_object(By.TEXT, "Hint", timeout=30)
        text_button = ad_button.get_text()
        return text_button

    def home_panel(self):
        ad_button = self.altdriver.wait_for_object(By.TEXT, "Home", timeout=30)
        ad_button.click()

    def shop_panel(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-NavigationBar-Shop", timeout=60)
        ad_button.click()

    def home_tab(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-NavigationBar-Home", timeout=30)
        ad_button.click()

    def puzzel_tab(self):
        button = self.altdriver.wait_for_object(By.NAME, "Button-NavigationBar-Jigsaws", timeout=50)
        button.click()
        button.click()

    def home_button(self):
        ad_button = self.altdriver.wait_for_object(By.NAME, "Button-Home", timeout=19)
        ad_button.click()

    def puzzel_hand(self):
        button = self.altdriver.wait_for_object(By.NAME, "FTUE-Hand", timeout=50)
        button.click()
