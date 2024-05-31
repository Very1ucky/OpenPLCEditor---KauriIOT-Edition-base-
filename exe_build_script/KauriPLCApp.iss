; -- 64Bit.iss --
; Demonstrates installation of a program built for the x64 (a.k.a. AMD64)
; architecture.
; To successfully run this installation and the program it installs,
; you must have a "x64" edition of Windows.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

; Имя приложения
#define   Name       "OpenPLC_Editor-KauriIOT_Edition"
; Версия приложения
#define   Version    "0.1"
; Фирма-разработчик
#define   Publisher  "KauriIOT"
; Сафт фирмы разработчика
#define   URL        "https://kauri-iot.com/"


[Setup]
AppId={{2E5AE828-DC3F-49B9-AE0C-2D0DCF98FFFE}
AppName={#Name}
AppVersion={#Version}
AppPublisher={#Publisher}
AppPublisherURL={#URL}
AppSupportURL={#URL}
AppUpdatesURL={#URL}
WizardStyle=modern
DefaultDirName={%USERPROFILE}\{#Name}
DefaultGroupName={#Name}
Compression=lzma2
SolidCompression=yes
OutputDir=E:\Temp\exes\test-setup
OutputBaseFilename=test-setup
LicenseFile=E:\Projects\OpenPLC_Editor\LICENSE
; "ArchitecturesAllowed=x64" specifies that Setup cannot run on
; anything but x64.
ArchitecturesAllowed=x64
; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "E:\Projects\OpenPLC_Editor\OpenPLC Editor.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "E:\Projects\OpenPLC_Editor\*"; Excludes: ".venv,python/.venv,.vscode,.git,exe_build_script,editor/kauri_parser/settings.json,editor/kauri_parser/settings.json,editor/kauri_parser/Sources/Common/Generated"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

                                                                                               
[Icons]
Name: "{group}\{#Name}"; Filename: "{app}\OpenPLC Editor.bat"; IconFilename: "{app}\brz.ico"; Tasks: desktopicon

[UninstallDelete]
Type: files; Name: "{app}\python\*"
Type: files; Name: "{app}\editor\kauri_parser\*"
