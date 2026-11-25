"Fail-closed AI media worker primitives. The original is never edited."
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
from .media_processing import _enhance_rgb
from dataclasses import dataclass
from pathlib import Path

MAX_INPUT_BYTES = 100 * 1024 * 1024
MAX_VIDEO_SECONDS = 180
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".3gp"}

@dataclass(frozen=True)
class WorkerResult:
    output_path: str
    output_mime: str
    source_sha256: str
    output_sha256: str
    source_size: int
    output_size: int
    engine: str
    output_width: int = 0
    output_height: int = 0

def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=True, text=True,
        timeout=timeout, shell=False, env={**os.environ, "OMP_NUM_THREADS": "1"})

def scan_or_fail(source: Path) -> None:
    scanner = shutil.which(os.getenv("CORE_CLAMDSCAN_BINARY", "clamdscan"))
    if not scanner:
        raise RuntimeError("ClamAV is not installed; refusing to process unscanned media")
    try:
        _run([scanner, "--no-summary", str(source)], timeout=120)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("ClamAV rejected the file or could not complete the scan") from exc

def _enhance_image(source: Path, output: Path, scale: int, timeout: int) -> None:
    binary = shutil.which(os.getenv("CORE_REALESRGAN_BINARY", "realesrgan-ncnn-vulkan"))
    if not binary:
        raise RuntimeError("Real-ESRGAN NCNN Vulkan worker is not installed")
    if scale not in (2, 3, 4):
        raise ValueError("Real-ESRGAN scale must be 2, 3 or 4")
    model = os.getenv("CORE_REALESRGAN_MODEL", "realesrgan-x4plus")
    _run([binary, "-i", str(source), "-o", str(output), "-n", model, "-s", str(scale)], timeout)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Real-ESRGAN did not produce an output image")

def restore_photo(source_path: str | Path, output_path: str | Path, *, scale: int = 4) -> WorkerResult:
    source, output = Path(source_path).resolve(strict=True), Path(output_path).resolve()
    if source == output: raise ValueError("Refusing to overwrite the original")
    if source.suffix.lower() not in IMAGE_SUFFIXES: raise ValueError("Unsupported image extension")
    if source.stat().st_size > MAX_INPUT_BYTES: raise ValueError("Input exceeds the 100 MiB worker limit")
    scan_or_fail(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    original_hash = sha256_file(source)
    with tempfile.TemporaryDirectory(prefix="core-ai-photo-") as temp_name:
        prepared = Path(temp_name) / "prepared.png"
        try:
            with Image.open(source) as original:
                ImageOps.exif_transpose(original).convert("RGB").save(prepared, format="PNG")
        except (OSError, ValueError) as exc:
            raise ValueError("Pillow could not decode the source photo for AI processing") from exc
        ai_output = Path(temp_name) / "realesrgan-output.png"
        _enhance_image(prepared, ai_output, scale, timeout=300)
        with Image.open(ai_output) as opened:
            opened.load()
            ai_rgb = np.asarray(ImageOps.exif_transpose(opened).convert("RGB"))
        # OpenCV + scikit-image refine local contrast, noise and edge detail
        # after neural upscaling. Pillow applies a restrained brightness/color finish.
        refined = Image.fromarray(_enhance_rgb(ai_rgb), mode="RGB")
        refined = ImageEnhance.Brightness(refined).enhance(1.04)
        refined = ImageEnhance.Color(refined).enhance(1.04)
        refined = ImageEnhance.Contrast(refined).enhance(1.03)
        refined.save(output, format="PNG")
    with Image.open(output) as enhanced:
        enhanced.load()
        width, height = enhanced.size
    return WorkerResult(str(output), "image/png", original_hash, sha256_file(output),
        source.stat().st_size, output.stat().st_size,
        f"Real-ESRGAN NCNN Vulkan x{scale} + OpenCV + scikit-image", width, height)

def restore_video(source_path: str | Path, output_path: str | Path, *, scale: int = 2) -> WorkerResult:
    source, output = Path(source_path).resolve(strict=True), Path(output_path).resolve()
    if source == output: raise ValueError("Refusing to overwrite the original")
    if source.suffix.lower() not in VIDEO_SUFFIXES: raise ValueError("Unsupported video extension")
    if source.stat().st_size > MAX_INPUT_BYTES: raise ValueError("Input exceeds the 100 MiB worker limit")
    ffmpeg = shutil.which(os.getenv("CORE_FFMPEG_BINARY", "ffmpeg"))
    ffprobe = shutil.which(os.getenv("CORE_FFPROBE_BINARY", "ffprobe"))
    if not ffmpeg or not ffprobe: raise RuntimeError("FFmpeg and FFprobe are required")
    scan_or_fail(source)
    probe = _run([ffprobe, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(source)], 30)
    try: duration = float(probe.stdout.strip())
    except ValueError as exc: raise RuntimeError("Could not determine video duration") from exc
    if duration <= 0 or duration > MAX_VIDEO_SECONDS:
        raise ValueError("Video duration must be between 0 and 180 seconds")
    output.parent.mkdir(parents=True, exist_ok=True)
    original_hash = sha256_file(source)
    with tempfile.TemporaryDirectory(prefix="core-video-restore-") as temp:
        work = Path(temp); frames = work / "frames"; enhanced = work / "enhanced"
        frames.mkdir(); enhanced.mkdir()
        _run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(source),
            "-map", "0:v:0", "-vsync", "0", str(frames / "frame-%08d.png")], 180)
        frame_list = sorted(frames.glob("frame-*.png"))
        if not frame_list or len(frame_list) > 5400:
            raise RuntimeError("Frame extraction returned no frames or exceeded the safety limit")
        for frame in frame_list: _enhance_image(frame, enhanced / frame.name, scale, 90)
        _run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-framerate", "30", "-i", str(enhanced / "frame-%08d.png"), "-i", str(source),
            "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(output)], 900)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("FFmpeg did not produce a restored video")
    dimensions = _run([ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", str(output)], 30)
    try:
        video_stream = json.loads(dimensions.stdout)["streams"][0]
        width, height = int(video_stream["width"]), int(video_stream["height"])
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Could not verify enhanced video dimensions") from exc
    return WorkerResult(str(output), "video/mp4", original_hash, sha256_file(output),
        source.stat().st_size, output.stat().st_size, f"Real-ESRGAN x{scale} + FFmpeg", width, height)
