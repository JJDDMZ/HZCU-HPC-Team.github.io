# 桌面端字号收敛与 Accomplishments 调整实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 1024px 以上收敛全站展示型字号和 People/个人详情密度，重排独立 Accomplishments 页面，移除首页奖项区块，保持常驻导航，并加入无 hover 的奖项入场轻微上浮。

**Architecture:** 继续使用 Hugo Blox 混合覆盖。内容保留在现有 Markdown/YAML 中；首页通过 landing 配置/模板移除 Accomplishments 区块，独立 Accomplishments 使用现有列表/Markdown 结构和 scoped SCSS。People、作者详情、导航和 CTA 通过现有本地 partial/SCSS 覆盖；奖项复用 `data-reveal` 与现有 `assets/js/editorial.js`，只新增目标选择器和 reduced-motion 规则，不引入新依赖。

**Tech Stack:** Hugo Extended 0.135.0, Hugo Blox modules, Go templates, SCSS compiled by Hugo, vanilla JavaScript, Python `unittest` generated-site suite.

---

## 文件职责地图

- `content/_index.md`: 首页 sections 数据；只移除首页 Accomplishments markdown section，不编辑独立奖项内容。
- `content/accomplishments/_index.md`: 独立奖项原始内容；保持内容不变，模板/SCSS负责呈现。
- `assets/scss/abstracts/_tokens.scss`: 如需新增桌面字号 token，只在此集中定义，避免散落 magic numbers。
- `assets/scss/pages/_home.scss`: 桌面展示型标题、首页 CTA 胶囊按钮与首页节奏。
- `assets/scss/components/_people.scss`: People 网格、头像、姓名字号和作者详情左栏桌面密度。
- `assets/scss/pages/_list.scss` / `layouts/_default/list.html` / 现有 editorial listing partial: Accomplishments 标题、年份与奖项条目的结构/样式。
- `assets/scss/components/_navigation.scss` / `layouts/partials/components/headers/editorial.html`: 常驻导航、滚动压缩可见性和右侧按钮字体。
- `assets/scss/template.scss`: 仅在现有模块导入顺序需要时调整，不复制远程主题。
- `assets/js/editorial.js`: 复用 reveal 机制；不添加 hover 动画。
- `tests/test_generated_site.py`: 先写失败测试，覆盖首页移除、奖项保留/分组、People/作者/CTA/导航 CSS 合同与 reduced-motion。
- `docs/superpowers/specs/2026-08-11-desktop-typography-and-accomplishments-design.md`: 已确认设计依据。

---

### Task 1: 锁定首页移除与 Accomplishments 内容保留

**Files:**
- Modify: `tests/test_generated_site.py`
- Modify: `content/_index.md`
- Test output: generated `index.html`, `accomplishments/index.html`

- [ ] **Step 1: Write the failing tests**

在 `GeneratedSiteTests` 新增：

```python
def test_homepage_removes_accomplishments_but_independent_page_keeps_awards(self):
    self.assertNotIn('id="accomplishments"', self.homepage)
    self.assertNotIn("ACCOMPLISHMENTS", self.homepage)
    accomplishments = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
    for expected in ("Accomplishments", "2022年", "2023年", "2024年", "2025年", "IPCC Excellence Award", "ASC2024 Second Prize"):
        with self.subTest(expected=expected):
            self.assertIn(expected, accomplishments)
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run:

```bash
PATH="$HOME/.local/bin:$PATH" ./scripts/test-site.sh
```

Expected: 新测试 FAIL，因为当前首页 `content/_index.md` 仍包含 `id: accomplishments` 和 `ACCOMPLISHMENTS` 文本。

- [ ] **Step 3: Implement the minimal content configuration change**

从 `content/_index.md` 删除仅首页使用的以下 section（保留独立页面内容）：

```yaml
  - block: markdown
    content:
      title: ACCOMPLISHMENTS
      text: |
        - **IPCC Excellence Award**
          *Date:* Aug. 2022
        - **CPC Excellence Award**
          *Date:* Aug. 2023
        - **ASC2024 Second Prize**
          *Date:* Feb. 2024
        - **ASC2025 Second Prize**
          *Date:* Feb. 2025
    design:
      columns: '1'
    id: accomplishments
```

- [ ] **Step 4: Run focused test to verify it passes**

Run the single test command above. Expected: PASS; independent page still contains all award text.

> Note: 用户原先要求不改奖项内容；本次新增明确要求移除首页区块，因此只改首页 section 配置，不改 `content/accomplishments/_index.md`。

---

### Task 2: Add failing desktop scale and People/profile contracts

**Files:**
- Modify: `tests/test_generated_site.py`
- Modify: `assets/scss/components/_people.scss`
- Modify: `assets/scss/pages/_home.scss`
- Modify: `assets/scss/pages/_list.scss` if Accomplishments title contract lives there

- [ ] **Step 1: Add failing source/CSS contracts**

```python
def test_desktop_type_scale_and_people_density_are_constrained(self):
    css = "".join(path.read_text(encoding="utf-8") for path in self.output.rglob("*.css"))
    people = (REPO_ROOT / "assets/scss/components/_people.scss").read_text(encoding="utf-8")
    self.assertIn("@media (min-width: 64rem)", people)
    self.assertIn("grid-template-columns: repeat(4", people)
    self.assertIn("max-width: 80rem", people)
    self.assertRegex(people, r"font-size: clamp\(1\.2rem, [^;]+, 1\.5rem\)")
    self.assertIn("--heading-hero-compact", css)
    self.assertIn("--heading-display-compact", css)
    self.assertIn("#profile-page .portrait-title h1", css)
