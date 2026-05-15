import inspect

import pytest
import requests

WEBHOOK_URL ="https://internal.n8n.kwalee.com/webhook/51437229-e829-425a-a184-12d0e8b38136"

def pytest_configure(config):
    global pytest_html
    pytest_html = config.pluginmanager.getplugin('html')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    1. Attaches screenshot to pytest-html report.
    2. Sends failure details + source code to n8n for Slack reporting.
    """
    # Execute the test and get the outcome
    outcome = yield
    rep = outcome.get_result()

    # We only act if the test failed during the 'call' phase (the actual test execution)
    if rep.when == "call" and rep.failed:

        # --- PART 1: EXISTING SCREENSHOT LOGIC (For HTML Report) ---
        # Try to find the test instance to get the screenshot
        test_instance = getattr(item, "instance", None) or getattr(item, "_testcase", None)
        screenshot_base64 = None

        if test_instance and hasattr(test_instance, "_screenshot_for_html"):
            screenshot_base64 = test_instance._screenshot_for_html

            # Attach to HTML Report
            extra = getattr(rep, "extra", [])
            extra.append(pytest_html.extras.html(
                f'<div><img src="data:image/png;base64,{screenshot_base64}" '
                f'style="width:400px;height:auto;" '
                f'alt="screenshot"></div>'
            ))
            rep.extra = extra

        # --- PART 2: NEW N8N AUTOMATION LOGIC (For Slack/AI) ---
        try:
            # A. Get Source Code for AI Translation
            raw_code = inspect.getsource(item.function)
        except Exception:
            raw_code = "Could not extract source code."

        # B. Get Error Message
        error_message = str(call.excinfo.value)

        # C. Prepare Payload
        payload = {
            "title": f"Test Failed: {item.name}",
            "steps": raw_code,  # Sending raw code for AI to translate
            "expected": "Test should pass successfully",
            "actual": error_message,
            "environment": "UAT",
            "priority": "High"
        }

        # D. Send to n8n (Fire and Forget)
        # Note: We do NOT send the screenshot_base64 here because
        # Slack webhooks generally crash if you send huge base64 strings.
        print(f"\n🚨 Sending Failure Report to n8n for {item.name}...")
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=2)
        except Exception as e:
            print(f"❌ Failed to send webhook: {e}")