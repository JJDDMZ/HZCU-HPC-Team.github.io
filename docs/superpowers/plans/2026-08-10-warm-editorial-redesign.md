# Warm Editorial Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不修改现有文字与素材的前提下，将 HZCU HPC Team 的 Hugo Blox 网站全站重建为暖色、二维、可访问的编辑式科技企业视觉系统。

**Architecture:** 保留 Hugo Blox 的内容模型、搜索、分页、分类和图片管线；使用本地 Hugo partial 覆盖导航、页脚、Hero、People 和内容预览结构，再以模块化 SCSS 统一页面视觉。一个无依赖的本地 JavaScript 文件负责导航状态和渐进式滚动揭示；Python `unittest` 对临时 Hugo 构建产物执行结构与内容回归检查。

**Tech Stack:** Hugo Extended 0.135.0、Hugo Blox Bootstrap v5、Go Modules、Go template、SCSS、原生 JavaScript、Python 3 标准库 `unittest`

---

## 实施边界

- 不编辑 `content/` 下的现有文字或 Front Matter 信息。
- 不编辑 `assets/media/`、作者头像、文章图片和 `static/` 中的素材。
- 不直接编辑 `public/` 或 `resources/`；它们都是构建产物。
- 不新增 npm、Vite、React、Three.js、远程字体或动画库。
- 不提交当前无关的 `.claude/`、`.superpowers/`；设计文档和本计划除外。
- 所有构建命令使用本机已准备的 Hugo/Go 环境：

```bash
export PATH="$HOME/.local/bin:$PATH"
export GOPROXY="https://goproxy.cn"
export GOSUMDB="off"
export GOMODCACHE="$HOME/go/pkg/mod"
```

## 文件职责映射

### 新增测试和验证文件

- `tests/test_generated_site.py`：构建到临时目录，验证关键路由、语义标记、内容保留、响应式图片和脚本加载。
- `scripts/test-site.sh`：统一配置 Hugo/Go 环境并运行 Python 回归测试。

### 新增模板覆盖

- `layouts/partials/components/headers/editorial.html`：刊头式导航、跳转链接、搜索入口和移动菜单。
- `layouts/partials/components/footers/editorial.html`：网站名称、现有菜单和许可信息的三段式页脚。
- `layouts/partials/blocks/hero.html`：首页 52/48 编辑式分屏和响应式 `banner.jpg`。
- `layouts/partials/blocks/people.html`：语义化成员分组、响应式头像与可访问链接。
- `layouts/partials/views/editorial.html`：统一的有图/无图内容条目。
- `layouts/partials/views/card.html`、`compact.html`、`list.html`：将现有视图名称代理到 editorial 视图，避免修改内容 Front Matter。
- `layouts/partials/editorial/listing.html`：Post、Diary、Recruitment、Memory 等列表页公共结构。
- `layouts/_default/list.html`、`layouts/section/post.html`：调用统一列表结构。
- `layouts/_default/_markup/render-image.html`：正文图片的 `srcset`、`sizes`、尺寸和图注。
- `layouts/partials/page_header.html`：文章页头和主图响应式输出。

### 新增样式和脚本

- `assets/scss/abstracts/_tokens.scss`：颜色、字体、字号、间距、容器和层叠令牌。
- `assets/scss/abstracts/_mixins.scss`：容器、焦点环和减少动态 mixin。
- `assets/scss/base/_foundation.scss`：全局背景、基础元素和 Bootstrap 主题重置。
- `assets/scss/base/_typography.scss`：标题、正文和文章排版。
- `assets/scss/base/_accessibility.scss`：跳转链接、焦点、触控目标和减少动态。
- `assets/scss/components/_navigation.scss`：桌面与移动导航。
- `assets/scss/components/_footer.scss`：三段式页脚。
- `assets/scss/components/_entries.scss`：索引条目、元数据和分页。
- `assets/scss/components/_people.scss`：People 和成员档案。
- `assets/scss/pages/_home.scss`：Hero、Introduction、Accomplishments 和 CTA。
- `assets/scss/pages/_list.scss`：栏目首页与 Publication 过滤器。
- `assets/scss/pages/_article.scss`：文章页头、正文、图像和作者卡。
- `assets/scss/template.scss`：只导入上述模块。
- `assets/js/editorial.js`：渐进式导航压缩和滚动揭示。

### 修改配置与文档

- `config/_default/params.yaml`：启用本地 header/footer block、禁用主题切换、加载 `editorial.js`。
- `CLAUDE.md`：记录测试命令和本地网络环境下的构建命令。

---

### Task 1: 建立可重复的 Hugo 回归测试

**Files:**
- Create: `tests/test_generated_site.py`
- Create: `scripts/test-site.sh`

- [ ] **Step 1: 编写最小构建测试**

创建 `tests/test_generated_site.py`：

```python
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get("HUGO_BIN", str(Path.home() / ".local/bin/hugo"))


class GeneratedSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="hzcu-hpc-site-"))
        env = os.environ.copy()
        env.setdefault("GOPROXY", "https://goproxy.cn")
        env.setdefault("GOSUMDB", "off")
        env.setdefault("GOMODCACHE", str(Path.home() / "go/pkg/mod"))
        result = subprocess.run(
            [
                HUGO,
                "--gc",
                "--minify",
                "--destination",
                str(cls.temp_dir),
                "--cleanDestinationDir",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temp_dir)

    def page(self, route: str) -> str:
        path = self.temp_dir / route.strip("/") / "index.html"
        if route == "/":
            path = self.temp_dir / "index.html"
        self.assertTrue(path.exists(), f"missing generated route: {route}")
        return path.read_text(encoding="utf-8")

    def all_css(self) -> str:
        return "\n".join(
            path.read_text(encoding="utf-8")
            for path in self.temp_dir.rglob("*.css")
        )

    def test_baseline_routes_build(self) -> None:
        for route in (
            "/",
            "/people/",
            "/post/",
            "/daily/",
            "/accomplishments/",
            "/contact/",
        ):
            self.page(route)

    def test_existing_homepage_information_is_preserved(self) -> None:
        homepage = self.page("/")
        self.assertIn("HZCU HPC Team", homepage)
        self.assertIn("浙大城市学院高性能计算", homepage)
        self.assertIn("INTRODUCTION", homepage)
        self.assertIn("ACCOMPLISHMENTS", homepage)
        self.assertIn("Meet the team", homepage)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 创建统一测试入口**

创建 `scripts/test-site.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"
export HUGO_BIN="${HUGO_BIN:-$HOME/.local/bin/hugo}"
export GOPROXY="${GOPROXY:-https://goproxy.cn}"
export GOSUMDB="${GOSUMDB:-off}"
export GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}"

python3 -m unittest tests/test_generated_site.py -v
```

然后执行：

```bash
chmod +x scripts/test-site.sh
```

- [ ] **Step 3: 运行基线测试**

Run:

```bash
./scripts/test-site.sh
```

Expected: `Ran 2 tests` 和 `OK`，Hugo 构建无错误。

- [ ] **Step 4: 记录内容与素材未改动基线**

Run:

```bash
git diff --exit-code -- content assets/media static
```

Expected: 无输出，退出码为 0。

- [ ] **Step 5: 提交测试基线**

```bash
git add tests/test_generated_site.py scripts/test-site.sh
git commit -m "test: add generated site regression checks" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 2: 建立暖色设计令牌和基础样式

