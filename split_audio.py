from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class SplitMode:
    key: str
    name: str
    description: str
    model_name: str
    demucs_args: tuple[str, ...]
    stem_mapping: dict[str, str]


MODES: dict[str, SplitMode] = {
    "4": SplitMode(
        key="4",
        name="4 Stems",
        description="Vocals, Drums, Bass, Other (Default)",
        model_name="htdemucs",
        demucs_args=(),
        stem_mapping={
            "vocals": "vocals",
            "drums": "drums",
            "bass": "bass",
            "other": "other",
        },
    ),
    "2": SplitMode(
        key="2",
        name="2 Stems",
        description="Vocal & Instrumental",
        model_name="htdemucs",
        demucs_args=("--two-stems", "vocals"),
        stem_mapping={
            "vocals": "vocals",
            "no_vocals": "instrumental",
            "minus_vocals": "instrumental",
        },
    ),
    "6": SplitMode(
        key="6",
        name="6 Stems",
        description="Vocals, Drums, Bass, Guitar, Piano, Other (htdemucs_6s)",
        model_name="htdemucs_6s",
        demucs_args=(),
        stem_mapping={
            "vocals": "vocals",
            "drums": "drums",
            "bass": "bass",
            "guitar": "guitar",
            "piano": "piano",
            "other": "other",
        },
    ),
}

DEFAULT_MODE = "4"
OUTPUT_ROOT = Path("output")

KNOWN_STEM_FILES = {
    "vocals.mp3",
    "drums.mp3",
    "bass.mp3",
    "other.mp3",
    "guitar.mp3",
    "piano.mp3",
    "instrumental.mp3",
    "no_vocals.mp3",
    "minus_vocals.mp3",
}


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse an optional audio path and stem mode from the command line."""
    parser = argparse.ArgumentParser(
        description="Split an audio file into stems with Demucs (2, 4, or 6 stems)."
    )
    parser.add_argument(
        "audio_file",
        nargs="?",
        help="Path to an audio file. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default=None,
        help="Stem separation mode: '4' (default 4-stems), '2' (vocal & instrumental), or '6' (htdemucs_6s). If omitted, you will be prompted.",
    )
    return parser.parse_args(argv)


def clean_dragged_path(raw_path: str) -> Path:
    """Remove whitespace, powershell call syntax, and quotes commonly added by drag-and-drop."""
    cleaned = raw_path.strip()
    if cleaned.startswith("& "):
        cleaned = cleaned[2:].strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "\"'":
        cleaned = cleaned[1:-1].strip()
    return Path(cleaned).expanduser()


def get_audio_path(argument: str | None) -> Path:
    """Resolve the command-line path or request one interactively."""
    raw_path = argument
    if raw_path is None:
        raw_path = input("Drag and drop an audio file here, then press Enter: ")
    if not raw_path or not raw_path.strip():
        raise ValueError("No audio file path was supplied.")
    audio_path = clean_dragged_path(raw_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Input audio file does not exist: {audio_path}")
    resolved = audio_path.resolve()
    print(f"File audio terdeteksi: {resolved.name}")
    return resolved


def normalize_mode_choice(user_input: str) -> str | None:
    """Map user input to standard mode key ('4', '2', '6')."""
    cleaned = user_input.strip().lower()
    if cleaned in ("", "1", "4", "4-stems", "4stems", "default"):
        return "4"
    if cleaned in ("2", "2-stems", "2stems", "two-stems", "vocal", "vocals", "instrumental"):
        return "2"
    if cleaned in ("3", "6", "6-stems", "6stems", "htdemucs_6s", "6s"):
        return "6"
    return None


def prompt_stem_mode(initial_choice: str | None = None) -> SplitMode:
    """Prompt the user to select the stem separation mode."""
    if initial_choice is not None:
        normalized = normalize_mode_choice(initial_choice)
        if normalized in MODES:
            return MODES[normalized]
        print(
            f"Peringatan: Opsi mode '{initial_choice}' tidak dikenal. Silakan pilih dari menu di bawah.",
            file=sys.stderr,
        )

    print("\nPilih mode pemisahan stem:")
    print("  [1] 4 Stems  - Default (Vocals, Drums, Bass, Other)")
    print("  [2] 2 Stems  - Vocal & Instrumental")
    print("  [3] 6 Stems  - Vocals, Drums, Bass, Guitar, Piano, Other (htdemucs_6s)")

    while True:
        try:
            choice = input("Pilihan Anda [1/2/3] (default: 1): ")
        except (KeyboardInterrupt, EOFError):
            print()
            raise KeyboardInterrupt

        normalized = normalize_mode_choice(choice)
        if normalized in MODES:
            selected_mode = MODES[normalized]
            print(f"-> Mode aktif: {selected_mode.name} ({selected_mode.description})\n")
            return selected_mode

        print("Pilihan tidak valid. Ketik 1 (4 stems), 2 (2 stems), atau 3 (6 stems).")


def verify_ffmpeg() -> None:
    """Ensure ffmpeg is available and executable before starting Demucs."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        raise RuntimeError(
            "ffmpeg was not found on PATH. Install it and restart the terminal."
        )
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as error:
        raise RuntimeError(f"ffmpeg could not be executed: {error}") from error
    if result.returncode != 0:
        details = result.stderr.strip()
        raise RuntimeError(
            f"ffmpeg is installed but failed its version check"
            f"{f': {details}' if details else '.'}"
        )


