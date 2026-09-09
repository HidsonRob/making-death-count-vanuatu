# Making Death Count — Android TWA

This folder is a **Trusted Web Activity (TWA)** wrapper for the live dashboard:

https://vanuatu-national-statistics-office.github.io/making-death-count-vanuatu/

It is **online TWA**, not a Capacitor offline APK. The app opens that HTTPS URL inside Chrome Custom Tabs / Trusted Web Activity. A network connection is required unless Chrome has the PWA cached.

The live GitHub Pages site currently serves the dashboard HTML, but `manifest.webmanifest` and `assets/icons/icon-512.png` may 404 until those PWA files are deployed. The TWA still launches the HTML start URL. Re-run `bubblewrap update` only after those files are live (or it will fail to download the manifest/icon).

Package ID: `vu.gov.vnso.makingdeathcount`  
Theme colour: `#0A3D62`

## Prerequisites

- Node.js 18+
- A **64-bit JDK** for Gradle (Android Studio JBR at `C:\Program Files\Android\Android Studio\jbr` works; JDK 21 is fine)
- Android SDK (Bubblewrap’s copy at `%USERPROFILE%\.bubblewrap\android_sdk`, or `%LOCALAPPDATA%\Android\Sdk`)
- `@bubblewrap/cli` (`npx @bubblewrap/cli`)

Bubblewrap’s own JDK 17 under `%USERPROFILE%\.bubblewrap\jdk` is valid for `bubblewrap doctor`, but it is a 32-bit VM and can run out of memory during `assembleDebug`. Use the 64-bit Android Studio JBR for Gradle.

Refresh PATH in PowerShell:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
$env:ANDROID_HOME = "$env:USERPROFILE\.bubblewrap\android_sdk"
```

Confirm Bubblewrap can see the toolchain:

```powershell
npx --yes @bubblewrap/cli doctor
```

If paths are wrong:

```powershell
npx --yes @bubblewrap/cli updateConfig --jdkPath="$env:USERPROFILE\.bubblewrap\jdk\jdk-17.0.11+9" --androidSdkPath="$env:USERPROFILE\.bubblewrap\android_sdk"
```

## Debug signing key

A local keystore is created at `android.keystore` (gitignored). Debug defaults (change these before any Play Store upload):

- File: `android-twa/android.keystore`
- Alias: `android`
- Store password: `android`
- Key password: `android`

Recreate the keystore:

```powershell
& "$env:JAVA_HOME\bin\keytool.exe" -genkeypair -v `
  -keystore android.keystore -alias android -keyalg RSA -keysize 2048 -validity 10000 `
  -storepass android -keypass android `
  -dname "CN=Making Death Count, OU=VNSO, O=Vanuatu Bureau of Statistics, L=Port Vila, C=VU"
```

## Generate / refresh the Android project

From this folder (`android-twa/`):

```powershell
npx --yes @bubblewrap/cli update --skipVersionUpgrade
```

If the live site does not yet serve `assets/icons/icon-512.png`, serve the repo locally and point `iconUrl` at it for one update, then restore the GitHub Pages icon URL in `twa-manifest.json`.

## Build the APK

### Option A — Bubblewrap (signed release APK)

```powershell
$env:BUBBLEWRAP_KEYSTORE_PASSWORD = "android"
$env:BUBBLEWRAP_KEY_PASSWORD = "android"
npx --yes @bubblewrap/cli build --skipPwaValidation
```

Outputs (in this folder):

- `app-release-signed.apk`
- `app-release-bundle.aab`

### Option B — Gradle debug APK (Android Studio / command line)

```powershell
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
.\gradlew.bat assembleDebug
```

APK: `app\build\outputs\apk\debug\app-debug.apk`

Convenience copies from the last successful build:

- `dist\making-death-count.apk` (repo root)
- `android-twa\app-debug.apk`

Open `android-twa` in Android Studio and use **Build → Build Bundle(s) / APK(s) → Build APK(s)** if you prefer the GUI.

Copy the APK to a convenient path, for example:

```powershell
New-Item -ItemType Directory -Force -Path ..\dist | Out-Null
Copy-Item app\build\outputs\apk\debug\app-debug.apk ..\dist\making-death-count.apk
```

## Digital Asset Links (required for fullscreen TWA)

Chrome only treats the app as a Trusted Web Activity (no browser URL bar) when Digital Asset Links succeed.

The file **must** be served at the **site root origin**, not under the project path:

```
https://vanuatu-national-statistics-office.github.io/.well-known/assetlinks.json
```

That is the GitHub Pages **user/org** site (`username.github.io`), not:

```
https://vanuatu-national-statistics-office.github.io/making-death-count-vanuatu/.well-known/assetlinks.json
```

Project Pages cannot satisfy this check. Publish `assetlinks.json` from a repo named `vanuatu-national-statistics-office.github.io` (or the org equivalent), or another host on the same origin.

A template is in `assetlinks.json`. After you have a signing certificate fingerprint:

```powershell
npx --yes @bubblewrap/cli fingerprint generateAssetLinks --output assetlinks.json
```

Or list the SHA-256 from the keystore:

```powershell
& "$env:JAVA_HOME\bin\keytool.exe" -list -v -keystore android.keystore -alias android -storepass android
```

Until asset links are live, the APK still works but Chrome may show a Custom Tab / URL bar.

Play App Signing uses a **different** certificate than this debug keystore. After Play signing, add the Play SHA-256 to `assetlinks.json` as well.

## Sideload / install

```powershell
adb install -r ..\dist\making-death-count.apk
```

## Regenerating from the live PWA

When `manifest.webmanifest` is deployed on GitHub Pages:

```powershell
npx --yes @bubblewrap/cli init --manifest="https://vanuatu-national-statistics-office.github.io/making-death-count-vanuatu/manifest.webmanifest" --directory="."
```

That command is interactive. This repo already contains a completed `twa-manifest.json`, so `update` is the non-interactive path.