**Files:**
- Create: `assets/scss/abstracts/_tokens.scss`
- Create: `assets/scss/abstracts/_mixins.scss`
- Create: `assets/scss/base/_foundation.scss`
- Create: `assets/scss/base/_typography.scss`
- Create: `assets/scss/base/_accessibility.scss`
- Modify: `assets/scss/template.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加会失败的设计系统测试**

在 `GeneratedSiteTest` 中加入：

```python
    def test_warm_editorial_design_tokens_compile(self) -> None:
        css = self.all_css()
        for token in (
            "--color-paper:#f2efe7",
            "--color-ink:#1f1e1a",
            "--color-clay:#b95232",
            "--font-display:",
            "--content-max:90rem",
        ):
            self.assertIn(token, css)

    def test_dark_theme_is_not_emitted(self) -> None:
        homepage = self.page("/")
        self.assertNotIn("theme-dropdown", homepage)
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `./scripts/test-site.sh`

Expected: `test_warm_editorial_design_tokens_compile` FAIL，缺少 `--color-paper`。

- [ ] **Step 3: 创建令牌与 mixin**

创建 `assets/scss/abstracts/_tokens.scss`：

```scss
:root {
  --color-paper: #f2efe7;
  --color-paper-deep: #e8e2d7;
  --color-ink: #1f1e1a;
  --color-muted: #625e55;
  --color-line: #c9c1b4;
  --color-line-strong: #8a8378;
  --color-clay: #b95232;
  --color-clay-dark: #8e3922;
  --color-sage: #788476;
  --color-inverse: #24241f;
  --color-inverse-text: #f2efe7;
  --font-display: Georgia, "Songti SC", STSong, "Noto Serif CJK SC", serif;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: clamp(1rem, 0.97rem + 0.12vw, 1.075rem);
  --text-lg: clamp(1.125rem, 1.06rem + 0.25vw, 1.3rem);
  --heading-sm: clamp(1.5rem, 1.25rem + 1vw, 2.15rem);
  --heading-md: clamp(2.2rem, 1.55rem + 2.8vw, 4.5rem);
  --heading-hero: clamp(3.7rem, 2.3rem + 6.2vw, 8.5rem);
  --space-1: 0.375rem;
  --space-2: 0.75rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
  --space-5: 2rem;
  --space-6: clamp(2.5rem, 5vw, 5rem);
  --space-7: clamp(4rem, 8vw, 8rem);
  --content-max: 90rem;
  --reading-max: 70ch;
  --page-gutter: clamp(1.25rem, 4vw, 4.5rem);
  --z-header: 50;
  --z-menu: 40;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
}
```

创建 `assets/scss/abstracts/_mixins.scss`：

```scss
@mixin editorial-container {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  margin-inline: auto;
}

@mixin focus-ring {
  outline: 3px solid var(--color-clay);
  outline-offset: 3px;
}

@mixin reduce-motion {
  @media (prefers-reduced-motion: reduce) {
    @content;
  }
}
```

- [ ] **Step 4: 创建基础、排版和无障碍样式**

创建 `assets/scss/base/_foundation.scss`：

```scss
html {
  background: var(--color-paper);
  color: var(--color-ink);
  scroll-behavior: smooth;
}

body,
.page-wrapper,
.page-body,
.home-section {
  background: var(--color-paper);
  color: var(--color-ink);
}

body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.7;
  overflow-x: clip;
}

a {
  color: inherit;
  text-decoration-color: var(--color-clay);
  text-underline-offset: 0.2em;
}

a:hover {
  color: var(--color-clay-dark);
}

img {
  max-width: 100%;
  height: auto;
  border-radius: 2px;
}

hr {
  border-color: var(--color-line);
}

.container,
.container-xl,
.universal-wrapper,
.article-container {
  max-width: var(--content-max);
}
```

创建 `assets/scss/base/_typography.scss`：

```scss
h1,
h2,
h3,
.section-heading h1,
.section-subheading {
  color: var(--color-ink);
  font-family: var(--font-display);
  font-weight: 500;
  letter-spacing: -0.035em;
}

h1 {
  font-size: var(--heading-md);
  line-height: 0.98;
}

h2 {
  font-size: var(--heading-sm);
  line-height: 1.08;
}

p,
li {
  text-wrap: pretty;
}

.article-style {
  font-size: var(--text-base);
  line-height: 1.78;
}

.article-style > p,
.article-style > ul,
.article-style > ol,
.article-style > blockquote {
  max-width: var(--reading-max);
}

.article-metadata,
.stream-meta,
.page-subtitle {
  color: var(--color-muted);
  font-size: var(--text-sm);
}
```

创建 `assets/scss/base/_accessibility.scss`：

```scss
.skip-link {
  position: fixed;
  top: var(--space-2);
  left: var(--space-2);
  z-index: 100;
  padding: 0.75rem 1rem;
  color: var(--color-inverse-text);
  background: var(--color-inverse);
  transform: translateY(-180%);
  transition: transform 180ms var(--ease-out);
}

.skip-link:focus {
  transform: translateY(0);
}

:focus-visible {
  outline: 3px solid var(--color-clay);
  outline-offset: 3px;
}

button,
.nav-link,
.js-search,
.pagination a,
.social-links a {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 5: 将入口文件改为纯导入**

用以下内容替换 `assets/scss/template.scss`：

```scss
@import "abstracts/tokens";
@import "abstracts/mixins";
@import "base/foundation";
@import "base/typography";
@import "base/accessibility";
@import "components/navigation";
@import "components/footer";
@import "components/entries";
@import "components/people";
@import "pages/home";
@import "pages/list";
@import "pages/article";
```

在尚未创建的导入位置先创建空文件：

```bash
mkdir -p assets/scss/components assets/scss/pages
touch assets/scss/components/{_navigation,_footer,_entries,_people}.scss
touch assets/scss/pages/{_home,_list,_article}.scss
```

- [ ] **Step 6: 禁用明暗切换并验证**

在 `config/_default/params.yaml` 的 `header.navbar` 中将：

```yaml
show_day_night: true
```

改为：

```yaml
show_day_night: false
```

Run: `./scripts/test-site.sh`

Expected: 所有 4 个测试 PASS。

- [ ] **Step 7: 提交基础设计系统**

```bash
git add assets/scss config/_default/params.yaml tests/test_generated_site.py
git commit -m "style: establish warm editorial design system" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 3: 重建全局导航和页脚

**Files:**
- Create: `layouts/partials/components/headers/editorial.html`
- Create: `layouts/partials/components/footers/editorial.html`
- Modify: `config/_default/params.yaml`
- Modify: `assets/scss/components/_navigation.scss`
- Modify: `assets/scss/components/_footer.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加导航与页脚失败测试**

```python
    def test_editorial_header_and_footer_are_rendered(self) -> None:
        homepage = self.page("/")
        self.assertIn('class="skip-link"', homepage)
        self.assertIn('class="editorial-header"', homepage)
        self.assertIn('aria-label="Primary navigation"', homepage)
        self.assertIn('class="editorial-footer-grid"', homepage)
        self.assertNotIn("theme-dropdown", homepage)

    def test_mobile_navigation_has_accessible_state(self) -> None:
        homepage = self.page("/")
        self.assertRegex(homepage, r'aria-controls="editorial-menu"')
        self.assertRegex(homepage, r'aria-expanded="false"')
        self.assertRegex(homepage, r'aria-label="[^"]+"')
