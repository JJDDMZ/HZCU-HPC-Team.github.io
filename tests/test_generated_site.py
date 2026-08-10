import base64
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROUTES = ("/", "/people/", "/post/", "/daily/", "/recruitment/", "/memory/", "/accomplishments/", "/contact/")
REQUIRED_HOME_STRINGS = (
    "HZCU HPC Team",
    "浙大城市学院高性能计算",
    "INTRODUCTION",
    "ACCOMPLISHMENTS",
    "Meet the team",
)
SVG_HERO = b'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 8"><rect width="12" height="8" fill="#b95232"/></svg>'''
ANIMATED_GIF_HERO = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH/C05FVFNDQVBFMi4wAwEAAAAh+QQACAAAACwAAAAAAQABAAACAkQBADs="
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
        fixture_params = fixture / "config/_default/params.yaml"
        fixture_params.write_text(fixture_params.read_text(encoding="utf-8").replace("gravatar: false", "gravatar: true"), encoding="utf-8")
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
        fixture_recruitment = fixture / "content/recruitment/recruitment2408/index.md"
        fixture_recruitment.write_text(
            fixture_recruitment.read_text(encoding="utf-8").replace(
                "date: 2025-09-01", "date: 2025-09-01\nexternal_link: https://example.com/recruitment\nsummary: \"<script>alert(1)</script> "
                + "x" * 400
                + "\""
            ),
            encoding="utf-8",
        )
        fixture_memory = fixture / "content/memory/example/index.md"
        fixture_memory.write_text(
            fixture_memory.read_text(encoding="utf-8").replace(
                "abstract: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis posuere tellusac convallis placerat. Proin tincidunt magna sed ex sollicitudin condimentum. Sed ac faucibus dolor, scelerisque sollicitudin nisi. Cras purus urna, suscipit quis sapien eu, pulvinar tempor diam.'",
                "abstract: \"<script>alert(2)</script> " + "y" * 400 + "\"",
            ),
            encoding="utf-8",
        )
        event_dir = fixture / "content/event/editorial-fixture"
        event_dir.mkdir(parents=True)
        (fixture / "content/event/_index.md").write_text("---\ntitle: Events\nview: card\n---\n", encoding="utf-8")
        (event_dir / "index.md").write_text(
            "---\ntitle: Editorial fixture event\ndate: 2026-01-01T10:00:00Z\ndate_end: 2026-01-01T11:00:00Z\nlocation: Fixture Hall\n---\n",
            encoding="utf-8",
        )
        (fixture / "layouts/_default/single.html").write_text('{{ define "main" }}{{ .Title }}{{ end }}', encoding="utf-8")
        small_post_dir = fixture / "content/post/editorial-small"
        small_post_dir.mkdir(parents=True)
        shutil.copy(fixture / "assets/media/icon.png", small_post_dir / "featured.png")
        (small_post_dir / "index.md").write_text(
            "---\ntitle: Editorial small\ndate: 2026-01-01\nimage:\n  path: featured.png\n---\nFixture entry.",
            encoding="utf-8",
        )
        homepage = fixture / "content/_index.md"
        homepage.write_text(homepage.read_text(encoding="utf-8").replace("filename: banner.jpg", "filename: icon.png", 1), encoding="utf-8")
        for extension, fixture_data in (("svg", SVG_HERO), ("gif", ANIMATED_GIF_HERO)):
            post_dir = fixture / f"content/post/editorial-{extension}"
            post_dir.mkdir(parents=True)
            (post_dir / f"featured.{extension}").write_bytes(fixture_data)
            (post_dir / "index.md").write_text(
                f"---\ntitle: Editorial {extension}\ndate: 2026-01-01\nimage:\n  path: featured.{extension}\n---\nFixture entry.",
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

    def test_svg_and_animated_gif_hero_assets_build_with_original_paths(self):
        for extension, fixture_data in (("svg", SVG_HERO), ("gif", ANIMATED_GIF_HERO)):
            with self.subTest(extension=extension):
                fixture_root = tempfile.TemporaryDirectory()
                self.addCleanup(fixture_root.cleanup)
                fixture = Path(fixture_root.name) / "site"
                shutil.copytree(
                    REPO_ROOT,
                    fixture,
                    ignore=shutil.ignore_patterns(".git", "public", "resources", ".hugo_build.lock"),
                )
                image_name = f"hero.{extension}"
                (fixture / "assets/media" / image_name).write_bytes(fixture_data)
                homepage = fixture / "content/_index.md"
                homepage.write_text(
                    homepage.read_text(encoding="utf-8").replace("filename: banner.jpg", f"filename: {image_name}", 1),
                    encoding="utf-8",
                )
                destination = Path(tempfile.mkdtemp())
                self.addCleanup(shutil.rmtree, destination)
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
                    [environment["HUGO_BIN"], "--destination", str(destination)],
                    cwd=fixture,
                    env=environment,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, f"Hugo build failed:\n{result.stdout}\n{result.stderr}")
                generated_homepage = (destination / "index.html").read_text(encoding="utf-8")
                self.assertIn(f"hero.{extension}", generated_homepage)
                self.assertNotIn("srcset=", generated_homepage)

    def test_editorial_entries_preserve_event_metadata_and_location(self):
        page = (self.fixture_output / "event/index.html").read_text(encoding="utf-8")
        self.assertIn("Fixture Hall", page)
        self.assertRegex(page, r"(?:Jan|2026)")

    def test_editorial_media_passthrough_and_responsive_candidates_are_safe(self):
        page = (self.fixture_output / "post/index.html").read_text(encoding="utf-8")
        for extension in ("svg", "gif"):
            with self.subTest(extension=extension):
                entry = page.split(f"Editorial {extension}", 1)[1].split("</article>", 1)[0]
                self.assertIn(f"featured.{extension}", entry)
                self.assertNotIn("srcset=", entry)

    def test_editorial_summary_policy_removes_html_and_bounds_all_sources(self):
        for route in ("recruitment", "memory"):
            with self.subTest(route=route):
                fixture = (self.fixture_output / f"{route}/index.html").read_text(encoding="utf-8")
                summary = fixture.split('class="editorial-entry__summary"', 1)[1].split("</div>", 1)[0]
                self.assertNotIn("<script>", summary)
                self.assertLess(len(summary), 250)

    def test_people_directory_preserves_groups_members_and_accessible_portraits(self):
        import re

        page = (self.output / "people/index.html").read_text(encoding="utf-8")
        self.assertIn('class="editorial-people"', page)
        self.assertIn('class="editorial-person"', page)
        self.assertEqual(page.count("<main"), 1)
        ids = re.findall(r'\bid="([^"]+)"', page)
        self.assertEqual(len(ids), len(set(ids)))
        directory = page.split('class="editorial-people"', 1)[1]
        self.assertEqual(directory.count("<h1"), 1)
        self.assertIn("Meet the Team", directory)

        expected_groups = {
            "Mentor": ("Rui Hu", "Kui Su 苏奎"),
            "Team members": (
                "Guobin Zhang 张国宾",
                "Menglin Feng 冯梦琳",
                "Sizhe Qiao 乔思喆",
                "Xunuo Xie 谢许诺",
                "Yanan Sheng 盛亚楠",
                "Yuhan Guo",
                "Yuxiang Chen",
                "Binhao Gong 龚斌豪",
                "Zheng Cai 蔡政",
                "Jiawei Lin 林家为",
                "Junchen Lv 吕俊辰",
                "Wenjia Qu 屈文佳",
            ),
            "Alumni": ("Eason W 王绅懿", "Nuo Xu 许诺", "Zhuhan Bao 鲍竹涵", "Chengdong S 沈铖栋", "Lingkai Li 李凌凯"),
        }
        for group, members in expected_groups.items():
            with self.subTest(group=group):
                self.assertRegex(directory, rf"<h2[^>]*>{re.escape(group)}</h2>")
                for member in members:
                    self.assertIn(member, directory)

        portraits = re.findall(r'<img[^>]*class="[^"]*editorial-person__portrait[^"]*"[^>]*>', directory)
        self.assertTrue(portraits)
        for portrait in portraits:
            with self.subTest(portrait=portrait):
                self.assertRegex(portrait, r'alt="Portrait of [^"]+"')
                self.assertIn("srcset=", portrait)
                self.assertIn("sizes=", portrait)

    def test_people_avatar_template_avoids_raster_upscaling_and_preserves_passthrough(self):
        template = (REPO_ROOT / "layouts/partials/blocks/people.html").read_text(encoding="utf-8")
        self.assertIn('and site.Params.features.avatar.gravatar $person.Params.email', template)
        self.assertIn('eq $avatar.MediaType.SubType "svg"', template)
        self.assertIn('eq $avatar.MediaType.SubType "gif"', template)
        self.assertIn("if le . $avatar.Width", template)
        self.assertIn("srcset=", template)
        self.assertIn("sizes=", template)

    def test_people_social_links_are_accessible(self):
        import re

        page = (self.output / "people/index.html").read_text(encoding="utf-8")
        social = re.findall(r'<ul class="network-icon editorial-person__social"[^>]*>.*?</ul>', page, re.S)
        self.assertTrue(social)
        for links in social:
            self.assertNotRegex(links.split(">", 1)[0], r'aria-hidden')
            self.assertRegex(links, r'<a[^>]+aria-label="[^"]+"[^>]+title="[^"]+"')

    def test_gravatar_enabled_falls_back_for_empty_email_and_hashes_nonempty_email(self):
        page = (self.fixture_output / "people/index.html").read_text(encoding="utf-8")
        self.assertIn("/author/binhao-gong", page)
        self.assertNotIn("s.gravatar.com/avatar/d41d8cd98f00b204e9800998ecf8427e", page)
        self.assertIn("s.gravatar.com/avatar/", page)

    def test_editorial_landmarks_and_hero_ids_are_unique(self):
        for route in ("/", "/post/", "/daily/"):
            with self.subTest(route=route):
                path = self.output / ("index.html" if route == "/" else f"{route.strip('/')}/index.html")
                page = path.read_text(encoding="utf-8")
                self.assertEqual(page.count("<main"), 1)
                ids = __import__("re").findall(r'\\bid="([^"]+)"', page)
                self.assertEqual(len(ids), len(set(ids)))

    def test_small_raster_candidates_do_not_upscale(self):
        homepage = (self.fixture_output / "index.html").read_text(encoding="utf-8")
        hero = homepage.split('class="editorial-hero__media"', 1)[1].split("</div>", 1)[0]
        hero_widths = [int(width) for width in __import__("re").findall(r"\s(\d+)w", hero)]
        self.assertTrue(hero_widths)
        self.assertTrue(all(width <= 512 for width in hero_widths))
        listing = (self.fixture_output / "post/index.html").read_text(encoding="utf-8")
        entry = listing.split("Editorial small", 1)[1].split("</article>", 1)[0]
        widths = [int(width) for width in __import__("re").findall(r"\s(\d+)w", entry)]
        self.assertTrue(widths)
        self.assertTrue(all(width <= 512 for width in widths))

    def test_text_link_colors_meet_wcag_contrast(self):
        import re

        def rgb(hex_color):
            return tuple(int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5))

        def luminance(hex_color):
            channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb(hex_color)]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        def contrast(foreground, background):
            light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
            return (light + 0.05) / (dark + 0.05)

        tokens = (REPO_ROOT / "assets/scss/abstracts/_tokens.scss").read_text(encoding="utf-8")
        typography = (REPO_ROOT / "assets/scss/base/_typography.scss").read_text(encoding="utf-8")
        entries = (REPO_ROOT / "assets/scss/components/_entries.scss").read_text(encoding="utf-8")
        colors = dict(re.findall(r"--(color-(?:paper|clay-dark)): (#[0-9a-f]{6})", tokens))
        self.assertIn("color: var(--color-clay-dark)", typography)
        self.assertIn("color: var(--color-clay-dark)", entries)
        self.assertGreaterEqual(contrast(colors["color-clay-dark"], colors["color-paper"]), 4.5)

    def test_editorial_sections_use_unified_index_and_entry_views(self):
        for route in ("post", "daily", "recruitment", "memory"):
            with self.subTest(route=route):
                page = (self.output / route / "index.html").read_text(encoding="utf-8")
                self.assertIn('class="editorial-index"', page)
                self.assertIn('class="editorial-entry', page)

    def test_editorial_entries_support_text_fallback_and_image_accessibility(self):
        diary = (self.output / "daily" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="editorial-entry text-only"', diary)
        self.assertIn("Sizhe", diary)
        self.assertNotIn('src=""', diary)
        self.assertNotIn("featured-image-placeholder", diary)
        post = (self.output / "post" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(post, r'class="editorial-entry[^\"]*with-image')
        self.assertIn("srcset=", post)
        self.assertIn("aria-label=\"Read", post)

    def test_homepage_recruitment_summary_is_a_concise_safe_excerpt(self):
        entry = self.homepage.split('浙大城市学院超算队2025年招新', 1)[1].split('</article>', 1)[0]
        summary = entry.split('class="editorial-entry__summary"', 1)[1].split('</div>', 1)[0]
        self.assertNotIn("<h2", summary)
        self.assertNotIn("<h3", summary)
        self.assertLess(len(summary), 500)

    def test_editorial_entries_keep_external_link_security_and_metadata(self):
        fixture = (self.fixture_output / "recruitment" / "index.html").read_text(encoding="utf-8")
        self.assertIn("editorial-entry__metadata", fixture)
        self.assertIn("editorial-entry__summary", fixture)
        self.assertIn('href="https://example.com/recruitment" target="_blank" rel="noopener"', fixture)

    def test_editorial_index_has_unique_heading_and_pagination(self):
        for route in ("post", "daily", "recruitment", "memory"):
            with self.subTest(route=route):
                page = (self.output / route / "index.html").read_text(encoding="utf-8")
                self.assertRegex(page, r'<section[^>]+aria-labelledby="[^"]+"')
                editorial_index = page.split('<section class="editorial-index"', 1)[1].split("</section>", 1)[0]
                self.assertEqual(editorial_index.count("<h1"), 1)
                self.assertNotIn('id="main-content"', editorial_index)

    def test_view_proxies_preserve_publication_citation(self):
        views = REPO_ROOT / "layouts/partials/views"
        for view in ("card", "compact", "list"):
            proxy = (views / f"{view}.html").read_text(encoding="utf-8")
            self.assertIn('partial "views/editorial" .', proxy)
            self.assertIn('"event" "project" "publication"', proxy)
        publication = (self.output / "publication" / "index.html").read_text(encoding="utf-8")
        self.assertIn("citation", publication)

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
