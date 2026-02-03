# RemiTA 🤖

Mobile test automation framework built with Python, Appium, and pytest.

## Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.11+** | Test language |
| **pytest** | Test runner & fixtures |
| **Appium 2.x** | Mobile automation engine |
| **WireMock** (Docker) | API mock server |
| **Allure** | Test reporting |

## Prerequisites

- Python 3.11+
- [Appium 2.x](https://appium.io/docs/en/latest/) with drivers:
  - `appium driver install uiautomator2` (Android)
  - `appium driver install xcuitest` (iOS)
- Docker & Docker Compose
- Android SDK / Xcode (depending on target platform)

## Project Structure

```
RemiTA/
├── config/                     # Platform & settings YAML
│   ├── settings.yaml           # Shared settings (URLs, timeouts)
│   ├── android.yaml            # Android capabilities
│   └── ios.yaml                # iOS capabilities
├── src/
│   ├── pages/                  # Page Object Model
│   │   ├── base_page.py        # Shared interactions
│   │   ├── login_page.py       # Login screen
│   │   └── home_page.py        # Home / dashboard
│   ├── utils/
│   │   ├── driver_factory.py   # Appium driver builder
│   │   ├── config_loader.py    # YAML config loader
│   │   ├── waits.py            # Custom wait helpers
│   │   └── wiremock_client.py  # WireMock REST client
│   └── models/
│       └── user.py             # Test data models
├── tests/
│   ├── conftest.py             # Fixtures & hooks
│   └── test_login.py           # Login test cases
├── wiremock/
│   ├── mappings/               # Stub definitions
│   └── __files/                # Response bodies
├── docker-compose.yml          # WireMock container
└── pyproject.toml              # Dependencies & pytest config
```

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/OnlyOneSky/RemiTA.git
cd RemiTA
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Start WireMock

```bash
docker compose up -d
```

### 3. Start Appium server

```bash
appium
```

### 4. Run tests

```bash
# Android (default)
pytest

# iOS
pytest --platform ios

# Smoke tests only
pytest -m smoke

# With Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

## Configuration

Edit YAML files in `config/` to match your environment:

- **`settings.yaml`** — Appium server URL, WireMock URL, timeouts
- **`android.yaml`** — Android device capabilities (update `app`, `appPackage`, `appActivity`)
- **`ios.yaml`** — iOS device capabilities (update `app`, `bundleId`)

## Writing Tests

1. **Create a page object** in `src/pages/` extending `BasePage`
2. **Define locators** as class-level tuples: `(AppiumBy.ACCESSIBILITY_ID, "element_id")`
3. **Write tests** in `tests/` using pytest fixtures (`driver`, `wiremock`)
4. **Add WireMock stubs** in `wiremock/mappings/` for API mocking

## License

Private — internal use only.
