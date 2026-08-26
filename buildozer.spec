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
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame-ce

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
# (str) android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
# android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (list) List of javac options to add
# android.add_javac_options = -Xlint:unchecked

# (list) Android additionnal libraries to copy into libs/armeabi
# android.add_libs_armeabi = libs/armeabi/liba.so

# (bool) Enable Android auto backup
android.allow_backup = True

# (str) Format to use where packaging ("apk" or "aab")
package = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