```

Run: `./scripts/test-site.sh`

Expected: FAIL，缺少 `editorial-header`。

- [ ] **Step 2: 创建本地 header block**

创建 `layouts/partials/components/headers/editorial.html`：

```go-html-template
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="editorial-header" data-editorial-header>
  <nav class="editorial-nav navbar navbar-expand-lg" aria-label="Primary navigation">
    <div class="editorial-nav__inner">
      <a class="editorial-nav__brand" href="{{ site.Home.RelPermalink }}">
        {{ site.Title }}
      </a>

      <button class="editorial-nav__toggle navbar-toggler" type="button"
        data-toggle="collapse" data-target="#editorial-menu"
        aria-controls="editorial-menu" aria-expanded="false"
        aria-label="{{ i18n "toggle_navigation" | default "Toggle navigation" }}">
        <span aria-hidden="true"></span><span aria-hidden="true"></span>
      </button>

      <div class="editorial-nav__menu navbar-collapse collapse" id="editorial-menu">
        <ul class="editorial-nav__links navbar-nav">
          {{ range site.Menus.main }}
            {{ $isActive := or ($.IsMenuCurrent "main" .) ($.HasMenuCurrent "main" .) }}
            <li class="nav-item">
              <a class="nav-link{{ if $isActive }} active{{ end }}"
                href="{{ .URL | relLangURL }}"{{ if $isActive }} aria-current="page"{{ end }}>
                {{ .Name | safeHTML }}
              </a>
            </li>
          {{ end }}
        </ul>
      </div>

      {{ if and site.Params.features.search.provider site.Params.header.navbar.show_search }}
        <a class="editorial-nav__search nav-link js-search" href="#"
          aria-label="{{ i18n "search" | default "Search" }}">
          <i class="fas fa-search" aria-hidden="true"></i>
        </a>
      {{ end }}
    </div>
  </nav>
</header>
```

- [ ] **Step 3: 创建本地 footer block**

创建 `layouts/partials/components/footers/editorial.html`：

```go-html-template
<div class="editorial-footer-grid">
  <div class="editorial-footer-brand">{{ site.Title }}</div>
  <nav class="editorial-footer-nav" aria-label="Footer navigation">
    {{ range site.Menus.main }}
      <a href="{{ .URL | relLangURL }}">{{ .Name | safeHTML }}</a>
    {{ end }}
  </nav>
  <div class="editorial-footer-license">
    {{ partial "site_footer_license" . }}
  </div>
</div>
```

- [ ] **Step 4: 配置 block 并实现样式**

在 `config/_default/params.yaml` 中设置：

```yaml
header:
  navbar:
    block: editorial
    enable: true
    align: r
    show_logo: true
    show_language: false
    show_day_night: false
    show_search: true
    highlight_active_link: true

footer:
  block: editorial
```

创建 `assets/scss/components/_navigation.scss`：

```scss
.page-header.header--fixed {
  z-index: var(--z-header);
}

.editorial-header {
  border-bottom: 1px solid var(--color-line);
  background: rgba(242, 239, 231, 0.98);
  transition: min-height 220ms var(--ease-out);
}

.editorial-nav__inner {
  display: flex;
  align-items: center;
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  min-height: 4.5rem;
  margin-inline: auto;
}

.editorial-nav__brand {
  color: var(--color-ink);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
  text-transform: uppercase;
}

.editorial-nav__menu {
  justify-content: flex-end;
}

.editorial-nav__links {
  gap: clamp(0.25rem, 1.5vw, 1.5rem);
}

.editorial-nav .nav-link {
  display: inline-flex;
  align-items: center;
  color: var(--color-muted);
  font-size: var(--text-sm);
  text-decoration: none;
  transition: color 180ms var(--ease-out);
}

.editorial-nav .nav-link::after {
  position: absolute;
  right: 0.75rem;
  bottom: 0.35rem;
  left: 0.75rem;
  height: 1px;
  background: var(--color-clay);
  content: "";
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 180ms var(--ease-out);
}

.editorial-nav .nav-link:hover::after,
.editorial-nav .nav-link.active::after {
  transform: scaleX(1);
}

.editorial-nav__toggle {
  margin-left: auto;
  border: 0;
}

.editorial-nav__toggle span {
  display: block;
  width: 1.4rem;
  height: 1px;
  margin: 0.35rem 0;
  background: var(--color-ink);
}

.editorial-header.is-compact .editorial-nav__inner {
  min-height: 3.75rem;
}

@media (max-width: 991.98px) {
  .editorial-nav__menu {
    position: absolute;
    z-index: var(--z-menu);
    top: 100%;
    right: 0;
    left: 0;
    padding: var(--space-4) var(--page-gutter);
    border-bottom: 1px solid var(--color-line);
    background: var(--color-paper);
  }

  .editorial-nav__links .nav-link {
    width: 100%;
    border-bottom: 1px solid var(--color-line);
  }
}
```

创建 `assets/scss/components/_footer.scss`：

```scss
.page-footer {
  border-top: 1px solid var(--color-line);
  background: var(--color-paper);
}

.site-footer {
  padding: var(--space-6) 0 var(--space-4);
  font-size: var(--text-sm);
}

.editorial-footer-grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: var(--space-5);
  text-align: left;
}

.editorial-footer-brand {
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.editorial-footer-nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
}

.editorial-footer-nav a,
.site-footer .powered-by a {
  color: var(--color-muted);
  text-decoration-thickness: 1px;
}

.editorial-footer-license,
.site-footer .powered-by {
  color: var(--color-muted);
  text-align: left;
}

