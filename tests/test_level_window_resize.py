"""Regression test: level changes must not progressively shrink the window."""

import unittest

from views.pygame_renderer import PygameRenderer


class LevelWindowResizeTests(unittest.TestCase):
    """Check stable sizing across repeated level changes."""

    def test_resize_repeat_is_stable(self) -> None:
        """Going 43 -> 51 -> 59 -> 43 must restore the first size."""
        renderer = PygameRenderer(43, 43)
        first = renderer.screen.get_size()
        self.assertEqual(first, (renderer.width, renderer.height))

        for _ in range(4):
            for size in (51, 59, 43):
                renderer.resize_grid(size, size)
                self.assertEqual(
                    renderer.screen.get_size(),
                    (renderer.width, renderer.height),
                )
                self.assertEqual(
                    renderer.height, size * renderer.tile_size + 80,
                )
            self.assertEqual(renderer.screen.get_size(), first)

    def test_hud_space_reserved(self) -> None:
        """All tested maze sizes leave a separate HUD strip."""
        renderer = PygameRenderer(43, 43)
        for size in (43, 51, 59):
            renderer.resize_grid(size, size)
            self.assertGreater(renderer.tile_size, 0)
            self.assertEqual(
                renderer.height - size * renderer.tile_size,
                renderer.HUD_HEIGHT,
            )


if __name__ == "__main__":
    unittest.main()
