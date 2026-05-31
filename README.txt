#  NK_VFX-Folder-Creator
#  VFX PROJECT FOLDER CREATOR ========================== A PySide6 / PySide2 desktop tool to generate industry-standard VFX pipeline folder structures in one click.  QUICK START (Windows)


VFX PROJECT FOLDER CREATOR
==========================
A PySide6 / PySide2 desktop tool to generate industry-standard
VFX pipeline folder structures in one click.

#  standalone

Double-click:  WIN.bat

QUICK START (Windows)
---------------------
  Double-click:  WIN.bat

  The .bat file will:
    1. Check Python is installed
    2. Check PySide6 or PySide2 is installed
    3. Offer to auto-install if neither is found
    4. Launch vfx_folder_creator.py

QUICK START (WIN / Linux / macOS)
----------------------------
  pip install PySide2
  pip install PySide6
  python vfx_folder_creator.py

FILES
-----
  vfx_folder_creator.py   — Main application (UI + logic)
  WIN.bat                 — Windows launcher
  requirements.txt        — Dependency notes
  README.txt              — This file

TEMPLATES
---------
  Feature Film       Full pipeline with assets, shots, renders, comp, audio, delivery
  Commercial / TVC   Streamlined for advertising productions
  Short Film         Lightweight indie structure
  Music Video        Minimal VFX layout
  Game Cinematic     Animation-focused game pipeline

SHOT SUB-FOLDERS (auto-created per shot)
-----------------------------------------
  plates | tracking | roto | paint | fx
  anim   | render   | comp | deliverable

REQUIREMENTS
------------
  Python 3.8+
  PySide6 >= 6.4  (recommended)
    OR
  PySide2 >= 5.15 (legacy)

#  Manual Installation (Windows, macOS, & Linux)

Step 1: Place the file
Move vfx_folder_creator.py into your Nuke plugin path (for example, your ~/.nuke directory).

Windows: C:\Users\<Username>\.nuke\

Linux/macOS: /home/<Username>/.nuke/

    nuke.pluginAddPath(r'./NK_VFX Folder')
