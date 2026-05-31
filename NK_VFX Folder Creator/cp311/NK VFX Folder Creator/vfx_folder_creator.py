# ============================================================
#  VFX Project Folder Structure Creator
#  Supports PySide6 (preferred) with fallback to PySide2
#  Author : VFX Pipeline Tool
# ============================================================

import sys
import os
import json
from pathlib import Path

# ------------------------------------------------------------------
# Qt shim — try PySide6 first, fall back to PySide2
# ------------------------------------------------------------------
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
        QFileDialog, QTreeWidget, QTreeWidgetItem, QGroupBox,
        QSplitter, QTextEdit, QScrollArea, QFrame, QTabWidget,
        QProgressBar, QStatusBar, QMessageBox, QSizePolicy,
        QSpacerItem, QComboBox
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QTextCursor
    QT_VERSION = "PySide6"
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
            QFileDialog, QTreeWidget, QTreeWidgetItem, QGroupBox,
            QSplitter, QTextEdit, QScrollArea, QFrame, QTabWidget,
            QProgressBar, QStatusBar, QMessageBox, QSizePolicy,
            QSpacerItem, QComboBox
        )
        from PySide2.QtCore import Qt, QThread, Signal, QTimer
        from PySide2.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QTextCursor
        QT_VERSION = "PySide2"
    except ImportError:
        print("ERROR: Neither PySide6 nor PySide2 is installed.")
        print("Install one of them:")
        print("  pip install PySide6")
        print("  pip install PySide2")
        sys.exit(1)

print(f"[INFO] Running with {QT_VERSION}")


