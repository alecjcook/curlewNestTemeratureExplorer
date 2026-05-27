import shutil
import subprocess
from pathlib import Path

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
Name: "{{commondesktop}}\\Curlew Explorer"; Filename: "{{app}}\\CurlewExplorer.exe"

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
    "pyinstaller",
    "--noconsole",
    "--onedir",
    "--noupx",
    "--name", "CurlewExplorer",
    "--icon", "assets/icon.ico",
    "--version-file", "version_info.txt",
    "--hidden-import", "scipy",
    "--hidden-import", "scipy.signal",
    "--hidden-import", "matplotlib",
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

inno_setup = r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"

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