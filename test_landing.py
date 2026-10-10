import re
import unittest
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE.joinpath("index.html").read_text(encoding="utf-8")

OBTAINIUM_HREF = (
    "https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/"
    "%7B%22id%22%3A%22org.grakovne.lissen%22%2C%22url%22%3A%22https%3A%2F%2F"
    "github.com%2FGrakovNe%2Flissen-android%22%2C%22author%22%3A%22GrakovNe%22"
    "%2C%22name%22%3A%22Lissen%22%7D"
)
OBTAINIUM_BADGE = "badge-obtainium.png"


def badges_section():
    match = re.search(r'<div class="download-badges">(.*?)</div>', HTML, re.DOTALL)
    assert match, "download-badges section not found"
    return match.group(1)


class TestObtainiumButton(unittest.TestCase):
    def setUp(self):
        self.badges = badges_section()

    def test_obtainium_anchor_present(self):
        self.assertIn(OBTAINIUM_HREF, self.badges)

    def test_obtainium_uses_embedded_badge(self):
        import base64

        match = re.search(r'<img src="data:image/png;base64,([^"]+)"', self.badges)
        self.assertIsNotNone(match, "obtainium badge is not an embedded data URI")
        embedded = base64.b64decode(match.group(1))
        self.assertEqual(embedded, HERE.joinpath(OBTAINIUM_BADGE).read_bytes())

    def test_obtainium_anchor_wraps_badge(self):
        anchor = re.search(
            r'<a\b[^>]*href="([^"]*obtainium[^"]*)"[^>]*>\s*<img src="([^"]+)" alt="([^"]+)"',
            self.badges,
        )
        self.assertIsNotNone(anchor, "obtainium anchor does not wrap a badge image")
        self.assertEqual(anchor.group(1), OBTAINIUM_HREF)
        self.assertTrue(anchor.group(2).startswith("data:image/png;base64,"))
        self.assertEqual(anchor.group(3), "Get it on Obtainium")

    def test_other_badges_still_present(self):
        for href in (
            "https://play.google.com/store/apps/details?id=org.grakovne.lissen",
            "https://f-droid.org/packages/org.grakovne.lissen",
        ):
            self.assertIn(href, self.badges)

    def test_rustore_removed(self):
        self.assertNotIn("rustore.ru", HTML)


class TestBadgeSizes(unittest.TestCase):
    def test_all_badge_imgs_same_height_attr(self):
        heights = re.findall(r'<img src="[^"]+" alt="Get it on [^"]+" height="(\d+)"', HTML)
        self.assertEqual(len(heights), 3)
        self.assertEqual(set(heights), {"60"})

    def test_css_single_height_rule(self):
        self.assertNotIn(".obtainium img", HTML)
        heights = re.findall(
            r"\.download-badges a img\s*\{[^}]*?height:\s*(\d+)px", HTML
        )
        self.assertEqual(sorted(map(int, heights)), [30, 55, 60])

    def test_anchors_center_items_vertically(self):
        rule = re.search(r"\.download-badges a\s*\{([^}]*)\}", HTML)
        self.assertIsNotNone(rule)
        self.assertIn("display: flex", rule.group(1))
        self.assertIn("align-items: center", rule.group(1))


class TestBadgeImage(unittest.TestCase):
    # Google Play / F-Droid SVGs render their visible pill at 56/60 of img height
    TARGET_VISIBLE_RATIO = 56 / 60

    def test_png_has_no_gray_ring(self):
        from PIL import Image

        im = Image.open(HERE / OBTAINIUM_BADGE).convert("RGBA")
        x0, y0, x1, y1 = im.getbbox()
        # first opaque pixel along the top edge must be dark pill, not a gray ring
        for x in range(x0 + 10, x1 - 10, 7):
            y = y0
            while im.getpixel((x, y))[3] <= 200:
                y += 1
            brightness = sum(im.getpixel((x, y))[:3]) / 3
            self.assertLess(brightness, 150, f"gray ring at ({x}, {y}): {im.getpixel((x, y))}")

    def test_png_padding_matches_store_badges(self):
        from PIL import Image

        im = Image.open(HERE / OBTAINIUM_BADGE).convert("RGBA")
        bbox = im.getbbox()
        ratio = (bbox[3] - bbox[1]) / im.height
        self.assertAlmostEqual(ratio, self.TARGET_VISIBLE_RATIO, delta=0.01)


class TestScreenshots(unittest.TestCase):
    def test_no_russian_screenshot_urls(self):
        self.assertNotIn("ru-RU/images/phoneScreenshots", HTML)

    def test_screenshots_have_no_language_switch_attrs(self):
        match = re.search(r'<div class="screenshots">(.*?)</div>', HTML, re.DOTALL)
        assert match, "screenshots section not found"
        self.assertNotIn("data-ru", match.group(1))
        self.assertNotIn("data-en", match.group(1))
        self.assertEqual(len(re.findall(r"en-US/images/phoneScreenshots", match.group(1))), 4)


if __name__ == "__main__":
    unittest.main()
