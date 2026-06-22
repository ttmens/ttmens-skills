---
name: flutter-android-build
description: "Flutter Android APK builds on remote Linux servers — environment setup, plugin compatibility fixes, release signing, and troubleshooting."
tags: [flutter, android, apk, build, remote-server, plugin-fix]
triggers:
  - flutter build apk
  - 编译乘客端司机端
  - Flutter Android 编译
  - Namespace not specified flutter
  - hashValues flutter error
---

# Flutter Android Build on Remote Linux Server

## When to Use
- Building Flutter Android APKs on headless Linux servers (no Android Studio)
- Migrating old Flutter projects to newer Flutter/AGP/Kotlin versions
- Fixing plugin compatibility issues with Flutter 3.x

## ⚠️ CRITICAL: One-Shot Build Strategy (NEVER fix-build-cycle)

**Root cause of 14-attempt build failures**: fixing one error, rebuilding, discovering next error, repeating.
Each rebuild wastes 3-8 minutes. The fix: **apply ALL known fixes BEFORE the first build**.

### Pre-Build Checklist (execute in order, every time)

```bash
# 1. Run the automated fix script FIRST
bash scripts/fix_flutter_plugins.sh

# 2. Verify ALL fixes applied
echo "=== Checking all fixes ==="
grep -r "namespace" ~/.pub-cache/hosted/pub.dev/amap_flutter_map-3.0.0/android/build.gradle && echo "✅ namespace"
grep -r "Object.hash" ~/.pub-cache/hosted/pub.dev/amap_flutter_base-3.0.0/lib/src/location.dart && echo "✅ hashValues→Object.hash"
grep -c "FlutterMain" ~/.pub-cache/hosted/pub.dev/amap_flutter_map-3.0.0/android/src/main/java/com/amap/flutter/map/utils/ConvertUtil.java | grep "^0$" && echo "✅ FlutterMain removed"

# 3. Only THEN build
flutter build apk --release --android-skip-build-dependency-validation
```

### Known Error Categories (fix ALL before building)

| Category | Errors | Fix Script Section |
|----------|--------|--------------------|
| Dart API | `hashValues` undefined | `fix_dart_api()` |
| Java API | `FlutterMain`, `Registrar` | `fix_java_api()` |
| Kotlin API | `Registrar` in speech_to_text | `fix_kotlin_api()` |
| AGP 8.x | Missing `namespace` | `fix_namespace()` |
| Gradle | Version mismatch, CRLF | `fix_gradle()` |
| Signing | Missing keystore/path | `fix_signing()` |
| SDK | compileSdk < 36 | `fix_sdk_version()` |
| Dependencies | intl version conflict | `fix_dependencies()` |

### Anti-Pattern (NEVER DO THIS)
```
❌ Fix hashValues → Build → FAIL → Fix namespace → Build → FAIL → Fix FlutterMain → Build → FAIL...
```

### Correct Pattern (ALWAYS DO THIS)
```
✅ Fix ALL (hashValues + namespace + FlutterMain + Registrar + compileSdk + intl + signing) → Build ONCE → SUCCESS
```

### Build Error Recovery (if build still fails)
If the one-shot build fails with an UNKNOWN error (not in the table above):
1. Read the FULL error output (not just the last line)
2. Identify ALL errors in the output (there may be multiple)
3. Fix ALL of them at once
4. Rebuild ONCE

## Version Matrix

| Component | Flutter 3.27 | Flutter 3.44 (dc1-priority) | Notes |
|-----------|-------------|---------------------------|-------|
| Flutter | 3.27.4 | 3.44.2 | Use server's pre-installed version |
| AGP | 8.11.1 | 8.11.1 | Required for Flutter 3.27+ |
| Kotlin | 2.2.20 | 2.1.0 | Must be 2.1.0+ to avoid metadata version errors |
| Gradle | 8.14.3 | 8.5 | Use server's cached version |
| compileSdk | 35 | 36 | Newer plugins (shared_pref, sqflite, record) require 36 |
| JDK | 17 | 17 | openjdk-17-jdk |

