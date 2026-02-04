# RemiTA Test Flow — How It All Works

A detailed guide to how RemiTA discovers devices, sets up the environment,
runs tests, and generates reports.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Component Map](#component-map)
- [Test Execution Flow](#test-execution-flow)
- [Fixture Lifecycle](#fixture-lifecycle)
- [Data Flow: A Single Test](#data-flow-a-single-test)
- [Page Object Model](#page-object-model)
- [Multi-Device Execution](#multi-device-execution)
- [Configuration Loading](#configuration-loading)
- [Key Files Reference](#key-files-reference)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR MACHINE (Host)                          │
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  pytest   │───▶│  Appium  │───▶│   Emulator   │    │ WireMock  │ │
│  │  (tests)  │    │  Server  │    │  or Device   │    │ (Docker)  │ │
│  └─────┬────┘    └──────────┘    │              │    └─────┬─────┘ │
│        │                         │  ┌────────┐  │          │       │
│        │                         │  │  App   │──┼──────────┘       │
│        │                         │  │ Under  │  │  HTTP requests   │
│        │                         │  │  Test  │  │  (10.0.2.2)      │
│        │                         │  └────────┘  │                  │
│        │                         └──────────────┘                  │
│        │                                                           │
│        └── WireMock API ──── Load stubs / Reset / Verify ──────────┘
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**How the components connect:**

| Component | Role | Communicates With |
|-----------|------|-------------------|
| **pytest** | Test runner — orchestrates everything | Appium (WebDriver), WireMock (REST API) |
| **Appium Server** | Translates WebDriver commands to device actions | Emulator/device (via UiAutomator2 / XCUITest) |
| **Emulator / Device** | Runs the app under test | App ↔ WireMock (HTTP) |
| **App Under Test** | The mobile app being tested | WireMock (mock API calls) |
| **WireMock** | Mock API server — returns predefined responses | Receives HTTP requests from the app |

---

## Component Map

```
RemiTA/
├── tests/
│   ├── conftest.py          ← Fixtures, hooks, device discovery
│   └── test_login.py        ← Test cases (one file per feature)
│
├── src/
│   ├── pages/               ← Page Object Model
│   │   ├── base_page.py     ← Shared actions (click, type, swipe, etc.)
│   │   ├── login_page.py    ← Login screen interactions
│   │   └── home_page.py     ← Home screen interactions
│   │
│   ├── models/
│   │   ├── device_info.py   ← Device data model
│   │   └── user.py          ← Test user data model
│   │
│   └── utils/
│       ├── device_manager.py   ← Auto-discovers connected devices
│       ├── app_installer.py    ← Installs APK/IPA on devices
│       ├── driver_factory.py   ← Creates Appium driver instances
│       ├── config_loader.py    ← Loads YAML configs
│       ├── wiremock_client.py  ← REST client for WireMock admin API
│       └── waits.py            ← Custom wait utilities
│
├── config/
│   ├── settings.yaml        ← Global settings (Appium URL, WireMock URL, timeouts)
│   ├── android.yaml          ← Android capabilities
│   └── ios.yaml              ← iOS capabilities
│
└── wiremock/
    ├── mappings/             ← Stub definitions (request → response)
    └── __files/              ← Response body JSON files
```

---

## Test Execution Flow

When you run `pytest tests/ -v`, here's what happens step by step:

```
pytest tests/ -v
     │
     ▼
┌─────────────────────────────────────────────┐
│  1. COLLECTION PHASE                        │
│                                             │
│  pytest discovers all test files & functions │
│  ↓                                          │
│  pytest_generate_tests() hook fires:        │
│  • Reads --platform flag (android/ios/all)  │
│  • Calls DeviceManager.discover_all()       │
│  • Parametrizes tests × devices             │
│                                             │
│  Result: 3 tests × 1 device = 3 test items  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  2. SESSION SETUP (once per device)         │
│                                             │
│  a) AppInstaller.ensure_installed()         │
│     • Checks if app is on device (adb/xcrun)│
│     • Installs APK/IPA (always reinstalls   │
│       latest when path is configured)       │
│                                             │
│  b) DriverFactory.get_driver_for_device()   │
│     • Loads YAML config (settings + platform│
│     • Injects device info into capabilities │
│     • Creates Appium WebDriver session      │
│                                             │
│  c) _setup_adb_reverse (Android only)       │
│     • Reads WireMock port from settings     │
│     • Runs: adb reverse tcp:PORT tcp:PORT   │
│     • Ensures emulator can reach host       │
│                                             │
│  d) WireMockClient connects                 │
│     • Reads base_url from settings.yaml     │
│     • Health check: GET /__admin/mappings   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  3. PER-TEST CYCLE (repeats for each test)  │
│                                             │
│  BEFORE TEST:                               │
│  ├─ _reset_app_state (autouse fixture)      │
│  │  • driver.terminate_app(package)         │
│  │  • driver.activate_app(package)          │
│  │  • sleep(3) — wait for app to load       │
│  │                                          │
│  TEST RUNS:                                 │
│  ├─ Test loads WireMock stubs               │
│  ├─ Test interacts with app via Page Objects│
│  ├─ App makes HTTP calls → WireMock responds│
│  ├─ Test asserts expected UI state          │
│  │                                          │
│  AFTER TEST:                                │
│  ├─ ON FAILURE: screenshot → Allure report  │
│  └─ _reset_wiremock (autouse fixture)       │
│     • POST /__admin/reset                   │
│     • Clears all stubs + request journal    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  4. SESSION TEARDOWN                        │
│                                             │
│  • driver.quit() — closes Appium session    │
│  • Allure config files copied to results    │
│  • Exit with pass/fail code                 │
└─────────────────────────────────────────────┘
```

---

## Fixture Lifecycle

Fixtures are the backbone of RemiTA's test setup. Here's the dependency
chain and scope:

```
                    SESSION SCOPE (once per device)
 ┌──────────────────────────────────────────────────────┐
 │                                                      │
 │  device_info ──▶ driver ──▶ _setup_adb_reverse       │
 │       │              │                               │
 │       │              │         wiremock               │
 │       │              │            │                   │
 │       ▼              ▼            ▼                   │
 │  ┌─────────────────────────────────────────────┐     │
 │  │          TEST SCOPE (each test)             │     │
 │  │                                             │     │
 │  │  _reset_app_state(driver)     [BEFORE]      │     │
 │  │         │                                   │     │
 │  │         ▼                                   │     │
 │  │    TEST FUNCTION                            │     │
 │  │         │                                   │     │
 │  │         ▼                                   │     │
 │  │  _reset_wiremock(wiremock)    [AFTER]        │     │
 │  │  pytest_runtest_makereport    [ON FAILURE]   │     │
 │  └─────────────────────────────────────────────┘     │
 │                                                      │
 └──────────────────────────────────────────────────────┘
```

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `device_info` | session | Device metadata from DeviceManager |
| `driver` | session | Appium WebDriver instance |
| `_setup_adb_reverse` | session | Port forwarding for Android emulators |
| `wiremock` | session | WireMockClient for stub management |
| `_reset_app_state` | test | Restarts the app before each test |
| `_reset_wiremock` | test | Clears stubs after each test |

---

## Data Flow: A Single Test

Let's trace `test_successful_login` from start to finish:

```
Step 1: Load WireMock Stub
──────────────────────────
Test Runner                          WireMock (Docker)
    │                                     │
    │  POST /__admin/mappings             │
    │  { request: POST /api/login,        │
    │    body: {user:"valid_user",...},    │
    │    response: 200 + success JSON }   │
    │────────────────────────────────────▶│
    │                                     │
    │  201 Created                        │
    │◀────────────────────────────────────│


Step 2: Interact with App via Appium
─────────────────────────────────────
Test Runner         Appium Server         Emulator (App)
    │                    │                      │
    │  type "valid_user" │                      │
    │  into username     │   UiAutomator2       │
    │───────────────────▶│─────────────────────▶│ types text
    │                    │                      │
    │  type "valid_pass" │                      │
    │───────────────────▶│─────────────────────▶│ types text
    │                    │                      │
    │  click login_btn   │                      │
    │───────────────────▶│─────────────────────▶│ taps button
    │                    │                      │


Step 3: App Calls Mock API
──────────────────────────
Emulator (App)                       WireMock (Docker)
    │                                     │
    │  POST http://10.0.2.2:8090/api/login│
    │  {"username":"valid_user",           │
    │   "password":"valid_pass"}           │
    │────────────────────────────────────▶│
    │                                     │
    │  200 OK                             │
    │  {"status":"success",               │
    │   "token":"eyJ...",                 │
    │   "user":{"display_name":           │
    │           "Remi Chen"}}             │
    │◀────────────────────────────────────│
    │                                     │
    │  App navigates to Home Screen       │


Step 4: Assert Result
─────────────────────
Test Runner         Appium Server         Emulator (App)
    │                    │                      │
    │  is welcome_message│                      │
    │  displayed?        │   find element       │
    │───────────────────▶│─────────────────────▶│
    │                    │                      │
    │  ✅ YES            │   element found      │
    │◀───────────────────│◀─────────────────────│
    │                    │                      │
    │  get welcome text  │                      │
    │───────────────────▶│─────────────────────▶│
    │                    │                      │
    │  "Welcome,         │                      │
    │   Remi Chen!"      │                      │
    │◀───────────────────│◀─────────────────────│
    │                    │                      │
    │  assert "Remi Chen"│                      │
    │  in welcome text   │                      │
    │  ✅ PASS           │                      │
```

---

## Page Object Model

RemiTA uses the **Page Object Model (POM)** design pattern. Each screen in the
app is represented by a Python class that encapsulates:

- **Locators** — how to find UI elements
- **Actions** — what a user can do on that screen
- **Queries** — how to read information from the screen

```
BasePage (base_page.py)
├── find_element(locator)     ← Wait + find
├── click(locator)            ← Wait + tap
├── type_text(locator, text)  ← Clear + type
├── get_text(locator)         ← Read text
├── is_displayed(locator)     ← Check visibility
├── swipe_up/down/left/right  ← Gesture helpers
├── take_screenshot(name)     ← Manual capture
└── go_back() / hide_keyboard()

LoginPage(BasePage)                HomePage(BasePage)
├── USERNAME_FIELD (locator)       ├── WELCOME_MESSAGE (locator)
├── PASSWORD_FIELD (locator)       ├── MENU_BUTTON (locator)
├── LOGIN_BUTTON (locator)         ├── LOGOUT_BUTTON (locator)
├── ERROR_MESSAGE (locator)        │
│                                  ├── get_welcome_message()
├── login(user, pass)              ├── tap_menu()
├── get_error_message()            ├── logout()
└── is_login_button_displayed()    └── is_home_displayed()
```

**Why POM?**

- **Tests don't know about locators** — if a button's `testID` changes, you
  update ONE page object, not every test
- **Reusable actions** — `login_page.login(user, pass)` used across multiple tests
- **Readable tests** — test code reads like a user story:
  ```python
  login_page.login("valid_user", "valid_pass")
  assert home_page.is_home_displayed()
  ```

---

## Multi-Device Execution

RemiTA automatically discovers all connected devices and runs the full
test suite on each one sequentially:

```
                   Device Discovery
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        Pixel 7     Galaxy S24   iPhone 15
        (emu)       (real)       (sim)
            │           │           │
       ┌────┘     ┌─────┘     ┌────┘
       ▼          ▼           ▼
    3 tests    3 tests     3 tests
    on this    on this     on this
    device     device      device
       │          │           │
       ▼          ▼           ▼
    Results    Results     Results
       │          │           │
       └──────────┼───────────┘
                  ▼
          Allure Report
       (tagged by device)
```

**How it works:**

1. `DeviceManager` scans `adb devices` (Android) and `xcrun simctl` (iOS)
2. `pytest_generate_tests` parametrizes each test with each device
3. Test IDs become: `test_login[Pixel_7_API_34]`, `test_login[Galaxy_S24]`, etc.
4. Each device gets its own Appium driver (session-scoped)
5. Allure report tags each result with the device name

**Filtering by platform:**

```bash
pytest --platform android    # Android devices only
pytest --platform ios        # iOS devices only
pytest --platform all        # Everything (default)
```

---

## Configuration Loading

RemiTA uses a layered config system:

```
config/settings.yaml     ← Global: Appium URL, WireMock URL, timeouts
      +
config/android.yaml      ← Platform: capabilities for Android
(or config/ios.yaml)
      ↓
ConfigLoader.load_merged_config("android")
      ↓
Merged dict with all settings + platform capabilities
```

**Settings** control framework behavior:

```yaml
appium:
  server_url: "http://127.0.0.1:4723"
wiremock:
  base_url: "http://localhost:8090"
timeouts:
  implicit_wait: 10
  explicit_wait: 15
```

**Platform configs** define Appium capabilities:

```yaml
capabilities:
  platformName: "Android"
  "appium:automationName": "UiAutomator2"
  "appium:app": "sample-app/android/.../app-release.apk"
  "appium:appPackage": "com.remita.sample"
  "appium:appActivity": ".MainActivity"
```

When testing your own app, you mainly edit the **platform configs** to point
to your APK/IPA and set your app's package/activity/bundleId.

---

## Key Files Reference

| File | What to Edit When... |
|------|---------------------|
| `config/settings.yaml` | Changing WireMock port, Appium URL, or timeouts |
| `config/android.yaml` | Changing Android capabilities, APK path, or package name |
| `config/ios.yaml` | Changing iOS capabilities, app path, or bundle ID |
| `tests/conftest.py` | Adding new fixtures or changing test lifecycle |
| `tests/test_*.py` | Adding new test cases |
| `src/pages/*_page.py` | Adding page objects for new screens |
| `wiremock/mappings/*.json` | Adding new API stubs |
| `wiremock/__files/*.json` | Adding new response bodies |
