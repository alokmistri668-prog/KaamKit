[app]
android.api = 33
android.min_api = 21
android.ndk = 25b
title = MeriApp
package.name = meriapp
package.domain = org.test
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 0.1
requirements = python3,kivy,plyer
android.permissions = VIBRATE
orientation = portrait
icon.filename = %(source.dir)s/icon.png
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 1
