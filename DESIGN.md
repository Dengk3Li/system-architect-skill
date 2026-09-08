---
name: System Architect Workspace
description: 以连续文件记录连接项目职责、内容身份与运行来源的研究档案工作台。
colors:
  paper: "#faf9f5"
  ink: "#20332f"
  muted: "#586760"
  line: "#d5dbd3"
  green: "#28614d"
  soft: "#e9efe8"
  warm: "#8b4c27"
  surface: "#fff"
typography:
  project-title:
    fontFamily: 'Georgia, "Songti SC", serif'
    fontSize: "30px"
    fontWeight: 500
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.4
  title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.55
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  table:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.55
  tag:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif'
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.7
  mono:
    fontFamily: 'ui-monospace, SFMono-Regular, Consolas, monospace'
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  control: "6px"
  module: "8px"
  tag: "4px"
  navigation: "5px"
  compact: "2px"
spacing:
  small: "8px"
  field: "10px"
  group: "12px"
  inset: "16px"
  section: "20px"
  panel: "22px"
  block: "24px"
  content: "26px"
  frame: "30px"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.surface}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-default:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-default-hover:
    backgroundColor: "{colors.soft}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
  view-tab:
    textColor: "{colors.muted}"
    typography: "{typography.body}"
    padding: "12px 0"
  view-tab-current:
    textColor: "{colors.green}"
  side-navigation:
    typography: "{typography.body}"
    rounded: "{rounded.navigation}"
    padding: "9px 10px"
  module-node:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.module}"
    padding: "16px"
  module-node-current:
    backgroundColor: "{colors.soft}"
  tag:
    textColor: "{colors.muted}"
    typography: "{typography.tag}"
    rounded: "{rounded.tag}"
    padding: "0 6px"
  file-row-current:
    backgroundColor: "{colors.soft}"
  history-row:
    typography: "{typography.label}"
    padding: "10px 0"
---

# Design System: System Architect Workspace

## Overview

**Creative North Star: "研究档案工作台"**

长时间核对目录、文件和实验记录时，视线需要在列表、关系和细节之间稳定往返。浅纸底、森林绿、细分隔线和连续文件行构成主要材料。名称、路径和数值占据阅读中心，选中状态安静而明确。

保留既有方向中的窄目录、相邻详情和沿来源回看的关系。模块表达职责，文件表达一次快照中的观察，运行表达登记的输入、配置和产物。布局可以随屏幕收拢，内容身份与证据口径保持一致。

本记录限定于 `skills/architecture-workspace/assets/workspace.html`、`workspace.css`、`workspace.js` 及生成的 `examples/research-workspace/index.html`，不替代既有架构编辑器的设计。数值以当前代码为准；截图提供指定状态的外观证据，行为说明来自源代码。该版本采用代码直接构建，没有批准的视觉稿或 QUALITY BAR 图卡，也没有首次使用成功率验证。方向合同与补记时间见 `docs/workspace-surface.md`；概念编号属于该合同，不属于可复用的视觉规则。

**Key Characteristics:**

- 浅纸底与白色阅读面，依靠边线和浅色选中面区分区域。
- 衬线项目名、无衬线正文、等宽路径与对齐数值各司其职。
- 文件行、模块入口和详情共享明确的文件观察身份。
- 状态用文字说明，测量、声明与未知各自保留来源。

## Colors

森林绿集中在有效操作、当前选择和数量比例；纸色、中性色与白色承载长时间阅读。颜色原值见 frontmatter，以下说明使用范围。

### Primary

- **森林绿 `green`**：主要保存按钮、链接、当前视图下划线、选中模块边线、比例条和键盘焦点。
- **浅叶色 `soft`**：文件选中行、模块选中面和普通按钮悬停面。

### Secondary

- **赭棕 `warm`**：摘要未知、未完成状态及口径提醒。状态同时保留可读文字。

### Neutral

- **浅纸 `paper`**：页面底、表头和摘要底。
- **白纸 `surface`**：顶栏、详情、输入控件与模块卡面。
- **深林墨 `ink`**：正文、主要数值和标题。
- **灰绿 `muted`**：目录、辅助说明、字段名和次级数值。
- **细线 `line`**：表格行、区域边界与控件边框。

导航当前项另用略深的浅绿底；状态标签有局部浅绿、浅棕底与配套边线。这些局部值随组件保存在 sidecar，尚未形成独立全局色阶。sidecar 的八级色阶仅为面板展示生成，不属于已使用的界面色彩或新增设计令牌。

