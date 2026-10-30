<h1 align="center"><b> Local AI Stem Splitter</b></h1>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" /></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" /></a>
  <a href="https://github.com/facebookresearch/demucs"><img src="https://img.shields.io/badge/Demucs-v4%20(HTDemucs)-0081FB?style=for-the-badge&logo=meta&logoColor=white" alt="Demucs v4" /></a>
  <a href="https://ffmpeg.org/"><img src="https://img.shields.io/badge/FFmpeg-Supported-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg" /></a>
  <img src="https://img.shields.io/badge/Audio%20Quality-320%20kbps%20MP3-brightgreen?style=for-the-badge" alt="320 kbps MP3" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-555555?style=for-the-badge" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <em>An interactive, AI-powered command-line audio stem splitter. Effortlessly isolate vocals, instrumentals, drums, bass, guitar, and piano in studio-grade 320 kbps MP3.</em>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-separation-modes">Separation Modes</a> •
  <a href="#-tech-stack--libraries">Tech Stack</a> •
  <a href="#-step-by-step-installation--usage">Getting Started</a> •
  <a href="#-expected-output">Expected Output</a> •
  <a href="#-troubleshooting">Troubleshooting</a>
</p>

---

## Overview

A lightweight, interactive CLI automation tool designed for musicians, DJs, music producers, content creators, and audio enthusiasts. It leverages Meta AI's state-of-the-art **Demucs v4 (Hybrid Transformer)** architecture to accurately separate mixed audio tracks into individual, isolated stems with minimal artifacts and maximum fidelity.

Fully offline after your first installation (all of the models will be saved in your computer cache).

---

## Key Features

- **Intuitive Drag-and-Drop**: Drag any audio file directly from File Explorer into your terminal prompt—no tedious manual path typing required.
- **Immediate Mode Selection**: Choose your desired stem separation mode (2, 4, or 6 stems) on the fly immediately after supplying the audio file.
- **Automatic Hardware Detection**: Automatically utilizes NVIDIA CUDA GPU acceleration when available, with a graceful fallback to multi-core CPU processing.
- **VRAM-Optimized (`--segment 7`)**: Utilizes intelligent chunking on CUDA GPUs to run comfortably even on modest graphics cards with 4 GB VRAM without running out of memory.
- **Studio-Quality 320 kbps MP3**: Converts all separated tracks directly into high-bitrate MP3 files using the high-performance LAME encoder.
- **Clean Output Organization**: Automatically organizes stems into dedicated per-song subdirectories inside `output/<song_name>/`, overwriting or cleaning up stale stems from prior runs.

---

## Separation Modes

The script supports three tailored separation modes:

| Mode | Target Use Case | Model / Option | Generated Output Files |
| :--- | :--- | :--- | :--- |
| **2 Stems** | Karaoke, acapellas, remixing, vocal removal | `htdemucs` (`--two-stems vocals`) | `vocals.mp3`, `instrumental.mp3` |
| **4 Stems** *(Default)* | Standard music production, sampling, stem mastering | `htdemucs` | `vocals.mp3`, `drums.mp3`, `bass.mp3`, `other.mp3` |
| **6 Stems** | Detailed instrument analysis, guitar/piano covers | `htdemucs_6s` | `vocals.mp3`, `drums.mp3`, `bass.mp3`, `guitar.mp3`, `piano.mp3`, `other.mp3` |

---

## Tech Stack & Libraries

This project combines state-of-the-art deep learning architectures with robust system utilities:

