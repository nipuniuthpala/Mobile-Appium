import base64
import datetime
import os
import time
from datetime import datetime
import allure
import pytest
from allure_commons.types import AttachmentType
from alttester import AltDriver


from pages.databricks_connector import DatabricksClient
from pages.game_play_page import GamePage
from pages.main_page import MainPage
from pages.overlay_pages import OverlayPage
from pages.start_page import StartPage
from tests.base_test import TestBase


class TestAndroidAnalytics(TestBase):
    install_id = None
    start_page = None

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    @classmethod
    def setUpClass(cls):
        # Set platform first
        cls.platform = os.getenv("APPIUM_PLATFORM", "android").lower()
        # Re-initialize Appium driver without reinstalling the app
        cls.appium_driver = cls._get_appium_options(reset_app=False)  # helper method from TestBase
        # helper method from TestBase
        cls.altdriver = None
        print(">>> Setting up TestAndroidAnalytics class")

        # Initialize page objects once

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
            self.click_Consent_IOS()

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
                    timeout=60,
                    enable_logging=True
                )

                connected = True
                print(f"✅ AltTester reconnected cleanly on attempt {attempt}")
                break

            except Exception as e:
                print(f"⚠️ Failed to connect AltTester on attempt {attempt}: {e}")
                time.sleep(retry_delay)

        if not connected:
            raise RuntimeError("Failed to reconnect AltTester after restarting the app.")

        #self.start_page = StartPage(self.altdriver, self.appium_driver)
        TestAndroidAnalytics.start_page = StartPage(self.altdriver, self.appium_driver)
        self.main_page = MainPage(self.altdriver, self.appium_driver)
        self.game_page = GamePage(self.altdriver, self.appium_driver)
        self.overlay_page = OverlayPage(self.altdriver, self.appium_driver)

    @pytest.mark.order(1)
    def test_Analytics_sdk_init(self):
        # self.start_page.click_GDPR()
        time.sleep(5)
        self.start_page.click_debug_menu()
        time.sleep(2)
        self.start_page.click_General()
        text = self.start_page.get_install_id()
        install_id = self.start_page.extract_install_id(text)
        TestAndroidAnalytics.install_id = install_id

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "sdk_init_success",
            "sdk_init_stage",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "sdk_init")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(2)
    def test_Analytics_level_started(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "level_value",
            "level_id",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "level_started")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(3)
    def test_Analytics_level_failed(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "level_value",
            "level_id",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "level_failed")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(4)
    def test_Analytics_level_completed(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "level_value",
            "level_id",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "level_completed")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(5)
    def test_Analytics_bank_snapshot(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "currencies_held"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "bank_snapshot")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)


    @pytest.mark.order(6)
    def test_Analytics_bank_transaction(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "currencies_spent",
            "currencies_earned"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "bank_transaction")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(7)
    def test_Analytics_screen_entered(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "screen_name",
            "screen_transition_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "screen_entered")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(8)
    def test_Analytics_screen_exited(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None
        required_fields = [
            "screen_name",
            "screen_transition_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "screen_exited")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(9)
    def test_Analytics_game_loaded(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 3
        wait_seconds = 20
        result = None

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "game_loaded")
            print(f"Result from Databricks: {result}")

            if result and len(result) > 0:
                print("✅ Found records!")
                print(result)
                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(10)
    def test_Analytics_ad_placement_reached(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "ad_placement",
            "ad_unique_id",
            "ad_mediator",
            "ad_revenue",
            "ad_auction_instance",
            "ad_network",
            "ad_auction_type",
            "ad_format",
            "ad_request_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ad_placement_reached")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(11)
    def test_Analytics_ad_loaded(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "ad_placement",
            "ad_unique_id",
            "ad_mediator",
            "ad_revenue",
            "ad_auction_instance",
            "ad_network",
            "ad_auction_type",
            "ad_format",
            "ad_request_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ad_loaded")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(12)
    def test_Analytics_ad_request_sent(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "ad_placement",
            "ad_unique_id",
            "ad_mediator",
            "ad_revenue",
            "ad_auction_instance",
            "ad_network",
            "ad_auction_type",
            "ad_format",
            "ad_request_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ad_request_sent")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(13)
    def test_Analytics_device_info(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "device_model",
            "device_os",
            "device_os_version",
            "device_screen_dpi",
            "device_screen_width",
            "device_screen_height",
            "device_system_memory",
            "device_processor_type"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ad_request_sent")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(14)
    def test_Analytics_app_life_cycle(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "install_store_country",
            "install_mode",
            "install_name",
            "install_bundle_id",
            "install_server_country",
            "player_id_type",
            "player_id_value",
            "previous_app_version",
            "event_created_time_ntp",
            "event_created_time_device",
            "sdk_init_stage",
            "kwsdk_version",
            "connection_type",
            "session_context",
            "event_type"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "app_lifecycle")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(15)
    def test_Analytics_session(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [

            "session_context"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "app_lifecycle")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(16)
    def test_Analytics_ntp_time_received(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [

            "event_created_time_ntp",
            "event_created_time_device"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ntp_time_received")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(17)
    def test_Analytics_ab_test(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [

            "event_created_time_ntp",
            "event_send_context"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ab_test")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(18)
    def test_Analytics_install(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "install_store_country",
            "install_mode",
            "install_name",
            "install_bundle_id",
            "install_server_country",

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "install")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(19)
    def test_Analytics_store_country_received(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "install_store_country",
            "install_mode",
            "install_name",
            "install_bundle_id",
            "install_server_country",

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "store_country_received")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(20)
    def test_Analytics_server_country_received(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "install_store_country",
            "install_mode",
            "install_name",
            "install_bundle_id",
            "install_server_country",

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "server_country_received")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)


    @pytest.mark.order(21)
    def test_Analytics_google_ump_acceptance(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "app_instance_id",
            "app_session_id",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "google_ump_acceptance")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(22)
    def test_Analytics_terms_and_conditions_acceptance(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "app_instance_id",
            "app_session_id",
            "event_send_context"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "terms_and_conditions_acceptance")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(23)
    def test_Analytics_user_update(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None

        required_fields = [
            "game_id",
            "device_platform",
            "app_version",
            "install_id",
            "app_instance_id",
            "app_session_id",
            "player_id_type",
            "player_id_value"
        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "user_update")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

    @pytest.mark.order(24)
    def test_Analytics_ad_completed(self):
        install_id = TestAndroidAnalytics.install_id
        assert install_id is not None, "install_id was not set by test_Analytics_sdk_init!"

        client = DatabricksClient()
        max_retries = 4
        wait_seconds = 20
        result = None
        required_fields = [
            "ad_placement",
            "ad_unique_id",
            "ad_mediator",
            "ad_revenue",
            "ad_auction_instance",
            "ad_network",
            "ad_auction_type",
            "ad_format",
            "ad_request_id"

        ]

        for attempt in range(1, max_retries + 1):
            print(f"🔄 Query attempt {attempt}/{max_retries} ...")

            result = client.getSdkInitEventsByInstallIdAndDate(install_id, "ad_completed")
            print(f"Result from Databricks: {result}")

            # ✅ Must be a non-empty list
            if isinstance(result, list) and len(result) > 0:
                print("✅ Found records!")

                # ✅ Validate each required field
                for field in required_fields:
                    assert field in result[0], f"❌ Missing field: {field}"
                    assert result[0][field] is not None, f"❌ Field '{field}' is None"
                    assert str(result[0][field]).strip() != "", f"❌ Field '{field}' is empty"

                break

            if attempt < max_retries:
                print(f"⏳ No records yet. Waiting {wait_seconds} seconds before retry...")
                time.sleep(wait_seconds)

            time.sleep(8)


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

    @classmethod
    def tearDownClass(cls):
        # Reconnect AltDriver because the last test closed it
        try:
            cls.altdriver = AltDriver(
                host='alttester.kwalee.com',
                port=13000,
                app_name='Queens Puzzle',
                timeout=60,
                enable_logging=True
            )
            print("✅ AltDriver reconnected in tearDownClass")
        except Exception as e:
            raise RuntimeError(f"❌ Could not reconnect AltDriver in tearDownClass: {e}")

        # Recreate StartPage using this new connection
        cls.start_page = StartPage(cls.altdriver, cls.appium_driver)
        cls.start_page.click_debug_menu()
        time.sleep(2)
        cls.start_page.click_game_btn()
        time.sleep(3)
        for _ in range(7):
            time.sleep(2)
            cls.start_page.click_clear_prefs()
        time.sleep(4)
        cls.start_page.click_btn_Back()
        time.sleep(2)
        cls.start_page.click_balancy_btn()
        for _ in range(7):
            cls.start_page.click_force_delete()
        time.sleep(4)