**The 状态有字 Rule.** 颜色提示状态，文字给出状态的准确含义；“已完成 · 登记”“完整 SHA-256”“未知”等标签保持可读。

## Typography

**Project Title Font:** Georgia，中文回退 Songti SC，再回退 serif。
**Body Font:** 系统无衬线栈，中文优先使用可用的 PingFang SC。
**Label/Mono Font:** 路径采用 ui-monospace、SFMono-Regular、Consolas；完整摘要采用不含 Consolas 的等宽回退栈。

项目名保留档案题签的衬线气质，操作区维持紧凑、熟悉的无衬线阅读。没有独立宣传性大标题层级，也没有依赖外部下载字体。

### Hierarchy

- **Project title**：frontmatter 的 `project-title`；手机降至（26px）。
- **Headline**：`headline` 用于主区域标题。运行标题为（23px），手机为（21px）；详情标题为（18px）。
- **Title**：`title` 用于输入、配置、产物和详情小节。
- **Body / Table**：正文与控件采用 `body`；连续文件表采用 `table`。文件名稍加重（550），其下目录为（11px）。
- **Label / Tag**：字段名、说明采用 `label`；紧凑状态标签采用 `tag`。完整摘要为（11px / 1.7），允许任意位置换行。
- **Values**：文件大小与汇总数值采用等宽数字；存储汇总为（23px / 500），手机为（21px）。普通数值保持正文宽度。

**The 名称先读 Rule.** 文件名单独成行，目录置于下一行；完整路径和摘要在详情中展开，数值使用等宽数字便于纵向核对。

## Layout

常规桌面工作区为目录、内容、详情三列（214px / minmax(0, 1fr) / 310px）；宽屏（≥1650px）改为（240px / minmax(0, 1fr) / 340px）。主内容常规内边距（26px），宽屏为（30px 36px）。导航与详情依靠边线分隔。

中等屏幕（≤1100px）保留两列（190px / minmax(0, 1fr)），详情移到内容下方，左侧目录跨两行。手机（≤700px）按顶栏、项目、视图、导航、内容、详情纵向排列，横向内边距主要为（16px）。导出按钮各占顶栏一半，模块和目录各自横向滚动，输入输出关系改为纵向。

间距采用混合的紧凑节奏：组内常见（8–12px），面内常见（16–26px），外框常见（30px）。当前实现没有严格的八像素栅格。表格单元格上下内边距为（12px），行高由文字决定。通用按钮最小高（36px），紧凑文件、关系和路径入口另有（24–28px）最小高；通用按钮尺寸不能代表全部交互目标。

表格横向溢出由局部容器承接，手机右侧列可横向查看。长文件名、路径和摘要允许换行。模块卡片保持可滚动的横向关系，手机不强制挤入同一屏。

## Elevation & Depth

当前界面没有投影、模糊背景或抬升效果。深度来自纸色与白色的相邻、细分隔线、浅色选中面，以及输入控件的边框。导出完成提示固定在底部中央，采用深墨底与白字，不承担遮罩或对话框职责。

**The 平面阅读 Rule.** 区域以底色和边线建立秩序；状态变化使用颜色、下划线与明确位置，不扩展成装饰性立体效果。

详情在显式选择文件后轻微进入（160ms，cubic-bezier(.16,1,.3,1)，从下方 5px 回到原位）。再次选择同一文件也会触发；当前没有仅在身份变化时触发的检测。筛选和排序立即更新。降低动效偏好下关闭动画与过渡，定位滚动保持即时。

## Shapes

控件使用小圆角，模块入口稍圆，表格与区域边界保持直线。圆角以 frontmatter 为准：按钮和输入使用 `control`，模块入口使用 `module`，状态标签使用 `tag`，目录入口使用 `navigation`，文件入口与比例轨道使用 `compact`。

主要边框为细实线（1px）。视图当前项使用底部线（2px），键盘焦点为外轮廓（2px）并外移（3px）。模块与目录图标采用内联 SVG 线条；没有纹理图片、照片或图标字体依赖。

## Components

### Buttons

普通按钮为透明底与细边框；主按钮为森林绿底、白字，用于保存离线工作台。内边距与圆角见 frontmatter。