@media (max-width: 767.98px) {
  .editorial-footer-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 5: 运行回归测试**

Run: `./scripts/test-site.sh`

Expected: header/footer 测试 PASS；所有旧测试继续 PASS。

- [ ] **Step 6: 提交导航与页脚**

```bash
git add layouts/partials/components config/_default/params.yaml assets/scss/components tests/test_generated_site.py
git commit -m "feat: add editorial navigation and footer" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 4: 实现首页编辑式分屏 Hero

**Files:**
- Create: `layouts/partials/blocks/hero.html`
- Modify: `assets/scss/pages/_home.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加 Hero 结构失败测试**

```python
    def test_homepage_hero_is_editorial_split(self) -> None:
        homepage = self.page("/")
        self.assertIn('class="editorial-hero"', homepage)
        self.assertIn('class="editorial-hero__copy"', homepage)
        self.assertIn('class="editorial-hero__media"', homepage)
        self.assertRegex(homepage, r'<img[^>]+srcset="[^"]+"[^>]+sizes="[^"]+"')
        self.assertIn("banner", homepage.lower())
```

Run: `./scripts/test-site.sh`

Expected: FAIL，缺少 `editorial-hero`。

- [ ] **Step 2: 创建 Hero partial**

创建 `layouts/partials/blocks/hero.html`：

```go-html-template
{{ $page := .wcPage }}
{{ $block := .wcBlock }}
<section class="editorial-hero" aria-labelledby="editorial-hero-title">
  <div class="editorial-hero__copy">
    {{ with $block.content.title }}
      <h1 id="editorial-hero-title" class="editorial-hero__title" data-reveal>
        {{ . | markdownify }}
      </h1>
    {{ end }}
    {{ with $block.content.text }}
      <div class="editorial-hero__lead" data-reveal>
        {{ . | $page.RenderString | emojify }}
      </div>
    {{ end }}
  </div>

  {{ with $block.content.image.filename }}
    {{ $image := resources.Get (path.Join "media" .) }}
    {{ with $image }}
      {{ $small := .Fill "640x760 Center webp" }}
      {{ $medium := .Fill "960x1080 Center webp" }}
      {{ $large := .Fill "1440x1500 Center webp" }}
      <figure class="editorial-hero__media" data-reveal>
        <img
          src="{{ $small.RelPermalink }}"
          srcset="{{ $small.RelPermalink }} 640w, {{ $medium.RelPermalink }} 960w, {{ $large.RelPermalink }} 1440w"
          sizes="(max-width: 767px) 100vw, 48vw"
          width="{{ $large.Width }}"
          height="{{ $large.Height }}"
          alt="{{ $block.content.title | plainify }}">
      </figure>
    {{ end }}
  {{ end }}
</section>
```

- [ ] **Step 3: 实现 Hero 样式**

在 `assets/scss/pages/_home.scss` 写入：

```scss
.home-section:first-of-type {
  padding: 0;
  border-bottom: 1px solid var(--color-line);
}

.editorial-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 1fr);
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  min-height: min(46rem, calc(100vh - 4.5rem));
  margin-inline: auto;
}

.editorial-hero__copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--space-7) var(--space-6) var(--space-7) 0;
  border-right: 1px solid var(--color-line);
}

.editorial-hero__title {
  max-width: 7ch;
  margin: 0;
  font-size: var(--heading-hero);
  line-height: 0.84;
  letter-spacing: -0.065em;
}

.editorial-hero__lead {
  max-width: 34rem;
  margin-top: var(--space-5);
  color: var(--color-muted);
  font-size: var(--text-lg);
  line-height: 1.65;
}

.editorial-hero__media {
  min-height: 34rem;
  margin: 0;
  overflow: hidden;
}

.editorial-hero__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  border-radius: 0;
}

@media (max-width: 767.98px) {
  .editorial-hero {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .editorial-hero__copy {
    padding: var(--space-7) 0 var(--space-6);
    border-right: 0;
  }

  .editorial-hero__media {
    min-height: 0;
    aspect-ratio: 4 / 3;
    border-top: 1px solid var(--color-line);
  }
}
```

- [ ] **Step 4: 构建并检查 Hero 内容未变化**

Run:

```bash
./scripts/test-site.sh
git diff --exit-code -- content assets/media static
```

Expected: 测试全部 PASS；第二条命令无输出。若 Hugo 以压缩形式输出 CSS，测试只检查规则语义存在，不依赖空格格式。

- [ ] **Step 5: 提交 Hero**

```bash
git add layouts/partials/blocks/hero.html assets/scss/pages/_home.scss tests/test_generated_site.py
git commit -m "feat: build editorial split homepage hero" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 5: 统一首页集合和全站列表条目

**Files:**
- Create: `layouts/partials/views/editorial.html`
- Create: `layouts/partials/views/card.html`
- Create: `layouts/partials/views/compact.html`
- Create: `layouts/partials/views/list.html`
- Create: `layouts/partials/editorial/listing.html`
- Create: `layouts/_default/list.html`
- Create: `layouts/section/post.html`
- Modify: `assets/scss/components/_entries.scss`
- Modify: `assets/scss/pages/_list.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加列表结构失败测试**

```python
    def test_collection_pages_use_editorial_entries(self) -> None:
        for route in ("/post/", "/daily/", "/recruitment/", "/memory/"):
            html = self.page(route)
            self.assertIn('class="editorial-index"', html)
            self.assertIn('class="editorial-entry', html)

    def test_entries_work_with_and_without_featured_images(self) -> None:
        post = self.page("/post/")
        diary = self.page("/daily/")
        self.assertIn("editorial-entry--with-image", post)
        self.assertIn("editorial-entry--text", diary)
        self.assertNotIn("broken-image", diary)
```

Run: `./scripts/test-site.sh`

Expected: FAIL，缺少 `editorial-index`。

- [ ] **Step 2: 创建统一条目 partial 和视图代理**

创建 `layouts/partials/views/editorial.html`：

```go-html-template
{{ $item := .item }}
{{ $link := $item.RelPermalink }}
{{ $target := "" }}
{{ with $item.Params.external_link }}
  {{ $link = . }}
  {{ $target = "target=\"_blank\" rel=\"noopener\"" }}
{{ end }}
{{ $featured := partial "blox-core/functions/get_featured_image.html" $item }}
{{ $summary := $item.Params.summary | default $item.Params.abstract | default $item.Summary }}

<article class="editorial-entry {{ if $featured }}editorial-entry--with-image{{ else }}editorial-entry--text{{ end }}" data-reveal>
  <div class="editorial-entry__content">
    {{ partial "page_metadata" (dict "page" $item "is_list" 1) }}
    <h2 class="editorial-entry__title">
      <a href="{{ $link }}" {{ $target | safeHTMLAttr }}>{{ $item.Title }}</a>
    </h2>
    {{ with $summary }}
      <div class="editorial-entry__summary">{{ . | markdownify | emojify }}</div>
    {{ end }}
    <a class="editorial-entry__link" href="{{ $link }}" {{ $target | safeHTMLAttr }}
      aria-label="Read {{ $item.Title }}">Read <span aria-hidden="true">→</span></a>
  </div>

  {{ with $featured }}
    {{ $small := .Fill "400x300 Smart webp" }}
    {{ $medium := .Fill "800x600 Smart webp" }}
    <a class="editorial-entry__media" href="{{ $link }}" {{ $target | safeHTMLAttr }} tabindex="-1" aria-hidden="true">
      <img src="{{ $small.RelPermalink }}"
        srcset="{{ $small.RelPermalink }} 400w, {{ $medium.RelPermalink }} 800w"
        sizes="(max-width: 767px) 100vw, 36vw"
        width="{{ $medium.Width }}" height="{{ $medium.Height }}"
        alt="" loading="lazy">
    </a>
  {{ end }}
</article>
```

三个代理文件内容分别相同：

```go-html-template
{{ partial "views/editorial.html" . }}
```

写入：

- `layouts/partials/views/card.html`
- `layouts/partials/views/compact.html`
- `layouts/partials/views/list.html`

- [ ] **Step 3: 创建公共列表结构并接入 section**

创建 `layouts/partials/editorial/listing.html`：

```go-html-template
<section class="editorial-index" id="main-content" aria-labelledby="editorial-index-title">
  <header class="editorial-index__header">
    <h1 id="editorial-index-title">{{ .Title }}</h1>
    {{ with .Content }}<div class="editorial-index__intro article-style">{{ . }}</div>{{ end }}
  </header>
  <div class="editorial-index__entries">
    {{ $paginator := .Paginate .Pages }}
    {{ range $index, $item := $paginator.Pages }}
      {{ partial "functions/render_view" (dict "page" $ "item" . "view" ($.Params.view | default "compact") "index" $index) }}
    {{ end }}
  </div>
  {{ partial "pagination" . }}
</section>
```

创建 `layouts/_default/list.html` 和 `layouts/section/post.html`，两者使用相同内容：

```go-html-template
{{- define "main" -}}
  {{ partial "editorial/listing.html" . }}
{{- end -}}
```

- [ ] **Step 4: 实现条目和列表样式**

创建 `assets/scss/components/_entries.scss`：

```scss
.editorial-entry {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(14rem, 0.75fr);
  gap: var(--space-5);
  padding: var(--space-5) 0;
  border-top: 1px solid var(--color-line);
}

.editorial-entry--text {
  grid-template-columns: minmax(0, 52rem);
}

.editorial-entry__title {
  max-width: 22ch;
  margin: var(--space-2) 0 var(--space-3);
}

.editorial-entry__title a {
  color: var(--color-ink);
  text-decoration: none;
}

.editorial-entry__summary {
  max-width: 60ch;
  color: var(--color-muted);
}

.editorial-entry__link {
  display: inline-flex;
  align-items: center;
  min-height: 2.75rem;
  margin-top: var(--space-3);
  font-size: var(--text-sm);
  font-weight: 700;
  text-decoration-thickness: 1px;
}

.editorial-entry__link span {
  margin-left: var(--space-1);
  transition: transform 200ms var(--ease-out);
}

.editorial-entry__link:hover span {
  transform: translateX(0.25rem);
}

.editorial-entry__media {
  overflow: hidden;
}

.editorial-entry__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 250ms var(--ease-out);
}

.editorial-entry:hover .editorial-entry__media img {
  opacity: 0.82;
}

@media (max-width: 767.98px) {
  .editorial-entry {
    grid-template-columns: 1fr;
  }

  .editorial-entry__media {
    grid-row: 1;
    aspect-ratio: 4 / 3;
  }
}
```

创建 `assets/scss/pages/_list.scss`：

```scss
.editorial-index {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  margin-inline: auto;
  padding: var(--space-7) 0;
}

.editorial-index__header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 0.55fr);
  gap: var(--space-6);
  padding-bottom: var(--space-6);
}

.editorial-index__header h1 {
  margin: 0;
  font-size: var(--heading-md);
}

.editorial-index__intro {
  align-self: end;
  color: var(--color-muted);
}

.pagination {
  gap: var(--space-2);
  margin-top: var(--space-6);
}

.page-link {
  border: 0;
  border-bottom: 1px solid var(--color-line);
  color: var(--color-ink);
  background: transparent;
}

@media (max-width: 767.98px) {
  .editorial-index__header {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 5: 验证列表与首页 collection**

Run: `./scripts/test-site.sh`

Expected: 所有测试 PASS；首页仍包含 `INTRODUCTION`，Post 和 Diary 均包含 editorial entry。

- [ ] **Step 6: 提交列表系统**

```bash
git add layouts/_default layouts/section layouts/partials/editorial layouts/partials/views assets/scss/components/_entries.scss assets/scss/pages/_list.scss tests/test_generated_site.py
git commit -m "feat: unify editorial content listings" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 6: 重建 People 与成员档案视觉

**Files:**
- Create: `layouts/partials/blocks/people.html`
- Modify: `assets/scss/components/_people.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加 People 失败测试**

```python
    def test_people_groups_and_profiles_are_accessible(self) -> None:
        people = self.page("/people/")
        self.assertIn('class="editorial-people"', people)
        self.assertIn('class="editorial-person"', people)
        self.assertIn("Team members", people)
        self.assertRegex(people, r'<img[^>]+alt="Portrait of [^"]+"')
        self.assertRegex(people, r'<img[^>]+srcset="[^"]+"[^>]+sizes="[^"]+"')
```

Run: `./scripts/test-site.sh`

Expected: FAIL，缺少 `editorial-people`。

- [ ] **Step 2: 创建 People block**

创建 `layouts/partials/blocks/people.html`：

```go-html-template
{{ $block := .wcBlock }}
<section class="editorial-people" aria-labelledby="editorial-people-title">
  {{ with $block.content.title }}
    <h1 id="editorial-people-title" class="editorial-people__title">{{ . | markdownify }}</h1>
  {{ end }}

  {{ range $group := $block.content.user_groups }}
    {{ $people := where (where site.Pages "Section" "authors") ".Params.user_groups" "intersect" (slice $group) }}
    {{ $people = sort $people ($block.content.sort_by | default "Params.last_name") (cond ($block.content.sort_ascending | default true) "asc" "desc") }}
    {{ if $people }}
      <section class="editorial-people__group" aria-labelledby="group-{{ $group | anchorize }}">
        <h2 id="group-{{ $group | anchorize }}">{{ $group | markdownify }}</h2>
        <div class="editorial-people__grid">
          {{ range $people }}
            {{ $avatar := (.Resources.ByType "image").GetMatch "*avatar*" }}
            {{ $profile := site.GetPage (printf "/authors/%s" (path.Base .File.Dir)) }}
            <article class="editorial-person" data-reveal>
              {{ with $avatar }}
                {{ $small := .Fill "320x320 Center webp" }}
                {{ $large := .Fill "640x640 Center webp" }}
                <a class="editorial-person__portrait" href="{{ $profile.RelPermalink }}" tabindex="-1" aria-hidden="true">
                  <img src="{{ $small.RelPermalink }}"
                    srcset="{{ $small.RelPermalink }} 320w, {{ $large.RelPermalink }} 640w"
                    sizes="(max-width: 575px) 50vw, (max-width: 991px) 33vw, 25vw"
                    width="{{ $large.Width }}" height="{{ $large.Height }}"
                    alt="Portrait of {{ $.Title }}" loading="lazy">
                </a>
              {{ end }}
              <div class="editorial-person__body">
                <h3><a href="{{ $profile.RelPermalink }}">{{ .Title }}</a></h3>
                {{ with .Params.role }}<p>{{ . | markdownify }}</p>{{ end }}
                {{ if $block.design.show_social }}{{ partial "social_links" . }}{{ end }}
              </div>
            </article>
          {{ end }}
        </div>
      </section>
    {{ end }}
  {{ end }}
</section>
```

实现时注意 Go template 作用域：头像 `alt` 必须使用当前人物标题。若 `with $avatar` 改变了点上下文，先在进入 `with` 前保存 `{{ $person := . }}`，再使用 `{{ $person.Title }}`；不要使用根上下文标题。

- [ ] **Step 3: 实现 People 和档案样式**

写入 `assets/scss/components/_people.scss`：

```scss
.editorial-people {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  margin-inline: auto;
  padding: var(--space-7) 0;
}

.editorial-people__title {
  margin-bottom: var(--space-7);
  font-size: var(--heading-md);
}

.editorial-people__group {
  padding: var(--space-6) 0;
  border-top: 1px solid var(--color-line);
}

.editorial-people__group > h2 {
  margin-bottom: var(--space-5);
  color: var(--color-clay-dark);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.editorial-people__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-6) var(--space-4);
}