```

- [ ] **Step 2: Run the focused test and verify RED**

Expected: FAIL because the compact tokens/media query/profile H1 selector do not yet exist.

- [ ] **Step 3: Implement minimal styles**

Add tokens in `_tokens.scss`:

```scss
--heading-hero-compact: clamp(3rem, 2rem + 3.5vw, 5.5rem);
--heading-display-compact: clamp(2.25rem, 1.6rem + 1.8vw, 4.5rem);
```

Add a desktop-only override in `_people.scss`:

```scss
@media (min-width: 64rem) {
  .editorial-people {
    max-width: 80rem;
    padding-block: 4rem 6rem;
  }

  .editorial-people__intro {
    margin-bottom: 3rem;
  }

  .editorial-people__group + .editorial-people__group {
    margin-top: 4rem;
    padding-top: 2.5rem;
  }

  .editorial-person h3 {
    font-size: clamp(1.2rem, 1.05rem + 0.35vw, 1.5rem);
  }

  #profile-page .portrait-title h1 {
    font-size: clamp(2.25rem, 1.8rem + 1vw, 2.5rem);
    line-height: 1.05;
  }
}
```

Use `_home.scss` for desktop hero/section display scale:

```scss
@media (min-width: 64rem) {
  .editorial-hero__copy h1 { font-size: var(--heading-hero-compact); }
  .home-section .section-heading h1,
  .home-section .section-heading h2 { font-size: var(--heading-display-compact); }
}
```

Use `_list.scss` to cap the independent Accomplishments page heading and preserve readable list width; do not lower base body text.

- [ ] **Step 4: Run focused tests to verify GREEN**

```bash
python3 -m unittest tests.test_generated_site.GeneratedSiteTests.test_desktop_type_scale_and_people_density_are_constrained -v
```

Expected: PASS.

---

### Task 3: Rebuild Accomplishments heading/list structure and entrance animation

**Files:**
- Modify: `layouts/_default/list.html` or the existing scoped editorial listing partial after confirming route/type; do not duplicate unrelated list templates.
- Modify: `assets/scss/pages/_list.scss`
- Modify: `assets/js/editorial.js` only for selector hook if existing generic `data-reveal` cannot target award entries.
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: Add failing structure/animation tests**

```python
def test_accomplishments_is_left_aligned_year_grouped_and_reveals_without_hover_motion(self):
    page = (self.output / "accomplishments/index.html").read_text(encoding="utf-8")
    self.assertRegex(page, r'<h1[^>]*>\s*Accomplishments\s*</h1>')
    for year in ("2022年", "2023年", "2024年", "2025年"):
        self.assertIn(year, page)
    css = "".join(path.read_text(encoding="utf-8") for path in self.output.rglob("*.css"))
    self.assertIn("data-reveal", page)
    self.assertIn("transform: translateY(12px)", css)
    self.assertIn("prefers-reduced-motion: reduce", css)
    self.assertNotRegex(css, r"accomplishments[^}]+:hover[^}]+transform")
```

- [ ] **Step 2: Run test to verify RED**

Expected: FAIL because current generic list may not expose year-grouped award entries or reveal hooks.

- [ ] **Step 3: Implement semantic award markup**

If existing Markdown rendering is not sufficient, add a local scoped Accomplishments list view that emits:

```html
<section class="editorial-accomplishments" aria-labelledby="accomplishments-title">
  <div class="editorial-accomplishments__header">
    <h1 id="accomplishments-title">Accomplishments</h1>
  </div>
  <div class="editorial-accomplishments__entries">
    <!-- preserve rendered source headings and award content in chronological groups -->
    <article class="editorial-accomplishment" data-reveal>
      <h2>2022年</h2>
      <div class="editorial-accomplishment__body">...</div>
    </article>
  </div>
</section>
```

Do not invent or duplicate award text; pass through the existing `.Content` after identifying the generated Markdown structure. If using the existing `editorial-index`/`article-style` wrapper is enough, add classes around it rather than replacing content.

- [ ] **Step 4: Add animation CSS without hover motion**

```scss
.editorial-accomplishment[data-reveal] {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 260ms var(--ease-out), transform 260ms var(--ease-out);
}