- **Hover**：普通按钮转浅叶色并加深边框。主按钮当前悬停仍保持原绿底，未定义独立悬停或按下视觉。
- **Focus**：按钮、链接、输入、选择器和展开摘要使用共享的森林绿焦点外轮廓。
- **Disabled**：分页边界按钮透明度降为（0.45），保留禁用语义。
- **Exports**：JSON 导出完整目录与运行元数据；离线 HTML 另保留当前阅读状态。完成提示显示（4 秒），通过 `role="status"` 宣告。

### Inputs / Fields

搜索框与选择器使用白底、细线和控件圆角。字段名置于上方，搜索占剩余宽度。搜索匹配名称、路径、性质、模块和扩展名，实时更新列表；默认按逻辑大小降序，同大小按路径排列，也可改为路径排序。

存储视图搜索会同步更新分组与明细，并恢复输入焦点和光标位置。普通文件视图只更新结果区域。控件有可读标签；当前没有独立的错误、必填或禁用输入样式。

### Navigation

顶部三个视图以文字和底部线区分当前页，并设置 `aria-current`。目录入口是整行按钮，模块和目录选择各有当前状态。手机将这两组入口改为横向滚动；不折叠成菜单图标。

选择模块会清空目录与业务性质条件、重置页码，并保留搜索；选择目录会重置页码。清空筛选会清除模块、目录、搜索与业务性质。每页最多（200）个文件。存储分组方式独立保留为业务性质、模块、扩展名或顶层目录。

### Cards / Containers

模块入口是白色、细边框的小圆角卡片，包含职责与文件汇总；选中时转浅叶色并显示绿边。输入、配置和产物引用使用整行按钮，列出文件名、所属快照、逻辑大小与摘要状态。连续文件表和详情采用平面容器。

### Chips / Status

标签为紧凑边框矩形。普通标签用于声明性质，浅绿用于已登记或已计算，浅棕用于未知与其他需要留意的状态。标签是状态文字，不是筛选器。

“已完成 · 登记”表达运行记录中的状态；“完整 SHA-256”表达文件内容身份。两者都不能替代结论有效性。相同路径的历次观察、直接快照引用、相同完整摘要关联分别命名。

### File Rows & Inspector

文件行以名称、目录、业务性质、内容身份和逻辑大小形成连续目录。选中行采用浅叶底；详情保留同一快照与路径下的文件观察。

显式选择文件或历史引用后，若现有条件会隐藏它，就清除模块、目录、搜索和业务性质条件，随后按当前排序定位到所在页。原有条件仍容纳该文件时继续保留。手机与中等屏幕会立即滚到详情，当前这一步没有显式把键盘焦点移入详情。

进入相关运行后，页面切到运行视图，滚动并聚焦所选运行标题。从运行返回文件视图时，滚动并聚焦选中行的文件按钮。普通视图切换、筛选与快照下拉没有统一的焦点迁移；这些局部行为不代表全面键盘流程验证。

### Storage Distribution

比例条与文件明细使用同一组筛选后的文件；上方汇总始终标明全快照的逻辑大小与已分配字节。比例条按逻辑大小从高到低排列，轨道高（9px），同时给出数值、百分比和可读比例标签。条形本身没有点击筛选动作，文件选择发生在下方明细表。

普通扫描的分配字节来自文件系统，并按存储对象去重；它不是可回收空间。合成例的文件大小与完整摘要来自临时文件的真实扫描；示例日期、修改时间、来源/存储标识和分配字节经过生成器归一化，其中分配字节按（4 KiB）块取整。合成例的运行、指标和结论均为登记的虚构内容。这些身份和口径提示随数据一起保留。

## Do's and Don'ts

### Do:

- **Do** 用纸面、细线和连续条目承载文件信息，让选择状态落在具体对象上。
- **Do** 保留状态文字、单位、快照标签和来源性质，使数据能独立阅读。
- **Do** 在跨运行追溯文件时保持快照与路径一致，并让选中文件出现在当前列表页。
- **Do** 用局部滚动容纳宽表格，在小屏保留完整操作与详情。
- **Do** 复用现有字体角色、紧凑控件和共享焦点环，并尊重降低动效偏好。

### Don't:

- **Don't** 用已登记状态或绿色标签表达科学验证、因果关系或删除建议。
- **Don't** 把合成例的归一化日期、分配字节或登记指标写成实际研究测量。
- **Don't** 把静态比例条、状态标签或装饰关系线描绘成已有的筛选操作。
- **Don't** 将现有实现概括成严格八像素栅格、统一行高、全部目标尺寸合规或完整键盘验证。
- **Don't** 将本次指定截图与修复评审扩展为全界面视觉批准或真实用户验证。
