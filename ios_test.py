import base64
import datetime
import os
import sys
import time

import allure
import pytest
import requests
from PIL.ImageChops import overlay
from allure_commons.types import AttachmentType
from alttester import AltDriver
from datetime import datetime

from pages.game_play_page import GamePage
from pages.main_page import MainPage
from pages.overlay_pages import OverlayPage
from pages.start_page import StartPage
from tests.base_test import TestBase


class TestIOS(TestBase):

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print(">>> Setting up TestiOS class")

        # Initialize page objects once
        cls.start_page = StartPage(cls.altdriver, cls.appium_driver)
        cls.main_page = MainPage(cls.altdriver, cls.appium_driver)
        cls.game_page = GamePage(cls.altdriver, cls.appium_driver)
        cls.overlay_page = OverlayPage(cls.altdriver, cls.appium_driver)

    def setUp(self):
        """Optional: restart the game before each test if needed."""
        print(f">>> Restarting game before {self._testMethodName}")
        if self.platform == "android":
            self.restart_game(self._app_package, self._android_app_activity)
            time.sleep(15)
            self.click_Consent()

        else:
            self.restart_ios_app(self._ios_bundle_id)
            time.sleep(10)
            #self.click_Consent_IOS()

        time.sleep(4)  # wait small time for plugin to initialize

        # --- RECONNECT ALTTSTER WITH RETRIES ---
        max_retries = 5
        retry_delay = 3
        connected = False

        for attempt in range(1, max_retries + 1):
            try:
                self.altdriver = AltDriver(
                    host='alttester.kwalee.com',
                    port=13000,
                    app_name='Queens Puzzle',
                    enable_logging=True,
                    timeout=60

                )
                # Update page objects to use the new driver
                self.start_page.altdriver = self.altdriver
                self.main_page.altdriver = self.altdriver
                self.game_page.altdriver = self.altdriver
                self.overlay_page.altdriver = self.altdriver

                connected = True
                print(f"✅ AltTester reconnected cleanly on attempt {attempt}")
                break

            except Exception as e:
                print(f"⚠️ Failed to connect AltTester on attempt {attempt}: {e}")
                time.sleep(retry_delay)

        if not connected:
            raise RuntimeError("Failed to reconnect AltTester after restarting the app.")

    @pytest.mark.order(1)
    def test_Privacy(self):

        sys.stdout.write("test_use_appium_as_example: AltTester reconnected. Waiting for game to load...\n")
        time.sleep(3)
        self.start_page.click_Privacy()

    @pytest.mark.order(2)
    def test_Terms(self):
        self.start_page.click_Terms()

    @pytest.mark.order(3)
    def test_FTUE(self):
        time.sleep(3)
        self.overlay_page.button_fail_close()
        self.start_page.click_GDPR()
        time.sleep(5)
        text = self.start_page.place_queen_text()
        assert text == '<color=#2E86EC>Double tap</color> to place a queen'
        self.start_page.btn_cell()
        self.start_page.btn_cell()
        self.start_page.btn_next()

        text1 = self.start_page.queensCannotTouchText()
        assert text1 == 'Queens <#FF6B26>cannot touch </color>other Queens'
        # text2 = self.start_page.tapOnceSpacesRuleOutText()
        # assert text2 == '<color=#2E86EC>Tap once</color><br> in these spaces to rule them out'
        self.start_page.btn_cell_all()
        text3 = self.start_page.cantBeInRowsText()
        assert text3 == "Queens <#FF6B26>can't be in rows or columns </color>with other Queens either."
        self.start_page.btn_cell_all_next()
        text4 = self.start_page.lastQueen()
        assert text4 == "This is the<color=#2E86EC> last Green space </color>so it has to be a Queen"
        self.start_page.btn_cell_all_next1()
        self.start_page.btn_cell_all_next1()
        text5 = self.start_page.figureOutLastQueen()
        assert text5 == "Can you figure out where the last Queen has to go?"
        text6 = self.start_page.needHintText()
        assert text6 == "If you need a hint click here"
        self.start_page.hint_icon()
        self.start_page.hint_icon()
        time.sleep(2)
        self.start_page.btn_cell_all_next2()
        #self.start_page.btn_cell_all_next2()
        time.sleep(10)

        self.start_page.click_debug_menu()
        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()

        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        time.sleep(3)
        self.start_page.click_level1_btn()

        time.sleep(4)
        ins1 = self.start_page.instruction1()
        assert ins1 == 'You can only have <#FF6B26>1 Queen</color> per colour.'
        self.start_page.click_tutorial()
        self.start_page.click_back()
        self.start_page.click_tutorial()
        ins2 = self.start_page.instruction2()
        assert ins2 == "Queens <#FF6B26>can't touch</color> other queens"
        self.start_page.click_tutorial()
        ins3 = self.start_page.instruction3()
        assert ins3 == "Queens <#FF6B26>can't be in the same row or column</color> as other queens"
        self.start_page.click_tutorial()
        ins4 = self.start_page.instruction4()
        assert ins4 == "<color=#2E86EC>Double Tap</color> to place a Queen"
        self.start_page.click_gotIt()
        time.sleep(5)
        # self.start_page.click_btn_clear()
        self.overlay_page.rating_confirm_btn()
        self.overlay_page.click_native_rating()
        time.sleep(5)
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(5)
        sizeX_1 = self.start_page.grid_size()[0]
        sizeY_1 = self.start_page.grid_size()[1]
        gridColours_1 = [int(x) for x in self.start_page.color_grid()]
        queensGrid_1 = [int(x) for x in self.start_page.queens_grid()]
        time.sleep(5)
        #assert self.overlay_page.text_Beating() == 'You are beating <color=#FFC107> 6.43% </color> of other players!'
        time.sleep(2)

        self.start_page.btn_level_2()

        time.sleep(4)
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)
        time.sleep(8)
        self.overlay_page.btn_rating_confirm()
        self.overlay_page.click_native_rating()
        time.sleep(3)
        self.start_page.home_button_text()
        time.sleep(3)
        self.main_page.shop_panel()
        time.sleep(3)
        assert self.overlay_page.starterPack() == 'Starter Pack'
        assert self.overlay_page.text_starter_pack_icons_1() == '2000'
        assert self.overlay_page.text_starter_pack_icons_2() == 'Forever'
        assert self.overlay_page.text_starter_pack_icons_3() == 'Auto X'
        assert self.overlay_page.text_description() == 'Remove non optional ads.\nReward based ads will still be available.'
        time.sleep(4)

    @pytest.mark.order(4)
    def test_queen_booster(self):
        self.start_page.click_debug_menu()
        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()
        self.overlay_page.button_fail_close()
        time.sleep(10)
        self.start_page.click_debug_menu()
        time.sleep(5)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.click_give_money()
        self.start_page.enter_level(4)
        self.start_page.click_jump_level()
        time.sleep(10)
        self.start_page.booster_claim()
        time.sleep(2)
        self.overlay_page.button_tryItForFree()
        time.sleep(5)
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        time.sleep(4)
        self.start_page.btn_play_game()
        time.sleep(2)
        self.start_page.booster_claim()
        time.sleep(4)

        # self.overlay_page.btn_rating_confirm()
        self.overlay_page.button_tryItForFree()
        time.sleep(2)
        self.start_page.booster_queen()
        time.sleep(2)
        text = self.start_page.booster_text()
        assert text == 'Stuck?  Use <color=#009688>Boosters</color> to help you out'
        # self.start_page.click_btn_clear()
        time.sleep(2)
        row, col = 3, 0  # example
        rows = sizeX
        cols = sizeY

        index_to_update = col * rows + row
        queensGrid[index_to_update] = 2
        print(queensGrid)
        time.sleep(5)
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(5)
        self.overlay_page.btn_rating()
        self.overlay_page.btn_rating_confirm()
        assert self.overlay_page.btn_RV_Reward(), "RV Reward button was not found!"
        self.start_page.btn_level_5()
        time.sleep(2)

    @pytest.mark.order(5)
    def test_header_booster_hint_count(self):
        self.overlay_page.button_fail_close()

        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(4)

        self.overlay_page.rating_confirm_btn()

        self.main_page.btn_play()
        text = self.main_page.header_1()
        assert text == '1 Queen \nper colour'
        text1 = self.main_page.header_2()
        assert text1 == '1 Queen per column & row'
        text2 = self.main_page.header_3()
        assert text2 == 'Queens cannot touch'
        assert self.main_page.booster_count() == '3'
        assert self.main_page.hint_count() == '3'
        time.sleep(4)
        self.start_page.booster_queen()
        time.sleep(4)
        assert self.main_page.booster_count() == '2'
        self.main_page.btn_hint()
        text3 = self.main_page.hint_text()
        assert text3 == 'There is already a Queen on <color=#47B3B0>Teal</color> so you can eliminate (X) these squares'
        text4 = self.main_page.hint_type_text()
        assert text4 == 'Colour Check'
        self.main_page.hint_apply()
        time.sleep(2)
        assert self.main_page.hint_count() == '2'
        self.start_page.booster_queen()
        time.sleep(4)
        self.start_page.booster_queen()

        time.sleep(4)

        self.start_page.click_debug_menu()
        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()
        self.start_page.btn_level_6()
        time.sleep(6)

        self.start_page.booster_queen()
        time.sleep(2)
        text5 = self.main_page.booster_plus_text()
        assert text5 == 'Queen Finder'
        text6 = self.main_page.booster_plus_description()
        assert text6 == 'Reveals a queen!'
        self.count = int(self.main_page.bank_currency_text())
        self.main_page.btn_booster_close()
        self.start_page.booster_queen()
        time.sleep(4)
        self.main_page.btn_booster_buy_coins()

    @pytest.mark.order(6)
    def test_hint_lives_count(self):

        time.sleep(3)
        self.start_page.btn_reward_close_game()
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.main_page.shop_panel()
        #assert self.overlay_page.starterPack() == 'Perfect Starter Pack'
        #assert self.overlay_page.text_starter_pack_icons_1() == '10'
        #assert self.overlay_page.text_starter_pack_icons_2() == '10'
        #assert self.overlay_page.text_starter_pack_icons_3() == 'Forever'
        assert self.overlay_page.text_description() == 'Remove non optional ads.\nReward based ads will still be available.'
        time.sleep(3)
        self.main_page.home_tab()

        self.main_page.btn_play()
        time.sleep(5)
        self.main_page.btn_hint()
        text3 = self.main_page.hint_text()
        assert text3 == 'This is the only square of <color=#9178D0>Purple</color>!  So it must be a Queen'
        text4 = self.main_page.hint_type_text()
        assert text4 == 'Naked Single'
        self.main_page.hint_apply()
        time.sleep(4)
        self.main_page.btn_hint()
        text3 = self.main_page.hint_text()
        assert text3 == 'You can eliminate (X) all squares that touch Queens'
        text4 = self.main_page.hint_type_text()
        assert text4 == 'Proximity Check (Shared)'
        self.main_page.hint_apply()
        time.sleep(5)
        self.main_page.btn_hint()
        time.sleep(3)

        text5 = self.main_page.hint_booster()
        assert text5 == 'Hint'
        text6 = self.main_page.booster_plus_description()
        assert text6 == 'Stuck? Reveal your next move instantly!'
        time.sleep(2)
        self.start_page.btn_reward_close_game()

        self.main_page.btn_booster_buy_coins()
        time.sleep(3)
        self.start_page.cell_09()
        time.sleep(3)
        self.game_page.counter_lives()
        time.sleep(2)
        self.start_page.cell_0()
        self.start_page.cell_15()
        time.sleep(5)
        self.overlay_page.button_Play_soft()

    @pytest.mark.order(7)
    def test_tutorial_appears_after_two_failures(self):
        self.start_page.click_debug_menu()
        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()

        self.overlay_page.button_fail_close()
        time.sleep(3)
        self.overlay_page.btn_reward_claim_close()

        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.main_page.btn_play()
        self.overlay_page.btn_reward_claim_close()

        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()

        time.sleep(4)
        self.game_page.counter_lives_full()
        self.start_page.cell_09()
        time.sleep(3)
        self.game_page.counter_lives()
        self.start_page.cell_0()
        self.start_page.cell_15()
        text = self.overlay_page.header_failure()
        assert text == 'Continue?'
        text1 = self.overlay_page.sub_header_failure()
        assert text1 == 'Get 3 More Lives'
        text2 = self.overlay_page.heart_amount()
        assert text2 == '3'
        text3 = self.overlay_page.item1_amount()
        assert text3 == '3'
        text4 = self.overlay_page.item2_amount()
        assert text4 == '1d'
        text5 = self.overlay_page.item3_amount()
        assert text5 == '500'
        text6 = self.overlay_page.last_chance_header()
        assert text6 == 'Last Chance Bundle'
        time.sleep(4)
        self.overlay_page.button_fail_close()
        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(6)
        self.start_page.cell_09()
        self.start_page.cell_0()
        self.start_page.cell_15()
        time.sleep(4)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(5)
        ins1 = self.start_page.instruction1()
        assert ins1 == 'You can only have <#FF6B26>1 Queen</color> per colour.'
        self.start_page.click_tutorial()
        self.start_page.click_back()
        self.start_page.click_tutorial()
        ins2 = self.start_page.instruction2()
        assert ins2 == "Queens <#FF6B26>can't touch</color> other queens"
        self.start_page.click_tutorial()
        ins3 = self.start_page.instruction3()
        assert ins3 == "Queens <#FF6B26>can't be in the same row or column</color> as other queens"
        self.start_page.click_tutorial()
        ins4 = self.start_page.instruction4()
        assert ins4 == "<color=#2E86EC>Double Tap</color> to place a Queen"
        self.start_page.click_gotIt()
        time.sleep(2)
        self.start_page.cell_09()
        self.start_page.cell_0()
        self.start_page.cell_15()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        time.sleep(3)

    @pytest.mark.order(8)
    def test_purchase_last_chance(self):
        time.sleep(3)
        self.overlay_page.button_fail_close()

        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(4)

        count_new = int(self.main_page.bank_currency_text())
        #assert count_new == 30

        self.start_page.click_debug_menu()
        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()
        time.sleep(4)
        self.main_page.btn_play()
        time.sleep(3)
        self.overlay_page.btn_reward_claim_close()

        time.sleep(2)

        self.start_page.btn_reward_close_game()
        time.sleep(4)
        self.game_page.counter_lives_full()
        self.start_page.cell_09()
        self.start_page.cell_0()
        self.start_page.cell_15()
        time.sleep(6)
        assert self.overlay_page.btn_store_purchase()

    @pytest.mark.order(9)
    def test_VIP_coin_counter(self):
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(3)
        self.main_page.shop_panel()
        time.sleep(3)
        self.overlay_page.btn_bank_currency()
        self.overlay_page.btn_store_purchase_free()
        time.sleep(3)
        self.main_page.puzzel_tab()
        assert self.overlay_page.sub_header_failure() == 'Level 15'
        self.main_page.home_panel()
        time.sleep(3)
        self.main_page.btn_play()
        self.overlay_page.button_vip()
        self.overlay_page.button_fail_close()
        time.sleep(2)
        self.overlay_page.button_vip()

    @pytest.mark.order(10)
    def test_vip_claim(self):

        time.sleep(3)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.start_page.home_button_popup_puzzel()
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]

        self.main_page.btn_play()
        time.sleep(4)
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(3)

    @pytest.mark.order(11)
    def test_home(self):
        self.overlay_page.btn_reward_claim_close()
        time.sleep(4)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.start_page.btn_reward_close_game()
        time.sleep(2)
        assert self.overlay_page.is_notification_displayed() == True
        #assert self.overlay_page.text_Title() == 'QUEENS'
        time.sleep(2)

        self.overlay_page.profile()
        self.overlay_page.profile_pic()
        time.sleep(3)

        self.overlay_page.tab_banners()
        self.overlay_page.button_banner_pick_1()
        self.overlay_page.button_banner_pick_2()
        self.overlay_page.button_banner_pick_3()
        time.sleep(2)

    @pytest.mark.order(12)
    def test_shop(self):
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(6)
        self.main_page.shop_panel()
        time.sleep(4)
        #assert self.overlay_page.starterPack() == 'No Ads Bundle'
        assert self.overlay_page.coin_count_lvl2_1() == '800'
        assert self.overlay_page.coin_count_lvl2_2() == '3200'
        assert self.overlay_page.coin_count_lvl2_3() == '26000'
        time.sleep(3)
        assert self.overlay_page.btn_store_purchase_rv()

    @pytest.mark.order(13)
    def test_skins(self):
        self.overlay_page.btn_reward_claim_close()
        time.sleep(10)
        self.start_page.click_debug_menu()
        time.sleep(5)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.click_give_money()
        self.start_page.enter_level(10)
        time.sleep(3)
        self.start_page.click_jump_level()
        time.sleep(9)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()

        self.start_page.btn_play_game()
        time.sleep(2)
        self.start_page.booster_claim_play()

        time.sleep(2)
        self.start_page.button_skins()
        count = int(self.main_page.bank_currency_text())
        self.start_page.tab_colors()
        self.start_page.tab_queens()
        self.start_page.cell_queen()
        self.start_page.skin_preview()
        assert self.start_page.text_free_skin() == 'Free'
        self.start_page.cell_heart_notification()

        time.sleep(2)
        self.start_page.cell_vip()
        self.overlay_page.button_fail_close()
        time.sleep(2)
        assert self.overlay_page.btn_RV_skin(), "not found"
        time.sleep(2)

        self.overlay_page.btn_store_click()
        time.sleep(4)
        count_new = int(self.main_page.bank_currency_text())
        assert count_new == count - 500

        time.sleep(2)
        self.start_page.tab_colors()
        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(12)
        assert self.overlay_page.text_discount_vip(), "not found"

    @pytest.mark.order(14)
    def test_spin_wheel_daily_rewards(self):

        time.sleep(10)
        self.start_page.click_debug_menu()
        time.sleep(5)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.click_give_money()
        self.start_page.enter_level(10)
        time.sleep(3)
        self.start_page.click_jump_level()
        time.sleep(9)

        self.overlay_page.btn_reward_claim_close()
        time.sleep(2)
        self.overlay_page.button_winStreak()

        assert self.overlay_page.day_streak_counter()
        assert self.overlay_page.day_streak_badges1()
        assert self.overlay_page.day_streak_badges2()
        assert self.overlay_page.day_streak_badges3()
        assert self.overlay_page.day_streak_badges4()
        assert self.overlay_page.day_streak_badges5()
        assert self.overlay_page.day_streak_badges6()
        assert self.overlay_page.day_streak_badges7()
        assert self.overlay_page.day_streak_badges8()
        assert self.overlay_page.day_streak_badges9()

        assert self.overlay_page.day_streak_player_stat1() == '10'
        assert self.overlay_page.day_streak_player_stat2() == '0%'
        assert self.overlay_page.day_streak_player_stat3() == '0'

        assert self.overlay_page.day_streak_player_stat1_value() == 'Levels'
        assert self.overlay_page.day_streak_player_stat2_value() == 'Win Rate'
        assert self.overlay_page.day_streak_player_stat3_value() == 'Max Streak'
        time.sleep(3)
        self.overlay_page.button_fail_close()
        time.sleep(3)

        self.overlay_page.btn_reward_spin_wheel()
        self.overlay_page.btn_free_spin()
        time.sleep(4)
        self.overlay_page.btn_free_spin_close()
        time.sleep(3)
        self.overlay_page.btn_reward_spin_wheel()
        self.overlay_page.btn_free_spin()

        time.sleep(4)

    @pytest.mark.order(15)
    def test_events(self):

        time.sleep(3)
        self.start_page.click_debug_menu()
        time.sleep(3)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.enter_level(30)
        self.start_page.click_jump_level()
        time.sleep(7)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.overlay_page.button_winStreak()
        self.overlay_page.button_fail_close()
        assert self.start_page.btn_play_locked()
        time.sleep(4)
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        self.start_page.btn_play_game_level(30)
        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.overlay_page.button_tryItForFree()
        assert self.overlay_page.text_event_time() == '0/3'

        self.overlay_page.btn_Queens_event_play()
        time.sleep(3)
        assert self.overlay_page.text_event_1() == 'Play levels as normal'
        assert self.overlay_page.text_event_2() == 'Unlock Gems by\nfinding Queens'
        assert self.overlay_page.text_event_3() == 'Get unique rewards!'

        time.sleep(2)
        self.overlay_page.btn_Queens_event()
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.overlay_page.button_tryItForFree()
        self.start_page.button_queens_event__play()
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(10)

        self.overlay_page.button_vip()
        time.sleep(2)
        assert self.overlay_page.txt_privacy(), "not found"
        #assert self.overlay_page.btn_vip_freeTrial()
        #assert self.overlay_page.text_vip()
        #assert self.overlay_page.text_club()
        self.overlay_page.button_fail_close()
        time.sleep(4)

    @pytest.mark.order(16)
    def test_events_leaderboard_settings(self):

        time.sleep(6)
        self.overlay_page.btn_continue()
        self.start_page.treasure_event()
        time.sleep(3)
        self.overlay_page.btn_event_info()
        time.sleep(7)
        self.overlay_page.button_fail_close()
        time.sleep(4)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.btn_rating_no_thanks()

        time.sleep(4)
        self.overlay_page.btn_leaderboard()
        self.overlay_page.btn_collect()
        self.overlay_page.btn_continue()
        self.overlay_page.tab_legends()
        time.sleep(4)
        self.overlay_page.btn_leaderboard_pencil()
        time.sleep(2)
        self.overlay_page.profile_edit("TestUserNew")
        self.overlay_page.btn_reward_claim_close()

        time.sleep(2)
        self.overlay_page.btn_settings()
        self.overlay_page.btn_toggle_music()
        self.overlay_page.btn_toggle_sound()
        self.overlay_page.btn_toggle_haptic()
        self.overlay_page.btn_toggle_autox()
        assert self.overlay_page.btn_feedback(), "not found"
        assert self.overlay_page.adPreferences(), "not found"
        assert self.overlay_page.btn_privacy(), "not found"
        time.sleep(2)
        assert self.overlay_page.terms(), "not found"
        assert self.overlay_page.build(), "not found"
        assert self.overlay_page.userId(), "not found"
        self.overlay_page.button_fail_close()
        time.sleep(2)


    @pytest.mark.order(17)
    def test_treasure_Event_gems(self):

        time.sleep(8)
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        time.sleep(3)
        self.overlay_page.btn_continue()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(2)

        self.start_page.btn_play_game_level(31)
        self.overlay_page.btn_continue()
        self.start_page.button_queens_event__play()
        time.sleep(7)
        self.overlay_page.button_fail_close()
        time.sleep(3)

        time.sleep(3)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(2)
        self.overlay_page.btn_reward_Try_it()
        self.overlay_page.btn_reward_claim_close()

        time.sleep(5)
        # self.main_page.btn_clear()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)

    @pytest.mark.order(18)
    def test_ios_settings_quit(self):
        time.sleep(3)
        self.main_page.home_tab()
        self.start_page.home_button_game()
        self.main_page.btn_play()
        self.overlay_page.btn_settings()
        assert self.overlay_page.btn_subscription()
        self.overlay_page.btn_quit()
        time.sleep(5)

    @pytest.mark.order(19)
    def test_daily_challenge(self):

        time.sleep(3)
        self.start_page.click_debug_menu()
        time.sleep(3)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.enter_level(49)
        self.start_page.click_jump_level()

        time.sleep(8)
        self.overlay_page.button_winStreak()
        time.sleep(3)
        self.overlay_page.button_fail_close()
        time.sleep(3)
        self.overlay_page.btn_continue()
        time.sleep(3)
        self.overlay_page.btn_continue()
        time.sleep(3)
        self.overlay_page.btn_reward_Try_it()

        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.btn_reward_Try_it()
        time.sleep(3)

        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]

        self.start_page.btn_play_game_level(49)
        time.sleep(5)
        self.overlay_page.btn_reward_Try_it()
        self.overlay_page.button_tryItForFree()
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_fail_close()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(20)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.overlay_page.button_fail_close()
        assert self.overlay_page.is_RV_Reward_displayed()

    @pytest.mark.order(20)
    def test_daily_challenge_level_bronze_silver_gold(self):

        time.sleep(4)
        self.start_page.click_debug_menu()
        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()

        self.overlay_page.btn_daily_challenge()
        # assert self.overlay_page.text_daily_challenge(), "not found"

        self.overlay_page.btn_arrow_daily_challenge()
        time.sleep(2)
        self.overlay_page.btn_arrow_daily_challenge_1()
        time.sleep(2)
        self.overlay_page.btn_trophies()
        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(2)
        # self.overlay_page.btn_challenge_info()
        # time.sleep(4)
        # self.overlay_page.button_fail_close()

        sizeX = self.start_page.grid_size_daily_challenge()[0]
        sizeY = self.start_page.grid_size_daily_challenge()[1]
        gridColours = [int(x) for x in self.start_page.color_grid_daily_challenge()]
        queensGrid = [int(x) for x in self.start_page.queens_grid_daily_challenge()]
        # self.overlay_page.btn_reward_claim_close()
        time.sleep(4)
        self.overlay_page.btn_play_daily_challenge()
        time.sleep(4)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.game_page.counter_lives_full_hard()

        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)

        time.sleep(25)

        self.overlay_page.rating_confirm_btn()
        self.overlay_page.click_native_rating()
        time.sleep(5)
        self.start_page.home_button_text()
        time.sleep(10)
        sizeX_1 = self.start_page.grid_size_daily_challenge()[0]
        sizeY_1 = self.start_page.grid_size_daily_challenge()[1]
        gridColours_1 = [int(x) for x in self.start_page.color_grid_daily_challenge()]
        queensGrid_1 = [int(x) for x in self.start_page.queens_grid_daily_challenge()]

        time.sleep(4)
        assert self.overlay_page.unlock_level()
        self.overlay_page.btn_play_daily_challenge_rv()
        time.sleep(4)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.game_page.counter_lives_full_hard()
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)

        time.sleep(25)
        self.overlay_page.rating_confirm_btn()
        self.overlay_page.click_native_rating()
        time.sleep(5)
        self.start_page.home_button_text()
        time.sleep(10)
        sizeX_2 = self.start_page.grid_size_daily_challenge()[0]
        sizeY_2 = self.start_page.grid_size_daily_challenge()[1]
        gridColours_2 = [int(x) for x in self.start_page.color_grid_daily_challenge()]
        queensGrid_2 = [int(x) for x in self.start_page.queens_grid_daily_challenge()]

        time.sleep(5)
        self.overlay_page.btn_play_daily_challenge_rv()
        time.sleep(4)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.game_page.counter_lives_full_hard()
        self.game_page.process_queens_grid(queensGrid_2, gridColours_2, sizeX_2, sizeY_2)
        time.sleep(25)

        self.overlay_page.rating_confirm_btn()
        self.overlay_page.click_native_rating()
        time.sleep(4)
        self.start_page.home_button_text()

        time.sleep(8)
        self.overlay_page.btn_trophies()
        time.sleep(5)
        # self.overlay_page.btn_reward_claim_close()

    @pytest.mark.order(21)
    def test_puzzel_tab(self):

        time.sleep(5)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(5)
        self.main_page.puzzel_tab()
        time.sleep(3)
        self.start_page.home_button_popup_puzzel()
        time.sleep(3)


        time.sleep(3)
        self.start_page.click_debug_menu()

        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        time.sleep(3)
        self.start_page.click_game_btn()

        time.sleep(3)
        self.start_page.enter_level(75)
        self.start_page.click_jump_level()
        time.sleep(8)

        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        self.start_page.btn_play_game_level(75)
        time.sleep(3)
        self.overlay_page.btn_reward_Try_it()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        self.start_page.btn_reward_close_game()

        time.sleep(5)

        # self.main_page.btn_clear()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(10)
        self.overlay_page.btn_rating()
        self.overlay_page.btn_rating_no_thanks()
        time.sleep(8)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        self.start_page.btn_reward_close_game()
        self.main_page.home_button()
        time.sleep(5)
        self.overlay_page.btn_navigation_jigsaw()
        time.sleep(3)
        self.overlay_page.btn_continue()
        time.sleep(7)
        self.overlay_page.button_fail_close()
        time.sleep(8)
        self.start_page.puzzel_hand_game()
        time.sleep(3)
        self.main_page.puzzel_tab()
        # self.overlay_page.btn_reward_claim_puzzels()
        time.sleep(6)
        self.overlay_page.btn_event_info()
        time.sleep(6)

    @pytest.mark.order(22)
    def test_very_hard_level(self):

        time.sleep(3)
        self.start_page.click_debug_menu()

        time.sleep(4)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        time.sleep(3)
        self.start_page.click_game_btn()
        time.sleep(3)
        self.start_page.enter_level(153)
        self.start_page.click_jump_level()
        time.sleep(5)

        time.sleep(5)
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        assert self.overlay_page.text_very_hard() == 'Very Hard'
        self.start_page.btn_play_game_very_hard()
        self.overlay_page.button_fail_close()
        time.sleep(2)

        self.game_page.counter_lives_full_hard()



        time.sleep(3)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(3)
        self.overlay_page.button_AutoX()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(15)
        self.overlay_page.btn_rating()
        self.overlay_page.btn_rating_no_thanks()
        self.overlay_page.btn_reward_Try_it()
        sizeX_1 = self.start_page.grid_size()[0]
        sizeY_1 = self.start_page.grid_size()[1]
        gridColours_1 = [int(x) for x in self.start_page.color_grid()]
        queensGrid_1 = [int(x) for x in self.start_page.queens_grid()]

        self.start_page.btn_level_154()

        time.sleep(3)
        self.overlay_page.btn_reward_Try_it()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(2)
        self.overlay_page.btn_reward_Try_it()
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)
        time.sleep(5)
        self.overlay_page.btn_Queens_event()
        self.overlay_page.widget_NoThanks()

    @pytest.mark.order(23)
    def test_hard_level(self):

        time.sleep(3)
        self.start_page.click_debug_menu()

        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        time.sleep(3)
        self.start_page.click_game_btn()
        time.sleep(5)
        self.start_page.enter_level(158)
        self.start_page.click_jump_level()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        time.sleep(5)
        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        assert self.overlay_page.text_very_hard() == 'Hard'
        self.start_page.btn_play_game_hard()
        time.sleep(2)

        self.game_page.counter_lives_full_hard()
        time.sleep(3)
        self.overlay_page.btn_reward_claim_close()
        self.overlay_page.button_AutoX()
        self.start_page.btn_reward_close_game()
        self.start_page.btn_booster_close_play()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(15)
        sizeX_1 = self.start_page.grid_size()[0]
        sizeY_1 = self.start_page.grid_size()[1]
        gridColours_1 = [int(x) for x in self.start_page.color_grid()]
        queensGrid_1 = [int(x) for x in self.start_page.queens_grid()]
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.start_page.btn_level_159()
        time.sleep(2)
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        time.sleep(2)
        self.overlay_page.button_AutoX()
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)
        time.sleep(15)

        sizeX_2 = self.start_page.grid_size()[0]
        sizeY_2 = self.start_page.grid_size()[1]
        gridColours_2 = [int(x) for x in self.start_page.color_grid()]
        queensGrid_2 = [int(x) for x in self.start_page.queens_grid()]
        self.start_page.btn_level_160()
        time.sleep(2)

        # no ads assert
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()
        self.game_page.process_queens_grid(queensGrid_2, gridColours_2, sizeX_2, sizeY_2)
        time.sleep(6)
        self.start_page.btn_2x_rv()
        time.sleep(4)
        #assert self.start_page.x2_Applied()
       # assert self.overlay_page.text_rewards_gems() == 2
        #assert self.overlay_page.text_rewards_puzzel() == 42
        #assert self.overlay_page.text_rewards_coins_hard() == 4

    @pytest.mark.order(24)
    def test_puzzel_tab_complete(self):

        time.sleep(5)
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.main_page.shop_panel()

        assert self.overlay_page.text_description() == 'Remove non optional ads.\nReward based ads will still be available.'

        self.start_page.btn_reward_close_game()
        time.sleep(5)
        self.main_page.puzzel_tab()

        time.sleep(3)
        self.start_page.click_debug_menu()

        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        self.start_page.click_debug_menu()
        self.main_page.home_tab()
        time.sleep(8)

        # self.overlay_page.btn_reward_claim_puzzels()
        time.sleep(3)

        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        self.start_page.btn_play_game_level(161)
        time.sleep(3)
        self.overlay_page.btn_reward_Try_it()
        self.overlay_page.btn_reward_claim_close()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        self.start_page.btn_reward_close_game()

        time.sleep(5)

        # self.main_page.btn_clear()
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(10)
        self.overlay_page.btn_rating()
        self.overlay_page.btn_rating_no_thanks()
        time.sleep(8)
        self.main_page.home_button()
        time.sleep(5)
        self.overlay_page.btn_navigation_jigsaw()
        time.sleep(7)
        self.overlay_page.button_fail_close()
        time.sleep(8)
        self.start_page.puzzel_hand_game()
        time.sleep(3)
        # self.overlay_page.btn_reward_claim_puzzels()
        time.sleep(3)
        self.main_page.puzzel_tab()
        time.sleep(20)
        self.overlay_page.click_puzzel_tab()
        # self.overlay_page.btn_reward_claim_puzzels()
        self.overlay_page.btn_reward_claim_close()
        assert self.overlay_page.msg_puzzel_Event()
        time.sleep(3)


    @pytest.mark.order(25)
    def test_puzzel_tab_finished(self):

        self.start_page.btn_reward_close_game()
        time.sleep(5)
        self.main_page.puzzel_tab()
        #assert self.overlay_page.text_count()
        #assert self.overlay_page.text_header()
        #self.overlay_page.finished_seasons()
        self.overlay_page.puzzel_free()
        self.overlay_page.button_fail_close()
        time.sleep(3)


    @pytest.mark.order(26)
    def test_royal_tournament(self):

        time.sleep(5)
        self.overlay_page.button_winStreak()
        assert self.overlay_page.day_streak_day()
        time.sleep(3)
        self.overlay_page.button_fail_close()
        self.overlay_page.button_fail_close()
        time.sleep(5)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(3)
        self.main_page.btn_play()
        time.sleep(5)
        self.overlay_page.button_fail_close()
        time.sleep(5)
        self.overlay_page.btn_reward_claim_close()
        time.sleep(5)
        self.overlay_page.btn_continue()
        time.sleep(8)
        self.start_page.click_debug_menu()

        time.sleep(4)

        self.start_page.click_game_btn()

        self.start_page.win_game()
        assert self.overlay_page.is_Timer()

        time.sleep(5)
        #self.overlay_page.btn_continue()
        time.sleep(3)
        self.start_page.click_debug_menu()
        self.start_page.click_btn_Back()
        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)

        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()

        time.sleep(3)
        self.start_page.click_game_btn()

        self.start_page.win_game()

        time.sleep(6)
        self.overlay_page.btn_continue()
        #self.start_page.click_debug_menu()
        #self.start_page.click_game_btn()
        # self.start_page.win_game()
        time.sleep(6)
        # self.overlay_page.btn_continue()
        #self.start_page.click_debug_menu()
        # self.start_page.click_game_btn()
        # self.start_page.win_game()


        #assert self.overlay_page.is_text_finished()
        # assert self.overlay_page.is_best_Results()
        #assert self.overlay_page.is_rank()

        self.start_page.btn_play_game()
        time.sleep(3)
        self.overlay_page.btn_continue()
        #assert self.overlay_page.is_panel_reduce_time()

    @pytest.mark.order(27)
    def test_pvp_challenge(self):
        self.start_page.btn_reward_close_game()
        time.sleep(5)
        self.start_page.btn_navigation_leader_board()
        # assert self.overlay_page.text_count()
        # assert self.overlay_page.text_header()
        # self.overlay_page.finished_seasons()
        self.start_page.btn_challenge()
        time.sleep(4)
        self.overlay_page.btn_continue()
        self.start_page.click_debug_menu()

        time.sleep(3)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_toggle_Reward_Video()
        time.sleep(4)
        self.start_page.click_btn_Back()
        self.start_page.click_game_btn()

        self.start_page.win_game()

        time.sleep(4)
        self.overlay_page.btn_reward_claim()

        time.sleep(3)
    @pytest.mark.order(28)
    def test_expert_mode(self):
        self.start_page.btn_play_expert()
        self.start_page.btn_play_expert_try_for_free()
        self.start_page.btn_cell_expert_ftue()
        self.start_page.btn_play_expert_next()

    def tearDown(self):

        """Capture screenshot on test failure and stop AltDriver (SDK expects a file path)."""
        try:
            # Ensure screenshot directory exists (absolute path)
            screenshots_dir = os.path.abspath("screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)

            # Determine if the test failed
            outcome = getattr(self, "_outcome", None)
            failed = False
            if outcome and hasattr(outcome, "errors"):
                for _, excinfo in outcome.errors:
                    if excinfo is not None:
                        failed = True
                        break

            if failed and hasattr(self, "altdriver") and self.altdriver:
                try:
                    # Build unique screenshot path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = os.path.join(
                        screenshots_dir,
                        f"{self._testMethodName}_{timestamp}.png"
                    )

                    # ✅ Pass the full path — required by AltTester SDK
                    self.altdriver.get_png_screenshot(screenshot_path)

                    # Read the screenshot back
                    with open(screenshot_path, "rb") as f:
                        png_bytes = f.read()

                    # Attach to Allure report
                    allure.attach(
                        png_bytes,
                        name=f"{self._testMethodName}_FAILED_SCREENSHOT",
                        attachment_type=AttachmentType.PNG
                    )

                    print(f"📸 Screenshot saved and attached to Allure: {screenshot_path}")

                    # Encode for pytest-html usage (if conftest.py hook exists)
                    self._screenshot_for_html = base64.b64encode(png_bytes).decode("utf-8")

                except Exception as e:
                    print(f"⚠️ Could not capture screenshot in tearDown: {e}")

        finally:
            # Always stop AltDriver safely
            if hasattr(self, "altdriver") and self.altdriver:
                try:
                    self.altdriver.stop()
                    print("✅ AltTester stopped successfully.")
                except Exception as e:
                    print(f"⚠️ Failed to stop AltTester: {e}")
                finally:
                    self.altdriver = None

