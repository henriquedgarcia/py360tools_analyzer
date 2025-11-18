from pathlib import Path
import json

name_list = ["cable_cam", "closet_tour", "pac_man", "sunset"]
projection_list = ['cmp', 'erp']
tiling_list = ['1x1', '3x2', '6x4', '9x6', '12x8']
quality_list = ["22", "28", "34"]

for name in name_list:
    for projection in projection_list:
        daa = {
            "video_list": [f"{name}"],
            "projection_list": [f"{projection}"],
            "tiling_list": f"{tiling_list}",
            "quality_list": f"{quality_list}",
            "rate_control": "qp",
            "resolution": "360x240",
            "fov_resolution": "293x240",
            "fov": "110x90",
            "duration": 60,
            "fps": 30,
            "gop": 30,
            "segment_template": "../decodable_lo/{name}/{projection}/{tiling}/tile{tile}/{rate_control}{quality}/chunk{chunk}.mp4",
            "head_movement_filename": "dataset/head_movement.hd5",
        }
        file_base = Path(f"{name}_{projection}.json")
        file_base.write_text(json.dumps(daa, indent=4))
