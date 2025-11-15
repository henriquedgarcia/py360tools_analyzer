from py360tools import ERP, CMP, Viewport, TileStitcher, ReadVideo
from pathlib import Path
from PIL import Image

path: Path = Path(f'video_name.mp4')
projection: str

def parse_cmd():

def main():
    v_reader = ReadVideo(path, gray=False, dtype='int8')
    cmp = CMP(proj_res='4320x2160', tiling='3x2')
    if projection == 'erp':
        proj_obj = ERP(proj_res='4320x2160', tiling='1x1')
    elif projection == 'cmp':
            proj_obj = CMP(proj_res='3240x2160', tiling='1x1')
    else:
        raise ValueError('Invalid projection type')

    proj_obj.tile_list[0].path = path
    TileStitcher()

    stitcher = TileStitcher(vptiles, erp)
    for n, proj_frame in enumerate(stitcher):
        viewport = vp.extract_viewport(proj_frame)
        vp_image = Image.fromarray(viewport)
        vp_image.save(f'vp_image_frame{n}.png')


if __name__ == '__main__':
    parse_cmd()
    main()