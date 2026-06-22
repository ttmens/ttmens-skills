#!/bin/bash
# fix_flutter_plugins.sh - Apply all compatibility fixes for Flutter 3.x + AGP 8.x
# Run AFTER `flutter pub get` has populated ~/.pub-cache/
#
# Usage: bash fix_flutter_plugins.sh

set -e

PUB_CACHE=~/.pub-cache/hosted/pub.dev

echo "=== Fixing amap_flutter_base ==="
cd $PUB_CACHE/amap_flutter_base-3.0.0/lib 2>/dev/null || { echo "Skip: amap_flutter_base not found"; }
if [ $? -eq 0 ]; then
    # Fix hashValues -> Object.hash
    sed -i 's/hashValues(/Object.hash(/g' src/location.dart src/amap_privacy_statement.dart 2>/dev/null || true
fi

echo "=== Fixing amap_flutter_map ==="
cd $PUB_CACHE/amap_flutter_map-3.0.0/lib 2>/dev/null || { echo "Skip: amap_flutter_map not found"; }
if [ $? -eq 0 ]; then
    # Fix hashValues -> Object.hash in all dart files
    find . -name "*.dart" -exec sed -i 's/hashValues(/Object.hash(/g' {} \;
    
    # Fix Java files - remove FlutterMain.getLookupKeyForAsset() wrapper
    cd $PUB_CACHE/amap_flutter_map-3.0.0/android/src/main/java/com/amap/flutter/map/utils
    sed -i 's/FlutterMain\.getLookupKeyForAsset(\([^)]*\))/\1/g' ConvertUtil.java 2>/dev/null || true
    
    # Fix PluginRegistry.Registrar -> FlutterPlugin
    cd $PUB_CACHE/amap_flutter_map-3.0.0/android/src/main/java/com/amap/flutter/map
    sed -i 's/import io\.flutter\.plugin\.PluginRegistry;/import io.flutter.embedding.engine.plugins.FlutterPlugin;/g' AMapFlutterMapPlugin.java 2>/dev/null || true
    sed -i 's/PluginRegistry\.Registrar/FlutterPlugin.FlutterPluginBinding/g' AMapFlutterMapPlugin.java 2>/dev/null || true
fi

echo "=== Fixing speech_to_text ==="
cd $PUB_CACHE/speech_to_text-6.6.0/android/src/main/kotlin/com/csdcorp/speech_to_text 2>/dev/null || { echo "Skip: speech_to_text not found"; }
if [ $? -eq 0 ]; then
    # Fix deprecated Registrar API
    sed -i 's/Registrar/FlutterPlugin.FlutterPluginBinding/g' SpeechToTextPlugin.kt 2>/dev/null || true
    sed -i 's/activity()/binding.activity/g' SpeechToTextPlugin.kt 2>/dev/null || true
    sed -i 's/context()/binding.applicationContext/g' SpeechToTextPlugin.kt 2>/dev/null || true
fi

echo "=== Injecting namespace for AGP 8.x ==="
for plugin in amap_flutter_location-3.0.0 amap_flutter_map-3.0.0 amap_flutter_base-3.0.0; do
    GRADLE=$PUB_CACHE/$plugin/android/build.gradle
    MANIFEST=$PUB_CACHE/$plugin/android/src/main/AndroidManifest.xml
    if [ -f "$GRADLE" ] && ! grep -q "namespace" "$GRADLE"; then
        if [ -f "$MANIFEST" ]; then
            PKG=$(grep -oP 'package="[^"]+"' "$MANIFEST" | head -1 | sed 's/package="//;s/"//')
            if [ -n "$PKG" ]; then
                sed -i "/android {/a\\    namespace \"$PKG\"" "$GRADLE"
                echo "  Added namespace=$PKG to $plugin"
            fi
        fi
    else
        echo "  $plugin: namespace already set or no build.gradle"
    fi
done

echo "=== All fixes applied ==="
