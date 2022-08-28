# Imgur gifify

Builds an animate gif from imgur user GrateArtiste's 2022 serial.

## Processing Steps

Running `make run` will:

- Call the imgur API to get a list of recent posts from GrateArtiste's account starting from the newest and going back until the cutoff date of 2021/12/31.
- For each image in the list, it will check if the file exists locally, and if not it will download it. Downloaded image filenames are the imgur image ID prefixed with the index of the image in the serial.
- Each downloaded image is reformatted to fit a standard file type. RGBA images are converted to RGB and images with non-standard dimensions are resized/cropped.
- The reformatted images are combined into an animated gif, with each frame defaulting to a specific duration. Custom frame durations are set to help the pacing of the animation and so people have time to read frames with lots of text.

## Usage

```sh

# install dependencies
make install

# run locally
make run

# clean artifacts
make clean

# lint
make lint

```
