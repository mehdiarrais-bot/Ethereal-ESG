# -*- mode: python ; coding: utf-8 -*-
# Build : depuis la racine du depot, apres `npm run build` dans frontend/ :
#   pyinstaller packaging/ethereal_esg.spec --noconfirm
# Sortie : dist/EtherealESG/EtherealESG.exe (mode onedir, a distribuer zippe).
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND_DIST = os.path.join(ROOT, "frontend", "dist")

if not os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
    raise SystemExit("frontend/dist/index.html absent : lancer `npm run build` avant PyInstaller.")

datas = [(FRONTEND_DIST, "frontend_dist")]
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EtherealESG",
    console=True,
    upx=False,  # UPX augmente les faux positifs antivirus
    icon=os.path.join(ROOT, "frontend", "dist", "favicon.ico"),
)
coll = COLLECT(exe, a.binaries, a.datas, name="EtherealESG", upx=False)
