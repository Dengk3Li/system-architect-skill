# System Architect Skill Suite

[English](README.md) | 简体中文

[![CI](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml)

一组把已批准需求和一手证据转化为低复杂度架构决策、质量目标、模块归属、接口、可重复架构图和人类反馈的 Agent Skill。

## 快速开始

使用通用 Skills CLI 安装：

```bash
npx skills add Dengk3Li/system-architect-skill --skill system-architect
npx skills add Dengk3Li/system-architect-skill --skill architecture-visualizer
```

让 Agent 为改动确定模块边界：

```text
Use $system-architect to place this change in one owned module and define the
interfaces needed for integration.
Use $architecture-visualizer to render this architecture as interactive HTML
and presentation-ready SVG.
```

把模块清单模板复制到目标仓库：

```bash
mkdir -p .system-architect
cp skills/system-architect/assets/module-boundaries.template.json \
  .system-architect/module-boundaries.json
```

用已确认的路径和接口替换全部示例，然后检查清单：

```bash
python3 skills/system-architect/scripts/check_module_scope.py --check-manifest
```

这份清单用于记录模块所有权和受保护的共享区域。

## 它能做什么

System Architect 帮助团队：

- 把已经确认的业务结果、关键流程和领域规则转化为架构决策；
- 通过信息隐藏、高内聚、窄耦合和构造证据控制意外复杂度；
- AI 生成的摘要、图谱和架构图保持为候选，直到一手证据完成验证；
- 定义可测量的质量目标并说明其业务后果；
- 让每个受管理文件只属于一个模块；
- 保护应用外壳、全局样式、共享 API 和设计变量；
- 为模块接口登记提供方、使用方、版本、错误、写入副作用和负责人；
- 按计划文件、工作区差异或暂存区差异检查修改范围；
- 在不重写整站的前提下，从前端单体中逐步拆出新功能；
- 区分观察到、已经接受和仍在提议的架构；
- 用一个架构模型重复生成面向不同读者的 HTML 和 SVG；
- 把前端建模为独立归属的能力模块，并明确页面、组件、界面状态、交互、数据合同和质量要求；
- 在离线前端架构工作区中移动、调整尺寸、批注元素，并把修改导出为待验证 JSON；
- 向人类利益相关者返回取舍、风险、假设和待决定事项；
- 模块归属、授权或接口没有证据时保留 `UNKNOWN`。

这个仓库同时提供架构指令和一个 Python 范围检查器。

## 我们在解决什么

编码 Agent 可以只根据提示词生成一份看起来合理的架构，却没有核对真实代码、运行状态、接口合同和已经批准的需求。下一个 Agent 又可能把这份摘要或架构图当成证据。经过几轮传递，系统开始围绕过去的 AI 解释设计，而不是围绕真实业务逻辑和代码设计。

实现阶段还有另一类问题。负责一个功能的开发者仍然可以修改主路由、应用外壳、共享 API、全局样式和兄弟模块。局部开发会因此增加耦合、制造重复状态，甚至覆盖产品范围之外的既有行为。

这套 Skill 从已经批准的需求 ID 和一手证据出发，吸收《代码大全》中复杂度控制、信息隐藏、高内聚、窄耦合和依据构造证据持续改进的思路。AI 生成的摘要、图谱和架构图保持为候选，只有源码、测试、运行观察、合同或人类决定能够完成验证。

仓库中的模块归属和真实 Git 差异共同约束写入范围。共享区域通过明确接口和经过授权的架构变更完成整合。产品经理继续负责产品范围；系统架构师负责落点、边界、质量目标和整合后果。

## 架构模型

### 业务驱动与质量要求

架构从已经确认的客户结果和业务结果出发。关键旅程、领域不变量、数据权威、失败后果、成本、可靠性、安全、性能、隐私、可运维性和可演进性成为显式设计输入；只采用真正影响当前系统的质量维度。

### 独立归属的模块

每个受管理文件必须匹配一个模块的 `owned_paths`。没有归属或被多个模块同时声明都会检查失败。

### 受保护的共享区域

应用外壳、全局变量、公共 API 适配器等共享区域可以标记为 protected。普通模块开发者不能修改。架构师或集成者需要真实授权，并明确声明架构变更。

### 带版本的接口

模块依赖公开合同，不读取其他模块的私有 DOM、存储、文件或内部函数。接口合同需要说明提供方、使用方、版本、行为和副作用负责人。

### 范围检查

检查器可以在开发前验证计划修改的文件，也可以在交付前检查真实 Git 差异。违规时返回退出码 `2`，可以直接阻断本地 hook 或 CI。

### 前端架构工作区

前端属于系统架构，不是后端设计完成后补上的一张展示图。重要的用户界面能力应当作为独立归属模块，关联已经批准的需求 ID；模块内部明确页面、组件、加载/空/错误/不可用/就绪状态、用户交互、数据写入权威、无障碍、响应式布局、性能和恢复行为。

从内置样板开始：

```bash
cp skills/architecture-visualizer/assets/frontend-module.template.json \
  architecture-model.json
python3 skills/architecture-visualizer/scripts/render_architecture.py \
  architecture-model.json --output-dir architecture-review
```

打开 `architecture-review/architecture.html`，选择前端视图并点击元素。元素可以移动、调整尺寸、编辑实现要求和添加批注。使用“导出已编辑模型”保存为 `architecture-model.edited.json`，通过验证和评审后再替换源模型。HTML 页面和浏览器内存是评审界面，不是架构权威。

这套交互吸收了 React Flow、Storybook、Excalidraw、draw.io 和 Structurizr 的成熟模式，同时保持渲染器零依赖。如果项目已经有获准使用的图形编辑器，可以把相同的稳定元素 ID 和前端模型接入现有编辑器。

## 使用例子

假设团队要为现有电商应用增加退款看板，产品范围已经确定。

System Architect 把页面和测试分配给 `refund-board`。这个模块通过公开的 `orders.events.v2` 读取订单事件。主导航属于受保护的 `app-shell`，最后由集成者通过 `shell.slot.v1` 接入。

退款模块开发者可以修改：

```text
src/features/refunds/**
tests/refunds/**
```

同一开发者不能修改：

```text
src/shell/**
src/api/**
src/features/orders/internal/**
```

如果订单事件缺少 payload、错误行为或写入权限说明，架构状态保持 `UNKNOWN`。Agent 不会为了继续编码而临时发明接口。

## 常见工作流程

1. 阅读已经确认的产品结果、业务约束、仓库规则和运行证据。
2. 明确的小改动直接处理；中等及以上工作按当前决策 frontier 分轮收敛。
3. 对话无法可靠回答时，用一次性原型或带引用的第一手资料研究补足证据。
4. 映射参与者、关键流程、领域规则、质量目标和数据权威。
5. 比较架构方案并说明决定性取舍。
6. 选择现有模块、新模块或受保护的共享合同变更。
7. 记录落点、归属、接口、证据、反馈和验证。只有难逆转、缺少背景会令人意外且存在真实取舍时才写 ADR。
8. 架构图有助于利益相关者决策时生成对应视图。
9. 整合前检查计划文件和实际差异。
10. 已授权的交付自动创建分支/worktree、提交、推送、创建并合并 PR；确认合并已进入目标分支、worktree 干净、没有活跃 writer 且引用证据已保留后，只清理本任务创建的 Git 资源。
11. 运行、成本、事故或用户证据出现后重新审视假设。

系统架构师负责模块落点和接口，不会接管所有模块的开发。

完整的决策与交付流程见 [architecture-workflow.md](skills/system-architect/references/architecture-workflow.md)。改编的第三方工作流材料及其许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 范围检查器

检查计划修改的文件：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --files src/catalog/view.ts tests/catalog_view_test.ts
```

检查相对 Git 基线的工作区差异，包括未跟踪文件：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --base HEAD
```

只检查暂存区：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --staged
```

检查经过授权的共享区域改动：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module app-shell \
  --role system-architect \
  --architecture-change \
  --files src/shell/navigation.ts
```

`--architecture-change` 只记录改动类型，本身不会授予权限。

## 在现有前端中逐步采用

不需要先把整个应用彻底模块化。

1. 把当前应用外壳和其他共享文件登记为 protected。
2. 新功能进入拥有独立归属的目录。
3. 通过窄适配器或插槽接入。
4. 只有真实需求提供了合适切点时，才把旧逻辑从共享文件迁出。

这样可以保留现有行为，同时缩小每项新任务的写入范围。

## 角色边界

| 角色 | 负责内容 |
|---|---|
| 产品经理 | 用户问题、优先级、发布范围、验收 |
| 系统架构师 | 模块落点、页面占比、文件归属、接口、整合顺序 |
| 架构可视化 | 稳定架构模型、读者视图、来源证据和图示反馈 |
| 模块开发者 | 一个登记模块内的实现和测试 |
| 集成者 | 通过声明接口修改经过授权的共享区域 |

产品范围和发布决定由配套的 [Product Manager Skill](https://github.com/Dengk3Li/product-manager-skill) 处理。

## 适用场景

适合：

- 多个 Agent 或多条对话在同一代码库工作；
- 前端功能共用路由、导航、全局样式或大型入口文件；
- 新模块需要连接现有数据或页面；
- 模块之间需要稳定的上下游合同；
- 旧单体需要逐步拆分；
- 一项改动可能覆盖范围之外的现有界面。

如果代码库很小，只有一个维护者，也没有共享整合区域，通常不需要增加这层边界。

## 仓库内容

```text
.codex-plugin/plugin.json
skills/system-architect/
  SKILL.md
  agents/openai.yaml
  assets/module-boundaries.template.json
  references/architecture-sources.md
  references/change-contract.md
  references/code-complete-principles.md
  scripts/check_module_scope.py
skills/architecture-visualizer/
  SKILL.md
  agents/openai.yaml
  assets/architecture-model.template.json
  assets/frontend-module.template.json
  references/architecture-model.md
  scripts/render_architecture.py
tests/test_architecture_visualizer.py
tests/test_check_module_scope.py
```

`SKILL.md` 是 Agent 运行时读取的指令。仓库 README 面向评估和安装这个 Skill 的使用者。

## 参考资料

规则参考了以下公开项目和方法：

- [Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Nx module boundaries](https://nx.dev/docs/guides/enforce-module-boundaries)
- [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md)
- [Building Evolutionary Architectures](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_second_edition_free_chapter.pdf)
- [MADR](https://adr.github.io/madr/)
- [C4 模型](https://c4model.com/diagrams)
- [C4 工具原则](https://c4model.com/tooling)
- [React Flow](https://reactflow.dev/) 与 [MIT 许可示例](https://reactflow.dev/examples)
- [Storybook](https://storybook.js.org/) 与 [交互测试](https://storybook.js.org/docs/9/writing-tests/interaction-testing)
- [Excalidraw](https://github.com/excalidraw/excalidraw)
- [draw.io](https://github.com/jgraph/drawio)
- [Structurizr](https://docs.structurizr.com/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [《代码大全（第 2 版）》](https://www.microsoftpressstore.com/store/code-complete-9780735619678)
- [《代码大全》示例章节：构造中的设计](https://www.microsoftpressstore.com/articles/article.aspx?p=2222451)

每项资料怎样转化为具体规则，以及与相关工具的区别，见 [architecture-sources.md](skills/system-architect/references/architecture-sources.md)。

## 开发与验证

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

检查 Skill 和插件清单：

```bash
python3 <skill-creator>/scripts/quick_validate.py skills/system-architect
python3 <plugin-creator>/scripts/validate_plugin.py .
```

范围检查器只使用 Python 标准库，没有第三方运行依赖。

## License

仓库公开可见，但目前没有授予开源许可证。
