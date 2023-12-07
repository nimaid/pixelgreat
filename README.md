# pixelgreat
A highly realistic RGB pixel filter for Python.

## Installation
First, install Python 3. Then run this command:
```commandline
pip install pixelgreat
```

## Command Line Usage
The command to convert a single image is `pixelgreat`:
```
usage: pixelgreat [-h] -i IMAGE_IN -o IMAGE_OUT -s PIXEL_SIZE [-os OUTPUT_SCALE] [-t SCREEN_TYPE]
                  [-d DIRECTION] [-a PIXEL_ASPECT] [-npx] [-b BLUR_AMOUNT] [-w WASHOUT]
                  [-sst SCANLINE_STRENGTH] [-ssp SCANLINE_SPACING] [-ssz SCANLINE_SIZE]
                  [-sb SCANLINE_BLUR] [-gst GRID_STRENGTH] [-p PADDING] [-r ROUNDING]
                  [-bst BLOOM_STRENGTH] [-bsz BLOOM_SIZE]

A highly realistic RGB pixel filter

Valid values are shown in {braces}
Default values are shown in [brackets]

options:
  -h, --help            show this help message and exit
  -i IMAGE_IN, --input IMAGE_IN
                        the image to convert
  -o IMAGE_OUT, --output IMAGE_OUT
                        where to save the converted image, and what filetype to save it as
  -s PIXEL_SIZE, --size PIXEL_SIZE
                        the size of the pixels {3 - no limit}
  -os OUTPUT_SCALE, --output-scale OUTPUT_SCALE
                        How much to scale the output size by {no limits, 1.0 is no scaling, 2.0 is
                        2x size} [1.0]
  -t SCREEN_TYPE, --type SCREEN_TYPE
                        the type of RGB filter to apply {LCD, CRT_TV, CRT_MONITOR} [LCD]
  -d DIRECTION, --direction DIRECTION
                        the direction of the RGB filter {V, H} [varies w/ screen type]
  -a PIXEL_ASPECT, --aspect PIXEL_ASPECT
                        the aspect ratio of the pixels, width / height {0.33 - 3.0} [1.0]
  -npx, --no-pixelate   if given, the image will not be pixelated, but the other filters will still
                        be applied
  -b BLUR_AMOUNT, --blur BLUR_AMOUNT
                        how much to blur the source image {0.0 - 1.0} [varies w/ screen type]
  -w WASHOUT, --washout WASHOUT
                        how much to brighten dark pixels {0.0 - 1.0} [varies w/ screen type]
  -sst SCANLINE_STRENGTH, --scanline-strength SCANLINE_STRENGTH
                        the strength of the CRT scanline filter {0.0 - 1.0} [varies w/ screen type]
  -ssp SCANLINE_SPACING, --scanline-spacing SCANLINE_SPACING
                        how far apart to space the CRT scanlines {0.33 - 3.0} [0.79]
  -ssz SCANLINE_SIZE, --scanline-size SCANLINE_SIZE
                        how wide the CRT scanlines are {0.0 - 1.0} [0.75]
  -sb SCANLINE_BLUR, --scanline-blur SCANLINE_BLUR
                        how much blur to apply to the CRT scanline filter {0.0 - 1.0} [0.25]
  -gst GRID_STRENGTH, --grid-strength GRID_STRENGTH
                        the strength of the RGB pixel grid filter {0.0 - 1.0} [1.0]
  -p PADDING, --padding PADDING
                        how much black padding to add around the pixels {0.0 - 1.0} [varies w/
                        screen type]
  -r ROUNDING, --rounding ROUNDING
                        how much to round the corners of the pixels {0.0 - 1.0} [varies w/ screen
                        type]
  -bst BLOOM_STRENGTH, --bloom-strength BLOOM_STRENGTH
                        the amount of bloom to add to the output image {0.0 - 1.0} [1.0]
  -bsz BLOOM_SIZE, --bloom-size BLOOM_SIZE
                        the size of the bloom added to the output image {0.0 - 1.0} [0.5]
```

Currently, there is no support for image sequences through the command line. However, this feature is planned.

## Usage In Custom Code

You can also import the module into your project.

Here is a short example script that opens a single image, applies the default settings at 4x scale, and saves the result:
```python
from PIL import Image
import pixelgreat as pg

# Open the image
image_in = Image.open("image.png")

# Call a single-use command to convert the image (slow)
image_out = pg.pixelgreat(
    image=image_in,
    pixel_size=20,
    output_scale=4
)

# Save the image
image_out.save("pixelated.png")

# Close the images
image_in.close()
image_out.close()
```

If you want to process multiple images using the same settings and output size each time, make a reusable object, like so:
```python
from PIL import Image
import pixelgreat as pg

image_names = ["image1.png", "image2.png", "image3.png"]

# Get the size of the first image
first_image = Image.open(image_names[0])
first_image_size = first_image.size
first_image.close()

# Scale it up by 4x to get the output size
output_size = (
    round(first_image_size[0] * 4),
    round(first_image_size[1] * 4),
)

# Make the re-usable converter object just once (slow)
converter = pg.Pixelgreat(
    output_size=first_image_size,
    pixel_size=20
)

# Loop through the images
for image_name in image_names:
    # Open image
    image_in = Image.open(image_name)
    
    # Convert the image with the reusable converter (fast)
    image_out = converter.apply(image_in)
    
    # Get new image filename
    main_name, ext = os.path.splitext(image_name)
    output_name = f"{main_name}_pixelated{ext}"
    
    # Save the image
    image_out.save(output_name)
    
    # Close the images
    image_in.close()
    image_out.close()
```

## Full Documentation
Here are the full definitions for the main class `Pixelgreat` and the main function `pixelgreat`:

### Class: Pixelgreat
#### \_\_init\_\_
- `output_size`
  - The size of the final output
  - A tuple, (width, height)
  - Each dimension must be at least 3 pixels
- `pixel_size`
  - The approximate size of a single pixel
  - Must be at least 3 pixels
- `screen_type`
  - The screen type, can be:
    - `pixelgreat.ScreenType.LCD`
    - `pixelgreat.ScreenType.CRT_TV`
    - `pixelgreat.ScreenType.CRT_MONITOR`
- `direction`
  - The direction of the pixels, can be:
    - `pixelgreat.Direction.VERTICAL`
    - `pixelgreat.Direction.HORIZONTAL`
- `pixel_aspect`
  - The aspect ratio of the pixels (width / height)
  - Must be no less than 0.33, but no bigger than 3.0
- `pixelate`
  - If the image should be pixelated before applying the filters
  - A boolean value
- `washout`

```python
class Pixelgreat:
    def __init__(,  # A tuple, (width, height)
                 ,   # The approximate size of a single pixel
                 =None,  # The screen type, can be pixelgreat.ScreenType.LCD, pixelgreat.ScreenType.LCD
                 =None,  
                 =None,  
                 =None,  
                 blur=None,  
                 washout=None,  
                 scanline_strength=None,  
                 scanline_spacing=None,  
                 scanline_size=None,  
                 scanline_blur=None,  
                 grid_strength=None,  
                 pixel_padding=None,  
                 rounding=None,  
                 bloom_strength=None,  
                 bloom_size=None,  
                 color_mode=None  
                 )
```