**⚠️ CRITICAL — ALWAYS use dc1-priority as the build server.** It has Flutter 3.44, JDK 17, Android SDK, Gradle caches, and all plugin patches pre-installed. Setting up from scratch wastes 30+ minutes and risks download failures. Do NOT attempt to install Flutter on a fresh server unless dc1-priority is confirmed unreachable.

**Connectivity**: Use Tailscale internal network when available (`ssh tencent-sg`, `ssh aliyun-us`, `ssh aliyun-bj`). Falls back to public IP if Tailscale is down. dc1-priority uses direct SSH on port 55084.

## Environment Setup (Clean Ubuntu Server)

```bash
# 1. Flutter SDK (use Chinese mirror for speed)
cd ~
curl -L -o flutter.tar.xz https://storage.flutter-io.cn/flutter_infra_release/releases/stable/linux/flutter_linux_3.27.4-stable.tar.xz
tar -xJf flutter.tar.xz

# 2. JDK
sudo apt-get install -y openjdk-17-jdk

# 3. Android cmdline-tools
wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdtools.zip
mkdir -p android-sdk/cmdline-tools
unzip -q cmdtools.zip -d android-sdk/cmdline-tools/
mv android-sdk/cmdline-tools/cmdline-tools android-sdk/cmdline-tools/latest

# 4. Accept licenses and install components
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME=$HOME/android-sdk
export PATH=$HOME/flutter/bin:$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH
printf "y\ny\ny\ny\ny\ny\ny\ny\n" | sdkmanager --licenses
sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-34"
```

## Plugin Compatibility Fixes (Critical)

### 1. Namespace Injection (AGP 8.x requirement)
Old plugins lack namespace in build.gradle. Fix:
```bash
PUB=~/.pub-cache/hosted/pub.dev
for plugin in amap_flutter_location-3.0.0 amap_flutter_map-3.0.0; do
  GRADLE=$PUB/$plugin/android/build.gradle
  MANIFEST=$PUB/$plugin/android/src/main/AndroidManifest.xml
  if [ -f "$GRADLE" ] && ! grep -q "namespace" "$GRADLE"; then
    PKG=$(grep -oP 'package="[^"]+"' "$MANIFEST" | head -1 | sed 's/package="//;s/"//')
    sed -i "/android {/a\\    namespace \"$PKG\"" "$GRADLE"
  fi
done
```

### 2. hashValues to Object.hash (Flutter 3.x)
```bash
find $PUB_CACHE -name "*.dart" -exec sed -i 's/hashValues(/Object.hash(/g' {} \;
```

### 3. FlutterMain Deprecated API (amap_flutter_map)
```bash
# In ConvertUtil.java - remove FlutterMain.getLookupKeyForAsset() wrapper
sed -i 's/FlutterMain\.getLookupKeyForAsset(\([^)]*\))/\1/g' ConvertUtil.java
```

### 4. PluginRegistry.Registrar to FlutterPlugin (new embedding)
```bash
# In AMapFlutterMapPlugin.java
sed -i 's/PluginRegistry\.Registrar/FlutterPlugin.FlutterPluginBinding/g' AMapFlutterMapPlugin.java
```

### 5. speech_to_text Kotlin API
```bash
# In SpeechToTextPlugin.kt
sed -i 's/Registrar/FlutterPlugin.FlutterPluginBinding/g' SpeechToTextPlugin.kt
sed -i 's/activity()/binding.activity/g' SpeechToTextPlugin.kt
sed -i 's/context()/binding.applicationContext/g' SpeechToTextPlugin.kt
```

## Project-Level Updates

### settings.gradle
```groovy
plugins {
    id "com.android.application" version "8.11.1" apply false
    id "org.jetbrains.kotlin.android" version "2.2.20" apply false
}
```

### gradle-wrapper.properties
```
distributionUrl=https\://services.gradle.org/distributions/gradle-8.14.3-all.zip
```

### app/build.gradle
```groovy
android {
    namespace = "com.yourpackage.name"
    compileSdk 35
}
```

## Release Signing

```bash
# Generate keystore
keytool -genkey -v -keystore app/release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias release-key -storepass YOUR_PASSWORD -keypass YOUR_PASSWORD \
  -dname "CN=YourApp, OU=Dev, O=YourOrg, L=City, S=State, C=US"

# Create key.properties in android/
cat > key.properties << EOF
storeFile=release-key.jks
storePassword=YOUR_PASSWORD
keyAlias=release-key
keyPassword=YOUR_PASSWORD
EOF
```