.editorial-person__portrait {
  display: block;
  aspect-ratio: 1;
  overflow: hidden;
}

.editorial-person__portrait img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.85);
  transition: opacity 250ms var(--ease-out);
}

.editorial-person:hover img {
  opacity: 0.84;
}

.editorial-person h3 {
  margin: var(--space-3) 0 var(--space-1);
  font-size: var(--text-lg);
}

.editorial-person h3 a {
  text-decoration: none;
}

.editorial-person p {
  margin: 0;
  color: var(--color-muted);
  font-size: var(--text-sm);
}

#profile-page .container {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
}

#profile-page .resume-biography {
  border-top: 1px solid var(--color-line);
}

@media (max-width: 991.98px) {
  .editorial-people__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .editorial-people__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-5) var(--space-3);
  }
}
```

- [ ] **Step 4: 修正模板作用域并运行测试**

Run: `./scripts/test-site.sh`

Expected: People 测试 PASS；生成页面每个头像具有对应人物姓名 alt，构建无 template scope 错误。

- [ ] **Step 5: 提交 People 改造**

```bash
git add layouts/partials/blocks/people.html assets/scss/components/_people.scss tests/test_generated_site.py
git commit -m "feat: redesign people directory" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 7: 重建文章排版与响应式正文图片

**Files:**
- Create: `layouts/_default/_markup/render-image.html`
- Modify: `layouts/partials/page_header.html`
- Modify: `assets/scss/pages/_article.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加文章图像和阅读栏失败测试**

```python
    def test_article_uses_reading_width_and_responsive_images(self) -> None:
        article = self.page("/post/2025-06-03-asc2024-prize/")
        self.assertIn('class="article editorial-article"', article)
        self.assertRegex(article, r'<img[^>]+srcset="[^"]+"[^>]+sizes="[^"]+"')
        self.assertIn("喜报", article)
        self.assertIn("国际二等奖", article)

    def test_diary_images_keep_alt_and_dimensions(self) -> None:
        diary = self.page("/daily/2025-12-21/")
        images = re.findall(r"<img\b[^>]*>", diary)
        self.assertTrue(images)
        for image in images:
            self.assertIn("alt=", image)
            self.assertIn("width=", image)
            self.assertIn("height=", image)
