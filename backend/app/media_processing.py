"""Safe derivative generation for media that has passed malware scanning."""
from __future__ import annotations
import json, shutil, subprocess
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None
MAX_PREVIEW_EDGE = 1920
IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".gif", ".heic", ".heif"}
@dataclass(frozen=True)
class DerivativeResult:
    kind: str
    source_width: int
    source_height: int
    output_width: int
    output_height: int
    source_orientation: int | None
    output_format: str
    output_path: str
def _require_clean_scan(scanner_state: str) -> None:
    if scanner_state != "clean":
        raise ValueError("Media processing is allowed only after a successful malware scan")
def _rotation_from_probe(payload: dict) -> int:
    for stream in payload.get("streams", []):
        for side_data in stream.get("side_data_list", []):
            if "rotation" in side_data:
                return int(round(float(side_data["rotation"]))) % 360
        rotate = stream.get("tags", {}).get("rotate")
        if rotate is not None:
            return int(round(float(rotate))) % 360
    return 0
def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout, shell=False)
def normalize_photo(source_path: str | Path, output_path: str | Path, *, scanner_state: str, max_edge: int = MAX_PREVIEW_EDGE) -> DerivativeResult:
    _require_clean_scan(scanner_state)
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    if source == output: raise ValueError("A derivative must never overwrite the original")
    if source.suffix.lower() not in IMAGE_FORMATS: raise ValueError("Unsupported photo extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(source) as opened:
            opened.load()
            source_width, source_height = opened.size
            exif = opened.getexif()
            orientation = int(exif.get(274, 1)) if exif else None
            oriented = ImageOps.exif_transpose(opened)
            oriented.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
            if oriented.mode not in ("RGB", "RGBA"):
                oriented = oriented.convert("RGBA" if "transparency" in oriented.info else "RGB")
            output_width, output_height = oriented.size
            oriented.save(output, format="WEBP", quality=88, method=6)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Photo cannot be safely decoded by the configured image processor") from exc
    return DerivativeResult("photo", source_width, source_height, output_width, output_height, orientation, "image/webp", str(output))
def normalize_video(source_path: str | Path, output_path: str | Path, *, scanner_state: str, ffmpeg_binary: str = "ffmpeg", ffprobe_binary: str = "ffprobe", timeout_seconds: int = 600) -> DerivativeResult:
    _require_clean_scan(scanner_state)
    source = Path(source_path).resolve(strict=True)
    output = Path(output_path).resolve()
    if source == output: raise ValueError("A derivative must never overwrite the original")
    if source.suffix.lower() not in {".mp4", ".m4v", ".mov", ".avi", ".mkv", ".webm", ".3gp"}:
        raise ValueError("Unsupported video extension")
    if shutil.which(ffmpeg_binary) is None or shutil.which(ffprobe_binary) is None:
        raise RuntimeError("FFmpeg and FFprobe must be installed on the private media worker")
    output.parent.mkdir(parents=True, exist_ok=True)
    probe = _run([ffprobe_binary, "-v", "error", "-show_streams", "-of", "json", str(source)], timeout=30)
    try: payload = json.loads(probe.stdout)
    except json.JSONDecodeError as exc: raise ValueError("FFprobe returned invalid metadata") from exc
    video_streams = [s for s in payload.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams: raise ValueError("The selected file contains no video stream")
    rotation = _rotation_from_probe({"streams": video_streams})
    _run([
        ffmpeg_binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(source), "-map", "0:v:0", "-map", "0:a?", "-map_metadata", "-1",
        "-vf", "scale=w='min(1920,iw)':h=-2:force_original_aspect_ratio=decrease",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output),
    ], timeout=timeout_seconds)
    if not output.is_file() or output.stat().st_size == 0: raise RuntimeError("FFmpeg did not produce a valid derivative")
    verify = _run([ffprobe_binary, "-v", "error", "-show_streams", "-of", "json", str(output)], timeout=30)
    verified_payload = json.loads(verify.stdout)
    verified_streams = [s for s in verified_payload.get("streams", []) if s.get("codec_type") == "video"]
    if not verified_streams or _rotation_from_probe({"streams": verified_streams}) != 0:
        output.unlink(missing_ok=True)
        raise RuntimeError("The normalized video derivative still reports a display rotation")
    width, height = int(verified_streams[0].get("width", 0)), int(verified_streams[0].get("height", 0))
    return DerivativeResult("video", 0, 0, width, height, rotation, "video/mp4", str(output))
