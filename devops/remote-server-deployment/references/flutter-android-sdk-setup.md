# Flutter + Android SDK (User-Level, No Sudo)

> Reference for `remote-server-deployment` skill.

## Prerequisites

- User-level JDK 17+ in `~/jdk/`
- Android command-line tools in `~/android-sdk/`
- Flutter SDK in `~/flutter/`

## Install JDK (user-level)

```bash
mkdir -p ~/jdk && cd ~/jdk
wget -q https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.9%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz
tar xf OpenJDK17U-jdk_x64_linux_hotspot_17.0.9_9.tar.gz
export JAVA_HOME=~/jdk/jdk-17.0.9+9
export PATH=$JAVA_HOME/bin:$PATH
```

## Android SDK (cmdline-tools)

Use Chinese mirrors if default Google URLs are slow:

```bash
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
# Download commandlinetools-linux from mirror or Google
yes | ~/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
export ANDROID_HOME=~/android-sdk
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

## Flutter

```bash
git clone https://github.com/flutter/flutter.git -b stable ~/flutter
export PATH=~/flutter/bin:$PATH
flutter doctor --android-licenses
```

## Build APK

```bash
cd /path/to/flutter/project
flutter pub get
flutter build apk --release
```

## Common Permission Fixes

```bash
chmod +x ~/flutter/bin/flutter
chmod -R u+rw ~/android-sdk
```

Document SDK paths in project RUNBOOK.md for reproducibility.