# ------------------------------------------------------------------
# Helper Functions for Icons
# ------------------------------------------------------------------
def _find_icons_dir():
    """Locate the icons directory relative to the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    potential_path = os.path.join(script_dir, "icons")
    if os.path.exists(potential_path):
        return potential_path
    return None

def _load_icon(icon_name, size=24):
    """
    Helper to load a QIcon from the icon directory.
    If the icon is missing, returns an empty QIcon to prevent crashes.
    """
    icon_dir = _find_icons_dir()
    if not icon_dir:
        return QIcon()

    # Support multiple formats
    for ext in [".png", ".svg", ".ico"]:
        icon_path = os.path.join(icon_dir, f"{icon_name}{ext}")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            return QIcon(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    return QIcon()

# ------------------------------------------------------------------
# VFX Folder Templates
# ------------------------------------------------------------------
VFX_TEMPLATES = {
    "Feature Film": {
        "_PIPELINE": ["config", "scripts", "tools", "templates"],
        "000_ADMIN": ["contracts", "schedules", "budgets", "reports", "correspondence"],
        "010_REFERENCES": ["art_dept", "on_set", "client_briefs", "mood_boards", "storyboards"],
        "020_ASSETS": {
            "characters": ["geo", "rig", "textures", "lookdev", "cache"],
            "props": ["geo", "rig", "textures", "lookdev", "cache"],
            "environments": ["geo", "textures", "lookdev", "cache", "scatter"],
            "vehicles": ["geo", "rig", "textures", "lookdev"],
            "fx_elements": [],
        },
        "030_SHOTS": [],  # populated dynamically
        "040_RENDERS": ["beauty", "passes", "previews", "finals"],
        "050_COMP": ["nuke_scripts", "ae_projects", "elements", "outputs"],
        "060_AUDIO": ["sfx", "music", "dialogue", "mix"],
        "070_DELIVERABLES": ["review", "vfx_pulls", "final_delivery", "archives"],
        "080_LIBRARY": ["hdri", "textures", "models", "plugins", "luts"],
    },
    "Commercial / TVC": {
        "_PIPELINE": ["config", "scripts"],
        "000_ADMIN": ["briefs", "schedules", "reports"],
        "010_REFERENCES": ["client_refs", "mood_boards", "storyboards"],
        "020_ASSETS": {
            "products": ["geo", "textures", "lookdev"],
            "environments": ["geo", "textures", "lookdev"],
            "fx_elements": [],
        },
        "030_SHOTS": [],
        "040_RENDERS": ["beauty", "passes", "finals"],
        "050_COMP": ["nuke_scripts", "outputs"],
        "060_DELIVERABLES": ["review", "finals", "archives"],
    },
    "Short Film": {
        "000_ADMIN": ["schedules", "reports"],
        "010_REFERENCES": ["art_dept", "storyboards"],
        "020_ASSETS": {
            "characters": ["geo", "rig", "textures"],
            "environments": ["geo", "textures"],
        },
        "030_SHOTS": [],
        "040_RENDERS": ["beauty", "finals"],
        "050_COMP": ["nuke_scripts", "outputs"],
        "060_DELIVERABLES": ["finals", "archives"],
    },
    "Music Video": {
        "000_ADMIN": ["briefs", "schedules"],
        "010_REFERENCES": ["mood_boards", "storyboards"],
        "020_ASSETS": {
            "elements": ["geo", "textures"],
        },
        "030_SHOTS": [],
        "040_RENDERS": ["beauty", "finals"],
        "050_COMP": ["outputs"],
        "060_DELIVERABLES": ["finals"],
    },
    "Game Cinematic": {
        "_PIPELINE": ["config", "scripts", "tools"],
        "000_ADMIN": ["schedules", "reports"],
        "010_REFERENCES": ["concept_art", "style_guide"],
        "020_ASSETS": {
            "characters": ["geo", "rig", "textures", "animation"],
            "environments": ["geo", "textures", "props"],
            "fx_elements": [],
        },
        "030_SHOTS": [],
        "040_RENDERS": ["beauty", "passes", "finals"],
        "050_COMP": ["nuke_scripts", "outputs"],
        "060_DELIVERABLES": ["finals", "archives"],
    },
}

SHOT_SUBFOLDERS = [
    "plates", "tracking", "roto", "paint", "fx", "assets", "jpeg", "light", "match-move", "mov",
    "anim", "render", "comp", "deliverable"
]

# ------------------------------------------------------------------
# UI Core Stylesheet (Enhanced Scrollbar Configurations)
# ------------------------------------------------------------------
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #242424;
    color: #e0e0e0;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #454545;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #b3b3b3;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLineEdit, QComboBox {
    background-color: #2e2e2e;
    border: 1px solid #1f1f1f;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #6e6e6e;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #7eb8f7;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}
QPushButton {
    background-color: #2a2a4a;
    border: 1px solid #4a4a7a;
    border-radius: 5px;
    padding: 7px 18px;
    color: #e0e0e0;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #242424;
    border-color: #7eb8f7;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #242424;
}
QPushButton#btn_create {
    background-color: #04aed4;
    border-color: #2a9a5a;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 30px;
}
QPushButton#btn_create:hover {
    background-color: #2a8a4a;
    border-color: #3aba7a;
}
QPushButton#btn_browse {
    background-color: #4f4f4f;
    border: none;
    padding: 6px 14px;
}
QPushButton#btn_browse:hover {
    background-color: #3a5a9a;
}
QCheckBox {
    spacing: 8px;
    color: #787878;
}
QCheckBox::indicator:checked {
    background-color: #00b9e3;
    border-color: #7eb8f7;
}
QTreeWidget {
    background-color: #2e2e2e;
    border: 1px solid #2b2b2b;
    border-radius: 4px;
    color: #c8c8e8;
    alternate-background-color: #242424;
}
QTreeWidget::item:hover {
    background-color: #333333;
}
QTreeWidget::item:selected {
    background-color: #333333;
    color: #ffffff;
}
QTextEdit {
    background-color: #2e2e2e;
    border: 1px solid #3a3a5c;
    border-radius: 4px;
    color: #88ff88;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 6px;
}
QProgressBar {
    border: 1px solid #3b3b3b;
    border-radius: 4px;
    background-color: #00960a;
    text-align: center;
    color: #ffffff;
    height: 20px;
}
QTabWidget::pane {
    border: 1px solid #404040;
    border-radius: 4px;
    background: #404040;
}
QTabBar::tab {
    background: #2e2d2d;
    border: 1px solid #2b2b2b;
    padding: 7px 18px;
    margin-right: 2px;
    border-radius: 4px 4px 0 0;
    color: #ffffff;
}
QTabBar::tab:selected {
    background: #403f3f;
    color: #7eb8f7;
    border-bottom-color: #383838;
}
QTabBar::tab:hover {
    background-color: #008796;
    color: #ffffff;
}
QSplitter::handle {
    background: #3a3a5c;
    width: 2px;
}

/* --- Dark Sci-Fi Scrollbar Blueprint --- */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 14px;
    margin: 0px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #444444;
    min-height: 25px;
    border-radius: 4px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #00b9e3; /* Electric Cyan accent matching checkboxes */
}
QScrollBar::handle:vertical:pressed {
    background-color: #04aed4;
}
QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    color: #7eb8f7;
    padding: 8px 0;
}
QLabel#subtitle_label {
    font-size: 11px;
    color: #7d7d7d;
}
QFrame#divider {
    background-color: #2b2b2b;
    max-height: 1px;
}
"""