## Build Command

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME=$HOME/android-sdk
export PATH=$HOME/flutter/bin:$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

cd ~/your-flutter-app
flutter pub get
flutter build apk --release --android-skip-build-dependency-validation
```

## Flutter 3.44+ Specific Fixes

### intl Version Pinning
flutter_localizations pins intl to 0.20.2. If pubspec.yaml has `intl: ^0.19.0`, pub get fails:
```bash
sed -i 's/intl: \^0.19.0/intl: ^0.20.2/' pubspec.yaml
```

### CardTheme → CardThemeData
Flutter 3.27+ renamed `CardTheme` to `CardThemeData`:
```bash
find lib -name "*.dart" -exec sed -i 's/CardTheme(/CardThemeData(/g' {} \;
```

### Kotlin Metadata Version Mismatch
Error: `Module was compiled with an incompatible version of Kotlin. The binary version of its metadata is 2.1.0, expected version is 1.9.0.`
Fix: Update Kotlin in settings.gradle to at least 2.1.0:
```bash
sed -i 's/org.jetbrains.kotlin.android" version "[^"]*"/org.jetbrains.kotlin.android" version "2.1.0"/' settings.gradle
```

### gradlew CRLF Line Endings
Error: `/usr/bin/env: 'bash\r': No such file or directory`
Fix:
```bash
sed -i "s/\r$//" android/gradlew && chmod +x android/gradlew
```

### compileSdk 36 Required
Newer plugins (shared_preferences_android, sqflite_android, record_android, flutter_plugin_android_lifecycle) require compileSdk 36:
```bash
sed -i 's/compileSdk = [0-9]*/compileSdk = 36/' android/app/build.gradle
```

## Gradle Download Pitfall

**CRITICAL**: `services.gradle.org` can be extremely slow (67KB/s) from China servers, causing builds to hang indefinitely. Use Tencent mirror instead:
```bash
# If Gradle download is stalled, kill and use mirror:
rm -rf ~/.gradle/wrapper/dists/gradle-8.5-all/
mkdir -p ~/.gradle/wrapper/dists/gradle-8.5-all/3zlzzgtsutfj0pbojr50n2l7z/
cd ~/.gradle/wrapper/dists/gradle-8.5-all/3zlzzgtsutfj0pbojr50n2l7z/
curl -L -o gradle-8.5-all.zip https://mirrors.cloud.tencent.com/gradle/gradle-8.5-all.zip
# Tencent mirror: ~14MB/s vs official ~67KB/s
```

## Web Deployment with Cloudflare Tunnel

For serving Admin Web publicly:
```bash
# Start backend first
cd ~/ridehermes/src/ride-hermes
nohup ./ride-hermes > /tmp/ride-hermes.log 2>&1 &

# Start Cloudflare tunnel pointing to web port
nohup ~/bin/cloudflared tunnel --url http://localhost:3002 > /tmp/cf-tunnel.log 2>&1 &
sleep 5 && grep 'trycloudflare.com' /tmp/cf-tunnel.log | tail -1
# Output: https://xxx-xxx-xxx.trycloudflare.com
```

## APK Backend URL Injection

Always use `--dart-define` to point APK to the correct backend:
```bash
flutter build apk --release \
  --android-skip-build-dependency-validation \
  --dart-define=API_BASE_URL=https://your-backend.trycloudflare.com \
  --dart-define=WS_URL=wss://your-backend.trycloudflare.com/ws/location
