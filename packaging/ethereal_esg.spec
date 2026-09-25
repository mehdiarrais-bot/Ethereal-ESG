# -*- mode: python ; coding: utf-8 -*-
# Build : depuis la racine du depot, apres `npm run build` dans frontend/ :
#   pip install -r packaging/requirements-desktop.txt
#   pyinstaller packaging/ethereal_esg.spec --noconfirm
# Sortie : dist/EtherealESG.exe — UN SEUL fichier, sans console : un
# double-clic ouvre l'application dans sa propre fenetre (pywebview, moteur
# WebView2 de Windows). Voir backend/desktop_entry.py.
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND_DIST = os.path.join(ROOT, "frontend", "dist")

if not os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
    raise SystemExit("frontend/dist/index.html absent : lancer `npm run build` avant PyInstaller.")

datas = [(FRONTEND_DIST, "frontend_dist")]
# Polices (OFL) et photos d'illustration (domaine public / CC0) des gabarits
# éditoriaux, lues via pdf_kit.assets_dir() (sys._MEIPASS/assets une fois figé).
datas += [(os.path.join(BACKEND, "assets"), "assets")]
# Gabarits par defaut de python-docx / python-pptx, donnees matplotlib.
datas += collect_data_files("docx")
datas += collect_data_files("pptx")
datas += collect_data_files("matplotlib")

hiddenimports = collect_submodules("uvicorn") + ["clauses", "clauses.fr"]

a = Analysis(
    [os.path.join(BACKEND, "desktop_entry.py")],
    pathex=[BACKEND],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "pytest", "pyright", "fitz", "pymupdf", "IPython"],
    noarchive=False,
)
pyz = PYZ(a.pure)

# Mode « onefile » : binaires et donnees dans l'exe lui-meme (pas de COLLECT).
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="EtherealESG",
    console=False,   # pas de fenetre noire : journal dans %APPDATA%\EtherealESG
    upx=False,       # UPX augmente les faux positifs antivirus
    icon=os.path.join(ROOT, "frontend", "dist", "favicon.ico"),
)
