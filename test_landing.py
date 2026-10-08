import re
import unittest
from pathlib import Path

HTML = Path(__file__).parent.joinpath("index.html").read_text(encoding="utf-8")

OBTAINIUM_HREF = (
    "https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/"
    "%7B%22id%22%3A%22org.grakovne.lissen%22%2C%22url%22%3A%22https%3A%2F%2F"
    "github.com%2FGrakovNe%2Flissen-android%22%2C%22author%22%3A%22GrakovNe%22"
    "%2C%22name%22%3A%22Lissen%22%7D"
)
OBTAINIUM_BADGE = (
    "https://raw.githubusercontent.com/ImranR98/Obtainium/main/assets/graphics/badge_obtainium.png"
)


class TestObtainiumButton(unittest.TestCase):
    def setUp(self):
        match = re.search(
            r'<div class="download-badges">(.*?)</div>', HTML, re.DOTALL
        )
        self.assertIsNotNone(match, "download-badges section not found")
        self.badges = match.group(1)

    def test_obtainium_anchor_present(self):
        self.assertIn(OBTAINIUM_HREF, self.badges)

    def test_obtainium_badge_image_present(self):
        self.assertIn(OBTAINIUM_BADGE, self.badges)

    def test_obtainium_anchor_wraps_badge(self):
        anchor = re.search(
            r'<a\b[^>]*href="([^"]*obtainium[^"]*)"[^>]*>\s*<img src="([^"]+)" alt="([^"]+)"',
            self.badges,
        )
        self.assertIsNotNone(anchor, "obtainium anchor does not wrap a badge image")
        self.assertEqual(anchor.group(1), OBTAINIUM_HREF)
        self.assertEqual(anchor.group(2), OBTAINIUM_BADGE)
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
    # badge_obtainium.png (646x250) has transparent padding: visible pill is 67.2% of height
    OBTAINIUM_VISIBLE_RATIO = 0.672

    def css_height(self, selector):
        match = re.search(
            re.escape(selector) + r"\s*\{[^}]*?height:\s*(\d+)px", HTML
        )
        self.assertIsNotNone(match, f"CSS rule for {selector} not found")
        return int(match.group(1))

    def test_obtainium_img_attr_is_89(self):
        match = re.search(
            r'class="obtainium"[^>]*>\s*<img[^>]*height="(\d+)"', HTML
        )
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 89)

    def test_visible_heights_match_at_all_breakpoints(self):
        for base_selector, obtainium_selector in (
            (".download-badges a img", ".download-badges .obtainium img"),
        ):
            base = self.css_height(base_selector)
            obtainium = self.css_height(obtainium_selector)
            self.assertAlmostEqual(
                obtainium * self.OBTAINIUM_VISIBLE_RATIO,
                base,
                delta=2,
                msg=f"obtainium {obtainium}px vs standard {base}px not visually equal",
            )

    def test_media_queries_scale_obtainium_too(self):
        obtainium_heights = re.findall(
            r"\.download-badges \.obtainium img\s*\{[^}]*?height:\s*(\d+)px",
            HTML,
        )
        self.assertEqual(len(obtainium_heights), 3, "desktop + 2 media queries")
        self.assertEqual(
            sorted(map(int, obtainium_heights)), [45, 82, 89]
        )


if __name__ == "__main__":
    unittest.main()
