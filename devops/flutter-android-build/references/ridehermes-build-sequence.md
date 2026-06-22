# RideHermes Complete Build Sequence (Proven 2026-06-21)

Complete end-to-end sequence for building both passenger and driver APKs on dc1-priority.

## Prerequisites
- Server: `dc1-priority` (113.98.62.224:55084) — Flutter 3.44.2, JDK 17, Android SDK pre-installed
- Connection: `ssh dc1-priority` (direct, no proxy needed)

## Step-by-Step Sequence

### 1. Sync Latest Code from Local
```bash
# On local machine:
cd /d/workspace/projects/pm-demo-repository/04-mvp-src/src
tar -czf /tmp/passenger-app-latest.tar.gz passenger-app/
tar -czf /tmp/driver-app-latest.tar.gz driver-app/
scp /tmp/passenger-app-latest.tar.gz dc1-priority:~/
scp /tmp/driver-app-latest.tar.gz dc1-priority:~/

# On dc1-priority:
cd ~ && rm -rf ridehermes/src/passenger-app ridehermes/src/driver-app
mkdir -p ridehermes/src
tar -xzf passenger-app-latest.tar.gz -C ridehermes/src/
tar -xzf driver-app-latest.tar.gz -C ridehermes/src/
```

### 2. Fix Dependencies (BOTH apps)
```bash
# For each app (passenger-app, driver-app):
cd ~/ridehermes/src/<app-name>

# Fix intl version (Flutter 3.44 requirement)
sed -i 's/intl: \^0.19.0/intl: ^0.20.2/' pubspec.yaml

# Fix CardTheme → CardThemeData (Flutter 3.27+ API change)
# Check both lib/theme/app_theme.dart and lib/app.dart
sed -i 's/CardTheme(/CardThemeData(/g' lib/theme/app_theme.dart 2>/dev/null
sed -i 's/CardTheme(/CardThemeData(/g' lib/app.dart 2>/dev/null

# Fix void return type (driver-app specific)
# Error: "This expression has type 'void' and can't be used" with await disconnect()
sed -i "s/await _ref.read(wsServiceProvider).disconnect();/_ref.read(wsServiceProvider).disconnect();/" lib/providers/driver_tracking_provider.dart 2>/dev/null

# Run pub get
export PATH=$HOME/flutter/bin:$PATH
flutter pub get
```

### 3. Fix Android Build Config (BOTH apps)
```bash
cd ~/ridehermes/src/<app-name>/android

# Fix Kotlin version (must be 2.1.0+ for metadata compatibility)
sed -i 's/org.jetbrains.kotlin.android" version "[^"]*"/org.jetbrains.kotlin.android" version "2.1.0"/' settings.gradle

# Fix compileSdk (must be 36 for newer plugins)
sed -i 's/compileSdk = [0-9]*/compileSdk = 36/' app/build.gradle

# Fix CRLF in gradlew (causes bash\r error)
sed -i "s/\r$//" gradlew && chmod +x gradlew
```

### 4. Create Release Keystore (BOTH apps)
```bash
cd ~/ridehermes/src/<app-name>/android

# Generate keystore
export JAVA_HOME=$HOME/jdk-17.0.2
export PATH=$JAVA_HOME/bin:$PATH
keytool -genkey -v -keystore app/release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias release-key -storepass ridehermes -keypass ridehermes \
  -dname "CN=RideHermes, OU=Dev, O=RideHermes, L=SG, S=SG, C=SG"

# Create key.properties
cat > key.properties << EOF
storeFile=release-key.jks
storePassword=ridehermes
keyAlias=release-key
keyPassword=ridehermes
EOF
```

### 5. Build APK with Backend URL
```bash
export JAVA_HOME=$HOME/jdk-17.0.2
export ANDROID_HOME=$HOME/android-sdk
export PATH=$HOME/flutter/bin:$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

# Get current Cloudflare tunnel URL
TUNNEL_URL=$(grep 'trycloudflare.com' /tmp/cf-tunnel.log | tail -1 | grep -oP 'https://[^\s]+')

cd ~/ridehermes/src/<app-name>
flutter build apk --release \
  --android-skip-build-dependency-validation \
  --dart-define=API_BASE_URL=$TUNNEL_URL \
  --dart-define=WS_URL=${TUNNEL_URL/https/wss}/ws/location
```

### 6. Download APKs to Local
```bash
# On local machine:
mkdir -p /d/workspace/deliverables
scp dc1-priority:~/ridehermes/src/passenger-app/build/app/outputs/flutter-apk/app-release.apk /d/workspace/deliverables/passenger-app.apk
scp dc1-priority:~/ridehermes/src/driver-app/build/app/outputs/flutter-apk/app-release.apk /d/workspace/deliverables/driver-app.apk
```

## Web Deployment Sequence
```bash
# On dc1-priority:
# 1. Start Go backend
cd ~/ridehermes/src/ride-hermes
nohup ./ride-hermes > /tmp/ride-hermes.log 2>&1 &

# 2. Admin Web is served on port 3002 (PM2 or node)
# 3. Start Cloudflare tunnel
pkill -f 'cloudflared tunnel' 2>/dev/null
nohup ~/bin/cloudflared tunnel --url http://localhost:3002 > /tmp/cf-tunnel.log 2>&1 &
sleep 8 && grep 'trycloudflare.com' /tmp/cf-tunnel.log | tail -1

# 4. Verify API
curl -s https://<tunnel-url>/api/v1/auth/login-or-register \
  -X POST -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","password":"admin123"}'
```

## Test Accounts
| Role | Phone | Password |
|------|-------|----------|
| Admin | 13800000000 | admin123 |
| Passenger | 13900000001 | test123 |
| Driver | 13900009999 | test123 |

## Timing
- Code sync: ~30s
- Fixes + pub get: ~2 min per app
- Build: ~1-2 min per app (cached), ~5 min (first build)
- Total: ~10 min for both APKs