# ------------------------------------------------------------------
# Worker thread for folder creation
# ------------------------------------------------------------------
class FolderWorker(QThread):
    progress = Signal(int, str)   # (percent, message)
    finished = Signal(bool, str)  # (success, summary)

    def __init__(self, root_path, structure, shots, extra_folders, readme):
        super().__init__()
        self.root_path = Path(root_path)
        self.structure = structure
        self.shots = shots
        self.extra_folders = extra_folders
        self.readme = readme
        self._created = []

    def run(self):
        try:
            all_paths = self._flatten(self.structure)
            # Add shots
            for shot in self.shots:
                for sub in SHOT_SUBFOLDERS:
                    all_paths.append(Path("030_SHOTS") / shot / sub)
            # Add extra
            for ef in self.extra_folders:
                ef = ef.strip()
                if ef:
                    all_paths.append(Path(ef))

            total = len(all_paths)
            for i, rel in enumerate(all_paths):
                full = self.root_path / rel
                full.mkdir(parents=True, exist_ok=True)
                self._created.append(str(rel))
                pct = int((i + 1) / total * 100)
                self.progress.emit(pct, f"Creating: {rel}")
                self.msleep(5)  # tiny delay for progress visibility

            # Optionally write README
            if self.readme:
                readme_path = self.root_path / "README.txt"
                with open(readme_path, "w") as f:
                    f.write(self._build_readme())

            self.finished.emit(True, f"✓ Created {len(self._created)} folders under:\n{self.root_path}")
        except Exception as e:
            self.finished.emit(False, f"✗ Error: {e}")

    def _flatten(self, node, prefix=Path()):
        paths = []
        if isinstance(node, dict):
            for k, v in node.items():
                cur = prefix / k
                paths.append(cur)
                paths.extend(self._flatten(v, cur))
        elif isinstance(node, list):
            for item in node:
                paths.append(prefix / item)
        return paths

    def _build_readme(self):
        lines = [
            "NK VFX PROJECT FOLDER STRUCTURE",
            "=" * 40,
            f"Root: {self.root_path}",
            "",
            "FOLDERS CREATED:",
        ]
        for p in self._created:
            lines.append(f"  {p}")
        lines += ["", "Generated by NK VFX Folder Creator", f"Qt: {QT_VERSION}"]
        return "\n".join(lines)


