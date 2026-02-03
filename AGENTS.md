# AGENTS.md — RemiTA Project Conventions

AI coding guide for the RemiTA mobile test automation framework.

## Tech Stack

- **Language:** Python 3.11+
- **Test runner:** pytest (with markers: smoke, regression, android, ios, login)
- **Mobile automation:** Appium 2.x (W3C protocol)
- **Android driver:** UiAutomator2
- **iOS driver:** XCUITest
- **Mock server:** WireMock (Docker)
- **Reporting:** Allure, pytest-html
- **Config:** YAML files in `config/`

## Architecture

### Page Object Model (POM)

Every screen in the app gets a page class in `src/pages/`:

```
BasePage (base_page.py)
  ├── LoginPage (login_page.py)
  ├── HomePage (home_page.py)
  └── ...future pages
```

**Rules:**
- All page objects extend `BasePage`
- Locators are class-level constants: `LOCATOR_NAME: Locator = (AppiumBy.STRATEGY, "value")`
- Prefer `AppiumBy.ACCESSIBILITY_ID` for cross-platform locators
- Methods return `None` for actions, typed values for queries
- Use `BasePage` helpers (`click`, `type_text`, `find_element`) — don't call `driver` directly in page objects

### Test Structure

- Tests live in `tests/`
- Each feature has a file: `test_<feature>.py`
- Tests are grouped in classes: `class Test<Feature>:`
- Follow **Arrange → Act → Assert** pattern
- Fixtures in `tests/conftest.py` handle driver & WireMock lifecycle

### WireMock Integration

- Stub JSON files in `wiremock/mappings/`
- Response bodies in `wiremock/__files/`
- Use `WireMockClient` to load stubs and verify requests in tests
- Stubs auto-reset before each test (via `reset_wiremock` fixture)

## Naming Conventions

| What | Pattern | Example |
|------|---------|---------|
| Page object file | `<page>_page.py` | `login_page.py` |
| Page object class | `<Page>Page` | `LoginPage` |
| Locator constant | `UPPER_SNAKE_CASE` | `USERNAME_FIELD` |
| Test file | `test_<feature>.py` | `test_login.py` |
| Test class | `Test<Feature>` | `TestLogin` |
| Test method | `test_<scenario>` | `test_successful_login` |
| WireMock mapping | `<endpoint>_<scenario>.json` | `login_success.json` |
| Utility module | `<purpose>.py` | `wiremock_client.py` |

## Key Files

| File | Purpose |
|------|---------|
| `config/settings.yaml` | Appium URL, WireMock URL, timeouts |
| `config/android.yaml` | Android desired capabilities |
| `config/ios.yaml` | iOS desired capabilities |
| `src/utils/driver_factory.py` | Builds Appium driver from config |
| `src/utils/wiremock_client.py` | WireMock admin API wrapper |
| `tests/conftest.py` | All pytest fixtures and hooks |

## Adding a New Feature

1. Create page object: `src/pages/<feature>_page.py`
2. Add locators and action methods
3. Export in `src/pages/__init__.py`
4. Add WireMock stubs if the feature calls APIs
5. Write tests: `tests/test_<feature>.py`
6. Mark tests: `@pytest.mark.smoke` / `@pytest.mark.regression`

## Don'ts

- Don't use `time.sleep()` — use explicit waits from `BasePage` or `waits.py`
- Don't hardcode capabilities — use YAML configs
- Don't access `driver` directly in tests — go through page objects
- Don't leave WireMock stubs from one test affecting another — the `reset_wiremock` fixture handles cleanup
