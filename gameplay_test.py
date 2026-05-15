import os
import time

import allure
import pytest
import pytest_html
from alttester import By

from pages.game_play_page import GamePage
from pages.main_page import MainPage
from pages.overlay_pages import OverlayPage
from pages.start_page import StartPage
from tests.base_test import TestBase


class TestGame(TestBase):

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.start_page = StartPage(cls.altdriver, cls.appium_driver)
        cls.main_page = MainPage(cls.altdriver, cls.appium_driver)
        cls.game_page = GamePage(cls.altdriver, cls.appium_driver)
        cls.overlay_page = OverlayPage(cls.altdriver, cls.appium_driver)

    @pytest.mark.order(1)
    def test_FTUE(self):

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
        assert text3 == "Queens <#FF6B26>can't be in rows or columns </color>with other Queens either.  "
        self.start_page.btn_cell_all_next()
        text4 = self.start_page.lastQueen()
        assert text4 == "This is the<color=#2E86EC> last Green space </color>so it has to be a Queen"
        self.start_page.btn_cell_all_next1()
        self.start_page.btn_cell_all_next1()
        text5 = self.start_page.figureOutLastQueen()
        assert text5 == "Can you figure out where the last Queen has to go?"
        text6 = self.start_page.needHintText()
        assert text6 == "If you need a hint click here "
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
        #self.start_page.click_btn_clear()
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
        #self.start_page.click_btn_clear()
        time.sleep(2)
        self.game_page.process_queens_grid(queensGrid_1, gridColours_1, sizeX_1, sizeY_1)
        time.sleep(1)

    def _run_gameplay(self, level, first_level, last_level):

        if level == first_level:
            time.sleep(10)
            self.start_page.click_debug_menu()
            time.sleep(5)
            self.start_page.click_game_btn()
            time.sleep(6)
            self.start_page.enter_level(first_level)
            time.sleep(4)
            self.start_page.click_jump_level()
            time.sleep(10)

            # Initial booster/game setup
            self.start_page.booster_claim_play()
            self.overlay_page.btn_rating()
            self.overlay_page.btn_rating_confirm()
            self.start_page.btn_reward_close_game()
            self.start_page.home_button_popup_puzzel()
            time.sleep(2)
            self.start_page.button_fail_close_game()
            self.start_page.button_queens_event__play()
            self.start_page.btn_reward_No_Thanks()
            time.sleep(5)

        # 👉 Gameplay part for ALL levels
        time.sleep(25)
        sizeX, sizeY = self.start_page.grid_size()
        gridColours = [int(x) for x in self.start_page.color_grid()]
        queensGrid = [int(x) for x in self.start_page.queens_grid()]
        level_id = self.start_page.level_id()
        self._update_test_name(level, level_id)
        if hasattr(self, "_request"):
            self._request.node.level_id = level_id

        print("🔄 Recovering via home navigation...")

        entered = False
        try:
            time.sleep(2)
            #self.start_page.btn_reward_No_Thanks()
            level_btn = self.altdriver.find_object(By.NAME, f"BTN_LEVEL_{level}")
            if level_btn:
                level_btn.click()
                self.overlay_page.btn_rating()
                self.overlay_page.btn_rating_confirm()
                self.start_page.booster_claim_play()
                self.start_page.btn_reward_close_game()
                self.start_page.button_queens_event__play()
                self.overlay_page.button_tryItForFree()
                time.sleep(3)
                self.start_page.btn_reward_No_Thanks()
                time.sleep(2)
                self.start_page.booster_claim_play()
                self.start_page.btn_booster_close_play()
                self.start_page.btn_reward_close_game()
                time.sleep(2)
                self.start_page.btn_reward_No_Thanks()
                time.sleep(3)
                self.start_page.button_fail_close_play()
                time.sleep(3)
                self.start_page.puzzel_hand_game()
                entered = True
                print(f"Clicked BTN_LEVEL_{level}")
        except Exception:
            pass

        if not entered:
            print(f"⚠️ Level button BTN_LEVEL_{level} not found. Fallback to Home -> Play.")
            try:
                time.sleep(10)
                self.start_page.btn_play_game_level(level)

                self.start_page.booster_claim_play()
                self.start_page.btn_reward_close_game()
                time.sleep(2)
                self.overlay_page.btn_rating()
                self.overlay_page.btn_rating_confirm()
                self.start_page.btn_reward_No_Thanks()
                time.sleep(10)
                self.start_page.btn_play_game_level(level)
                time.sleep(2)
                self.start_page.home_button_text()
                self.start_page.booster_claim_play()
                self.overlay_page.button_tryItForFree()
                self.start_page.btn_reward_close_game()
                time.sleep(2)
                self.start_page.btn_reward_No_Thanks()
                time.sleep(2)
                self.start_page.button_queens_event__play()
                time.sleep(2)
                self.start_page.btn_navigation_jigsaw_play()
                time.sleep(2)
                self.start_page.button_fail_close_game()
                time.sleep(2)
                self.start_page.puzzel_hand_game()
                self.start_page.home_button_popup_puzzel()
                time.sleep(2)
                self.start_page.puzzel_tab_game()
                time.sleep(3)
                self.start_page.home_tab_gamePlay()
                self.start_page.home_button_game()
                self.start_page.btn_booster_close_play()
                time.sleep(3)
                self.start_page.button_fail_close_play()
                time.sleep(3)
                self.start_page.puzzel_hand_game()
                self.start_page.home_button_popup_puzzel()
                time.sleep(5)
                self.start_page.btn_play_game()
                time.sleep(1)
                self.start_page.btn_play_game_hard()
                time.sleep(1)
                self.start_page.btn_play_game_very_hard()
                time.sleep(3)
                self.start_page.puzzel_hand_game()

                entered = True
            except Exception as e:
                pytest.fail(f"Fallback navigation failed at level {level}: {e}")

        time.sleep(5)

        # --- Step 3: Solve using the grid ---
        try:
            # self.start_page.click_btn_clear()
            self.game_page.process_queens_grid(queensGrid, gridColours, sizeX, sizeY)
            print(f"✅ Solved grid for level {level}{level_id}")
            time.sleep(10)
            return level_id
        except Exception as e:
            pytest.fail(f"Failed to solve level {level}: {e}")

        if level == last_level:
            # Cleanup after each level
            self.start_page.click_debug_menu()
            time.sleep(3)
            self.start_page.click_game_btn()
            time.sleep(3)
            for _ in range(6):
                self.start_page.click_clear_prefs()
            time.sleep(4)
            self.start_page.click_btn_Back()
            time.sleep(2)
            self.start_page.click_balancy_btn()
            for _ in range(6):
                self.start_page.click_force_delete()
            self.altdriver.stop()

    def _update_test_name(self, level, level_id):
        """Dynamically rename the test in reports/output (Allure + best-effort for pytest-html)."""
        new_name = f"test_gameplay_level_{level}_{level_id}"
        self._testMethodName = new_name

        # Best-effort: set nodeid if present (pytest internals vary across versions)
        # Pytest-html rename
        try:
            if hasattr(self, "_request"):
                self._request.node._nodeid = new_name
        except Exception:
            pass

        print(f"🧩 Test renamed to: {new_name}")
        try:
            allure.dynamic.title(new_name)
        except Exception:
            pass

    @classmethod
    def add_level_tests(cls):
        """
        Read overrides from environment first (Jenkins should export START_LEVEL & LEVEL_COUNT).
        If not present, fall back to config.properties.
        """
        # Prefer environment variables (Jenkins should export these before pytest is invoked)
        env_start = os.environ.get("START_LEVEL")
        env_count = os.environ.get("LEVEL_COUNT")

        # Determine config path robustly
        config_path = "config.properties"

        if env_start and env_count:
            try:
                first_level = int(env_start.strip())
                level_count = int(env_count.strip())
                print(f"🚀 Dynamic tests from ENV: START_LEVEL={first_level}, LEVEL_COUNT={level_count}")
            except Exception as e:
                print(f"❌ Invalid env START_LEVEL/LEVEL_COUNT: {e}. Falling back to config file.")
                env_start = env_count = None  # force fallback
        if not env_start or not env_count:
            # Try reading config via TestBase helper
            try:
                app_config = TestBase.read_config_properties(str(config_path))
                first_level = int(app_config.get("START_LEVEL", 1).strip())
                level_count = int(app_config.get("LEVEL_COUNT", 1).strip())
                print(
                    f"🚀 Dynamic tests from CONFIG: START_LEVEL={first_level}, LEVEL_COUNT={level_count} (path: {config_path})")
            except Exception as e:
                # ultimate fallback
                first_level = 1
                level_count = 1
                print(f"⚠️ Failed to read START_LEVEL/LEVEL_COUNT from env/config: {e}. Using defaults: 1,1")

        last_level = first_level + level_count - 1

        # create tests for levels [first_level .. last_level]
        for level in range(first_level, last_level + 1):
            def make_test(level=level, first_level=first_level, last_level=last_level):
                def test_func(self):
                    # call gameplay runner
                    return self._run_gameplay(level, first_level, last_level)

                # set python function name for nicer display in some reporters

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


# create the tests at module import time (pytest collection will find them)
TestGame.add_level_tests()
