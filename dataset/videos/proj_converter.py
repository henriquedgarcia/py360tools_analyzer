from pathlib import Path

import numpy as np
from PIL import Image
from py360tools import CMP, ERP, ReadVideo


path: Path = Path(f'video_name.mp4')
projection: str


def parse_cmd():
    ...


def main():
    v_reader = ReadVideo(path, gray=False, dtype='int8')
    erp = ERP(proj_res='4320x2160')
    cmp = CMP(proj_res='3240x2160')

    for n, proj_frame in enumerate(v_reader):
        cmp_coord = cmp.xyz2nm(erp.xyz)

        cmp_coord.transpose((1, 2, 0))
        saida = np.zeros((200, 100))
        # import cv2
        # cv2.remap(src=proj_frame,
        #           map1=cmp_coord[1], map2=cmp_coord[0],
        #           interpolation=cv2.INTER_LINEAR,
        #           borderMode=cv2.BORDER_WRAP,
        #           dst=saida)
        vp_image = Image.fromarray(saida)
        vp_image.save(f'vp_image_frame{n}.png')


if __name__ == '__main__':
    parse_cmd()
    main()
