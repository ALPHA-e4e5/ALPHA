[app]

# (str) Title of your application
title = AirMouse

# (str) Package name
package.name = airmouse

# (str) Package domain (must be unique to avoid conflicts with other apps)
package.domain = org.yourname

# (str) Source files to include in the APK
source.include_exts = py, png, jpg, kv

# (list) Application requirements
# Include plyer for gyroscope, websockets for communication, and kivy for UI
requirements = python3, kivy, plyer, android

# (str) Supported orientation options
orientation = portrait

# (bool) Enable full screen mode (no status bar)
fullscreen = 1

# (str) Icon for the app (should be 512x512 PNG image)
# You can place your icon in the assets folder or specify a path to an image
icon.filename = assets/icon.png

# (str) Presplash screen (a simple image shown at startup)
presplash.filename = assets/presplash.png

# (list) Permissions required by the app
# 'INTERNET' for WebSocket communication and 'ACCESS_NETWORK_STATE' to verify network connectivity
android.permissions = INTERNET, ACCESS_NETWORK_STATE, USB_PERMISSION, BODY_SENSORS, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, FOREGROUND_SERVICE
# (int) API levels for Android
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.package_name = com.yourdomain.airmouse
# (str) Additional Java classes to add (leave empty for this app)
android.add_jars =

# (str) Additional Java resources to add (leave empty for this app)
android.add_resources =

# (bool) Enables a custom keyboard (useful if app needs text entry)
android.enable_android_physical_keys = False

# (str) Screen sizes (most commonly used screen configurations)
screen_density = 480

# (bool) Build .apk and .aab
# Uncomment the below line if you also want an .aab for Google Play
# packaging a single .apk is typically easier for testing
# android.aab = True
source.dir = .
version = 1.0.0

[buildozer]

# (str) Command to execute the app on an Android device
# Useful for testing - this can be set to your Android device path
# run.start_command = ./bin/