# ------------------------------------------------------------------
# Main Window
# ------------------------------------------------------------------
class VFXFolderCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Resolve absolute path to the script's directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Fix the Icon Loading: Use the helper or an absolute path
        icon_path = os.path.join(self.script_dir, "icons", "VFX Project Folder Creator.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback if no 'icons' subfolder exists
            self.setWindowIcon(_load_icon("VFX Project Folder Creator"))

        self.setWindowTitle(f" NK VFX Project Folder Creator  [{QT_VERSION}]")
        
        # 3. Handle Scaling: 1500px might be too big for some laptops
        self.setMinimumSize(1560, 860) 
        
        self.worker = None
        self._init_ui()
        self.setStyleSheet(DARK_STYLE)
        self._refresh_tree()

    # ---- UI Construction ----------------------------------------

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = self._build_header()
        root_layout.addWidget(header)

        # Main content
        tabs = QTabWidget()
        tabs.setContentsMargins(6, 2, 10, 6)
        tabs.addTab(self._build_creator_tab(), "𝐆𝐞𝐧𝐞𝐫𝐚𝐥")
        tabs.setStyleSheet("""
            QTabBar {
                /* Adds a margin on both the left and right of the tab row */
                left: 8px; 
                right: 8px;
            }
            QTabBar::tab {
                border-radius: 2px;
                padding: 12px;
            }
        """)
        tabs.addTab(self._build_about_tab(), "About")
        root_layout.addWidget(tabs)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready  |  {QT_VERSION}")

    def _build_header(self):
        w = QWidget()
        w.setStyleSheet("background-color: #2b2a2a;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(20, 12, 20, 12)

        # 1. Path Logic
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        icon_file = os.path.join(script_dir, "icons", "VFX Project Folder Creator.png")
        icon_file_url = icon_file.replace("\\", "/")

        # 2. LEFT SIDE: Title + Subtitle
        vl = QVBoxLayout()
        vl.setSpacing(2) # Keeps sub right under title

        title = QLabel()
        title.setObjectName("title_label")
        # Added vertical-align:middle to keep text centered with the icon
        title.setText(f'<img src="{icon_file_url}" width="94" height="64"> &nbsp; <span style="vertical-align: middle;">NK VFX Project Folder Creator</span>')
        title.setStyleSheet("QLabel#title_label { font-weight: bold; font-size: 34px;}")

        sub = QLabel("Industry-standard VFX pipeline folder structures | PySide6 / PySide2")
        sub.setObjectName("subtitle_label")
        sub.setStyleSheet("color: #888888; font-size: 14px; margin-left: 8px;") # margin matches icon width to align text

        vl.addWidget(title)
        vl.addWidget(sub)
        lay.addLayout(vl)

        # 3. THE FIX: The Stretch
        lay.addStretch()

        # 4. RIGHT SIDE: Qt Badge
        qt_badge = QLabel(f"{QT_VERSION}")
        qt_badge.setStyleSheet("""
            background: transparent; 
            color: #696969; 
            border-radius: 4px;
            padding: 4px 10px; 
            font-weight: bold; 
            font-size: 12px;
        """)
        
        lay.addWidget(qt_badge, alignment=Qt.AlignRight | Qt.AlignRight)

        return w

    def _build_creator_tab(self):
        w = QWidget()
        outer = QHBoxLayout(w)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL
        left = QWidget()
        llay = QVBoxLayout(left)
        llay.setSpacing(10)

        # Project Info
        info_grp = QGroupBox("Project Information")
        ig = QGridLayout(info_grp)
        ig.setSpacing(8)

        ig.addWidget(QLabel("Project Name:"), 0, 0)
        self.le_name = QLineEdit()
        self.le_name.setPlaceholderText("e.g.  PROJ_001_ClientName")
        ig.addWidget(self.le_name, 0, 1, 1, 2)

        ig.addWidget(QLabel("Root Directory:"), 1, 0)
        self.le_root = QLineEdit()
        self.le_root.setPlaceholderText("C:/Projects  or  /mnt/projects")
        ig.addWidget(self.le_root, 1, 1)
        self.btn_browse = QPushButton("")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setIcon(_load_icon("folder", 45))
        self.btn_browse.clicked.connect(self._browse_root)
        ig.addWidget(self.btn_browse, 1, 2)

        ig.addWidget(QLabel("Template:"), 2, 0)
        self.cb_template = QComboBox()
        self.cb_template.addItems(list(VFX_TEMPLATES.keys()))
        self.cb_template.currentTextChanged.connect(self._refresh_tree)
        ig.addWidget(self.cb_template, 2, 1, 1, 2)

        llay.addWidget(info_grp)

        # Shots
        shots_grp = QGroupBox("Shots  (one per line, e.g. 010, 020, 030)")
        sg = QVBoxLayout(shots_grp)
        self.te_shots = QTextEdit()
        self.te_shots.setPlaceholderText("010\n020\n030\n040\n050")
        self.te_shots.setFixedHeight(150)
        self.te_shots.textChanged.connect(self._refresh_tree)
        sg.addWidget(self.te_shots)
        llay.addWidget(shots_grp)

        # Options
        opt_grp = QGroupBox("Options")
        og = QVBoxLayout(opt_grp)
        self.chk_readme = QCheckBox("Generate README.txt")
        self.chk_readme.setChecked(True)
        self.chk_gitkeep = QCheckBox("Add .gitkeep to empty folders")
        self.chk_gitkeep.setChecked(False)
        og.addWidget(self.chk_readme)
        og.addWidget(self.chk_gitkeep)
        llay.addWidget(opt_grp)

        # Extra folders
        extra_grp = QGroupBox("Extra Custom Folders  (relative paths, one per line)")
        eg = QVBoxLayout(extra_grp)
        self.te_extra = QTextEdit()
        self.te_extra.setPlaceholderText("090_CUSTOM/my_folder\n090_CUSTOM/another")
        self.te_extra.setFixedHeight(70)
        eg.addWidget(self.te_extra)
        llay.addWidget(extra_grp)

        # Create button
        self.btn_create = QPushButton("⬡  CREATE FOLDER STRUCTURE")
        self.btn_create.setObjectName("btn_create")
        self.btn_create.clicked.connect(self._create_folders)
        llay.addWidget(self.btn_create)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        llay.addWidget(self.progress_bar)

        llay.addStretch()
        splitter.addWidget(left)

        # RIGHT PANEL
        right = QWidget()
        right.setObjectName("RightPanel") 

        rlay = QVBoxLayout(right) 
        rlay.setSpacing(8)
        rlay.setContentsMargins(10, 10, 10, 10)

        # Helper function to create horizontal header rows with icons
        def create_section_header(text, icon_name):
            header_widget = QWidget()
            header_lay = QHBoxLayout(header_widget)
            header_lay.setContentsMargins(6, 4, 6, 4)
            header_lay.setSpacing(8)
            
            icon_label = QLabel()
            icon_pix = _load_icon(icon_name, 18) 
            icon_label.setPixmap(icon_pix.pixmap(18, 18))
            header_lay.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("background: transparent; padding: 0px;") 
            header_lay.addWidget(text_label)
            
            header_lay.addStretch()
            return header_widget

        # 1. Add the Folder Tree section header and widget
        folder_header = create_section_header("Folder Structure Preview", "folder")
        rlay.addWidget(folder_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Folder Tree")
        
        # FIXED: Removed 'border: none' from inline string which broke the dark scrollbar inheritances
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #aaaaaa;
                padding: 4px;
                border: 1px solid #242424;
                font-weight: bold;
            }
        """)
        rlay.addWidget(self.tree, 2)

        # 2. Add the Log section header and widget
        log_header = create_section_header("Log", "terminal") 
        rlay.addWidget(log_header)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(150)
        
        # FIXED: Cleared conflicting scrollbar directives from local widget block
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 6px;
            }
        """)
        rlay.addWidget(self.log, 1)

        # Global stylesheet applied to the right container and targeted children
        right.setStyleSheet("""
            QWidget#RightPanel {
                background-color: #1e1e1e; 
            }
            QWidget > QLabel { 
                color: #ffffff;
                font-weight: bold;
            }
            QWidget {
                background-color: #333333; 
                border-radius: 4px;
            }
        """)

        splitter.addWidget(right)
        splitter.setSizes([420, 660])

        outer.addWidget(splitter)
        return w

    def _build_about_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(30, 20, 30, 20)

        info = QTextEdit()
        info.setReadOnly(True)
        info.setHtml(f"""
        <div style="color:#e0e0e0; font-family:'Segoe UI',Arial; line-height:1.7">
        <h2 style="color:#7eb8f7;">VFX Project Folder Creator</h2>
        <p style="color:#888;">Industry-standard pipeline folder structure generator for VFX productions.</p>
        <hr style="border-color:#3a3a5c">

        <h3 style="color:#7eb8f7;">Author</h3>
        <table cellspacing="0" cellpadding="0" style="margin-bottom:6px;">
          <tr>
            <td style="padding-right:12px; vertical-align:middle;">
              <span style="font-size:17px; font-weight:bold; color:#e0e0e0;">Nitin Kashyap</span>
            </td>
          </tr>
          <tr>
            <td style="padding-top:8px;">
              <a href="https://www.linkedin.com/in/nitin-kashyap"
                 style="display:inline-block; background:#0a66c2; color:#ffffff;
                        text-decoration:none; padding:5px 14px; border-radius:4px;
                        font-size:12px; font-weight:bold; margin-right:8px;">
                &#128101; LinkedIn
              </a>
              <a href="https://github.com/nitin-kashyap"
                 style="display:inline-block; background:#24292e; color:#ffffff;
                        text-decoration:none; padding:5px 14px; border-radius:4px;
                        font-size:12px; font-weight:bold; margin-right:8px;
                        border:1px solid #444;">
                &#128040; GitHub
              </a>
              <a href="https://nitin-kashyap.github.io"
                 style="display:inline-block; background:#2a2a4a; color:#7eb8f7;
                        text-decoration:none; padding:5px 14px; border-radius:4px;
                        font-size:12px; font-weight:bold;
                        border:1px solid #4a4a7a;">
                &#127760; Portfolio
              </a>
            </td>
          </tr>
        </table>
        <hr style="border-color:#3a3a5c; margin-top:14px;">

        <h3 style="color:#7eb8f7;">Qt Backend</h3>
        <p>Currently running: <b style="color:#88ff88;">{QT_VERSION}</b></p>
        <p>The tool auto-detects PySide6 (preferred) and falls back to PySide2.</p>
        <h3 style="color:#7eb8f7;">Templates Available</h3>
        <ul>
            <li><b>Feature Film</b> — Full pipeline with assets, shots, renders, comp, audio, delivery</li>
            <li><b>Commercial / TVC</b> — Streamlined for advertising productions</li>
            <li><b>Short Film</b> — Lightweight structure for indie/short projects</li>
            <li><b>Music Video</b> — Minimal VFX-focused layout</li>
            <li><b>Game Cinematic</b> — Game engine-friendly with animation folders</li>
        </ul>
        <h3 style="color:#7eb8f7;">Shot Sub-folders Created Per Shot</h3>
        <p style="color:#aaa;">{" | ".join(SHOT_SUBFOLDERS)}</p>
        <h3 style="color:#7eb8f7;">How to Run</h3>
        <p>Double-click <b style="color:#ffcc44;">WIN.bat</b> (Windows) or run:</p>
        <pre style="background:#212121; padding:8px; border-radius:4px; color:#88ff88;">python vfx_folder_creator.py</pre>
        </div>
        """)
        lay.addWidget(info)
        return w

    # ---- Logic --------------------------------------------------

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        if d:
            self.le_root.setText(d)

    def _get_shots(self):
        raw = self.te_shots.toPlainText().strip()
        if not raw:
            return []
        return [s.strip() for s in raw.splitlines() if s.strip()]

    def _get_extra(self):
        raw = self.te_extra.toPlainText().strip()
        if not raw:
            return []
        return [s.strip() for s in raw.splitlines() if s.strip()]

    def _refresh_tree(self):
        self.tree.clear()
        tmpl_name = self.cb_template.currentText()
        structure = VFX_TEMPLATES.get(tmpl_name, {})
        shots = self._get_shots()

        root_item = QTreeWidgetItem(self.tree, ["[PROJECT_ROOT]"])
        root_item.setForeground(0, QColor("#ffffff"))
        font = QFont()
        font.setBold(True)
        root_item.setFont(0, font)

        self._populate_tree(root_item, structure)

        # Shots
        if shots:
            shots_item = QTreeWidgetItem(root_item, ["030_SHOTS"])
            shots_item.setForeground(0, QColor("#ffaa44"))
            for shot in shots:
                si = QTreeWidgetItem(shots_item, [shot])
                si.setForeground(0, QColor("#ffdd88"))
                for sub in SHOT_SUBFOLDERS:
                    QTreeWidgetItem(si, [sub])

        self.tree.expandAll()
        self.tree.expandToDepth(2)

    def _populate_tree(self, parent, node):
        if isinstance(node, dict):
            for k, v in node.items():
                child = QTreeWidgetItem(parent, [k])
                child.setForeground(0, QColor("#88ccff"))
                self._populate_tree(child, v)
        elif isinstance(node, list):
            for item in node:
                QTreeWidgetItem(parent, [item])

    def _log(self, msg, color="#88ff88"):
        self.log.setTextColor(QColor(color))
        self.log.append(msg)
        self.log.moveCursor(QTextCursor.End)

    def _create_folders(self):
        name = self.le_name.text().strip()
        root = self.le_root.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing Info", "Please enter a Project Name.")
            return
        if not root:
            QMessageBox.warning(self, "Missing Info", "Please select a Root Directory.")
            return
        if not os.path.isdir(root):
            QMessageBox.warning(self, "Invalid Path", f"Directory does not exist:\n{root}")
            return

        tmpl = VFX_TEMPLATES[self.cb_template.currentText()]
        full_root = os.path.join(root, name)

        self._log(f"\n[START] Creating: {full_root}", "#7eb8f7")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.btn_create.setEnabled(False)

        self.worker = FolderWorker(
            root_path=full_root,
            structure=tmpl,
            shots=self._get_shots(),
            extra_folders=self._get_extra(),
            readme=self.chk_readme.isChecked()
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.status_bar.showMessage(msg)
        if pct % 10 == 0:
            self._log(f"  {msg}", "#aaaacc")

    def _on_finished(self, success, summary):
        self.progress_bar.setValue(100)
        self.btn_create.setEnabled(True)
        if success:
            self._log(f"\n{summary}", "#44ff88")
            self.status_bar.showMessage("✓ Folder structure created successfully!")
            QMessageBox.information(self, "Success", summary)
        else:
            self._log(f"\n{summary}", "#ff4444")
            self.status_bar.showMessage("✗ Error occurred.")
            QMessageBox.critical(self, "Error", summary)
        QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
def main():
    app = QApplication.instance()
    is_standalone = False
    if app is None:
        app = QApplication(sys.argv)
        is_standalone = True

    global main_win
    main_win = VFXFolderCreator()
    main_win.show()

    if is_standalone:
        sys.exit(app.exec())
    
    return main_win

if __name__ == "__main__":
    main()