.editorial-accomplishment[data-reveal].is-reveal-ready {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .editorial-accomplishment[data-reveal],
  .editorial-accomplishment[data-reveal].is-reveal-ready {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
```

Do not add `.editorial-accomplishment:hover` transform rules.

- [ ] **Step 5: Run focused and full tests**

```bash
python3 -m unittest tests.test_generated_site.GeneratedSiteTests.test_accomplishments_is_left_aligned_year_grouped_and_reveals_without_hover_motion -v
PATH="$HOME/.local/bin:$PATH" ./scripts/test-site.sh
```

Expected: focused test and full suite PASS.

---

### Task 4: Remove homepage Accomplishments and restyle CTA

**Files:**
- Modify: `content/_index.md`
- Modify: `assets/scss/pages/_home.scss`
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: Add failing CTA contract**

```python
def test_meet_the_team_cta_is_a_light_pill_button(self):
    css = "".join(path.read_text(encoding="utf-8") for path in self.output.rglob("*.css"))
    self.assertIn("border-radius: 999px", css)
    self.assertRegex(css, r"font-weight:\s*500")
    self.assertIn("min-height: 44px", css)
    self.assertNotIn('id="accomplishments"', self.homepage)
```

- [ ] **Step 2: Run focused test to verify RED**

Expected: FAIL before CTA/home removal changes.

- [ ] **Step 3: Implement**

Use the removal from Task 1 and scope the CTA:

```scss
.home-section .cta-group .btn {
  min-height: 44px;
  padding: 0.7rem 1.4rem;
  border-radius: 999px;
  font-size: 1.1rem;
  font-weight: 500;
}
```

Keep existing accessible focus ring and color-only hover/focus state.

- [ ] **Step 4: Run tests**

Expected: homepage has no Accomplishments section; `/accomplishments/` keeps all award content; CTA contract passes.

---

### Task 5: Make navigation persistent and refine nav font

**Files:**
- Modify: `assets/js/editorial.js`
- Modify: `assets/scss/components/_navigation.scss`
- Modify: `layouts/partials/components/headers/editorial.html` only if sticky wrapper is absent.
- Modify: `tests/test_generated_site.py`

- [ ] **Step 1: Add failing persistent-nav tests**

```python
def test_editorial_header_stays_visible_and_nav_font_is_light(self):
    css = "".join(path.read_text(encoding="utf-8") for path in self.output.rglob("*.css"))
    self.assertRegex(css, r"\.editorial-header[^}]+position:\s*sticky")
    self.assertNotRegex(css, r"\.editorial-header[^}]+(?:display:\s*none|visibility:\s*hidden)")
    self.assertIn('font-family: "Anthropic Sans", "Styrene A", Inter', css)
    self.assertRegex(css, r"\.editorial-menu-link[^}]+font-weight:\s*450")
```

- [ ] **Step 2: Run RED**

Expected: FAIL because current scroll enhancement may hide/unhide header and nav font still uses heavier default.

- [ ] **Step 3: Implement persistent header**

Remove any JS branch that changes header visibility; retain only:

```js
header.classList.toggle("is-compact", window.scrollY > 24);
```

Ensure CSS includes:

```scss
.editorial-header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
}

.editorial-menu-link {
  font-family: "Anthropic Sans", "Styrene A", Inter, "Helvetica Neue", Arial, sans-serif;
  font-weight: 450;
  letter-spacing: 0.01em;
}
```

Use a fallback `font-weight: 400` if variable-weight 450 is unsupported; do not add remote font files.

- [ ] **Step 4: Run focused/full tests**

Expected: sticky header contract, nav controls, existing mobile menu/search tests, and full suite PASS.

---

### Task 6: Final verification and documentation

**Files:**
- Modify: `tests/test_generated_site.py` only for discovered regressions.
- Modify: `docs/superpowers/plans/2026-08-11-desktop-typography-accomplishments.md` only to record evidence; no implementation commits required.

- [ ] **Step 1: Run complete verification**

```bash
PATH="$HOME/.local/bin:$PATH" \
GOPROXY="${GOPROXY:-https://goproxy.cn}" \
GOSUMDB="${GOSUMDB:-off}" \
GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}" \
./scripts/test-site.sh

PATH="$HOME/.local/bin:$PATH" \
GOPROXY="${GOPROXY:-https://goproxy.cn}" \
GOSUMDB="${GOSUMDB:-off}" \
GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}" \
HUGO_BIN="${HUGO_BIN:-hugo}" \
"$HUGO_BIN" --gc --minify

git diff --check
git diff --exit-code -- content assets/media static
```

Expected: all generated-site tests PASS, Hugo exits 0, protected path diff exits 0, whitespace check has no output.

- [ ] **Step 2: Run local HTTP smoke**

```bash
hugo server --buildDrafts --buildFuture --bind 127.0.0.1 --port 1313
```

Request `/`, `/people/`, `/accomplishments/`, `/author/sizhe-qiao-乔思喆/`, and `/publication/`; expect HTTP 200, then stop server.

- [ ] **Step 3: Record manual limitation honestly**

If Playwright/Chromium remains unavailable, leave viewport/keyboard/JS-disabled visual checks unchecked in the plan. Do not claim screenshots or browser interaction were performed.

- [ ] **Step 4: Final diff review**

```bash
git status --short
git diff --stat
git diff --check
```

Do not commit unless the user explicitly requests it.
