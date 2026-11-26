import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image
import pytest

import backend.app.ai_media_worker as worker


def test_photo_strength_changes_the_saved_derivative(tmp_path, monkeypatch):
    source = tmp_path / "family.jpg"
    Image.new("RGB", (16, 12), (80, 100, 120)).save(source, format="JPEG")
    original = source.read_bytes()
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)
    monkeypatch.setattr(worker.shutil, "which", lambda name: "/usr/bin/realesrgan-ncnn-vulkan")
    monkeypatch.setattr(worker, "_enhance_rgb", lambda rgb: rgb)

    def fake_run(command, timeout):
        destination = Path(command[command.index("-o") + 1])
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32, 24), (80, 100, 120)).save(destination, format="PNG")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(worker, "_run", fake_run)
    low = tmp_path / "low.png"
    high = tmp_path / "high.png"
    worker.restore_photo(source, low, scale=2, strength=0)
    worker.restore_photo(source, high, scale=2, strength=100)

    assert low.read_bytes() != high.read_bytes()
    assert source.read_bytes() == original


def test_video_worker_applies_trim_crop_strength_and_audio_filters(tmp_path, monkeypatch):
    source = tmp_path / "family.mp4"
    source.write_bytes(b"test-video-source")
    output = tmp_path / "derivatives" / "family-enhanced.mp4"
    binaries = {
        "ffmpeg": "/usr/bin/ffmpeg",
        "ffprobe": "/usr/bin/ffprobe",
        "realesrgan-ncnn-vulkan": "/usr/bin/realesrgan-ncnn-vulkan",
    }
    monkeypatch.setattr(worker.shutil, "which", lambda name: binaries.get(name))
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)
    calls = []

    def fake_run(command, timeout):
        calls.append(command)
        if command[0] == binaries["ffprobe"]:
            if "-select_streams" in command:
                payload = {"streams": [{"width": 640, "height": 480}]}
            else:
                payload = {
                    "format": {"duration": "10.0"},
                    "streams": [
                        {"codec_type": "video", "avg_frame_rate": "30/1", "width": 640, "height": 480},
                        {"codec_type": "audio"},
                    ],
                }
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")
        if "-fps_mode" in command:
            pattern = Path(command[-1])
            frame = pattern.with_name("frame-00000001.png")
            Image.new("RGB", (320, 240), (90, 110, 130)).save(frame, format="PNG")
        else:
            destination = Path(command[-1])
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"encoded-video")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(worker, "_run", fake_run)
    monkeypatch.setattr(
        worker, "_enhance_image",
        lambda source_frame, output_frame, scale, timeout: shutil.copyfile(source_frame, output_frame),
    )

    original = source.read_bytes()
    result = worker.restore_video(
        source, output, scale=2, strength=80,
        start_seconds=2, end_seconds=7,
        crop_x=10, crop_y=20, crop_width=320, crop_height=240,
        enhance_audio=True,
    )

    extract = next(command for command in calls if "-fps_mode" in command)
    encode = next(command for command in calls if command[0] == binaries["ffmpeg"] and "-fps_mode" not in command)
    assert extract[extract.index("-ss") + 1] == "2.0"
    assert extract[extract.index("-t") + 1] == "5.0"
    assert extract[extract.index("-vf") + 1] == "crop=320:240:10:20"
    assert "-af" in encode and "afftdn" in encode[encode.index("-af") + 1]
    assert result.engine.find("strength 80%") >= 0
    assert output.read_bytes() == b"encoded-video"
    assert source.read_bytes() == original


def test_video_worker_rejects_crop_outside_source(tmp_path, monkeypatch):
    source = tmp_path / "family.mp4"
    source.write_bytes(b"test-video-source")
    monkeypatch.setattr(worker.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(worker, "scan_or_fail", lambda path: None)

    def fake_run(command, timeout):
        payload = {
            "format": {"duration": "10.0"},
            "streams": [{"codec_type": "video", "avg_frame_rate": "30/1", "width": 640, "height": 480}],
        }
        return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

    monkeypatch.setattr(worker, "_run", fake_run)
    with pytest.raises(ValueError, match="outside the source video"):
        worker.restore_video(
            source, tmp_path / "out.mp4",
            crop_x=600, crop_y=0, crop_width=80, crop_height=100,
        )


def test_audio_filter_uses_neural_rnnoise_when_model_is_configured(tmp_path, monkeypatch):
    model = tmp_path / "rnnoise-model.rnnn"
    model.write_bytes(b"test-model-placeholder")
    monkeypatch.setenv("CORE_RNNOISE_MODEL", str(model))

    audio_filter, label = worker._build_audio_filter(has_audio=True, enhance_audio=True)

    assert "arnndn=m=" in audio_filter
    assert str(model) in audio_filter
    assert "RNNoise neural" in label


def test_audio_filter_fails_closed_when_configured_model_is_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("CORE_RNNOISE_MODEL", str(tmp_path / "missing.rnnn"))
    with pytest.raises(RuntimeError, match="RNNoise model file is missing"):
        worker._build_audio_filter(has_audio=True, enhance_audio=True)
