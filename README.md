<div align="center">

# Transcript

**Offline speech transcription for Windows.**

Fast, private, and completely local — no internet required after the first run.

[![License: MIT][license-badge]][license-url]
[![Latest Release][release-badge]][release-url]
[![Windows 10/11][windows-badge]][release-url]

<br/>

[**Download**][release-url]&nbsp;&nbsp;•&nbsp;&nbsp;[**Report a Bug**][issues-url]&nbsp;&nbsp;•&nbsp;&nbsp;[**Request a Feature**][issues-url]

</div>

---

## Features

- **Three input modes** — Toggle, Push-to-talk, or Voice Activity Detection
- **CPU-only** — runs locally using int8 quantized Whisper (no GPU needed)
- **Auto-copy & auto-paste** — transcriptions go straight to your cursor
- **Global hotkey** — <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Z</kbd> from any app
- **Always-on-top** — minimal floating window, no taskbar clutter
- **Zero network** — your voice never leaves your machine

## Quick Start

1. Download the installer from [Releases][release-url]
2. Run `Transcript_v0.2_Setup.exe` — no admin rights required
3. Press <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Z</kbd> and speak
4. Release — transcription is pasted automatically

> The Whisper model (~500 MB) is downloaded on first use to `%USERPROFILE%\.cache\faster_whisper\`.

## Download

| Platform | Link |
|----------|------|
| Windows 10/11 | [Latest Release][release-url] |

## Building from Source

<details>
<summary>Prerequisites & build steps</summary>

**Requires** Python 3.14+

```bash
# Install dependencies
pip install -r requirements.txt pyinstaller

# Build executable + installer
scripts\build.bat
```

Or run each step manually:

```bash
pyinstaller Transcript.spec
iscc setup.iss
```

</details>

## Roadmap

- [x] Whisper int8 CPU transcription
- [x] Three input modes (Toggle / Push-to-talk / VAD)
- [x] Global hotkey with auto-paste
- [x] Minimal floating window UI
- [ ] Multi-language support
- [ ] GPU acceleration (CUDA / ROCm)
- [ ] Custom hotkey configuration UI
- [ ] Export formats (SRT, TXT)
- [ ] System tray integration

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Transcription | [faster-whisper][faster-whisper-url] (int8, CPU) |
| GUI | [PySide6][pyside6-url] (Qt6) |
| Audio | [sounddevice][sounddevice-url] |
| VAD | [webrtcvad][webrtcvad-url] |
| Packaging | [PyInstaller][pyinstaller-url] + [Inno Setup][inno-url] |

## License

Distributed under the MIT License. See [`LICENSE`][license-url] for details.

---

<div align="center">

**[renato0x](https://github.com/renato0x)**

</div>

<!-- Badges -->
[license-badge]: https://img.shields.io/github/license/renato0x/Transcript?style=flat-square&color=blue
[release-badge]: https://img.shields.io/github/v/release/renato0x/Transcript?style=flat-square
[windows-badge]: https://img.shields.io/badge/Windows-10%20%7C%2011-blue?style=flat-square&logo=windows&logoColor=white

<!-- Links -->
[license-url]: https://github.com/renato0x/Transcript/blob/master/LICENSE
[release-url]: https://github.com/renato0x/Transcript/releases/latest
[issues-url]: https://github.com/renato0x/Transcript/issues
[faster-whisper-url]: https://github.com/SYSTRAN/faster-whisper
[pyside6-url]: https://doc.qt.io/qtforpython-6/
[sounddevice-url]: https://python-sounddevice.readthedocs.io/
[webrtcvad-url]: https://github.com/wiseman/py-webrtcvad
[pyinstaller-url]: https://pyinstaller.org/
[inno-url]: https://jrsoftware.org/isinfo.php
