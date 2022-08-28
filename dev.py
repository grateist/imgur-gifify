"""Dev."""

from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    from gifify import images
    images.assemble_gif()
