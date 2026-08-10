import os
import shutil
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
        cls.fixture_root = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture_root.cleanup)
        fixture = Path(cls.fixture_root.name) / "site"
        shutil.copytree(REPO_ROOT, fixture, ignore=shutil.ignore_patterns(".git", "public", "resources", ".hugo_build.lock"))
        cls.fixture_menus = fixture / "config/_default/menus.yaml"
        cls.fixture_menus.write_text(
            cls.fixture_menus.read_text(encoding="utf-8")
            + """
  - name: Resources
    identifier: resources
    url: resources
    weight: 80
  - name: Exact child
    parent: resources
    url: post/2025-06-03-ASC2024-prize/
    weight: 10
  - name: Descendant child
    parent: resources
    url: post
    weight: 20
  - name: Empty child
    parent: resources
    url: ""
    weight: 30
  - name: External child
    parent: resources
    url: https://example.com
    weight: 40
""",
            encoding="utf-8",
        )
        cls.fixture_output = Path(tempfile.mkdtemp())
        cls.addClassCleanup(shutil.rmtree, cls.fixture_output)
        fixture_environment = environment = os.environ.copy()
        fixture_environment.update({"PATH": f"{Path.home() / '.local/bin'}:{fixture_environment.get('PATH', '')}", "GOPROXY": "https://goproxy.cn", "GOSUMDB": "off", "GOMODCACHE": str(Path.home() / "go/pkg/mod")})
        fixture_environment.setdefault("HUGO_BIN", "hugo")
        fixture_result = subprocess.run(
            [fixture_environment["HUGO_BIN"], "--destination", str(cls.fixture_output)],
            cwd=fixture,
            env=fixture_environment,
            capture_output=True,
            text=True,
        )
        if fixture_result.returncode:
            raise RuntimeError(f"Hugo fixture build failed with exit code {fixture_result.returncode}:\n{fixture_result.stdout}\n{fixture_result.stderr}")
        cls.fixture_article = (cls.fixture_output / "post/2025-06-03-ASC2024-prize/index.html").read_text(encoding="utf-8")
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

    def test_homepage_hero_is_editorial_split(self):
        for expected in (
            'class="editorial-hero"',
            'class="editorial-hero__copy"',
            'class="editorial-hero__media"',
            'srcset="',
            'sizes="',
            'banner',
        ):
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

    def test_editorial_menu_overrides_bootstrap_collapse_on_desktop(self):
        css = "".join(
            stylesheet.read_text(encoding="utf-8")
            for stylesheet in self.output.rglob("*.css")
        )
        normalized_css = "".join(css.split())
        self.assertIn("@media(min-width:992px){.editorial-menu.collapse{display:flex}", normalized_css)
        self.assertIn(".editorial-menu.collapse:not(.show){display:none}", normalized_css)

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

    def test_descendant_page_marks_its_menu_section_as_current_location(self):
        article = self.output / "post" / "2025-06-03-ASC2024-prize" / "index.html"
        page = article.read_text(encoding="utf-8")
        self.assertRegex(
            page,
            r'<a class="editorial-menu-link is-active" href="/post" aria-current="location">\s*<span>Post</span>',
        )

    def test_fixture_dropdown_states_and_external_links_are_generated(self):
        page = self.fixture_article
        self.assertIn('class="editorial-menu-details is-active"', page)
        self.assertIn('<summary aria-current="location">', page)
        self.assertRegex(page, r'<a class="is-active" href="/post/2025-06-03-ASC2024-prize/" aria-current="page">')
        self.assertRegex(page, r'<a class="is-active" href="/post" aria-current="location">')
        self.assertRegex(page, r'<a class="" href="https://example.com" target="_blank" rel="noopener">')
        self.assertNotRegex(page, r'<a class="is-active" href="/"')

    def test_dark_theme_is_not_emitted(self):
        self.assertNotIn("theme-dropdown", self.homepage)


if __name__ == "__main__":
    unittest.main()