```

同时将本地 `layouts/_default/single.html` 创建为：

```go-html-template
{{- define "main" -}}
<article class="article editorial-article" id="main-content">
  {{ partial "page_header" . }}
  <div class="article-container editorial-article__container">
    <div class="article-style">{{ .Content }}</div>
    {{ partial "page_footer" . }}
  </div>
</article>
{{- end -}}
```

先只加入测试和 single 模板，然后运行 `./scripts/test-site.sh`。

Expected: responsive image 测试 FAIL，因为主图或正文图缺少 `sizes`。

- [ ] **Step 2: 覆盖 Markdown 图片 renderer**

创建 `layouts/_default/_markup/render-image.html`：

```go-html-template
{{ $destination := .Destination }}
{{ $caption := .Title | default "" }}
{{ $alt := .Text | default ($caption | plainify) }}
{{ $isRemote := strings.HasPrefix $destination "http" }}
{{ $image := "" }}
{{ if not $isRemote }}
  {{ $image = (.Page.Resources.ByType "image").GetMatch $destination }}
  {{ if not $image }}{{ $image = resources.Get (path.Join "media" $destination) }}{{ end }}
{{ end }}

<figure class="editorial-figure">
  {{ with $image }}
    {{ if or (eq .MediaType.SubType "svg") (eq .MediaType.SubType "gif") }}
      <img src="{{ .RelPermalink }}" width="{{ .Width }}" height="{{ .Height }}"
        alt="{{ $alt }}" loading="lazy" data-zoomable>
    {{ else }}
      {{ $small := .Fit "480x480 webp" }}
      {{ $medium := .Fit "800x800 webp" }}
      {{ $large := .Fit "1400x1400 webp" }}
      <img src="{{ $small.RelPermalink }}"
        srcset="{{ $small.RelPermalink }} 480w, {{ $medium.RelPermalink }} 800w, {{ $large.RelPermalink }} 1400w"
        sizes="(max-width: 767px) calc(100vw - 40px), 70ch"
        width="{{ $medium.Width }}" height="{{ $medium.Height }}"
        alt="{{ $alt }}" loading="lazy" data-zoomable>
    {{ end }}
  {{ else }}
    <img src="{{ $destination | safeURL }}" alt="{{ $alt }}" loading="lazy">
  {{ end }}
  {{ with $caption }}<figcaption>{{ . | markdownify }}</figcaption>{{ end }}
</figure>
```

- [ ] **Step 3: 修改 page header 的主图输出**

以主题原始 `layouts/partials/page_header.html` 为基线复制到本地，然后只替换两处 `<img>` 输出：

Banner 图片使用：

```go-html-template
{{ $small := $img.Fit "640x640 webp" }}
{{ $medium := $img.Fit "1200x1200 webp" }}
<img src="{{ $small.RelPermalink }}"
  srcset="{{ $small.RelPermalink }} 640w, {{ $medium.RelPermalink }} 1200w"
  sizes="100vw" width="{{ $medium.Width }}" height="{{ $medium.Height }}"
  class="article-banner" alt="{{ $alt }}">
```

Featured 图片使用：

```go-html-template
{{ $small := $featured.Fit "640x1200 webp" }}
{{ $medium := $featured.Fit "1200x2000 webp" }}
{{ $large := $featured.Fit "1800x2400 webp" }}
<img src="{{ $small.RelPermalink }}"
  srcset="{{ $small.RelPermalink }} 640w, {{ $medium.RelPermalink }} 1200w, {{ $large.RelPermalink }} 1800w"
  sizes="(max-width: 767px) calc(100vw - 40px), 70ch"
  width="{{ $medium.Width }}" height="{{ $medium.Height }}"
  alt="{{ with $.Params.image.alt_text }}{{ . }}{{ else }}{{ $.Title }}{{ end }}"
  class="featured-image">
```

保留原 partial 的标题、subtitle、metadata、placement 和 caption 分支，不删除任何内容功能。

- [ ] **Step 4: 实现文章样式**

写入 `assets/scss/pages/_article.scss`：

```scss
.editorial-article {
  padding: var(--space-6) 0 var(--space-7);
}

.editorial-article .article-container,
.editorial-article__container {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--reading-max));
  margin-inline: auto;
}

.editorial-article .article-container > h1 {
  margin-bottom: var(--space-4);
  font-size: var(--heading-md);
}

.editorial-article .article-metadata {
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-line);
}

.editorial-article .article-style {
  margin-top: var(--space-6);
}

.editorial-article .article-style h2,
.editorial-article .article-style h3 {
  margin-top: var(--space-6);
}

.editorial-figure {
  margin: var(--space-5) 0;
}

.editorial-figure img {
  width: 100%;
}

.editorial-figure figcaption,
.article-header-caption {
  margin-top: var(--space-2);
  color: var(--color-muted);
  font-size: var(--text-sm);
  text-align: left;
}

.article-style blockquote {
  margin: var(--space-5) 0;
  padding-left: var(--space-4);
  border-left: 2px solid var(--color-clay);
  color: var(--color-muted);
}

.article-style pre,
.article-style table {
  max-width: 100%;
  overflow-x: auto;
}

.author-card,
.article-widget {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
  box-shadow: none;
}
```

- [ ] **Step 5: 运行文章回归测试**

Run: `./scripts/test-site.sh`

Expected: 文章和 Diary 测试 PASS，Hugo 无图片处理错误。

- [ ] **Step 6: 提交文章系统**

```bash
git add layouts/_default layouts/partials/page_header.html assets/scss/pages/_article.scss tests/test_generated_site.py
git commit -m "feat: add editorial article layout" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 8: 完成首页其余区块、Accomplishments、Contact 和 Publication