### 1. Programming Language
- **[Python 3.9+](https://www.python.org/)**: Core language powering the workflow, system validation, CLI parsing, and file management.

### 2. Deep Learning & Audio AI
- **[Demucs v4](https://github.com/facebookresearch/demucs) (Meta AI Research)**:
  - *Hybrid Transformer Demucs* (HTDemucs), the industry benchmark for music source separation combining waveform (time-domain) and spectrogram (frequency-domain) neural networks.
  - Model `htdemucs`: Pre-trained 4-stem model and 2-stem isolation engine.
  - Model `htdemucs_6s`: 6-source model capable of isolating individual guitar and piano tracks.
- **[PyTorch](https://pytorch.org/) (`torch`)**:
  - Neural network runtime powering Demucs inference with native CUDA hardware acceleration.

### 3. Multimedia & Audio Encoding
- **[FFmpeg](https://ffmpeg.org/)**:
  - System-level multimedia backbone used to decode arbitrary input audio formats (`.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`, `.aac`, etc.).
  - Encodes extracted stem tensors into high-quality MP3s via `libmp3lame` at **320 kbps constant bitrate (CBR)**.

### 4. Python Standard Library
- **`pathlib`**: Cross-platform path resolution and safe filesystem operations.
- **`argparse`**: Robust CLI flag handling (`--mode`, `audio_file`).
- **`tempfile`**: Sandboxed temporary staging to ensure final output directories only receive verified stems.
- **`dataclasses`**: Structured, type-safe separation mode definitions.
- **`subprocess` & `shutil`**: System tool verification (FFmpeg PATH checks) and atomic file moves.

---

## Step-by-Step Installation & Usage

Follow this comprehensive guide to set up and run the stem splitter from scratch.

### Step 1: System Prerequisites
Ensure your system meets the following requirements:
1. **Operating System**: Windows 10/11, macOS, or Linux.
2. **Python**: Version 3.9 through 3.12 ([Download Python](https://www.python.org/downloads/)).
   > *Windows users: Be sure to check the box **"Add Python to PATH"** during installation.*
3. **Internet Connection**: Required for the initial dependency installation and first-time model downloads.

---

### Step 2: Clone or Download the Repository
Open your terminal (PowerShell or Command Prompt on Windows, Terminal on macOS/Linux):

```bash
git clone https://github.com/username/audio-stem-splitter.git
cd audio-stem-splitter
```

*(If your project is already in `D:\Splitter`, navigate directly via `cd D:\Splitter`)*.

---

### Step 3: Set Up a Virtual Environment
A virtual environment isolates project dependencies from your system-wide Python installation.

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> [!NOTE]
> If PowerShell displays a script execution policy error (`PSSecurityException`), run the following command once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> Then re-run `.\.venv\Scripts\Activate.ps1`.

**Windows Command Prompt (CMD):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

When activated, you will see `(.venv)` displayed at the beginning of your terminal prompt.

---

### Step 4: Install and Verify FFmpeg
FFmpeg is required by Demucs to read and write audio files. Choose your preferred installation method:

- **Windows via winget (Recommended):**
  ```powershell
  winget install Gyan.FFmpeg.Shared
  ```
- **Windows via Chocolatey:**
  ```powershell
  choco install ffmpeg
  ```
- **macOS via Homebrew:**
  ```bash
  brew install ffmpeg
  ```
- **Debian / Ubuntu Linux:**
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```

**Verify FFmpeg Installation:**  
Restart your terminal and run:
```bash
ffmpeg -version
```
If version information is displayed, FFmpeg is correctly installed and accessible in your system `PATH`.

---

### Step 5: Install Python Dependencies (PyTorch & Demucs)
With your virtual environment active, upgrade `pip` and install the required packages:

1. Upgrade `pip`:
   ```powershell
   python -m pip install --upgrade pip
   ```

2. Install PyTorch:
   - **For NVIDIA GPU with CUDA (Highly Recommended for fast processing):**
     ```powershell
     python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     ```
   - **For CPU Only (if you do not have an NVIDIA GPU):**
     ```powershell
     python -m pip install -U torch
     ```

3. Install Demucs:
   ```powershell
   python -m pip install -U demucs
   ```

---

### Step 6: Running the Program

#### Method A: Interactive Drag-and-Drop (Easiest)
1. Run the script without arguments:
   ```powershell
   python .\split_audio.py
   ```
2. The terminal will prompt:
   ```text
   Drag and drop an audio file here, then press Enter:
   ```
3. Drag any audio file (`.mp3`, `.wav`, `.flac`, etc.) from File Explorer into the terminal window and press **Enter**.
4. The stem mode selection menu will appear immediately:
   ```text
   File audio terdeteksi: my_song.mp3

   Pilih mode pemisahan stem:
     [1] 4 Stems  - Default (Vocals, Drums, Bass, Other)
     [2] 2 Stems  - Vocal & Instrumental
     [3] 6 Stems  - Vocals, Drums, Bass, Guitar, Piano, Other (htdemucs_6s)
   Pilihan Anda [1/2/3] (default: 1): 
   ```
5. Enter your choice:
   - Press **Enter** or type `1` for standard **4 Stems**.
   - Type `2` for **2 Stems** (Vocal & Instrumental).
   - Type `3` (or `6`) for **6 Stems**.

#### Method B: Command-Line Interface (CLI)
You can also specify the audio file and mode directly via arguments:

```powershell
# Interactive mode (prompts for stem choice after reading the file):
python .\split_audio.py "C:\Music\song.mp3"

# Direct mode (skips menu and processes automatically):
python .\split_audio.py "C:\Music\song.mp3" -m 2    # 2 Stems (Vocal & Instrumental)
python .\split_audio.py "C:\Music\song.mp3" -m 4    # 4 Stems (Standard default)
python .\split_audio.py "C:\Music\song.mp3" -m 6    # 6 Stems (htdemucs_6s)
```

---

## Expected Output

### 1. Terminal Execution Log
During separation, progress bars and execution details will be printed in real-time:

```text
File audio terdeteksi: 04 - Kanye West - ALL THE LOVE.mp3

Pilih mode pemisahan stem:
  [1] 4 Stems  - Default (Vocals, Drums, Bass, Other)
  [2] 2 Stems  - Vocal & Instrumental
  [3] 6 Stems  - Vocals, Drums, Bass, Guitar, Piano, Other (htdemucs_6s)
Pilihan Anda [1/2/3] (default: 1): 2
-> Mode aktif: 2 Stems (Vocal & Instrumental)

Memproses 04 - Kanye West - ALL THE LOVE.mp3 (2 Stems) menggunakan model htdemucs di CUDA...
Separating track 04 - Kanye West - ALL THE LOVE.mp3
100%|████████████████████████████████████████████████████████████| 32.5/32.5 [00:45<00:00, 1.40s/s]

Stems berhasil disimpan ke: D:\Splitter\output\04 - Kanye West - ALL THE LOVE
  - instrumental.mp3
  - vocals.mp3
```

### 2. Directory Structure of Generated Stems
Separated stems are neatly placed inside `output/<song_name>/`:

#### Mode 2 Stems (Vocal & Instrumental):
```text
output/
└── 04 - Kanye West - ALL THE LOVE/
    ├── instrumental.mp3    <-- High-quality backing track
    └── vocals.mp3          <-- Isolated acapella vocals
```

#### Mode 4 Stems (Default):
```text
output/
└── 04 - Kanye West - ALL THE LOVE/
    ├── bass.mp3            <-- Isolated bassline & sub-bass
    ├── drums.mp3           <-- Isolated drums, percussion & beat
    ├── other.mp3           <-- Synths, keys, strings & background FX
    └── vocals.mp3          <-- Isolated vocals
```

#### Mode 6 Stems:
```text
output/
└── 04 - Kanye West - ALL THE LOVE/
    ├── bass.mp3            <-- Isolated bass
    ├── drums.mp3           <-- Isolated drums & beat
    ├── guitar.mp3          <-- Isolated acoustic / electric guitars
    ├── other.mp3           <-- Background elements & soundscapes
    ├── piano.mp3           <-- Isolated piano & keyboard parts
    └── vocals.mp3          <-- Isolated vocals
```

> **Audio Quality Guarantee**: All output stems are encoded as **320 kbps MP3** files, ensuring universal compatibility across all DAWs (FL Studio, Ableton Live, Logic Pro, Reaper) and media players without compromising acoustic clarity.

---

## Troubleshooting & FAQs

### First-Time Model Download
- When running a model for the first time, Demucs automatically downloads its pre-trained weights (`htdemucs` ~80–300 MB, `htdemucs_6s` ~300 MB).
- Model weights are stored in your user cache (`~/.cache/torch/hub/` or `~/.cache/huggingface/`). Subsequent runs are completely offline and will not re-download weights.

### `ffmpeg was not found on PATH`
Demucs cannot process audio without FFmpeg. Ensure FFmpeg is installed and added to your system environment variables. Open a fresh terminal and run `ffmpeg -version` to verify.

### CUDA Out of Memory (GPU VRAM Full)
The script automatically applies `--segment 7` on CUDA devices to keep VRAM usage around ~3–4 GB. If you still encounter an Out-of-Memory (OOM) error, close other GPU-intensive applications (e.g., 3D games, browser hardware acceleration) or run with CPU mode.

### File Paths Containing Spaces
When typing paths in the CLI, always wrap them in quotation marks:
```powershell
python .\split_audio.py "D:\My Music\Song Title.mp3"
```
When dragging and dropping onto the interactive prompt, surrounding quotes added by Windows terminal are automatically stripped and handled.

---

## License & Acknowledgments
- Audio source separation powered by **[Demucs](https://github.com/facebookresearch/demucs)** by Meta AI Research (Défossez et al.).
- Released under the open-source **MIT License** for personal, educational, and creative audio production purposes.
