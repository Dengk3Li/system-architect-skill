# 架构、代码地图与 Skill 证据

本次评估读取 7 个官方仓库的 README、默认分支提交、发布与许可信息，重点读取 Archify、Archmap、dependency-cruiser 的实现或命令定义；CodeBoarding 补查分析结果模型。下表状态截止 2026-09-08 03:41:27 UTC，GitHub 快照见 `architecture-sources.json`。除 Archify 的指定官方网页交互外均未试用，没有执行第三方安装脚本。

| 项目 | 实际机制与适用任务 | 安装及持续成本 | 维护/发布与许可 | 取舍 |
|---|---|---|---|---|
| [Archify](https://github.com/tt-a1i/archify/blob/2ead014aa8ec91f104cd052f1a6ca82de5e26c31/README.md) | Agent 作者化 JSON，确定性渲染/校验，多图类型，架构 Delta，来源 revision 核验；适合解释和分享系统 | 产物浏览无安装；生成需 Agent 和 Node >=18；开发依赖与生成运行分开。语义提炼仍有 Agent 成本 | main 2026-09-08；稳定 v2.16.0，2026-08-30；MIT | 采用直接示例、逐层阅读和导出思路；保留独立文件模型，不嵌入整套渲染系统 |
| [Archmap](https://github.com/juxstin1/archmap-plugin/blob/c87a31068728b1297de9350eb39233fdc7366bb6/README.md) | Claude Code 插件生成/修复/比较代码地图，保留布局及快照；任务围绕代码架构 | Claude Code 为主要入口；bash，推荐 jq；Codex 需配置模板路径和命令映射，hook 不能直接移植 | main 2026-04-25；Release 标签 2026-04-15；MIT | 采用稳定布局与模型引用概念；不复制运行时绑定和 hooks |
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser/blob/ee229c36bb25201610e06e07333df8cf2c0d7880/README.md) | 提取 JS/TS 等依赖，检查规则并输出图/报告；结构依赖是可测事实 | npm 开发依赖、项目规则；SVG 路线额外需要 Graphviz；语言覆盖有限 | main 2026-09-07；v18.2.0，2026-08-10；MIT | 确定性依赖适配的优先候选；首版沿用显式模块关系，不宣称自动代码发现 |
| [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding/blob/e38c07e31b615ff5cb479b8d117d741d247e6b60/README.md) | 静态分析、语言服务和 Agent 分析结合，生成代码结构解释 | Python 3.12/3.13、语言服务二进制及部分 Node 依赖；模型配置/成本另计；setup 会下载运行环境，未执行 | main 2026-09-06；v0.14.0，2026-09-06；MIT | 学习源码位置和分析诊断分层；不为只读文件视图引入语言服务栈 |
| [CodeCharta](https://github.com/MaibornWolff/codecharta/blob/9d1c40c3b45eb316d40c690b9eedad6d691305e9/README.md) | 将代码度量和目录组织为可交互 3D 地图，分析与 Web Studio 分开 | 先生成/导入度量文件再打开可视化；需要学习面积/高度/颜色映射；本次未测性能 | main 2026-09-07；vis-2.1.1，2026-09-07；BSD-3-Clause（API 识别，具体复用前再核原文） | 学习一个数据模型多种度量；首版用有明细的比例条，不把图形面积误当业务重要性 |
| [Structurizr Lite](https://github.com/structurizr/lite/blob/cdcbb1ba784fad75d3c05fa1a3364ab17b221e51/README.md) | 既有 C4/模型驱动工作区路线；当前 README 明确停止更新，指向合并后的 local 工具 | 旧 Lite 服务环境及 DSL 学习成本；新 local 产品未在本次深入核查 | 仓库 archived；main 2026-02-01；最后 Release v2025.11.08；MIT | 采用模型与多视图分离理念；不引入已停止更新的 Lite |
| [Cocoon Architecture Diagram Generator](https://github.com/Cocoon-AI/architecture-diagram-generator/blob/4b9087d55268c79a935105439dbcd37b630fc3f3/README.md) | Skill/模板生成 HTML/SVG，提供示例与导出；Archify 官方标明其来源关系 | 生成依赖 Agent，浏览产物轻；README 同时注明 Google Fonts，离线与外部字体仍需具体产物核查 | main 2026-05-13；1.1，2026-05-09；MIT | 采用产物可携带与例子先行；新增工作台无需外部字体或模板依赖 |

## 重点代码核查

Archify 的 [package.json](https://github.com/tt-a1i/archify/blob/2ead014aa8ec91f104cd052f1a6ca82de5e26c31/archify/package.json) 明确 Node 门槛和开发依赖；[architecture-delta.mjs](https://github.com/tt-a1i/archify/blob/2ead014aa8ec91f104cd052f1a6ca82de5e26c31/archify/delta/architecture-delta.mjs) 通过规范化结构比较稳定 ID，而非让模型描述前后差异；[repository-evidence.mjs](https://github.com/tt-a1i/archify/blob/2ead014aa8ec91f104cd052f1a6ca82de5e26c31/archify/renderers/shared/repository-evidence.mjs) 要求完整提交号，检查本地 Git 对象、文件和行号。这里确认的是代码约束存在，未运行上游测试。架构源码核验不等于文件实验输入输出已被采集。

Archify 的 [更新检查实现](https://github.com/tt-a1i/archify/blob/2ead014aa8ec91f104cd052f1a6ca82de5e26c31/archify/scripts/check-update.mjs) 和 README 还描述可关闭的版本提示网络请求；“单文件产物可离线”与“所有生成命令永不联网”应分别判断。本工作台无需更新检查或第三方资源请求。

Archmap 的 [generate 命令](https://github.com/juxstin1/archmap-plugin/blob/c87a31068728b1297de9350eb39233fdc7366bb6/commands/generate.md) 读取现有布局并在渲染时复用，定义了不同 Agent 的模板/任务适配。它属于需要 Agent 执行的工作流定义，本次未把 Markdown 指令当成运行实证。适合吸收“对象 ID 和人工布局不因重新生成而丢失”的原则。

dependency-cruiser 的 [cruise 入口](https://github.com/sverweij/dependency-cruiser/blob/ee229c36bb25201610e06e07333df8cf2c0d7880/src/main/cruise.mjs) 实际串联参数/规则校验、缓存检查、依赖抽取、分析和报告。它适合在未来提供 observed dependency evidence；目录名或 AI 解释则属于另一种声明，不能混进同一个证据等级。

CodeBoarding 的 [AnalysisData](https://github.com/CodeBoarding/CodeBoarding/blob/e38c07e31b615ff5cb479b8d117d741d247e6b60/static_analyzer/analysis_result.py) 明确保留 call graph、class hierarchies、package relations、source files 与 diagnostics。架构发现的深度有真实实现成本。首版选择接收现有模块边界，避免将“枚举目录”包装为“理解所有代码”。

## 采用边界

以上采用均为产品与建模原则，新增实现未复制第三方代码或图片，也没有引入候选平台依赖。未来若集成，应固定具体版本、接口及许可证，分别验证安装、导入和用户任务。无需因候选 Star 高低预先决定采用。
