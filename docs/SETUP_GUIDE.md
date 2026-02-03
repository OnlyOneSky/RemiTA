# RemiTA Setup Guide

Complete setup guide for the RemiTA mobile test automation framework.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Android Environment](#android-environment)
- [iOS Environment](#ios-environment)
- [Appium Setup](#appium-setup)
- [WireMock Setup](#wiremock-setup)
- [Sample App](#sample-app)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Test framework |
| Node.js | 18+ | Appium server, sample app |
| Docker | Latest | WireMock mock server |
| Git | Latest | Version control |
| Java (JDK) | 17 | Android builds |

### macOS (Homebrew)

```bash
brew install python@3.11 node openjdk@17 git docker
```

Set JAVA_HOME in your shell profile (`~/.zshrc`):

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```

---

## Project Setup

### 1. Clone the repo

```bash
git clone https://github.com/OnlyOneSky/RemiTA.git
cd RemiTA
```

### 2. Create virtual environment & install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install -e .
```

### 3. IDE Setup (PyCharm)

Go to **Settings → Project → Python Interpreter → Add Interpreter → Existing** and select `.venv/bin/python`.

---

## Android Environment

### 1. Install Android SDK

```bash
brew install --cask android-commandlinetools
```

### 2. Set environment variables

Add to `~/.zshrc`:

```bash
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
```

Reload: `source ~/.zshrc`

### 3. Install SDK packages

```bash
# Accept licenses
yes | sdkmanager --licenses

# Install required packages
sdkmanager "platforms;android-36" \
           "build-tools;36.0.0" \
           "platform-tools" \
           "emulator" \
           "system-images;android-34;google_apis;arm64-v8a"
```

### 4. Create an emulator (AVD)

```bash
# Create a Pixel 7 emulator with Android 14
echo "no" | avdmanager create avd \
  -n "Pixel_7_API_34" \
  -k "system-images;android-34;google_apis;arm64-v8a" \
  -d "pixel_7"

# Verify
avdmanager list avd
```

### 5. Start the emulator

```bash
# With GUI
emulator -avd Pixel_7_API_34

# Headless (no window — useful for CI/servers)
emulator -avd Pixel_7_API_34 -no-window -no-audio -gpu swiftshader_indirect

# Verify it's running
adb devices -l
```

> **Tip:** The emulator takes 30-60 seconds to fully boot. Wait for `sys.boot_completed` = 1:
> ```bash
> adb shell getprop sys.boot_completed
> ```

### 6. Device info commands

```bash
# List connected devices
adb devices -l

# Get device model
adb -s emulator-5554 shell getprop ro.product.model

# Get Android version
adb -s emulator-5554 shell getprop ro.build.version.release

# Get manufacturer
adb -s emulator-5554 shell getprop ro.product.manufacturer
```

---

## iOS Environment

> Requires macOS with Xcode installed.

### 1. Install Xcode

Download from the App Store or [developer.apple.com](https://developer.apple.com/xcode/).

```bash
xcode-select --install
sudo xcodebuild -license accept
```

### 2. List available simulators

```bash
xcrun simctl list devices available
```

### 3. Boot a simulator

```bash
# Boot an iPhone 15 (find exact name from list above)
xcrun simctl boot "iPhone 15"

# Verify
xcrun simctl list devices booted
```

---

## Appium Setup

### 1. Install Appium 2.x

```bash
npm install -g appium
```

### 2. Install platform drivers

```bash
# Android
appium driver install uiautomator2

# iOS
appium driver install xcuitest
```

### 3. Verify installation

```bash
appium driver list --installed
```

### 4. Start Appium server

```bash
appium
# Default: http://127.0.0.1:4723
```

---

## WireMock Setup

WireMock is our API mock server. We package it as a custom Docker image with all stubs baked in — no volume mounts needed.

### Prerequisites

You need Docker installed. Options:

```bash
# Option A: Docker Desktop (GUI)
brew install --cask docker

# Option B: Colima + Docker CLI (lightweight, no GUI)
brew install colima docker
colima start
```

### Option 1: Pull the pre-built image (recommended)

Download `remita-wiremock.tar` from the [GitHub Release](https://github.com/OnlyOneSky/RemiTA/releases):

```bash
# Load the image
docker load -i remita-wiremock.tar

# Run it
docker run -d --name remita-wiremock -p 8090:8080 remita-wiremock:latest
```

### Option 2: Build from source

```bash
cd RemiTA
docker compose up -d
```

This builds the image from `wiremock/Dockerfile` and starts it.

### Verify it's running

```bash
# Check the container
docker ps | grep wiremock

# Check the stubs are loaded
curl http://localhost:8090/__admin/mappings
```

You should see the login stubs (success + failure) in the response.

### Stop / Restart

```bash
# Stop
docker stop remita-wiremock

# Start again
docker start remita-wiremock

# Or with docker-compose
docker compose down
docker compose up -d
```

### Managing stubs

**Pre-loaded stubs (baked into image):**
- `wiremock/mappings/` — Stub definitions (request matching → response)
- `wiremock/__files/` — Response body JSON files

**Adding new stubs:**
1. Add mapping JSON to `wiremock/mappings/`
2. Add response body to `wiremock/__files/` (if using `bodyFileName`)
3. Rebuild the image: `docker compose build`

**Programmatic stubs (in tests):**
Tests can also create/delete stubs at runtime via `WireMockClient`:

```python
# In a test
wiremock.create_stub({
    "request": {"method": "GET", "url": "/api/users"},
    "response": {"status": 200, "jsonBody": {"users": []}}
})
```

**Useful admin endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `GET /__admin/mappings` | List all stubs |
| `POST /__admin/mappings` | Create a stub |
| `DELETE /__admin/mappings` | Delete all stubs |
| `POST /__admin/reset` | Reset stubs + request journal |
| `GET /__admin/requests` | View recorded requests |
| `POST /__admin/requests/count` | Count matching requests |

### Rebuilding the image after changes

When you update stubs and want to share the new image:

```bash
# Rebuild
docker compose build

# Export
docker save remita-wiremock:latest -o remita-wiremock.tar

# Share the .tar or create a new GitHub Release
```

---

## Sample App

The included React Native (Expo) sample app serves as the test target.

### Build Android APK

```bash
cd sample-app

# Install dependencies
npm install

# Generate native Android project
npx expo prebuild --platform android --no-install

# Build debug APK
cd android && ./gradlew assembleDebug

# APK location:
# android/app/build/outputs/apk/debug/app-debug.apk
```

### Install on emulator/device

```bash
adb install sample-app/android/app/build/outputs/apk/debug/app-debug.apk
```

### App Screens

| Screen | Elements (testID) | API Call |
|--------|------------------|----------|
| **Login** | `username_input`, `password_input`, `login_button`, `error_message` | `POST /api/login` |
| **Home** | `welcome_message`, `menu_button`, `logout_button` | — |

---

## Running Tests

### Start all services first

```bash
# Terminal 1: WireMock
docker compose up -d

# Terminal 2: Emulator (or connect a device)
emulator -avd Pixel_7_API_34 -no-window -no-audio -gpu swiftshader_indirect

# Terminal 3: Appium
appium

# Terminal 4: Run tests
source .venv/bin/activate
```

### Test commands

```bash
# Run all tests on all connected devices
pytest

# Android only
pytest --platform android

# iOS only
pytest --platform ios

# Smoke tests only
pytest -m smoke

# Regression suite
pytest -m regression

# Specific test file
pytest tests/test_login.py

# With verbose output
pytest -v --tb=long
```

### View Allure report

```bash
# Install Allure CLI (first time only)
brew install allure

# Generate and open report
allure serve allure-results
```

---

## Troubleshooting

### Emulator won't start

```bash
# Check if hardware acceleration is available
emulator -accel-check

# Try with different GPU mode
emulator -avd Pixel_7_API_34 -gpu host
```

### adb not found

Ensure `ANDROID_HOME` is set and `platform-tools` is in your PATH:

```bash
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH="$ANDROID_HOME/platform-tools:$PATH"
```

### Appium can't find device

```bash
# Kill and restart adb
adb kill-server
adb start-server
adb devices
```

### WireMock connection refused

```bash
# Check Docker is running
docker ps

# Restart WireMock
docker compose down && docker compose up -d
```

### Tests fail with "No devices found"

The `DeviceManager` auto-discovers devices. Make sure:
1. Emulator is fully booted (`adb shell getprop sys.boot_completed` → `1`)
2. Or a physical device is connected and USB debugging is enabled
3. `adb devices` shows your device as `device` (not `unauthorized` or `offline`)
