# Transcript

Minimal, private, offline speech transcription for Windows.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) running locally — no internet connection required after the initial model download.


## Features

- **Three input modes**: Toggle, Push-to-talk, Voice Activity Detection
- **CPU-only**: Runs entirely on your machine using int8 quantized Whisper
- **Auto-copy & auto-paste**: Transcriptions are copied to clipboard and pasted automatically
- **Global hotkey**: Ctrl+Alt+Z — works from any application
- **Always-on-top**: Frameless black floating window, 270×85 px
- **Minimal UX**: No tray icon, no menu bar — just a lightweight overlay
- **Offline**: No data leaves your computer

## Quick Start

1. Download the latest installer from [Releases](https://github.com/renato0x/Transcript/releases)
2. Run `Transcript_v1.0.0_Setup.exe` (no admin rights required)
3. Press **Ctrl+Alt+Z** to start transcribing
4. Speak — release to paste the transcription

The model (~500 MB) is downloaded on first use to `%USERPROFILE%\.cache\faster_whisper\`.

## Modes

| Mode | Behaviour |
|------|-----------|
| **Toggle** | Click to start recording, click to stop |
| **Push-to-talk** | Hold Ctrl+Alt+Z while speaking, release to transcribe |
| **VAD** | Starts recording automatically when speech is detected, stops after silence |

Click the mode indicator (bottom-left) to cycle between modes.

## Building from Source

Requires Python 3.14+.

```
pip install -r requirements.txt
pyinstaller Transcript.spec
iscc setup.iss
```

Or run `scripts\build.bat` to do both steps automatically.

## Tech Stack

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (int8, CPU)
- [PySide6](https://doc.qt.io/qtforpython-6/) (Qt6 GUI)
- [sounddevice](https://python-sounddevice.readthedocs.io/) (audio capture)
- [webrtcvad](https://github.com/wiseman/py-webrtcvad) (voice activity detection)
- [PyInstaller](https://pyinstaller.org/) (packaging)

## License

MIT
