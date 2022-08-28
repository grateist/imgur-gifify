"""Collect user's posts into a gif."""

from gifify import images
from gifify import imgur_api

if __name__ == '__main__':
    print('STATUS: Fetching list of image links from API')
    image_urls = imgur_api.fetch_all_image_links()
    print('STATUS: Saving images locally')
    images.copy_down_images(image_urls)
    print('STATUS: Resizing images')
    images.resize_images()
    print('STATUS: Assembling gif')
    images.assemble_gif()
