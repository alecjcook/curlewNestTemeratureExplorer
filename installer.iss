
[Setup]
AppName=Curlew Explorer
AppVersion=1.0.3
AppPublisher=AJC Software
DefaultDirName={localappdata}\Curlew Explorer
DefaultGroupName=Curlew Explorer
OutputDir=installer
OutputBaseFilename=CurlewExplorerSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\CurlewExplorer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Curlew Explorer"; Filename: "{app}\CurlewExplorer.exe"
Name: "{userdesktop}\Curlew Explorer"; Filename: "{app}\CurlewExplorer.exe"

[Run]
Filename: "{app}\CurlewExplorer.exe"; Description: "Launch Curlew Explorer"; Flags: nowait postinstall skipifsilent