```

## Common Errors and Fixes

| Error | Fix |
|-------|-----|
| Namespace not specified | Inject namespace into plugin android/build.gradle |
| hashValues not defined | Replace with Object.hash() |
| FlutterMain cannot be found | Remove FlutterMain wrapper, use asset name directly |
| Registrar unresolved | Migrate to FlutterPlugin.FlutterPluginBinding |
| SigningConfig release missing storeFile | Create keystore plus key.properties |
| compileSdkVersion not found | Use compileSdk (no Version) for AGP 8.x |
| intl version solving failed | Update to `intl: ^0.20.2` |
| CardTheme can't be assigned to CardThemeData? | Replace `CardTheme(` with `CardThemeData(` |
| Kotlin metadata version 2.1.0 expected 1.9.0 | Update Kotlin to 2.1.0+ in settings.gradle |
| bash\r: No such file or directory | Fix CRLF: `sed -i "s/\r$//" gradlew` |
| Gradle download hangs | Use Tencent mirror (see Gradle Download Pitfall section) |
| plugins require Android SDK 36 | Set `compileSdk = 36` in app/build.gradle |
| void type can't be used (await disconnect) | Remove `await` — method returns void, not Future |

## Dart void Return Type Error

Error: `This expression has type 'void' and can't be used.` with `await someService.disconnect();`
Cause: The method returns `void` (not `Future<void>`), so `await` is invalid.
Fix: Remove the `await` keyword:
```bash
# Wrong:
sed -i 's/await _ref.read(wsServiceProvider).disconnect();/_ref.read(wsServiceProvider).disconnect();/' lib/providers/driver_tracking_provider.dart
```

## References

- `references/ridehermes-build-sequence.md` — Complete proven end-to-end build sequence for RideHermes (passenger + driver APKs + web deployment), including all fixes in order, test accounts, and timing estimates.

## Automation

A reusable fix script is available at `scripts/fix_flutter_plugins.sh` — run it after `flutter pub get` to apply all plugin patches in one shot.

## Complete Redeployment Workflow (Web + APK)

When you need to deploy web publicly and rebuild APKs pointing to it:

```bash
# 1. Start backend on build server
cd ~/ridehermes/src/ride-hermes
nohup ./ride-hermes > /tmp/ride-hermes.log 2>&1 &
sleep 2 && curl -s http://localhost:8686/health  # verify

# 2. Start Cloudflare tunnel (creates new public URL)
nohup ~/bin/cloudflared tunnel --url http://localhost:3002 > /tmp/cf-tunnel.log 2>&1 &
sleep 5 && grep 'trycloudflare.com' /tmp/cf-tunnel.log | tail -1
# → https://module-prev-shall-griffin.trycloudflare.com

# 3. Verify public API
curl -s "https://YOUR_URL.trycloudflare.com/api/v1/auth/login-or-register" \
  -X POST -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","password":"admin123"}'

# 4. Rebuild BOTH APKs with new URL
TUNNEL_URL="https://YOUR_URL.trycloudflare.com"
for app in passenger-app driver-app; do
  cd ~/ridehermes/src/$app
  flutter build apk --release \
    --android-skip-build-dependency-validation \
    --dart-define=API_BASE_URL=$TUNNEL_URL \
    --dart-define=WS_URL=${TUNNEL_URL/https/wss}/ws/location
done

# 5. Download APKs to local
scp dc1-priority:~/ridehermes/src/passenger-app/build/app/outputs/flutter-apk/app-release.apk \
    /d/workspace/deliverables/passenger-app.apk
scp dc1-priority:~/ridehermes/src/driver-app/build/app/outputs/flutter-apk/app-release.apk \
    /d/workspace/deliverables/driver-app.apk
```

**⚠️ Cloudflare tunnel URL changes on every restart.** If you restart the tunnel, you MUST rebuild APKs with the new URL. The default `appConfig.dart` baseUrl (`ride.accseal.cn`) is used when `--dart-define` is not specified.

## Performance Notes

- **ALWAYS use dc1-priority as default build server** — it has Flutter 3.44, JDK 17, Android SDK, and Gradle caches pre-installed. Setting up from scratch wastes 30+ minutes.
- Flutter SDK download: Use `storage.flutter-io.cn` mirror (10MB/s) vs Google official (200KB/s from Asia)
- Gradle distribution: Use `mirrors.cloud.tencent.com/gradle/` (14MB/s) vs `services.gradle.org` (67KB/s from China)
- First build downloads Gradle distribution (~200MB) — allow 5+ minutes
- flutter pub get resolves all plugin dependencies to ~/.pub-cache/
- Plugin source patches must be applied AFTER flutter pub get (plugins are downloaded fresh)
- Cloudflare tunnel URL changes on restart — rebuild APKs with new URL if tunnel restarts
