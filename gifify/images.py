"""Image handling."""

from pathlib import Path
from urllib.parse import urlparse

import imageio
from PIL import Image
import requests

ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = ROOT_DIR / 'output'
IMAGE_DIR = OUTPUT_DIR / 'local_images'
RESIZE_DIR = OUTPUT_DIR / 'resized_images'

FRAME_SIZE = (1630, 1420)
TOP_LEFT = (0, 0)
FRAME_BOX = (0, 0, 1630, 1420)
BLACK_BG = (0, 0, 0)
COLOR_MODE = 'RGB'
DEFAULT_FRAME_DURATION = 0.8


def copy_down_images(image_urls):
    """Download images if they're not present locally."""
    IMAGE_DIR.mkdir(exist_ok=True, parents=True)
    image_index = 0
    for image_url in image_urls:
        image_index += 1
        backfill_image(image_index, image_url)


def backfill_image(image_index, image_url):
    """Check if the file exists locally, otherwise download it."""
    local_path = build_local_path(image_index, image_url)
    if local_path.is_file():
        print(f'IMAGES: {local_path} found locally')
        return
    download_image(image_url, local_path)
    print(f'IMAGES: {local_path} saved')


def build_local_path(image_index, image_url):
    """Build local path from URL."""
    imgur_id = urlparse(image_url).path[1:].split('.')[0]
    return IMAGE_DIR / f'{image_index:05d}-{imgur_id}.png'


def download_image(url: str, local_path: Path):
    """Download remote url to local path."""
    image_data = requests.get(url).content
    try:
        Path(local_path).write_bytes(image_data)
    except Exception as e:
        local_path.unlink(missing_ok=True)
        raise e


def assemble_gif():
    """Assemble gif from local PNGs."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_filepath = OUTPUT_DIR / 'movie.gif'
    output_filepath.unlink(missing_ok=True)
    image_files = sorted(RESIZE_DIR.glob('*.png'))
    opts = {
        'mode': 'I',
        'duration': build_duration_arg(image_files)
    }
    with imageio.get_writer(output_filepath, **opts) as writer:
        write_gif(writer, image_files)
    file_size = convert_bytes(output_filepath.stat().st_size)
    print(f'IMAGES: Created output file {output_filepath} ({file_size})')


def convert_bytes(byte_count):
    """Convert bytes to human readable formats."""
    unit_size = 1024.0
    for unit in ('bytes', 'kb', 'mb', 'gb', 'tb'):
        if byte_count < unit_size:
            return "%3.1f %s" % (byte_count, unit)
        byte_count /= unit_size

def build_duration_arg(image_files):
    """Build list of durations for frames."""
    durations = []
    custom_durations = get_custom_durations()
    for i in range(0, len(image_files)):
        image_frame = i + 1
        duration = DEFAULT_FRAME_DURATION
        if image_frame in custom_durations:
            duration = custom_durations[image_frame]
        durations.append(duration)
    return durations


def get_custom_durations():
    """Get custom durations from config file."""
    durations = {}
    with open(ROOT_DIR / 'frame-durations.txt', 'r') as f:
        for line in f:
            sanitized_line = line.strip()
            if sanitized_line == '' or sanitized_line.startswith('#'):
                continue
            line_pieces = sanitized_line.split(',')
            assert len(line_pieces) == 2, line_pieces
            frame_index = int(line_pieces[0].strip())
            timing = float(line_pieces[1].strip())
            durations.update({frame_index: timing})
    return durations


def write_gif(writer, image_files):
    """Write gif file."""
    for filename in image_files:
        image = imageio.imread(filename)
        writer.append_data(image)


def resize_images():
    """Resize images into same shape."""
    RESIZE_DIR.mkdir(exist_ok=True, parents=True)
    for filename in IMAGE_DIR.glob('*.png'):
        resized_image = RESIZE_DIR / filename.name
        if resized_image.exists():
            print(f'IMAGES: Resized {resized_image} exists')
            continue
        replacement = get_normalized_image(filename)
        replacement.save(resized_image)
        print(f'IMAGES: Saved resized {resized_image}')


def get_normalized_image(filename):
    """Get normalized image."""
    image = Image.open(filename)
    if image.mode == COLOR_MODE and image.size == FRAME_SIZE:  # desired
        return image
    replacement = get_rgb_image(image)
    if replacement.size == FRAME_SIZE:
        return replacement
    if replacement.size == (1631, 1420):  # crop 1 pixel width
        return replacement.crop(FRAME_BOX)
    if replacement.size == (1630, 1418):  # pad 2 pixels height
        tmp = Image.new(COLOR_MODE, FRAME_SIZE, BLACK_BG)
        tmp.paste(replacement, TOP_LEFT)
        return tmp
    if replacement.size == (816, 710):  # double size, crop 2 pixels width
        return replacement.resize((1632, 1420)).crop(FRAME_BOX)
    raise Exception(
        'Unexpected image type:'
        f' {image.mode} {image.size} '
        f'for {filename}'
    )


def get_rgb_image(image):
    """Get RGB image."""
    if image.mode == COLOR_MODE:
        return image
    image.load()
    replacement = Image.new(COLOR_MODE, image.size, BLACK_BG)
    replacement.paste(image, TOP_LEFT, mask=image.split()[3])
    return replacement
