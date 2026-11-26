from pathlib import Path
import subprocess

import pytest
from PIL import Image

import backend.app.ai_media_worker as worker


def test_realesrgan_creates_four_times_png_without_modifying_original(tmp_path, monkeypatch):
    source = tmp_path / "family.jpg"
    output = tmp_path / "derivatives" / "family-ai.png"
    Image.new("RGB", (24, 16), (70, 100, 130)).save(source, format="JPEG")
    original = source.read_bytes()
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)
    monkeypatch.setattr(worker.shutil, "which", lambda name: "/usr/bin/realesrgan-ncnn-vulkan")

    calls = []
    def fake_run(command, timeout):
        calls.append(command)
        destination = Path(command[command.index("-o") + 1])
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (96, 64), (120, 150, 180)).save(destination, format="PNG")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(worker, "_run", fake_run)
    result = worker.restore_photo(source, output, scale=4)

    assert output.exists()
    assert result.output_mime == "image/png"
    assert result.output_width == 96 and result.output_height == 64
    assert result.engine.startswith("Real-ESRGAN NCNN Vulkan x4 + OpenCV + scikit-image")
    assert result.source_sha256 != result.output_sha256
    assert source.read_bytes() == original
    assert calls[0][calls[0].index("-s") + 1] == "4"


def test_realesrgan_fails_closed_when_worker_binary_is_missing(tmp_path, monkeypatch):
    source = tmp_path / "family.jpg"
    Image.new("RGB", (8, 8), "navy").save(source, format="JPEG")
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)
    monkeypatch.setattr(worker.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="not installed"):
        worker.restore_photo(source, tmp_path / "enhanced.png", scale=4)


def test_realesrgan_refuses_to_overwrite_original(tmp_path, monkeypatch):
    source = tmp_path / "family.jpg"
    Image.new("RGB", (8, 8), "navy").save(source, format="JPEG")
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)
    with pytest.raises(ValueError, match="overwrite the original"):
        worker.restore_photo(source, source, scale=4)
