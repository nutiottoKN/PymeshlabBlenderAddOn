# PymeshlabBlenderAddOn

## Description
This Blender add-on is designed for processing 3D models using Pymeshlab algorithms. These allow operations such as merging close vertices, reducing the polygon count, and performing other optimization tasks.

Unfortunately, the add-on currently works only on Linux, as it crashes on Windows for an unknown reason. The exact cause of the issue is unclear, but it prevents the add-on from running smoothly on the Windows platform.

## Adding an Add-on to Blender
### 1. Using Flatpak Blender version 
<sub> sudo ln -s /var/lib/flatpak/app/org.blender.Blender/x86_64/stable/active/files/blender/blender /usr/local/bin/blender </sub>
### 2. Install PyMeshLab python library under Blender
<sup> sudo "/var/lib/flatpak/app/org.blender.Blender/x86_64/stable/active/files/blender/4.2/python/bin/python3.11" -m pip install pymeshlab </sup>
### 3. Adding the PyMeshlab Add-od to Blender
***1. Open Blender***
***2. Go to Edit -> Preferences -> Add-ons***
***3. Install from Disk...***
***4. Enable Add-on***