**Files:**
- Modify: `assets/scss/pages/_home.scss`
- Modify: `assets/scss/pages/_list.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加内容保留与区块可用性测试**

```python
    def test_accomplishments_and_contact_content_remain(self) -> None:
        homepage = self.page("/")
        accomplishments = self.page("/accomplishments/")
        contact = self.page("/contact/")
        for text in ("IPCC Excellence Award", "CPC Excellence Award", "ASC2024 Second Prize"):
            self.assertIn(text, homepage)
            self.assertIn(text, accomplishments)
        self.assertIn("Contact", contact)

    def test_publication_filters_remain_available(self) -> None:
        publications = self.page("/publication/")
        self.assertIn("filter-search", publications)
        self.assertIn("container-publications", publications)
```

Run: `./scripts/test-site.sh`

Expected: 内容保留测试 PASS；这一步建立之后样式改动的回归保护。

- [ ] **Step 2: 补充首页编辑节奏样式**

追加到 `assets/scss/pages/_home.scss`：

```scss
.home-section:not(:first-of-type) {
  padding: var(--space-7) 0;
  border-bottom: 1px solid var(--color-line);
}

.home-section .section-heading {
  margin-bottom: var(--space-6);
  text-align: left;
}

.home-section .section-heading h1 {
  font-size: var(--heading-md);
}

.home-section .editorial-entry:first-child {
  grid-template-columns: minmax(0, 1fr) minmax(20rem, 1fr);
  padding-top: 0;
  border-top: 0;
}

#accomplishments .article-style > ul {
  max-width: none;
  margin: 0;
  padding: 0;
  list-style: none;
}

#accomplishments .article-style > ul > li {
  display: grid;
  grid-template-columns: minmax(10rem, 0.35fr) minmax(0, 1fr);
  gap: var(--space-4);
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-line);
}

#accomplishments strong {
  color: var(--color-clay-dark);
  font-family: var(--font-display);
  font-size: var(--text-lg);
}

.cta-group {
  display: block;
  text-align: left;
}

.cta-group .btn {
  width: 100%;
  padding: var(--space-5) 0;
  border: 0;
  border-bottom: 1px solid var(--color-ink);
  border-radius: 0;
  color: var(--color-ink);
  background: transparent;
  font-family: var(--font-display);
  font-size: var(--heading-sm);
  text-align: left;
}

.wg-contact .contact-widget {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-6);
}

