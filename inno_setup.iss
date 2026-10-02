[Setup]
AppName=SignalSense
AppVersion=1.0
DefaultDirName={pf}\SignalSense
DefaultGroupName=SignalSense
OutputDir=Output
OutputBaseFilename=SignalSense_Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=frontend\public\vite.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SignalSense.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SignalSense"; Filename: "{app}\SignalSense.exe"
Name: "{commondesktop}\SignalSense"; Filename: "{app}\SignalSense.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SignalSense.exe"; Description: "{cm:LaunchProgram,SignalSense}"; Flags: nowait postinstall skipifsilent
