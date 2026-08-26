[app]

# (str) Title of your application
title = Minesweeper 2D

# (str) Package name
package.name = minesweeper2d

# (str) Package domain (needed for android/ios packaging)
package.domain = org.minesweeper.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,ogg

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# NOTE: Use 'pygame' (not 'pygame-ce') - python-for-android only has a recipe for 'pygame'
requirements = python3==3.11.9,pygame

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
# android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android archs to build for
# Build only arm64-v8a for faster builds and modern device support
android.archs = arm64-v8a

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Enable Android auto backup
android.allow_backup = True

# (str) Format to use where packaging ("apk" or "aab")
# android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
