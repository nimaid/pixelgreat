import unittest
import tempfile
import os

from pixelgreat import helpers


class TestHelpers(unittest.TestCase):
    def test_strip_all(self):
        # 1) Just run a few samples to verify it works (simple behavior)
        vals = (
            (
                "   \n  Hello, world!  \n ",
                "Hello, world!"
            ),
            (
                "      \r\n  Hello, world!  \r\n ",
                "Hello, world!"
            ),
            (
                "   \r\n  Hello, world!  \n ",
                "Hello, world!"
            ),
            (
                "    Hello, world!  \r\n ",
                "Hello, world!"
            ),
            (
                "Hello, world!  \r\n ",
                "Hello, world!"
            ),
            (
                "  Hello, world!  ",
                "Hello, world!"
            )
        )

        for test_vals in vals:
            self.assertEqual(helpers.strip_all(test_vals[0]), test_vals[1])

    def test_file_path(self):
        # 1) Make some temporary files and verify we can see them
        temp_files = list()
        for x in range(30):
            temp_files.append(tempfile.NamedTemporaryFile())

        for file in temp_files:
            self.assertEqual(helpers.file_path(file.name), file.name)

        # 2) Delete the temporary files and verify we get a FileNotFound error
        for file in temp_files:
            file.close()

        for file in temp_files:
            self.assertRaises(FileNotFoundError, helpers.file_path, file.name)

    def test_clip(self):
        # 1) Just test a bunch of values to verify it works
        vals = (
            (
                (1, 0, 1),
                1
            ),
            (
                (1, 0, 0.5),
                .5
            ),
            (
                (0, 0, 0.5),
                0
            ),
            (
                (-4, 0, 0.5),
                0
            ),
            (
                (100, 0, 12.345),
                12.345
            )
        )

        for test_vals in vals:
            self.assertEqual(
                helpers.clip(test_vals[0][0], test_vals[0][1], test_vals[0][2]),
                test_vals[1]
            )

    def test_get_centered_dimensions(self):
        pass

    def test_round_to_division(self):
        pass

    def test_tile_image(self):
        pass

    def test_lighten_image(self):
        pass


if __name__ == '__main__':
    unittest.main()
