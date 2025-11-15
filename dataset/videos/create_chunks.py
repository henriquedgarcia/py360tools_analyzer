import json
import os
from pathlib import Path
from subprocess import PIPE, Popen, STDOUT
from typing import Optional

from py360tools import CMP, ERP, Projection, Tile


def run_command(cmd: str,
                folder: Path,
                log_file: Optional[Path] = None,
                ):
    if folder is not None:
        folder.mkdir(parents=True, exist_ok=True)

    stdout_lines = [cmd + '\n']
    process = Popen(cmd, shell=True, stderr=STDOUT, stdout=PIPE, encoding='UTF-8')

    print('\t', end='')
    while True:
        print('.', end='')
        stdout = process.stdout.read()
        if not stdout: break
        stdout_lines.append(stdout)
    process.wait()
    print(f' finish. \n', end='')

    if log_file is None:
        return

    log_file.write_text(''.join(stdout_lines))
    return


class Config:
    def __init__(self, file):
        self.file = Path(file)
        self.data = json.loads(self.file.read_text())

        self.video_path = self.data['video_path']
        self.name = self.data['name']
        self.projection = self.data['projection']
        self.resolution = self.data['resolution']
        self.duration = self.data['duration']
        self.fps = self.data['fps']
        self.gop = self.data['gop']
        self.rate_control = self.data['rate_control']

        self.tiling_list = self.data['tiling_list']
        self.quality_list = self.data['quality_list']

        self.shape = tuple(map(int, self.resolution.split('x')[::-1]))


