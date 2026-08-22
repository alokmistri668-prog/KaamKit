[app]
title = MeriApp
package.name = meriapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3==3.10.11,hostpython3==3.10.11,kivy,plyer

orientation = portrait

icon.filename = %(source.dir)s/icon.png

android.api = 35
android.minapi = 24

[buildozer]
log_level = 2
warn_on_root = 1
