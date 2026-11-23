from pathlib import Path
import json, subprocess
import pytest
from PIL import Image
from backend.app.media_processing import normalize_photo, normalize_video
@pytest.mark.parametrize("orientation,expected_size", [
    (1, (40, 20)), (2, (40, 20)), (3, (40, 20)), (4, (40, 20)),
    (5, (20, 40)), (6, (20, 40)), (7, (20, 40)), (8, (20, 40)),
])
def test_all_exif_orientations_create_correct_derivative_without_changing_original(tmp_path, orientation, expected_size):
    source = tmp_path / f"phone-photo-{orientation}.jpg"
    output = tmp_path / "derivatives" / f"phone-photo-{orientation}.webp"
    image = Image.new("RGB", (40, 20), "red")
    exif = image.getexif()
    exif[274] = orientation
    image.save(source, format="JPEG", exif=exif)
    original = source.read_bytes()
    result = normalize_photo(source, output, scanner_state="clean")
    assert result.source_orientation == orientation
    assert (result.source_width, result.source_height) == (40, 20)
    assert (result.output_width, result.output_height) == expected_size
    assert result.output_format == "image/webp"
    assert output.is_file() and source.read_bytes() == original
    with Image.open(output) as preview:
        assert preview.size == expected_size
        assert preview.getexif().get(274) is None

def test_photo_processing_refuses_quarantined_file(tmp_path):
    source=tmp_path/"photo.jpg"; source.write_bytes(b"not decoded")
    with pytest.raises(ValueError,match="successful malware scan"):
        normalize_photo(source,tmp_path/"preview.webp",scanner_state="quarantined")
def test_video_processing_refuses_quarantined_file(tmp_path):
    source=tmp_path/"video.mov"; source.write_bytes(b"untrusted")
    with pytest.raises(ValueError,match="successful malware scan"):
        normalize_video(source,tmp_path/"preview.mp4",scanner_state="quarantined")
def test_video_processor_uses_ffmpeg_autorotation_and_verifies_derivative(tmp_path,monkeypatch):
    import backend.app.media_processing as processor
    source=tmp_path/"phone-video.mov"; output=tmp_path/"derivatives"/"phone-video.mp4"
    source.write_bytes(b"test-video")
    monkeypatch.setattr(processor.shutil,"which",lambda _:"/usr/bin/fake-media-tool")
    calls=[]
    def fake_run(command,**kwargs):
        calls.append(command)
        if command[0]=="ffmpeg":
            Path(command[-1]).parent.mkdir(parents=True,exist_ok=True)
            Path(command[-1]).write_bytes(b"normalized-video")
            return subprocess.CompletedProcess(command,0,"","")
        if str(source) in command:
            payload={"streams":[{"codec_type":"video","width":1920,"height":1080,"side_data_list":[{"rotation":90}]}]}
        else:
            payload={"streams":[{"codec_type":"video","width":1080,"height":1920,"side_data_list":[{"rotation":0}]}]}
        return subprocess.CompletedProcess(command,0,json.dumps(payload),"")
    monkeypatch.setattr(processor,"_run",fake_run)
    result=normalize_video(source,output,scanner_state="clean")
    ffmpeg_call=next(call for call in calls if call[0]=="ffmpeg")
    assert "-noautorotate" not in ffmpeg_call and "libx264" in ffmpeg_call
    assert result.source_orientation==90 and (result.output_width,result.output_height)==(1080,1920)
    assert result.output_format=="video/mp4" and output.read_bytes()==b"normalized-video"
    assert source.read_bytes()==b"test-video"