def select_device() -> tuple[str, bool]:
    """Return the Demucs device and whether GPU-specific options are needed."""
    try:
        import torch
    except ImportError as error:
        raise RuntimeError(
            "PyTorch is not installed. Run: python -m pip install -U torch"
        ) from error

    use_cuda = bool(torch.cuda.is_available())
    return ("cuda" if use_cuda else "cpu", use_cuda)


def locate_and_move_stems(
    processing_root: Path,
    song_name: str,
    destination: Path,
    mode: SplitMode,
) -> None:
    """Find Demucs stem directory, verify expected outputs, and move to destination."""
    stem_directory = processing_root / mode.model_name / song_name
    if not stem_directory.is_dir():
        matches = [p for p in processing_root.rglob(song_name) if p.is_dir()]
        if matches:
            stem_directory = matches[0]
        else:
            raise RuntimeError(
                f"Demucs completed without creating the expected directory: {stem_directory}"
            )

    found_files = {p.stem: p for p in stem_directory.glob("*.mp3")}

    if mode.key == "2":
        if "vocals" not in found_files or not (
            "no_vocals" in found_files or "minus_vocals" in found_files
        ):
            raise RuntimeError(
                f"Demucs did not produce expected 2-stem MP3 files. Found: {list(found_files.keys())}"
            )
    else:
        missing = [stem for stem in mode.stem_mapping.keys() if stem not in found_files]
        if missing:
            raise RuntimeError(
                f"Demucs did not produce all expected MP3 stems: {', '.join(missing)}"
            )

    destination.mkdir(parents=True, exist_ok=True)

    # Move new stems to destination
    target_filenames = set()
    for stem_name, file_path in found_files.items():
        target_name = mode.stem_mapping.get(stem_name, stem_name)
        target_file = destination / f"{target_name}.mp3"
        os.replace(file_path, target_file)
        target_filenames.add(f"{target_name}.mp3")

    # Clean up stale stem files from previous runs with different stem counts
    for existing_file in destination.glob("*.mp3"):
        if (
            existing_file.name in KNOWN_STEM_FILES
            and existing_file.name not in target_filenames
        ):
            try:
                existing_file.unlink()
            except OSError:
                pass


def run_demucs(
    audio_path: Path,
    mode: SplitMode = MODES[DEFAULT_MODE],
    output_root: Path = OUTPUT_ROOT,
) -> Path:
    """Run Demucs with the selected mode and place MP3 stems in output/<song_name>/."""
    try:
        from demucs.separate import main as demucs_main
    except ModuleNotFoundError as error:
        if error.name == "demucs":
            raise RuntimeError(
                "Demucs is not installed. Run: python -m pip install -U demucs"
            ) from error
        raise RuntimeError(
            f"Demucs could not be loaded because dependency '{error.name}' "
            "is missing. Run: python -m pip install -U demucs"
        ) from error
    except ImportError as error:
        raise RuntimeError(f"Demucs could not be loaded: {error}") from error

    device, is_cuda = select_device()
    song_name = audio_path.stem
    destination = output_root / song_name
    output_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".demucs-",
        dir=output_root,
    ) as temporary_directory:
        demucs_arguments = [
            "-n",
            mode.model_name,
            "-o",
            temporary_directory,
            "--mp3",
            "--mp3-bitrate",
            "320",
            "-d",
            device,
        ]
        if mode.demucs_args:
            demucs_arguments.extend(mode.demucs_args)
        if is_cuda:
            demucs_arguments.extend(["--segment", "7"])
        demucs_arguments.append(str(audio_path))

        print(
            f"Memproses {audio_path.name} ({mode.name}) menggunakan model {mode.model_name} di {device.upper()}..."
        )
        try:
            demucs_main(demucs_arguments)
        except SystemExit as error:
            raise RuntimeError(
                f"Demucs failed with exit code {error.code}."
            ) from error

        locate_and_move_stems(
            processing_root=Path(temporary_directory),
            song_name=song_name,
            destination=destination,
            mode=mode,
        )

    return destination


def main(argv: Sequence[str] | None = None) -> int:
    """Validate prerequisites, split the audio, and report the output path."""
    try:
        parsed = parse_arguments(argv)
        audio_path = get_audio_path(parsed.audio_file)
        mode = prompt_stem_mode(parsed.mode)
        verify_ffmpeg()
        output_directory = run_demucs(audio_path, mode=mode)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    print(f"\nStems berhasil disimpan ke: {output_directory.resolve()}")
    for stem_file in sorted(output_directory.glob("*.mp3")):
        print(f"  - {stem_file.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
