import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROUTES = ("/", "/people/", "/post/", "/daily/", "/accomplishments/", "/contact/")
REQUIRED_HOME_STRINGS = (
    "HZCU HPC Team",
    "浙大城市学院高性能计算",
    "INTRODUCTION",
    "ACCOMPLISHMENTS",
    "Meet the team",
)


class GeneratedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.destination = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.destination.cleanup)
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{Path.home() / '.local/bin'}:{environment.get('PATH', '')}",
                "GOPROXY": "https://goproxy.cn",
                "GOSUMDB": "off",
                "GOMODCACHE": str(Path.home() / "go/pkg/mod"),
            }
        )
        environment.setdefault("HUGO_BIN", "hugo")
        result = subprocess.run(
            [environment["HUGO_BIN"], "--destination", cls.destination.name],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(
                f"Hugo build failed with exit code {result.returncode}:\n"
                f"{result.stdout}\n{result.stderr}"
            )
        cls.output = Path(cls.destination.name)
        cls.homepage = (cls.output / "index.html").read_text(encoding="utf-8")

    def test_required_routes_are_generated(self):
        for route in REQUIRED_ROUTES:
            with self.subTest(route=route):
                output_path = self.output / route.strip("/") / "index.html" if route != "/" else self.output / "index.html"
                self.assertTrue(output_path.is_file(), f"Missing generated route: {route}")

    def test_homepage_contains_required_strings(self):
        for expected in REQUIRED_HOME_STRINGS:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)

    def test_warm_editorial_design_tokens_compile(self):
        css = "\n".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        for token in (
            "--color-paper:#f2efe7",
            "--color-ink:#1f1e1a",
            "--color-clay:#b95232",
            "--font-display:",
            "--content-max:90rem",
        ):
            with self.subTest(token=token):
                self.assertIn(token, normalized_css)

    def test_skip_link_target_exists_on_every_generated_page(self):
        for route in REQUIRED_ROUTES:
            output_path = self.output / route.strip("/") / "index.html" if route != "/" else self.output / "index.html"
            with self.subTest(route=route):
                page = output_path.read_text(encoding="utf-8")
                self.assertIn('id="main-content"', page)

    def test_editorial_navigation_and_footer_are_emitted(self):
        for expected in (
            'class="skip-link"',
            "editorial-header",
            'aria-label="Primary navigation"',
            "editorial-footer-grid",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)

    def test_mobile_navigation_is_accessible(self):
        self.assertIn('aria-controls="editorial-menu"', self.homepage)
        self.assertIn('aria-expanded="false"', self.homepage)
        self.assertRegex(self.homepage, r'<button[^>]+aria-label="[^"]+"')

    def test_dark_theme_is_not_emitted(self):
        self.assertNotIn("theme-dropdown", self.homepage)


if __name__ == "__main__":
    unittest.main()
