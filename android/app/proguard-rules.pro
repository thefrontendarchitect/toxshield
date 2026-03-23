# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# === Capacitor WebView Bridge ===
# Keep the Capacitor bridge classes so R8 doesn't strip/rename them
-keep class com.getcapacitor.** { *; }
-keep class com.toxshield.app.** { *; }
-dontwarn com.getcapacitor.**

# Keep JavaScript interface methods for WebView communication
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep Capacitor plugin classes registered via reflection
-keep @com.getcapacitor.annotation.CapacitorPlugin class * { *; }

# Keep AndroidX classes used by Capacitor
-keep class androidx.core.** { *; }
-keep class androidx.appcompat.** { *; }
