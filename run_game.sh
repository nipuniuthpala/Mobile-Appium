#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]|| [ -z "$3" ]||[ -z "$4" ]; then
  echo "Error: Missing arguments. Usage: ./your_script.sh /path/to/your_app.apk com.example.package"
  exit 1
fi

APP_PATH=$1
APP_PACKAGE=$2
APP_NAME=$3
APP_ACTIVITY=$4
LEVEL=$5
COUNT=$6

CONFIG_FILE="config.properties"
sed -i '' "s|^app=.*|app=$APP_PATH|" "$CONFIG_FILE"
sed -i '' "s|^app.package=.*|app.package=$APP_PACKAGE|" "$CONFIG_FILE"
sed -i '' "s|^appName=.*|appName=$APP_NAME|" "$CONFIG_FILE"
sed -i '' "s|^android_app_activity=.*|android_app_activity=$APP_ACTIVITY|" "$CONFIG_FILE"
sed -i '' "s|^START_LEVEL=.*|START_LEVEL=$LEVEL|" "$CONFIG_FILE"
sed -i '' "s|^LEVEL_COUNT=.*|LEVEL_COUNT=$COUNT|" "$CONFIG_FILE"

echo "==> Uninstalling the app from the device..."
echo "Installing dependencies"
chmod 0755 requirements.txt
python -m pip install -r requirements.txt

echo "Starting Appium..."
appium --log-no-colors --log-timestamp -p 4723 --keep-alive-timeout 300 > appium.log 2>&1 &
sleep 10
ps -ef|grep appium
APPIUM_PID=$!
adb uninstall "$APP_PACKAGE"
echo "uninstalled"
#App file is under the app/ folder inside the current working folder
export APPIUM_APPFILE=$PWD/app/$APP_PATH

adb install "$APPIUM_APPFILE"
## Appium Options:
export APPIUM_URL="http://localhost:4723"
export APPIUM_DEVICE="Local Device"
export APPIUM_PLATFORM="android"
export APPIUM_AUTOMATION="uiautomator2"

## Remove any previously taken screenshots:
rm -rf screenshots

## Run the test:
echo "Running tests"
START_LEVEL=$LEVEL LEVEL_COUNT=$COUNT python -m pytest tests/expert_mode_test.py::TestExpertGame -s --alluredir=allure-results --html=reports/${APP_NAME}_report.html --self-contained-html

echo "Starting the Allure report..."
allure serve allure-results &

echo "==> Killing the app..."
adb shell am force-stop "$APP_PACKAGE"


echo "Tests done"
adb reverse --remove-all

echo "==> Stopping Appium server..."
kill $APPIUM_PID
