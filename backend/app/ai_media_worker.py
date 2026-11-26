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

def restore_photo(source_path: str | Path, output_path: str | Path, *, scale: int = 4, strength: int = 65) -> WorkerResult:
    source, output = Path(source_path).resolve(strict=True), Path(output_path).resolve()
    if source == output: raise ValueError("Refusing to overwrite the original")
    if source.suffix.lower() not in IMAGE_SUFFIXES: raise ValueError("Unsupported image extension")
    if source.stat().st_size > MAX_INPUT_BYTES: raise ValueError("Input exceeds the 100 MiB worker limit")
    if not 0 <= int(strength) <= 100: raise ValueError("Enhancement strength must be between 0 and 100")
    scan_or_fail(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    original_hash = sha256_file(source)
    factor = int(strength) / 100.0
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
        # Neural upscaling is followed by deterministic finishing whose strength
        # is controlled by the user's slider and affects the exported file.
        refined = Image.fromarray(_enhance_rgb(ai_rgb), mode="RGB")
        refined = ImageEnhance.Brightness(refined).enhance(1.0 + 0.035 * factor)
        refined = ImageEnhance.Color(refined).enhance(1.0 + 0.10 * factor)
        refined = ImageEnhance.Contrast(refined).enhance(1.0 + 0.08 * factor)
        refined = ImageEnhance.Sharpness(refined).enhance(1.0 + 0.25 * factor)
        refined.save(output, format="PNG")
    with Image.open(output) as enhanced:
        enhanced.load()
        width, height = enhanced.size
    return WorkerResult(str(output), "image/png", original_hash, sha256_file(output),
        source.stat().st_size, output.stat().st_size,
        f"Real-ESRGAN NCNN Vulkan x{scale} + OpenCV + scikit-image · strength {strength}%", width, height)

def _build_audio_filter(has_audio: bool, enhance_audio: bool) -> tuple[str, str]:
    if not has_audio or not enhance_audio:
        return "", ""
    model_setting = os.getenv("CORE_RNNOISE_MODEL", "").strip()
    if model_setting:
        model_path = Path(model_setting).expanduser().resolve()
        if not model_path.is_file():
            raise RuntimeError("Configured RNNoise model file is missing")
        return (
            f"arnndn=m={model_path},highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11",
            " + RNNoise neural noise reduction + loudness normalization",
        )
    return (
        "highpass=f=70,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11",
        " + FFmpeg DSP noise reduction + loudness normalization (RNNoise model not configured)",
    )


def restore_video(
    source_path: str | Path,
    output_path: str | Path,
    *,
    scale: int = 2,
    strength: int = 65,
    start_seconds: float = 0.0,
    end_seconds: float | None = None,
    crop_x: int | None = None,
    crop_y: int | None = None,
    crop_width: int | None = None,
    crop_height: int | None = None,
    enhance_audio: bool = True,
) -> WorkerResult:
    source, output = Path(source_path).resolve(strict=True), Path(output_path).resolve()
    if source == output: raise ValueError("Refusing to overwrite the original")
    if source.suffix.lower() not in VIDEO_SUFFIXES: raise ValueError("Unsupported video extension")
    if source.stat().st_size > MAX_INPUT_BYTES: raise ValueError("Input exceeds the 100 MiB worker limit")
    if scale not in (2, 3, 4): raise ValueError("Video AI scale must be 2, 3 or 4")
    if not 0 <= int(strength) <= 100: raise ValueError("Enhancement strength must be between 0 and 100")
    ffmpeg = shutil.which(os.getenv("CORE_FFMPEG_BINARY", "ffmpeg"))
    ffprobe = shutil.which(os.getenv("CORE_FFPROBE_BINARY", "ffprobe"))
    if not ffmpeg or not ffprobe: raise RuntimeError("FFmpeg and FFprobe are required")
    scan_or_fail(source)
    probe = _run([ffprobe, "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,avg_frame_rate,width,height",
        "-of", "json", str(source)], 30)
    try:
        metadata = json.loads(probe.stdout)
        duration = float(metadata.get("format", {}).get("duration", 0))
        video_stream = next(item for item in metadata["streams"] if item.get("codec_type") == "video")
        rate = str(video_stream.get("avg_frame_rate") or "30/1")
        numerator, denominator = rate.split("/", 1)
        fps = float(numerator) / max(1.0, float(denominator))
        has_audio = any(item.get("codec_type") == "audio" for item in metadata["streams"])
    except (ValueError, KeyError, StopIteration, TypeError, ZeroDivisionError) as exc:
        raise RuntimeError("Could not determine video duration, frame rate or streams") from exc
    if duration <= 0 or duration > MAX_VIDEO_SECONDS:
        raise ValueError("Video duration must be between 0 and 180 seconds")
    start = float(start_seconds)
    end = duration if end_seconds is None else float(end_seconds)
    if start < 0 or end <= start or end > duration:
        raise ValueError("Trim range must be inside the source video and have positive duration")
    segment_duration = end - start
    crop_values = (crop_x, crop_y, crop_width, crop_height)
    if any(value is not None for value in crop_values):
        if any(value is None for value in crop_values):
            raise ValueError("All four crop values are required together")
        x, y, width, height = (int(value) for value in crop_values)
        source_width = int(video_stream.get("width", 0))
        source_height = int(video_stream.get("height", 0))
        if x < 0 or y < 0 or width < 2 or height < 2 or x + width > source_width or y + height > source_height:
            raise ValueError("Crop rectangle is outside the source video")
        if width % 2 or height % 2:
            raise ValueError("Crop width and height must be even for MP4 export")
        crop_filter = f"crop={width}:{height}:{x}:{y}"
    else:
        crop_filter = ""
    output.parent.mkdir(parents=True, exist_ok=True)
    original_hash = sha256_file(source)
    fps = min(60.0, max(1.0, fps))
    fps_arg = f"{fps:.6f}".rstrip("0").rstrip(".")
    factor = int(strength) / 100.0
    contrast = 1.0 + 0.16 * factor
    saturation = 1.0 + 0.14 * factor
    brightness = 0.025 * factor
    sharpen = 0.65 * factor
    video_finish = f"eq=contrast={contrast:.4f}:saturation={saturation:.4f}:brightness={brightness:.4f},unsharp=5:5:{sharpen:.4f}:3:3:0.0"
    audio_filter, audio_label = _build_audio_filter(has_audio, enhance_audio)
    with tempfile.TemporaryDirectory(prefix="core-video-restore-") as temp:
        work = Path(temp); frames = work / "frames"; enhanced = work / "enhanced"
        frames.mkdir(); enhanced.mkdir()
        extract = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
            "-ss", str(start), "-t", str(segment_duration), "-i", str(source),
            "-map", "0:v:0"]
        if crop_filter:
            extract += ["-vf", crop_filter]
        extract += ["-fps_mode", "passthrough", str(frames / "frame-%08d.png")]
        _run(extract, 300)
        frame_list = sorted(frames.glob("frame-*.png"))
        if not frame_list or len(frame_list) > 5400:
            raise RuntimeError("Frame extraction returned no frames or exceeded the safety limit")
        for frame in frame_list:
            _enhance_image(frame, enhanced / frame.name, scale, timeout=90)
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
            "-framerate", fps_arg, "-i", str(enhanced / "frame-%08d.png"),
            "-ss", str(start), "-t", str(segment_duration), "-i", str(source),
            "-map", "0:v:0", "-map", "1:a?", "-vf", video_finish,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]
        if has_audio and enhance_audio:
            command += ["-af", audio_filter]
        command += ["-shortest", "-movflags", "+faststart", str(output)]
        _run(command, 900)
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
        source.stat().st_size, output.stat().st_size,
        f"Real-ESRGAN NCNN Vulkan x{scale} + FFmpeg · strength {strength}%{audio_label}", width, height)
