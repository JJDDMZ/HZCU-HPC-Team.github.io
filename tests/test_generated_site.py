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
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{Path.home() / '.local/bin'}:{environment.get('PATH', '')}",
                "GOPROXY": "https://goproxy.cn",
                "GOSUMDB": "off",
                "GOMODCACHE": str(Path.home() / "go/pkg/mod"),
            }
        )
        result = subprocess.run(
            [environment.get("HUGO_BIN", str(Path.home() / ".local/bin/hugo")), "--destination", cls.destination.name],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            cls.destination.cleanup()
            raise RuntimeError(
                f"Hugo build failed with exit code {result.returncode}:\n"
                f"{result.stdout}\n{result.stderr}"
            )
        cls.output = Path(cls.destination.name)
        cls.homepage = (cls.output / "index.html").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.destination.cleanup()

    def test_required_routes_are_generated(self):
        for route in REQUIRED_ROUTES:
            with self.subTest(route=route):
                output_path = self.output / route.strip("/") / "index.html" if route != "/" else self.output / "index.html"
                self.assertTrue(output_path.is_file(), f"Missing generated route: {route}")

    def test_homepage_contains_required_strings(self):
        for expected in REQUIRED_HOME_STRINGS:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.homepage)


if __name__ == "__main__":
    unittest.main()
