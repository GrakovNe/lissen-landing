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
            r'<a href="([^"]*obtainium[^"]*)">\s*<img src="([^"]+)" alt="([^"]+)"',
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
            "https://www.rustore.ru/catalog/app/org.grakovne.lissen",
        ):
            self.assertIn(href, self.badges)


if __name__ == "__main__":
    unittest.main()
