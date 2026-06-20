; Transcript — Inno Setup Script
; renato0x

#define MyAppName "Transcript"
#ifndef MyAppVersion
#define MyAppVersion "1.0.1"
#endif
#define MyAppPublisher "renato0x"
#define MyAppURL "https://github.com/renato0x/Transcript"

[Setup]
AppId={{F4A7B3C2-8D5E-4F1A-9B6C-3E2D5A8F7B1C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=Transcript_v{#MyAppVersion}_Setup
Compression=lzma2/max
SolidCompression=yes
UninstallDisplayIcon={app}\Transcript.exe
UninstallDisplayName={#MyAppName}
PrivilegesRequired=lowest
DisableDirPage=auto
DisableFinishedPage=no
SetupIconFile=logo.ico

VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Transcript — Local speech transcription

WizardImageFile=banner.bmp
WizardSmallImageFile=small.bmp
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
 WelcomeLabel1=Welcome to Transcript {#MyAppVersion}
 WelcomeLabel2=This will install Transcript on your computer.%n%nLightweight, private, offline speech transcription.

[Files]
Source: "dist\Transcript\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Icons]
Name: "{userdesktop}\Transcript"; Filename: "{app}\Transcript.exe"; WorkingDir: "{app}"; Tasks: desktopicon; Comment: "Transcript — Local speech transcription"
Name: "{group}\Transcript"; Filename: "{app}\Transcript.exe"; WorkingDir: "{app}"; Comment: "Transcript — Local speech transcription"
Name: "{group}\Uninstall Transcript"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Transcript.exe"; Description: "Run Transcript now"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if ShellExec('open', 'taskkill', '/f /im Transcript.exe', '', SW_HIDE, ewNoWait, ResultCode) then
    Sleep(500);
end;

function InitializeUninstall: Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if ShellExec('open', 'taskkill', '/f /im Transcript.exe', '', SW_HIDE, ewNoWait, ResultCode) then
    Sleep(500);
end;
