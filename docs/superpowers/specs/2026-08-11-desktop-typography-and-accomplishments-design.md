# 桌面端字号收敛与 Accomplishments 重排设计

日期：2026-08-11
状态：已确认，待创建实现计划

## 1. 目标

在不损害移动端可读性、触控尺寸和键盘可用性的前提下，降低电脑端整体字号与页面密度，重点修正 People、个人详情页和 Accomplishments。首页移除 Accomplishments 区块，独立 Accomplishments 页面继续保留并改为清晰的奖项档案列表。

## 2. 已确认的范围

### 2.1 桌面端整体收敛

- 仅从 `min-width: 64rem`（约 1024px）开始应用桌面收敛；768–1023px 使用现有平板规则，手机不同步缩小。
- 不降低正文基础字号；主要收敛展示型标题、区块标题、页面留白和卡片密度。
- Hero 主标题最大值约从 `7rem` 收敛至 `5.5rem`。
- 普通列表/页面大标题最大值约收敛至 `4.5rem`。
- 区块标题最大值约收敛至 `3.25rem`。
- 最终数值以生成站点截图/结构测试和现有 token 体系为准，不引入远程字体依赖。

### 2.2 People 页面

- 桌面端保持 4 列，不改为 5 列。
- People 主内容最大宽度收窄至约 `76–80rem`，头像视觉面积减少约 15–20%。
- 人名桌面最大字号从当前约 `1.75rem` 收敛至约 `1.45–1.5rem`。
- 组间距、卡片纵向间距和介绍区域留白减少约 15%。
- 社交按钮继续保持至少 `44×44px`。
- 768px 以下沿用现有 2–3 列响应式布局。

### 2.3 个人详情页

- 左侧个人姓名桌面字号约 `2.25–2.5rem`。
- 职位、组织、头像和社交区域只收紧间距；正文大小不变。
- 保持左右栏结构、个人内容、头像、社交链接和作者元数据。

### 2.4 Accomplishments 页面

- 最上方靠左显示 `Accomplishments`，标题使用收敛后的桌面字号。
- 标题下方直接列出奖项，不增加 Hero 图片或大面积空白装饰。
- 按 2022、2023、2024、2025 年份分组；每条奖项保留名称、完整说明和日期。
- 桌面奖项内容保持约 `65–70ch` 阅读宽度并靠左，手机自然折行。
- 不修改 `content/accomplishments/_index.md` 的奖项内容，只调整模板/样式呈现。

### 2.5 Accomplishments 入场动画

- 每条奖项首次进入视口时执行一次轻微上浮并淡入：约 `12px` 位移，约 `220–280ms`。
- 可按条目增加短延迟，但总延迟不超过约 `180ms`。
- 不添加鼠标悬停动画，不使用 hover 位移、缩放、弹跳或阴影变化。
- 键盘聚焦只显示清晰焦点环，不改变位置。
- `prefers-reduced-motion: reduce` 时取消位移/淡入，内容立即显示。
- 禁用 JavaScript 时奖项内容仍正常可见。

### 2.6 首页调整

- 从首页移除 `ACCOMPLISHMENTS` 区块。
- 独立 `/accomplishments/` 页面完整保留。
- 首页其他区块顺序和内容不变。
- 首页最下方 `Meet the Team` CTA 保留并调整为胶囊按钮：
  - `border-radius: 999px`；
  - 字重约 `500`，比当前更细；
  - 字号相对按钮高度提高至约 `1.05–1.15rem`；
  - 最小触控高度保持 `44px`；
  - 保留颜色 hover/focus 反馈，但不使用位移或缩放。

### 2.7 常驻顶部导航与字体

- 顶部导航栏始终可见，不因滚动隐藏或移出视口。
- 可保留轻微压缩状态，但只改变高度/内边距，不改变可见性。
- 导航按钮需避免遮挡正文，继续保持移动菜单、键盘焦点和搜索行为。
- 右侧导航按钮使用更细字重和克制字距，目标约 `font-weight: 450`、`letter-spacing: 0.01em`。
- 字体栈优先使用设备已有的：

  ```css
  "Anthropic Sans", "Styrene A", Inter, "Helvetica Neue", Arial, sans-serif
  ```

- 不远程下载或新增未经授权的 Claude/Anthropic 字体；未安装时安全回退到现有无衬线字体。

## 3. 技术边界

- 沿用现有 Hugo Blox 混合覆盖、模块化 SCSS 和轻量 `assets/js/editorial.js`。
- 优先复用现有 People、landing/list/article partial 和设计 token；不复制整个远程主题。
- 不修改 `content/`、`assets/media/` 或 `static/` 中的既有内容和素材。
- 不引入 npm、浏览器框架、远程字体或新的运行时依赖。
- 动画必须复用已有渐进式 reveal 和 reduced-motion 机制。

## 4. 验证要求

实现前先为以下行为补失败测试：

- 首页不再生成 `ACCOMPLISHMENTS` 区块，但 `/accomplishments/` 保留所有年份、奖项、说明和日期。
- People 桌面 token/选择器体现 4 列、收窄宽度、较小人物字号；社交按钮仍至少 44px。
- 作者详情页桌面姓名字号收敛，左右栏和内容仍生成。
- Accomplishments 标题在最上方靠左，奖项按年份分组，条目带入场 reveal hook。
- 奖项 CSS 不包含 hover 位移/缩放，包含 reduced-motion 立即显示规则。
- Meet the Team CTA 胶囊、字重/字号/最小高度契约存在。
- 导航为常驻定位/可见，压缩状态不使用 display:none/visibility:hidden；导航字体栈包含安全回退和较细字重。

运行：

```bash
PATH="$HOME/.local/bin:$PATH" \
GOPROXY="${GOPROXY:-https://goproxy.cn}" \
GOSUMDB="${GOSUMDB:-off}" \
GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}" \
./scripts/test-site.sh

hugo --gc --minify
git diff --check
git diff --exit-code -- content assets/media static
```

浏览器自动化不可用时，不声称完成视口截图或键盘人工验收；使用生成站点结构、编译 CSS、HTTP smoke 和本地预览记录实际证据。
