#!/bin/bash

# ==== Argument check ====
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Error: Missing arguments."
  echo "Usage: ./run_tests_ios.sh <app_file.ipa> <bundle_id> <app_name>"
  exit 1
fi

APP_PATH=$1
APP_PACKAGE=$2
APP_NAME=$3

CONFIG_FILE="config.properties"

# ==== Update config.properties ====
echo "Updating $CONFIG_FILE with app path and package name..."
sed -i '' "s|^app=.*|app=$APP_PATH|" "$CONFIG_FILE"
sed -i '' "s|^app.appBundleId=.*|app.appBundleId=$APP_PACKAGE|" "$CONFIG_FILE"
sed -i '' "s|^appName=.*|appName=$APP_NAME|" "$CONFIG_FILE"

# ==== Install Python dependencies ====
echo "Installing dependencies..."
chmod 0755 requirements.txt
python -m pip install -r requirements.txt

# ==== Start Appium ====
echo "Starting Appium..."
appium --log-no-colors --log-timestamp -p 4723 --keep-alive-timeout 300 > appium.log 2>&1 &
sleep 10
ps -ef | grep appium
APPIUM_PID=$!

# ==== Absolute path to .ipa ====
export APPIUM_APPFILE=$PWD/app/$APP_PATH

# ==== Uninstall existing app if installed ====
echo "Checking if app is already installed..."
ios-deploy --exists --bundle_id "$APP_PACKAGE" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "App $APP_PACKAGE is installed. Uninstalling..."
  ios-deploy --uninstall_only --bundle_id "$APP_PACKAGE"
else
  echo "App $APP_PACKAGE is not installed. Skipping uninstall."
fi

# ==== Install app on device ====
echo "Installing the app on device..."
ios-deploy --bundle "$APPIUM_APPFILE" || {
  echo "❌ Error installing the app. Make sure the device is connected and trusted."
  kill $APPIUM_PID
  exit 1
}

# ==== Appium Environment Variables ====
export APPIUM_URL="http://localhost:4723"
export APPIUM_DEVICE="Local Device"
export APPIUM_PLATFORM="ios"
export APPIUM_AUTOMATION="XCUITest"

# ==== Cleanup old screenshots ====
rm -rf screenshots

# ==== Run Tests ====
echo "Running tests..."
#python -m pytest tests/ios_test.py::TestIOS -s --alluredir=allure-results \
#  --html=reports/${APP_NAME}_report.html --self-contained-html

python -m pytest tests/ios_test.py::TestIOS -s --alluredir=allure-results --html=reports/${APP_NAME}_report.html --self-contained-html
python -m pytest tests/ios_analytics_test.py::TestIOSAnalytics -s --alluredir=allure-results --html=reports/${APP_NAME}_analytics_report.html --self-contained-html

# ==== Start Allure report ====
echo "Starting the Allure report..."
allure serve allure-results &

# ==== Stop App ====
echo "==> Terminating the app..."
xcrun simctl terminate booted "$APP_PACKAGE" || echo "App might not be running."

# ==== Cleanup ====
echo "Tests done"
echo "Stopping Appium server..."
kill $APPIUM_PID