class MakeChunks:
    def __init__(self, config: Config):
        self.config = config
        self.proj_types = {'erp': ERP, 'cmp': CMP}

    name: str
    projection: str
    tiling: str
    proj_obj: Projection
    tile: Tile
    quality: int
    chunk: int
    remove = False

    def run(self):
        self.name = self.config.name
        self.projection = self.config.projection
        proj = self.proj_types[self.projection]
        n_chunks = self.config.duration * self.config.fps / self.config.gop

        for self.tiling in self.config.tiling_list:
            self.proj_obj = proj(proj_res=self.config.resolution,
                                 tiling=self.tiling)
            for self.tile in self.proj_obj.tile_list:
                for self.quality in self.config.quality_list:
                    print(' | make_tile ', end='')
                    self.make_tile()

                print(' | make_dash ', end='')
                self.make_dash()

                for self.quality in self.config.quality_list:
                    for self.chunk in range(1, n_chunks + 1):
                        print(' | make_decodable ', end='')
                        self.make_decodable()

    def make_tile(self):
        if self.tile_video_is_ok():
            return
        if not self.lossless_is_ok():
            return

        cmd = self.make_tile_cmd()
        run_command(cmd=cmd, folder=self.tile_folder, log_file=self.tile_log)

    def tile_video_is_ok(self):
        try:
            compressed_file_size = self.tile_video.stat().st_size
            compressed_log_text = self.tile_log.read_text()
        except FileNotFoundError:
            return False

        if compressed_file_size == 0:
            return False
        elif 'encoded 1800 frames' not in compressed_log_text:
            return False
        elif 'encoder         : Lavc59.18.100 libx265' not in compressed_log_text:
            return False

        return True

    def lossless_is_ok(self):
        try:
            lossless_video_size = self.lossless_video.stat().st_size
        except FileNotFoundError:
            return False

        if lossless_video_size == 0:
            return False

        return True

    def make_tile_cmd(self) -> str:
        y1, x1 = self.tile.position
        y2, x2 = self.tile.position + self.tile.shape
        crop_params = f'scale={self.config.shape[1]}:{self.config.shape[0]},crop=w={x2 - x1}:h={y2 - y1}:x={x1}:y={y1}'

        gop_options = f'keyint={self.config.gop}:min-keyint={self.config.gop}:open-gop=0'
        misc_options = f':scenecut=0:info=0'
        qp_options = ':ipratio=1:pbratio=1' if self.config.rate_control == 'qp' else ''
        lossless_option = ':lossless=1' if self.quality == '0' else ''
        codec_params = f'-x265-params {gop_options}{misc_options}{qp_options}{lossless_option}'
        codec = f'-c:v libx265'
        output_options = f'-{self.config.rate_control} {self.quality} -tune psnr'

        cmd = ('bash -c '
               '"'
               'bin/ffmpeg -hide_banner -y -psnr '
               f'-i {self.lossless_video.as_posix()} '
               f'{output_options} '
               f'{codec} {codec_params} '
               f'-vf {crop_params} '
               f'{self.tile_video.as_posix()}'
               f'"')

        return cmd

    def make_dash(self):
        if self.dash_is_ok():
            return

        cmd = self._make_dash_cmd_mp4box()
        if cmd is not None:
            run_command(cmd, self.mpd_folder, self.mp4box_log)

    def dash_is_ok(self):
        try:
            segment_log_txt = self.mp4box_log.read_text()
        except FileNotFoundError:
            return False

        if f'Dashing P1 AS#1.1(V) done (60 segs)' not in segment_log_txt:
            self.mp4box_log.unlink(missing_ok=True)
            return False
        return True

    def _make_dash_cmd_mp4box(self):
        # test gop: "python3 tiled-360-streaming/bin/gop/gop_all.py"
        filename = []
        for self.quality in self.config.quality_list:
            if not self.tile_video_is_ok():
                print(f'\t{self.tile_video} is not ok')
                return None
            filename.append(self.tile_video.as_posix())

        filename_ = ' '.join(filename)

        cmd = ('bash -c '
               "'"
               'bin/MP4Box '
               '-dash 1000 -frag 1000 -rap '
               '-segment-name %s_ '
               '-profile live '
               f'-out {self.dash_mpd.as_posix()} '
               f'{filename_}'
               "'")
        return cmd

    def make_decodable(self):
        if self.decodable_is_ok():
            return
        if self.dash_is_ok_2():
            return
        cmd = self.make_decodable_cmd()
        run_command(cmd, self.mpd_folder, self.mp4box_log)

    def decodable_is_ok(self):
        try:
            chunk_size = self.decodable_chunk.stat().st_size
        except FileNotFoundError:
            return False

        if chunk_size == 0:
            return False
        return True

    def dash_is_ok_2(self):
        if not self.dash_m4s.exists():
            return False
        if not self.dash_init.exists():
            return False
        return True

    def make_decodable_cmd(self):
        cmd = (f'bash -c "cat {self.dash_init.as_posix()} {self.dash_m4s.as_posix()} '
               f'> {self.decodable_chunk.as_posix()}"')
        return cmd

    @property
    def tile_folder(self):
        return Path(f'tmp/tile/{self.name}/{self.projection}/{self.tiling}/'
                    f'tile{self.tile}/')

    @property
    def tile_video(self):
        return self.tile_folder / f'{self.config.rate_control}{self.quality}.mp4'

    @property
    def tile_log(self):
        return self.tile_folder / f'{self.config.rate_control}{self.quality}.log'

    @property
    def lossless_video(self):
        return self.config.video_path

    @property
    def mpd_folder(self):
        return Path(f'tmp/dash/{self.name}/{self.projection}/{self.tiling}/'
                    f'tile{self.tile}/')

    @property
    def mp4box_log(self):
        return self.mpd_folder.parent / f'tile{self.tile}.log'

    @property
    def dash_mpd(self):
        return self.mpd_folder / f'tile{self.tile}.mpd'

    @property
    def dash_m4s(self) -> Path:
        return self.mpd_folder / f'tile{self.tile}_{self.config.rate_control}{self.quality}_{self.chunk}.m4s'

    @property
    def dash_init(self) -> Path:
        return self.mpd_folder / f'tile{self.tile}_{self.config.rate_control}{self.quality}_init.mp4'

    @property
    def decodable_folder(self) -> Path:
        return Path(f'{self.name}/{self.projection}/{self.tiling}/'
                    f'{self.config.rate_control}{self.quality}/'
                    f'tile{self.tile}/')

    @property
    def decodable_chunk(self) -> Path:
        return self.decodable_folder / f'chunk{self.chunk}.mp4'


if __name__ == '__main__':
    path = Path(__file__).absolute().parent
    os.chdir(path)

    config_file = Path('chunk_config.json')

    cfg = Config(config_file)
    MakeChunks(cfg).run()
