import shutil
import subprocess
import sys
from pathlib import Path


def find_inno_setup():
    iscc_path = shutil.which("ISCC.exe") or shutil.which("ISCC")
    if iscc_path:
        return iscc_path

    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return None

# ====================================
# Load version
# ====================================

version = {}

with open("version.py", "r") as f:
    exec(f.read(), version)

VERSION = version["VERSION"]

print("=" * 40)
print("Curlew Explorer Build Pipeline")
print("=" * 40)
print(f"Version: {VERSION}")

# ====================================
# Clean old builds
# ====================================

print("\nCleaning old builds...")

for folder in ["build", "dist", "installer"]:
    path = Path(folder)

    if path.exists():
        shutil.rmtree(path)

spec_file = Path("CurlewExplorer.spec")

if spec_file.exists():
    spec_file.unlink()

# ====================================
# Generate installer.iss
# ====================================

print("\nGenerating installer.iss...")

installer_script = f"""
[Setup]
AppName=Curlew Explorer
AppVersion={VERSION}
AppPublisher=AJC Software
DefaultDirName={{localappdata}}\\Curlew Explorer
DefaultGroupName=Curlew Explorer
OutputDir=installer
OutputBaseFilename=CurlewExplorerSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\\CurlewExplorer\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\Curlew Explorer"; Filename: "{{app}}\\CurlewExplorer.exe"
Name: "{{userdesktop}}\\Curlew Explorer"; Filename: "{{app}}\\CurlewExplorer.exe"

[Run]
Filename: "{{app}}\\CurlewExplorer.exe"; Description: "Launch Curlew Explorer"; Flags: nowait postinstall skipifsilent
"""

with open("installer.iss", "w") as f:
    f.write(installer_script)

# ====================================
# Build executable
# ====================================

print("\nBuilding executable...")

pyinstaller_command = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconsole",
    "--onedir",
    "--noupx",
    "--name", "CurlewExplorer",
    "--icon", "assets/icon.ico",
    "--version-file", "version_info.txt",
    "--hidden-import", "scipy",
    "--hidden-import", "scipy.signal",
    "--hidden-import", "matplotlib",
    "--collect-submodules", "curlew_explorer",
    "--add-data", "assets/frame0;assets/frame0",
    "gui.py"
]

result = subprocess.run(pyinstaller_command)

if result.returncode != 0:
    print("\nPyInstaller build FAILED.")
    exit(1)

# ====================================
# Build installer
# ====================================

print("\nBuilding installer...")

inno_setup = find_inno_setup()

if inno_setup is None:
    print("\nInno Setup compiler was not found.")
    print("The executable build succeeded, but the installer could not be created.")
    print("Install Inno Setup 6 or 7, or add ISCC.exe to your PATH, then run build.py again.")
    print("\nExecutable:")
    print("dist/CurlewExplorer/")
    exit(1)

result = subprocess.run([
    inno_setup,
    "installer.iss"
])

if result.returncode != 0:
    print("\nInstaller build FAILED.")
    exit(1)

# ====================================
# Complete
# ====================================

print("\n" + "=" * 40)
print("BUILD COMPLETE")
print("=" * 40)

print(f"\nVersion: {VERSION}")

print("\nExecutable:")
print("dist/CurlewExplorer/")

print("\nInstaller:")
print("installer/CurlewExplorerSetup.exe")
