"""Deterministic, non-generative media enhancement pipeline.

Originals are read-only inputs. Every output is written to a distinct path,
validated, and returned with source/output metadata for archive registration.
"""
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
from skimage import exposure, filters, restoration, util

MAX_INPUT_BYTES = 100 * 1024 * 1024
MAX_VIDEO_SECONDS = 180
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".3gp"}


@dataclass(frozen=True)
class MediaResult:
    output_path: str
    source_sha256: str
    output_sha256: str
    source_size: int
    output_size: int
    source_width: int
    source_height: int
    output_width: int
    output_height: int
    source_orientation: int
    output_format: str
    engine: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_input(source: Path, output: Path, suffixes: set[str]) -> None:
    if source.resolve() == output.resolve():
        raise ValueError("The original file must never be overwritten")
    if source.suffix.lower() not in suffixes:
        raise ValueError("Unsupported media extension")
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError("Input media is empty or missing")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Input exceeds the 100 MiB processing limit")
    if output.exists():
        raise FileExistsError(f"Derivative destination already exists: {output}")


def _require_clean(scanner_state: str) -> None:
    if scanner_state != "clean":
        raise ValueError("A successful malware scan is required before processing")


def _enhance_rgb(rgb: np.ndarray) -> np.ndarray:
    """Gentle CLAHE, bilateral denoising and restrained unsharp masking."""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("Expected an RGB image")
    if rgb.shape[0] * rgb.shape[1] > 40_000_000:
        raise ValueError("Image exceeds the safe 40 megapixel processing limit")

    # OpenCV: adaptive local contrast in LAB luminance, without shifting hues.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.35, tileGridSize=(8, 8))
    lightness = clahe.apply(lightness)
    lab = cv2.merge((lightness, a_channel, b_channel))
    balanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    # OpenCV: mild denoising. Keep fine details; do not invent texture.
    denoised = cv2.bilateralFilter(balanced, d=5, sigmaColor=22, sigmaSpace=22)

    # scikit-image: restrained local contrast and detail recovery.
    normalized = util.img_as_float32(denoised)
    luminance = 0.2126 * normalized[..., 0] + 0.7152 * normalized[..., 1] + 0.0722 * normalized[..., 2]
    p_low, p_high = np.percentile(luminance, (1.0, 99.0))
    if p_high > p_low + 1e-4:
        normalized = exposure.rescale_intensity(normalized, in_range=(p_low, p_high), out_range=(0.0, 1.0))
    sharpened = filters.unsharp_mask(normalized, radius=1.0, amount=0.45, preserve_range=True, channel_axis=-1)
    sharpened = np.clip(sharpened, 0.0, 1.0)
    return util.img_as_ubyte(sharpened)


def normalize_photo(source_path: str | Path, output_path: str | Path, *, scanner_state: str) -> MediaResult:
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    _assert_input(source, output, IMAGE_SUFFIXES)
    _require_clean(scanner_state)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    source_size = source.stat().st_size

    try:
        with Image.open(source) as opened:
            orientation = int(opened.getexif().get(274, 1) or 1)
            original_width, original_height = opened.size
            oriented = ImageOps.exif_transpose(opened)
            has_alpha = "A" in oriented.getbands()
            if has_alpha:
                rgba = oriented.convert("RGBA")
                alpha = np.asarray(rgba.getchannel("A"))
                rgb = np.asarray(rgba.convert("RGB"))
            else:
                alpha = None
                rgb = np.asarray(oriented.convert("RGB"))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Pillow could not decode the original image") from exc

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
            if (output_width, output_height) != (result_image.width, result_image.height):
                raise RuntimeError("Derivative dimensions failed validation")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return MediaResult(
        output_path=str(output),
        source_sha256=source_hash,
        output_sha256=sha256_file(output),
        source_size=source_size,
        output_size=output.stat().st_size,
        source_width=original_width,
        source_height=original_height,
        output_width=output_width,
        output_height=output_height,
        source_orientation=orientation,
        output_format="image/webp",
        engine="Pillow+OpenCV+scikit-image",
    )


def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        command, check=True, capture_output=True, text=True,
        timeout=timeout, shell=False,
    )


def _probe_video(path: Path) -> dict:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("FFprobe is required for safe video processing")
    result = _run([
        ffprobe, "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ], 30)
    try:
        payload = json.loads(result.stdout)
        stream = next(item for item in payload["streams"] if item.get("codec_type") == "video")
        width, height = int(stream["width"]), int(stream["height"])
        duration = float(payload.get("format", {}).get("duration", 0))
    except (ValueError, KeyError, StopIteration, TypeError) as exc:
        raise RuntimeError("FFprobe returned incomplete video metadata") from exc
    rotation = 0
    for side_data in stream.get("side_data_list", []):
        if "rotation" in side_data:
            rotation = int(round(float(side_data["rotation"]))) % 360
    if rotation in (90, 270):
        width, height = height, width
    if duration <= 0 or duration > MAX_VIDEO_SECONDS:
        raise ValueError("Video duration must be between 0 and 180 seconds")
    return {"width": width, "height": height, "duration": duration, "rotation": rotation}


def normalize_video(source_path: str | Path, output_path: str | Path, *, scanner_state: str) -> MediaResult:
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    _assert_input(source, output, VIDEO_SUFFIXES)
    _require_clean(scanner_state)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for video processing")
    source_meta = _probe_video(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    source_size = source.stat().st_size
    temporary = output.with_name(output.stem + ".partial.mp4")
    # FFmpeg autorotation is intentionally enabled. Denoising, restrained
    # contrast and unsharp filters operate on decoded frames; original audio
    # is mapped separately and re-encoded without touching the source.
    try:
        _run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
            "-i", str(source),
            "-map", "0:v:0", "-map", "0:a?",
            "-vf", "hqdn3d=1.2:1.2:4:4,eq=contrast=1.04:saturation=1.04,unsharp=5:5:0.35:3:3:0.0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(temporary),
        ], 900)
        output_meta = _probe_video(temporary)
        if (output_meta["width"], output_meta["height"]) != (source_meta["width"], source_meta["height"]):
            raise RuntimeError("Processed video dimensions do not match the orientation-corrected source")
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("FFmpeg produced an empty video derivative")
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return MediaResult(
        output_path=str(output),
        source_sha256=source_hash,
        output_sha256=sha256_file(output),
        source_size=source_size,
        output_size=output.stat().st_size,
        source_width=source_meta["width"],
        source_height=source_meta["height"],
        output_width=output_meta["width"],
        output_height=output_meta["height"],
        source_orientation=source_meta["rotation"],
        output_format="video/mp4",
        engine="FFmpeg+OpenCV-compatible filters",
    )
