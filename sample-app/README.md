# RemiTA Sample App

A minimal React Native (Expo) app used as the test target for the RemiTA test automation framework.

## Screens

| Screen | Elements (testID / accessibilityLabel) |
|--------|---------------------------------------|
| **Login** | `username_input`, `password_input`, `login_button`, `error_message` |
| **Home** | `welcome_message`, `menu_button`, `logout_button` |

## API

The app calls `POST /api/login` with `{ username, password }` — mocked by WireMock during tests.

- **Android emulator:** calls `http://10.0.2.2:8080` (routes to host)
- **iOS simulator / device:** calls `http://127.0.0.1:8080`

## Build

### Development (Expo Go)

```bash
cd sample-app
npm start
```

### Build APK (Android)

```bash
npx expo install expo-dev-client
npx expo prebuild --platform android
cd android && ./gradlew assembleDebug
# APK → android/app/build/outputs/apk/debug/app-debug.apk
```

### Build IPA (iOS)

```bash
npx expo prebuild --platform ios
cd ios && xcodebuild -workspace sampleapp.xcworkspace -scheme sampleapp -configuration Debug -sdk iphonesimulator
```

### Cloud Build (EAS)

```bash
npm install -g eas-cli
eas build --platform all --profile preview
```
