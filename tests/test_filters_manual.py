import unittest
import os
import shutil
from PIL import Image

from pixelgreat import filters

tests_dir = os.path.dirname(os.path.realpath(__file__))

test_image = Image.open(os.path.join(tests_dir, "images", "PM5544.png"))
save_dir = os.path.join(tests_dir, "processed_images")


class MakeManualTestAssets(unittest.TestCase):
    def make_image(self,
                   save_location,
                   screen_type,
                   pixel_size,
                   pixel_padding,
                   direction,
                   pixel_aspect,
                   washout=0.0,
                   blur=0.0,
                   bloom_size=0.0,
                   rounding=0.0,
                   scanline_spacing=1.0,
                   scanline_size=0.75,
                   scanline_blur=0.25,
                   scanline_strength=1.0,
                   bloom_strength=1.0,
                   grid_strength=1.0,
                   pixelate=True,
                   output_scale=1
                   ):

        # Compute image
        image = filters.CompositeFilter(
            size=test_image.size,
            screen_type=screen_type,
            pixel_size=pixel_size,
            pixel_padding=pixel_padding,
            direction=direction,
            washout=washout,
            blur=blur,
            bloom_size=bloom_size,
            pixel_aspect=pixel_aspect,
            rounding=rounding,
            scanline_spacing=scanline_spacing,
            scanline_size=scanline_size,
            scanline_blur=scanline_blur,
            scanline_strength=scanline_strength,
            bloom_strength=bloom_strength,
            grid_strength=grid_strength,
            pixelate=pixelate,
            output_size=(
                round(test_image.width * output_scale),
                round(test_image.height * output_scale)
            ),
            color_mode=test_image.mode
        ).apply(test_image)

        # Build filename
        output_name = ""

        if screen_type == filters.ScreenType.LCD:
            output_name += "LCD"
        elif screen_type == filters.ScreenType.CRT_TV:
            output_name += "TV"
        else:
            output_name += "MON"

        output_name += f"_pxs{pixel_size}"

        output_name += f"_pxa{pixel_aspect:.2f}"

        if direction == filters.Direction.VERTICAL:
            output_name += "_dV"
        elif direction == filters.Direction.HORIZONTAL:
            output_name += "_dH"

        if scanline_strength > 0:
            output_name += f"_ssp{scanline_spacing:.2f}"

        if grid_strength > 0:
            output_name += f"_pxp{pixel_padding:.2f}"

        if washout > 0:
            output_name += f"_w{washout:.2f}"

        if blur > 0:
            output_name += f"_b{blur:.2f}"

        if bloom_size > 0 and bloom_strength > 0:
            output_name += f"_bs{bloom_size:.2f}"

        if screen_type in [filters.ScreenType.LCD, filters.ScreenType.CRT_TV]:
            output_name += f"_r{rounding:.2f}"

        if scanline_strength > 0:
            output_name += f"_ssz{scanline_size:.2f}"

        if scanline_strength > 0:
            output_name += f"_sb{scanline_blur:.2f}"

        if scanline_strength > 0:
            output_name += f"_sst{scanline_strength:.2f}"

        if bloom_size > 0 and bloom_strength > 0:
            output_name += f"_bls{bloom_strength:.2f}"

        if grid_strength > 0:
            output_name += f"_gs{grid_strength:.2f}"

        if pixelate:
            output_name += "_pxt"

        output_name += ".png"

        # Save
        image.save(os.path.join(save_location, output_name))
        print(f"Saved: {output_name}")

    def test_make_images(self):
        # Clear the directory
        if os.path.exists(save_dir) and os.path.isdir(save_dir):
            shutil.rmtree(save_dir)

        os.mkdir(save_dir)

        # Compute the images
        for px_size in [400, 280, 130, 66, 33, 22, 10, 7, 6, 5, 4, 3]:
            for pixel_aspect in [(1/3), (1/2), 1, 2, 3]:
                for direction in [filters.Direction.VERTICAL, filters.Direction.HORIZONTAL]:
                    for scanline_spacing in [1.0, 0.79]:
                        self.make_image(
                            save_location=save_dir,
                            screen_type=filters.ScreenType.CRT_TV,
                            pixel_size=px_size,
                            pixel_padding=0.25,
                            direction=direction,
                            washout=0.5,
                            blur=0.5,
                            bloom_size=0.5,
                            pixel_aspect=pixel_aspect,
                            rounding=0.5,
                            scanline_spacing=scanline_spacing,
                            scanline_size=0.75,
                            scanline_blur=0.25,
                            scanline_strength=1,
                            bloom_strength=1,
                            grid_strength=1,
                            pixelate=True,
                            output_scale=4
                        )

                        self.make_image(
                            save_location=save_dir,
                            screen_type=filters.ScreenType.CRT_MONITOR,
                            pixel_size=px_size,
                            pixel_padding=0.1,
                            direction=direction,
                            washout=0.5,
                            blur=0.75,
                            bloom_size=0.5,
                            pixel_aspect=pixel_aspect,
                            scanline_spacing=scanline_spacing,
                            scanline_size=0.75,
                            scanline_blur=0.25,
                            scanline_strength=1,
                            bloom_strength=1,
                            grid_strength=1,
                            pixelate=True,
                            output_scale=4
                        )

                    self.make_image(
                        save_location=save_dir,
                        screen_type=filters.ScreenType.LCD,
                        pixel_size=px_size,
                        pixel_padding=0.25,
                        direction=direction,
                        washout=0.1,
                        blur=0,
                        bloom_size=0.5,
                        pixel_aspect=pixel_aspect,
                        rounding=0,
                        scanline_strength=0,
                        bloom_strength=1,
                        grid_strength=1,
                        pixelate=True,
                        output_scale=4
                    )


if __name__ == '__main__':
    unittest.main()
