import os
import time

import allure
import pytest
import pytest_html
from alttester import By

from pages.game_play_double import GameExpertPage
from pages.game_play_page import GamePage
from pages.main_page import MainPage
from pages.overlay_pages import OverlayPage
from pages.start_page import StartPage
from tests.base_test import TestBase


class TestExpertGame(TestBase):

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.start_page = StartPage(cls.altdriver, cls.appium_driver)
        cls.main_page = MainPage(cls.altdriver, cls.appium_driver)
        cls.game_page = GamePage(cls.altdriver, cls.appium_driver)
        cls.overlay_page = OverlayPage(cls.altdriver, cls.appium_driver)
        cls.game_expert_page = GameExpertPage(cls.altdriver, cls.appium_driver)

    # ---------------- FTUE ----------------
    @pytest.mark.order(1)
    def test_FTUE(self):
        self.start_page.click_GDPR()
        time.sleep(5)

        self.start_page.btn_cell()
        self.start_page.btn_cell()
        self.start_page.btn_next()

        # text2 = self.start_page.tapOnceSpacesRuleOutText()
        # assert text2 == '<color=#2E86EC>Tap once</color><br> in these spaces to rule them out'
        self.start_page.btn_cell_all()

        self.start_page.btn_cell_all_next()

        self.start_page.btn_cell_all_next1()
        self.start_page.btn_cell_all_next1()

        self.start_page.hint_icon()
        self.start_page.hint_icon()
        time.sleep(2)
        self.start_page.btn_cell_all_next2()
        self.start_page.btn_cell_all_next2()
        time.sleep(10)

        sizeX = self.start_page.grid_size()[0]
        sizeY = self.start_page.grid_size()[1]
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        self.start_page.click_level1_btn()
        time.sleep(4)
        ins1 = self.start_page.instruction1()

        self.start_page.click_tutorial()
        self.start_page.click_back()
        self.start_page.click_tutorial()
        ins2 = self.start_page.instruction2()
        self.start_page.click_tutorial()
        ins3 = self.start_page.instruction3()

        self.start_page.click_tutorial()
        ins4 = self.start_page.instruction4()

        self.start_page.click_gotIt()
        # self.start_page.click_btn_clear()
        time.sleep(5)
        self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
        time.sleep(5)
        self.start_page.btn_reward_close_game()
        self.start_page.btn_booster_close_play()

        sizeX_1 = self.start_page.grid_size()[0]
        sizeY_1 = self.start_page.grid_size()[1]
        gridColours_1 = [int(x) for x in self.start_page.color_grid()]
        queensGrid_1 = [int(x) for x in self.start_page.queens_grid()]
        time.sleep(5)
        self.start_page.btn_reward_close_game()
        self.start_page.btn_booster_close_play()
        time.sleep(4)
        self.start_page.click_debug_menu()
        time.sleep(7)
        self.start_page.click_Ad()
        time.sleep(4)
        self.start_page.click_toggle_Ad()
        self.start_page.click_toggle_Video()
        self.start_page.click_toggle_Reward_Video()
        self.start_page.click_toggle_Interstitial_Video()
        self.start_page.click_btn_Back()

        self.start_page.click_debug_menu()
        self.start_page.btn_booster_close_play()
        self.start_page.btn_reward_close_game()
        time.sleep(4)
        self.start_page.btn_booster_close_play()
        self.start_page.btn_level_2()
        time.sleep(2)
        self.overlay_page.btn_rating()
        self.overlay_page.btn_rating_confirm()
        # self.start_page.click_btn_clear()
        time.sleep(2)
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)
        time.sleep(1)

    # ---------------- GAMEPLAY ----------------
    def _run_gameplay(self, level, first_level, last_level):
        print(f"▶️ Running _run_gameplay: level={level}, first_level={first_level}, last_level={last_level}")

        # 🔹 Jump to level 100 only for the actual first Expert level



        print(f"▶️ Playing Expert level {level}")

        # Close leftover overlays
        self.overlay_page.button_fail_close()
        self.overlay_page.btn_reward_claim_close()
        self.start_page.btn_reward_close_game()

        # Read grid
        sizeX, sizeY = self.start_page.grid_size_expert()
        queensGrid = [int(x) for x in self.start_page.queens_grid_expert()]

        # Click Play
        if self.start_page.is_element_present_expert_play():
            self.start_page.btn_play_expert()
        else:
            print("▶️ Play Expert button not found, clicking Next button instead")
            self.start_page.btn_play_expert_next()
        time.sleep(4)

        # Solve ONE level
        self.game_expert_page.click_all_queens_from_grid(
            queensGrid, sizeX, sizeY
        )

        time.sleep(4)

        # Go next only if not last
        if level != last_level:
            self.overlay_page.button_fail_close()
            self.overlay_page.btn_reward_claim_close()
            self.start_page.btn_reward_close_game()

        # Final cleanup for the last level
        if level == last_level:
            print("🧹 Final cleanup")
            self.start_page.click_debug_menu()
            self.start_page.click_game_btn()
            for _ in range(6):
                self.start_page.click_clear_prefs()

            self.start_page.click_btn_Back()
            self.start_page.click_balancy_btn()
            for _ in range(6):
                self.start_page.click_force_delete()

            self.altdriver.stop()

    # ---------------- DYNAMIC TESTS ----------------
    @classmethod
    def add_level_tests(cls):
        env_start = os.environ.get("START_LEVEL")
        env_count = os.environ.get("LEVEL_COUNT")

        if env_start and env_count:
            first_level = int(env_start)
            level_count = int(env_count)
        else:
            app_config = TestBase.read_config_properties("config.properties")
            first_level = int(app_config.get("START_LEVEL", 1))
            level_count = int(app_config.get("LEVEL_COUNT", 1))

        last_level = first_level + level_count - 1

        # ------------------- FIRST JUMP TEST -------------------
        def test_jump_to_100(self):
            print(f"🔹 First-time jump to 100 and back to expert {first_level}")
            # these calls require driver, so they will work when test runs, not here
            self.start_page.click_debug_menu()
            self.start_page.click_game_btn()
            self.start_page.enter_level(100)
            self.start_page.click_jump_level()

            self.start_page.click_debug_menu()
            self.start_page.click_game_btn()
            self.start_page.enter_expert_level(first_level)
            self.start_page.click_jump_expert_level()
            time.sleep(5)

        setattr(cls, f"test_gameplay_jump_to_100", test_jump_to_100)

        # ------------------- NORMAL LEVEL TESTS -------------------
        for level in range(first_level, last_level + 1):
            def make_test(level=level, first_level=first_level, last_level=last_level):
                def test_func(self):
                    return self._run_gameplay(level, first_level, last_level)

                test_func.__name__ = f"test_gameplay_level_{level}"
                return test_func

            setattr(cls, f"test_gameplay_level_{level}", make_test())

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item, call):
        outcome = yield
        rep = outcome.get_result()
        # check if the test has level_id attached
        if hasattr(item, "level_id"):
            rep.level_id = item.level_id

    @pytest.hookimpl(optionalhook=True)
    def pytest_html_results_table_extra(report, extra):
        if hasattr(report, 'level_id'):
            extra.append(pytest_html.extras.text(f"Level ID: {report.level_id}"))


# ---------------- CREATE TESTS ----------------
TestExpertGame.add_level_tests()