@media (max-width: 767.98px) {
  .home-section .editorial-entry:first-child,
  #accomplishments .article-style > ul > li,
  .wg-contact .contact-widget {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 3: 补充 Publication 和普通内容页样式**

追加到 `assets/scss/pages/_list.scss`：

```scss
.universal-wrapper {
  width: min(calc(100% - (2 * var(--page-gutter))), var(--content-max));
  padding: var(--space-7) 0;
}

.form-row {
  gap: var(--space-2);
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-line);
  border-bottom: 1px solid var(--color-line);
}

.form-control {
  min-height: 2.75rem;
  border-color: var(--color-line-strong);
  border-radius: 0;
  color: var(--color-ink);
  background: var(--color-paper);
}

.view-citation,
.pub-list-item,
.view-list-item {
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--color-line);
}

.article-style > h2 {
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-line);
}
```

- [ ] **Step 4: 运行完整内容回归测试**

Run:

```bash
./scripts/test-site.sh
git diff --exit-code -- content assets/media static
```

Expected: 所有测试 PASS；内容和素材目录无改动。

- [ ] **Step 5: 提交区块完善**

```bash
git add assets/scss/pages tests/test_generated_site.py
git commit -m "style: complete editorial page treatments" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 9: 加入渐进式二维品牌动效

**Files:**
- Create: `assets/js/editorial.js`
- Modify: `config/_default/params.yaml`
- Modify: `assets/scss/base/_accessibility.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加脚本加载和减少动态测试**

```python
    def test_editorial_script_is_bundled(self) -> None:
        homepage = self.page("/")
        scripts = re.findall(r'<script[^>]+src="([^"]+)"', homepage)
        self.assertTrue(any("wowchemy" in src for src in scripts))
        source = (ROOT / "assets/js/editorial.js").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", source)
        self.assertIn("IntersectionObserver", source)
        self.assertIn("data-editorial-header", source)

    def test_reduced_motion_css_is_compiled(self) -> None:
        self.assertIn("prefers-reduced-motion:reduce", self.all_css())
```

Run: `./scripts/test-site.sh`

Expected: ERROR 或 FAIL，因为 `assets/js/editorial.js` 尚不存在。

- [ ] **Step 2: 创建原生脚本**

创建 `assets/js/editorial.js`：

```javascript
(() => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const header = document.querySelector("[data-editorial-header]");

  const updateHeader = () => {
    if (!header) return;
    header.classList.toggle("is-compact", window.scrollY > 24);
  };

  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  if (reducedMotion.matches || !("IntersectionObserver" in window)) {
    document.querySelectorAll("[data-reveal]").forEach((element) => {
      element.classList.add("is-visible");
    });
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8%", threshold: 0.12 },
  );

  document.querySelectorAll("[data-reveal]").forEach((element, index) => {
    element.classList.add("is-reveal-ready");
    element.style.setProperty("--reveal-delay", `${Math.min(index % 3, 2) * 90}ms`);
    observer.observe(element);
  });
})();
```

- [ ] **Step 3: 配置 Hugo Blox 打包脚本**

在 `config/_default/params.yaml` 顶层加入：

```yaml
plugins_js:
  - editorial
```

- [ ] **Step 4: 添加渐进式动效 CSS**

追加到 `assets/scss/base/_accessibility.scss`：

```scss
[data-reveal].is-reveal-ready {
  opacity: 0;
  transform: translateY(0.875rem);
  transition:
    opacity 420ms var(--ease-out) var(--reveal-delay, 0ms),
    transform 420ms var(--ease-out) var(--reveal-delay, 0ms);
}

[data-reveal].is-reveal-ready.is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  [data-reveal],
  [data-reveal].is-reveal-ready {
    opacity: 1;
    transform: none;
  }
}
```

该实现满足无 JavaScript 时内容默认可见：只有脚本加入 `is-reveal-ready` 后，元素才会进入等待状态。

- [ ] **Step 5: 运行脚本与构建测试**

Run: `./scripts/test-site.sh`

Expected: 所有测试 PASS；生成 bundle 中包含本地插件，无 JavaScript 语法构建错误。

- [ ] **Step 6: 提交动效**

```bash
git add assets/js/editorial.js assets/scss/base/_accessibility.scss config/_default/params.yaml tests/test_generated_site.py
git commit -m "feat: add accessible editorial motion" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 10: 强化生成站点的无障碍与结构审计

**Files:**
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: 添加图片、标题和横向溢出静态审计**

在测试文件中加入以下辅助方法与测试：

```python
    def tags(self, html: str, tag: str) -> list[str]:
        return re.findall(rf"<{tag}\\b[^>]*>", html, flags=re.IGNORECASE)

    def test_key_pages_have_one_primary_heading(self) -> None:
        for route in ("/", "/people/", "/post/", "/daily/", "/contact/"):
            headings = self.tags(self.page(route), "h1")
            self.assertEqual(1, len(headings), f"{route} should have one h1")

    def test_generated_images_have_alt_text(self) -> None:
        for route in (
            "/",
            "/people/",
            "/post/2025-06-03-asc2024-prize/",
            "/daily/2025-12-21/",
        ):
            for image in self.tags(self.page(route), "img"):
                self.assertRegex(image, r'\balt="[^"]*"')

    def test_navigation_touch_targets_are_defined(self) -> None:
        css = self.all_css()
        self.assertIn("min-height:2.75rem", css)
        self.assertIn("outline:3px solid var(--color-clay)", css)
```

- [ ] **Step 2: 运行测试并记录实际失败**

Run: `./scripts/test-site.sh`

Expected: 如果某页面有两个 H1 或某主题图片缺少 alt，测试明确打印对应 route。不要放宽测试；修复产生问题的本地 partial 或把非主标题改为 H2。

- [ ] **Step 3: 修复审计发现的问题**

只修改本计划已创建的本地模板。修复规则固定为：

- 每页一个 H1；区块标题从 H2 开始。
- 装饰图像使用 `alt=""` 和 `aria-hidden="true"`。
- 有语义的图片使用现有标题或人物名称作为 alt。
- 图标按钮必须有 `aria-label`，图标自身 `aria-hidden="true"`。
- 不删除搜索、菜单、作者或文章内容来通过测试。

Run: `./scripts/test-site.sh`

Expected: 全部 PASS。

- [ ] **Step 4: 提交审计测试与修复**

```bash
git add tests/test_generated_site.py layouts assets/scss
git commit -m "test: enforce editorial accessibility contract" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

### Task 11: 更新仓库开发说明并进行最终验收

**Files:**
- Modify: `CLAUDE.md`
- Verify: all changed files

#### 当前验收记录（2026-08-11）

- [x] `./scripts/test-site.sh`：64 个生成站点回归测试通过（以执行时的最新测试总数为准）。
- [x] 生产式 Hugo 构建：Hugo Extended 0.135.0 执行 `hugo --gc --minify` 成功，生成 118 个页面、125 个处理后图片和 13 个别名，退出码为 0。
- [x] 受保护目录差异检查：`git diff --exit-code -- content assets/media static` 无输出、退出码为 0；`git diff --check` 无输出。
- [x] 本地预览路由 smoke：`hugo server --buildDrafts --buildFuture --bind 127.0.0.1 --port 57869` 启动成功；`/`、`/people/`、作者页、列表页、文章页、Diary、Accomplishments、Contact、Publication 和 `/tour/` 共 11 条受影响路由均返回 HTTP 200，之后服务器已正常停止。
- [ ] 浏览器自动化在当前环境不可用（仅有 Node，无 Playwright/Chromium/Chrome）；以下人工验收仍待完成：375px、768px、1024px、1440px 的视觉检查，键盘 Tab/焦点检查，以及禁用 JavaScript 的基础可访问性检查。不得将这些检查标记为已完成，直到在浏览器中实际执行并记录结果。

- [x] **Step 1: 更新开发命令**

在 `CLAUDE.md` 的 Commands 节记录仓库回归测试入口：

```markdown
Run the repository regression suite with:

```bash
./scripts/test-site.sh
```
```

受限网络说明必须是可选的：要求 Hugo Extended 0.135.0 与 Go 位于调用方的 `PATH`，说明直接 GitHub 访问取决于环境，并仅以保留调用方既有 `GOPROXY`、`GOSUMDB`、`GOMODCACHE` 和 `HUGO_BIN` 值的示例展示组织批准的网络配置。不得断言某台机器的 `~/.local` 路径、强制指定代理或校验和数据库，或推荐特定 GitHub 中继服务。

同时说明仓库没有第三方测试框架，但 `scripts/test-site.sh` 使用 Python 标准库构建并检查关键页面；单个测试可运行：

```bash
python3 -m unittest tests.test_generated_site.GeneratedSiteTests.test_homepage_hero_is_editorial_split -v
```

- [x] **Step 2: 运行完整自动验证**

当前记录：Python 标准库生成站点回归套件 64 项全部通过；Hugo Extended 0.135.0 生产式构建成功；差异与受保护路径检查通过。

Run:

```bash
./scripts/test-site.sh
hugo --gc --minify

git diff --check
git diff --exit-code -- content assets/media static
```

Expected:

- Python 测试全部 PASS；
- Hugo 报告成功生成页面，退出码 0；
- `git diff --check` 无输出；
- 内容和素材目录无 diff。

- [x] **Step 3: 启动最终本地预览并执行路由 smoke**

Run:

```bash
hugo server --buildDrafts --buildFuture --bind 127.0.0.1 --port 1313
```

Expected: 输出 `Web Server is available at http://localhost:1313/`。在服务器运行期间，请求受影响路由（至少 `/`、`/people/`、`/post/`、`/publication/`）并记录 HTTP 成功响应；仅看到启动日志不足以完成 smoke 检查。

- [ ] **Step 4: 按目标视口执行人工视觉、键盘与无 JavaScript 验收**

当前环境没有可用的浏览器自动化；本步骤尚未执行。请在可用浏览器中逐页检查：

- `/`
- `/people/`
- `/author/sizhe-qiao-乔思喆/`
- `/post/`
- `/post/2025-06-03-asc2024-prize/`
- `/daily/`
- `/daily/2025-12-21/`
- `/accomplishments/`
- `/contact/`
- `/publication/`

每页分别检查 375px、768px、1024px、1440px，并确认：

- 页面主体没有横向滚动；
- 导航不遮住内容，移动菜单可打开和关闭；
- Tab 顺序合理，焦点环始终可见；
- 首页 Hero 在桌面分栏、移动端纵向；
- 有图和无图条目均无空白占位；
- People 在手机 2 列、平板 3 列、桌面 4 列；
- 正文宽度、行高、图片和长中文标题可读；
- 搜索和 Publication 过滤器仍可操作；
- 开启系统“减少动态效果”后，所有内容立即出现且没有位移动画；
- 禁用 JavaScript 后，内容、链接和导航基础功能仍可访问。

如果任一项不满足，记录页面和宽度，修复对应本地 SCSS 或 partial，然后重新执行 Step 2。

- [ ] **Step 5: 最终提交**

仅在 Step 2、Step 3 和 Step 4 的所有必需检查均实际完成并记录后提交；当前不可将浏览器相关验收作为已完成。本次任务不创建提交。

```bash
git add CLAUDE.md docs/superpowers/specs/2026-08-10-warm-editorial-redesign-design.md docs/superpowers/plans/2026-08-10-warm-editorial-redesign.md
git commit -m "docs: document editorial site workflow" -m "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: 检查最终工作区**

当前工作区检查仅用于记录状态；Task 11 不应声称视觉重建相关文件已提交，因为本任务明确不创建提交。

Run:

```bash
git status --short
git log --oneline -11
```

Expected: 仅保留实施前已经存在且不属于本功能的未跟踪 `.claude/`、`.superpowers/`；视觉重建相关文件均已提交。不要提交 `.superpowers/brainstorm/` 视觉草稿。
