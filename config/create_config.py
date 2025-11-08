from pathlib import Path
import json

name_list = ["cable_cam", "closet_tour", "pac_man", "sunset"]
projection_list = ['cmp', 'erp']
tiling_list = ['1x1', '3x2', '6x4', '9x6', '12x8']

for name in name_list:
    for projection in projection_list:
        for tiling in tiling_list:
            daa = {
                "video": f"{name}",
                "projection": f"{projection}",
                "tiling": f"{tiling}",
                "resolution": "360x240",
                "fov_resolution": "293x240",
                "fov": "110x90",
                "duration": 60,
                "fps": 30,
                "quality_list": ["22", "28", "34"],
                "segment_template": f"../decodable_lo/{name}/{projection}/{tiling}/" + "tile{tile}/qp{quality}/chunk{chunk}.mp4",
                "head_movement_filename": "dataset/head_movement.hd5",
            }
            file_base = Path(f"{name}_{projection}_{tiling}.json")
            file_base.write_text(json.dumps(daa, indent=4))
