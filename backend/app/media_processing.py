"""Free deterministic media enhancement. Originals are immutable inputs."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from skimage import exposure, filters, util

MAX_INPUT_BYTES = 100 * 1024 * 1024
MAX_VIDEO_SECONDS = 180
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".3gp"}


@dataclass(frozen=True)
class DerivativeResult:
    kind: str
    source_width: int
    source_height: int
    output_width: int
    output_height: int
    source_orientation: int
    output_format: str
    output_path: str
    source_sha256: str
    output_sha256: str
    source_size: int
    output_size: int
    engine: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_clean_scan(scanner_state: str) -> None:
    if scanner_state != "clean":
        raise ValueError("Media processing is allowed only after a successful malware scan")


def _assert_input(source: Path, output: Path, allowed: set[str]) -> None:
    if source.resolve() == output.resolve():
        raise ValueError("A derivative must never overwrite the original")
    if source.suffix.lower() not in allowed:
        raise ValueError("Unsupported media extension")
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("Input media is empty or missing")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Input exceeds the 100 MiB processing limit")
    if output.exists():
        raise FileExistsError(f"Derivative destination already exists: {output}")


def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout, shell=False)


def _enhance_rgb(rgb: np.ndarray) -> np.ndarray:
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("Expected an RGB image")
    if rgb.shape[0] * rgb.shape[1] > 40_000_000:
        raise ValueError("Image exceeds the safe 40 megapixel processing limit")

    # OpenCV: local contrast in LAB luminance and mild edge-preserving denoising.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    lightness = cv2.createCLAHE(clipLimit=1.35, tileGridSize=(8, 8)).apply(lightness)
    balanced = cv2.cvtColor(cv2.merge((lightness, a_channel, b_channel)), cv2.COLOR_LAB2RGB)
    denoised = cv2.bilateralFilter(balanced, 5, 22, 22)

    # scikit-image: gentle tonal normalization and restrained unsharp masking.
    normalized = util.img_as_float32(denoised)
    luminance = 0.2126 * normalized[..., 0] + 0.7152 * normalized[..., 1] + 0.0722 * normalized[..., 2]
    low, high = np.percentile(luminance, (1.0, 99.0))
    if high > low + 1e-4:
        normalized = exposure.rescale_intensity(normalized, in_range=(low, high), out_range=(0.0, 1.0))
    sharpened = filters.unsharp_mask(normalized, radius=1.0, amount=0.4, preserve_range=True, channel_axis=-1)
    sharpened = np.nan_to_num(sharpened, nan=0.0, posinf=1.0, neginf=0.0)
    return util.img_as_ubyte(np.clip(sharpened, 0.0, 1.0))


def normalize_photo(source_path: str | Path, output_path: str | Path, *, scanner_state: str) -> DerivativeResult:
    _require_clean_scan(scanner_state)
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    _assert_input(source, output, IMAGE_SUFFIXES)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash, source_size = sha256_file(source), source.stat().st_size

    try:
        with Image.open(source) as opened:
            opened.load()
            source_width, source_height = opened.size
            exif = opened.getexif()
            orientation = int(exif.get(274, 1) or 1) if exif else 1
            oriented = ImageOps.exif_transpose(opened)
            alpha = np.asarray(oriented.convert("RGBA").getchannel("A")) if "A" in oriented.getbands() else None
            rgb = np.asarray(oriented.convert("RGB"))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Pillow could not safely decode the original photo") from exc

    enhanced = _enhance_rgb(rgb)
    result_image = Image.fromarray(enhanced, mode="RGB")
    if alpha is not None:
        result_image.putalpha(Image.fromarray(alpha, mode="L"))

    temporary = output.with_name(output.name + ".partial")
    try:
        result_image.save(temporary, format="WEBP", quality=94, method=5)
        with Image.open(temporary) as check:
            check.verify()
        with Image.open(temporary) as check:
            output_width, output_height = check.size
        if (output_width, output_height) != result_image.size:
            raise RuntimeError("Photo derivative dimensions failed validation")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return DerivativeResult(
        "photo", source_width, source_height, output_width, output_height, orientation,
        "image/webp", str(output), source_hash, sha256_file(output), source_size,
        output.stat().st_size, "Pillow+OpenCV+scikit-image",
    )


def _probe_video(path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("FFprobe is required for video validation")
    result = _run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], timeout=30)
    try:
        payload = json.loads(result.stdout)
        stream = next(s for s in payload["streams"] if s.get("codec_type") == "video")
        width, height = int(stream["width"]), int(stream["height"])
        duration = float(payload.get("format", {}).get("duration", 1.0))
    except (ValueError, KeyError, StopIteration, TypeError) as exc:
        raise RuntimeError("FFprobe returned incomplete video metadata") from exc
    rotation = 0
    for side in stream.get("side_data_list", []):
        if "rotation" in side:
            rotation = int(round(float(side["rotation"]))) % 360
    if rotation in (90, 270):
        width, height = height, width
    if duration <= 0 or duration > MAX_VIDEO_SECONDS:
        raise ValueError("Video duration must be between 0 and 180 seconds")
    return {"width": width, "height": height, "duration": duration, "rotation": rotation}


def _opencv_video_pass(source: Path, output: Path, max_frames: int = 5400) -> bool:
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        capture.release()
        return False
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if width < 1 or height < 1:
        capture.release()
        raise RuntimeError("OpenCV could not read video dimensions")
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        capture.release()
        raise RuntimeError("OpenCV could not initialize video encoding")
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    count = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            y, cr, cb = cv2.split(ycrcb)
            y = clahe.apply(y)
            adjusted = cv2.cvtColor(cv2.merge((y, cr, cb)), cv2.COLOR_YCrCb2BGR)
            adjusted = cv2.bilateralFilter(adjusted, 5, 18, 18)
            blurred = cv2.GaussianBlur(adjusted, (0, 0), 1.0)
            writer.write(cv2.addWeighted(adjusted, 1.16, blurred, -0.16, 0))
            count += 1
            if count > max_frames:
                raise ValueError("Video exceeds the 5400-frame safety limit")
    finally:
        capture.release()
        writer.release()
    if count == 0:
        raise RuntimeError("OpenCV decoded no video frames")
    return True


def normalize_video(source_path: str | Path, output_path: str | Path, *, scanner_state: str) -> DerivativeResult:
    _require_clean_scan(scanner_state)
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    _assert_input(source, output, VIDEO_SUFFIXES)
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is required for video processing")
    ffmpeg = "ffmpeg"
    source_meta = _probe_video(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash, source_size = sha256_file(source), source.stat().st_size
    temporary = output.with_name(output.stem + ".partial.mp4")
    opencv_pass = output.with_name(output.stem + ".opencv-pass.mp4")
    muxed = output.with_name(output.stem + ".muxed.mp4")
    try:
        _run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
            "-i", str(source), "-map", "0:v:0", "-map", "0:a?",
            "-vf", "hqdn3d=1.2:1.2:4:4,eq=contrast=1.04:saturation=1.04,unsharp=5:5:0.35:3:3:0.0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(temporary),
        ], timeout=900)

        # OpenCV adds a separate frame-level local contrast, denoise and sharpening pass.
        try:
            if _opencv_video_pass(temporary, opencv_pass):
                _run([
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
                    "-i", str(opencv_pass), "-i", str(source),
                    "-map", "0:v:0", "-map", "1:a?",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(muxed),
                ], timeout=900)
                muxed.replace(temporary)
        finally:
            opencv_pass.unlink(missing_ok=True)
            muxed.unlink(missing_ok=True)

        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("FFmpeg did not produce a video derivative")
        output_meta = _probe_video(temporary)
        if (output_meta["width"], output_meta["height"]) != (source_meta["width"], source_meta["height"]):
            raise RuntimeError("Video dimensions failed orientation validation")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        opencv_pass.unlink(missing_ok=True)
        muxed.unlink(missing_ok=True)
        raise

    return DerivativeResult(
        "video", source_meta["width"], source_meta["height"],
        output_meta["width"], output_meta["height"], source_meta["rotation"],
        "video/mp4", str(output), source_hash, sha256_file(output),
        source_size, output.stat().st_size, "FFmpeg+OpenCV",
    )
