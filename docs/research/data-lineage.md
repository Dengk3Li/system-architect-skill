# 数据版本、实验追溯与知识关联：一手证据扫描

证据截止：2026-09-08 03:34:42 UTC。范围：9 个官方仓库，涵盖数据版本、实验跟踪、数据血缘、研究工作区与知识关联。本文是总体竞品扫描的一个有界分支，不代表穷尽 GitHub，也不按 Star 排名。

## 结论与首版取舍

建议首版采用一个本地只读的关系模型，把“目录和模块的职责”与“文件快照和实验运行”连接起来。DVC、DataLad、MLflow 和 OpenLineage 已经证明这些概念各自有成熟机制；它们的现成产品主要服务数据版本或运行追踪，目录的业务职责仍需要独立建模。这个缺口是本次所查资料中的适配判断，尚未通过用户访谈或完整竞品试用验证。

首版自行实现小型快照清单、显式运行记录、来源关系和可分享的脱敏视图；采用通用数据建模原则，保留未来读取 DVC、MLflow、OpenLineage 导出记录的接口。首版无需集成这些平台的运行时，也无需接管实验执行、数据备份、恢复、删除或权限。

| 能力来源 | 决策 | 原因 |
|---|---|---|
| DVC 的元数据与内容分离、输入输出锁定 | 采用概念；首版重做最小只读清单 | 能保存文件事实，避免把大文件塞进架构模型；DVC 本身还管理缓存、检出、流水线，超出本次范围 |
| DataLad 的显式输入、输出、命令和数据集标识 | 采用概念；规划只读导入 | 贴近研究追溯；Git 与 git-annex 工作流不适合作为陌生用户的必选前提 |
| MLflow 的运行页、参数和指标对比 | 采用交互组织；规划只读导入 | Run 是很好的任务入口；其数据摘要不是完整文件校验，模型注册与服务部署也超出首版 |
| OpenLineage 的 Job / Run / Dataset 及事件模型 | 采用概念；预留事件映射 | 清楚区分过程定义、一次执行和数据；完整标准兼容仍需映射和验证，不能只改字段名就宣称兼容 |
| Marquez 的聚焦血缘与运行详情 | 借鉴交互；不集成服务 | 图与详情互相定位有价值；API、Postgres 和 Web 部署成本高于本地首版所需 |
| lakeFS 的不可变数据提交和分支 | 不采用其存储平台；保留外部版本引用 | 它面向对象存储中的数据湖；普通本地目录无需引入服务端数据仓库 |
| Aim 的参数、上下文与曲线比较 | 借鉴比较方式；不集成跟踪 SDK | 精于训练指标，不等于任意文件内容版本；首版无需改变训练代码 |
| Renku 的数据、代码和环境关联 | 借鉴项目组织；不集成平台 | 当前 Renku 是协作计算平台，Kubernetes 等部署超出单机只读工作台 |
| Logseq 的稳定节点、反向链接和局部关系 | 借鉴关系导航；自行实现 | 知识引用能连接结论与证据，但引用本身不验证文件版本；现版 DB 路线和 AGPL 代码不宜当成可直接嵌入的小组件 |

## 搜索与证据方法

搜索方式：公开网页搜索定位项目与相关资料，再通过 GitHub 官方 API 核验仓库身份、默认分支提交、目录树、最近五项 Release、README、许可证及选定源码/测试。检索式：

- `site:github.com DVC MLflow DataLad data versioning experiments provenance`
- `site:github.com OpenLineage Marquez dataset run job facets`
- `site:github.com lakeFS Aim Renku experiment data lineage`
- `site:github.com Logseq knowledge graph local markdown files`

限定：搜索结果中出现非官方 Logseq 组织，未作为能力证据。`iterative/dvc` 已被 GitHub 重定向为 `treeverse/dvc`，本报告使用当前官方地址。所有代码链接固定到本次读取的 commit；Release 链接与发布时间另行记录。仓库的 `pushed_at` 可能来自其他分支或自动更新，因此维护判断同时列出默认分支提交与发布记录。

证据等级：**文档宣称**指作者 README/文档描述；**代码核验**指本次实际阅读了实现、模式或测试，确认相应字段/逻辑存在；**实际试用**指执行软件并观察行为。本次实际试用均为“未进行”，没有安装软件、运行第三方安装脚本、启动平台或执行仓库测试。代码阅读不证明完整用户体验、性能、兼容性或无缺陷。

## 四个重点候选

### DVC

目标用户是需要版本化数据、模型和实验的 ML 开发者。README 明确提供 Git 中的元数据、Git 外的数据缓存、依赖和产物声明、实验比较；示例从 `dvc add` 到 `stage add`、`exp run`、`exp show`，任务路径完整。[README][dvc-readme]

代码核验：`dvcfile.py` 将流水线声明和锁文件分开，并验证模式；`output.py` 维护路径、哈希、大小、目录成员数和版本元数据；测试直接构造含 `md5`、`size`、`path` 的 `.dvc` 记录并验证读取和写回。由此可以确认“位置、内容身份、版本声明分离”在代码中存在。这里只核验所列实现，并未运行 DVC，也未验证全部存储后端。[锁文件实现][dvc-code]、[输出模型][dvc-output]、[测试][dvc-test]

与目录架构的缺口：DVC 流水线描述怎样生成数据，目录与模块的业务职责、模块间允许关系、设计结论仍需另一层模型。内容哈希也不表达“这是原始输入还是已确认结论”。

成本：个人本地使用可不设服务器，但需要安装 DVC、维护 Git/DVC 元数据并理解缓存；云存储按后端增加可选依赖和凭证。默认引入版本管理会改变用户工作方式，首版仅规划读取已经存在的 `.dvc`/`dvc.lock`。[安装说明][dvc-readme]

许可：Apache-2.0。最近 Release 为 3.67.1，2026-03-31；本次默认分支提交日期为 2026-08-06，提交内容是构建依赖更新。可以确认有近期维护，不能仅用仓库 pushed 时间推断功能迭代频率。[许可][dvc-license]、[发布][dvc-release]

### MLflow

目标用户覆盖传统 ML、生成式 AI 与 Agent 开发者。README 当前重点呈现 tracing、评估与部署，同时保留实验跟踪；官方 quickstart 用独立 API 记录参数、指标和产物目录。它的完整产品范围明显超过“文件历史”。[README][mlflow-readme]、[实际示例代码][mlflow-example]

代码核验：Dataset 模型独立保存 `name`、`digest`、`source`、`source_type`，并可附加 schema/profile。digest 允许调用方提供；pandas 摘要只选前 10,000 行中的特定列，并结合总行数与列名，最终截断为 8 位 MD5。因此 MLflow dataset digest 可用于其跟踪语义，不能当成任意文件的完整内容身份或完整性证明。[Dataset][mlflow-code]、[摘要实现][mlflow-digest]

与目录架构的缺口：运行、指标和模型导向的体验便于比较结果，但任意目录的职责、存储占用和非 ML 文件历史不在所核验模型的核心。数据源记录也不自动证明输入文件已备份或可重新取得。

成本：需要 Python 包与跟踪调用，查看 UI 需要运行服务；团队部署还需决定元数据和产物存储位置。可用性和部署成本应分别比较，不能因为有本地模式就等同打开一个 HTML。读取导出元数据可保留未来集成可能。[示例][mlflow-example]、[部署说明][mlflow-docker]

许可：Apache-2.0。最近主产品 Release v3.16.0，2026-09-04；默认分支 2026-09-08 有提交。Release 列表还包含 `model-catalog/latest`，它不是当前主产品版本，已排除。该版本发布说明包含 trace 视图等改动，表明定位正在扩展，不能按旧版实验看板理解当前全部产品。[许可][mlflow-license]、[发布][mlflow-release]

### DataLad

目标用户是管理分布式、可复现研究数据的研究者与团队。README 说明建立在 Git 和 git-annex 上，以数据集及嵌套数据集组织数据，底层存储和权限由外部系统承担。[README][datalad-readme]

代码核验：`run.py` 把显式输入、输出、命令、退出码、相对工作目录和数据集 ID 写入运行记录，并支持记录放在提交消息或 sidecar 文件；其命令也会准备输入、处理输出并保存改变。测试确认无文件变化的命令默认不创建新的数据集提交。这是有意设计，不应被改写成“记录了每一次尝试”。本产品若要保留失败或无产物实验，Run 必须能独立于文件快照变化而存在。[运行实现][datalad-code]、[无变化测试][datalad-test]

与目录架构的缺口：嵌套数据集最接近层级组织，但数据集层级仍不等于业务模块职责；可复现命令与组织边界需要显式关联。既有 DataLad 项目适合只读导入元数据，普通用户不应被要求先迁移所有文件。

成本：除 Python 包外，官方安装步骤要求事先安装近期 git-annex；用户要理解 Git、数据集、获取数据和运行保存语义。成本高于元数据快照，优势也更深，不能称为“大号目录浏览器”。[安装说明][datalad-readme]

许可：COPYING 明确主体 MIT，同时列出部分第三方代码的其他许可。GitHub license API 返回 NOASSERTION，本报告以许可证原文为准；如复制特定代码仍需逐文件核验。最近 Release 1.6.2，2026-08-13；默认分支提交为 2026-09-05。[COPYING][datalad-license]、[发布][datalad-release]

### OpenLineage

目标用户是需要跨编排器、处理引擎和目录系统共享数据血缘的团队。它是元数据标准及采集生态，不能把它和完整可视化产品混为一谈。模型区分 Job、Run、Dataset；Dataset 按 namespace/name 定位，输入和输出可携带本次运行特有 facets。[README][ol-readme]、[规范][ol-spec]

代码核验：JSON Schema、Python 生成模型与序列化示例都提供 RunEvent、Job、Run、inputs/outputs。规范要求 START 及 COMPLETE/FAIL/ABORT 之一；外部 dataset version 是附加信息，并非协议自行计算的文件哈希。sourceCodeLocation facet 可带源码版本。客户端旧 `run.py` 已弃用，当前 `event_v2.py` 导出生成模型；未来实现应以当前 schema 和事件类为依据。[Schema][ol-schema]、[当前生成模型][ol-code]、[序列化样例][ol-example]、[版本 facet][ol-version]

与目录架构的缺口：协议描述数据流和运行事件，不扫描本地目录，不自动发现文件类型或分配模块职责，也不保存文件内容。名称和版本值由上游提供，导入时需要保留来源与原始标识。

成本：只借鉴模型无需依赖；产生和消费真实事件需要安装客户端或集成采集器，并选择传输及存储后端。首版可用自有小型 JSON，之后做明确的版本化映射；暂不宣称完整 OpenLineage 兼容。

许可：Apache-2.0。最近 Release 1.53.0，2026-09-01；默认分支 2026-09-07 的提交涉及 Spark 流式输出采集。客户端发布版本与规范版本不同，示例 schema 版本不能直接当作 SDK 最新版本。[许可][ol-license]、[发布][ol-release]

## 补充候选

| 项目 | 真实机制与使用成本 | 目录架构关联及适配判断 | 维护与许可 |
|---|---|---|---|
| lakeFS | README 将对象存储呈现为支持分支、提交和回退的数据仓库；支持本地 quickstart 或 Docker 服务。生产用途还要配置真实对象存储。[来源][lakefs-readme] | 适合数据湖隔离与版本，不是普通本地文件目录；只保留外部 dataset/version 引用。作者的无复制分支和可扩展性说明本次未做性能试验。 | Apache-2.0；v1.86.0，2026-08-05；默认分支 2026-08-16。[许可][lakefs-license]、[发布][lakefs-release] |
| Aim | README 示例用 Run 记录参数，按 step/context 跟踪指标，再启动 UI；源码提供 Run 身份、只读模式及系统指标选项。[README][aim-readme]、[源码][aim-code] | 可借鉴比较同一次训练不同上下文的交互；Run hash 是运行标识，不能误当文件内容哈希。系统参数和终端日志采集有隐私边界，首版无需默认复制它。 | Apache-2.0；v3.29.1，2025-05-08；默认分支 2025-12-31。pushed_at 近期不改变这个发布/默认分支事实。[许可][aim-license]、[发布][aim-release] |
| Marquez | OpenLineage 元数据服务及可视化；Compose 实际包含 API 与 Postgres，Web 是另一层配置。README 描述 lineage graph 和 job run history。[README][marquez-readme]、[Compose][marquez-code] | 可借鉴围绕选中数据集/运行展开相邻关系与详情。首版不需要常驻元数据服务；未实际验证渲染性能及历史版本解析细节。 | Apache-2.0；0.50.0，2024-10-24；默认分支 2026-04-12 有查询优化提交。不能因发布较旧断言废弃。[许可][marquez-license]、[发布][marquez-release] |
| Renku | 当前 README 将项目组装为数据连接器、源码库和计算环境；部署文档列出 Kubernetes、Postgres、Redis、Solr、Keycloak 等服务。[README][renku-readme]、[架构][renku-code] | 连接数据、代码和环境很贴近研究工作，但当前产品重心是协作计算。旧版知识图谱描述不能直接归到当前 Renku 2；首版不引入平台。 | Apache-2.0；2.20.0，2026-08-27，新增持久项目存储等；默认分支同日。[许可][renku-license]、[发布][renku-release] |
| Logseq | 当前 README 明确 DB 版 beta、移动与 RTC alpha；schema 实际包含 block UUID、parent、page、refs 和 tags，以及文件路径字段。[README][logseq-readme]、[schema][logseq-code] | 学习稳定节点与反向链接，让结论链接具体运行/文件版本；不能用知识链接代替内容校验。当前 DB 版与旧 Markdown 图路线应分开看待。 | AGPL-3.0；2.0.1 发布于 2026-07-13，正文明确为 beta，虽 API prerelease=false；nightly 2026-09-07，默认分支 2026-09-08。[许可][logseq-license]、[发布][logseq-release] |

## 对首版模型和交互的具体建议

以下为基于证据的产品建议，尚不代表已实现或接受的系统合同。

1. **分开四种身份。** `Module` 是职责；`FileEntry` 是某个相对路径的观察结果；`ContentIdentity` 是算法、完整摘要与校验状态；`Snapshot` 是一次扫描中的文件成员集合。同路径可出现不同内容；同内容可出现在多个路径。内容相同可提示候选复制或改名，单凭哈希不能证明用户做过移动操作。
2. **把 Run 单独存储。** Run 引用输入/配置/输出的明确快照条目或外部版本，并带时间、状态、指标、结论和来源证据。失败、取消、无输出也能有 Run；缺失记录保留“未知”，不由文件时间戳推断成功。只读工作台导入或记录已有运行信息，首版无需执行实验。
3. **把职责关系和来源关系用同一详情入口连接。** 从模块打开目录与产物；从产物打开版本差异、使用它的运行和对应结论。默认展示一个选中对象及直接邻居，提供展开动作，避免第一次打开就出现整屏复杂网络。
4. **文件性质保持两条线。** 格式来自扩展名及可选确定性识别，业务性质来自显式标签或已声明的输入/输出角色。扩展名是观察线索，不等于真实格式；AI 只能提出“可能是训练输入”的候选标签，显示依据并允许用户确认。
5. **占用口径明确。** 首版先呈现逻辑字节总量、目录分布、文件格式分布与大文件列表。若显示实际分配字节或按内容去重的总量，应单独命名并说明扫描能力。硬链接、稀疏文件、压缩、克隆与不可读文件会改变口径；“相同内容”不等于“删除后可释放空间”。公开示例用合成数值，真实扫描不自动删除。
6. **区分事实与解释。** Evidence 保存来源、观测时间、工具/导入方式及原始引用；结论链接证据，并显示人为记录或 AI 候选。导入平台 digest 保留原算法与语义，不能升级成完整 SHA-256 文件校验。哈希未完成或文件扫描中变化时明确显示未验证。
7. **陌生用户先得到一个结果。** 提供合成研究项目，允许从一个目录找到最大产物、比较两次运行、定位共同输入、查看结论依据，并导出脱敏 JSON/独立报告。导出的是元数据快照和关系，不应暗示已经备份真实文件内容。

确定性能力：路径枚举、字节统计、完整哈希、文件差异、显式关系校验、标签规则、运行状态与导出。AI 可选能力：解释陌生目录的可能职责、概括实验结论、提出待确认关联。AI 不决定版本事实、执行状态、可删除性或权限。即便 AI 不可用，核心查看、比较、追溯与导出任务仍应成立。

## 可复核边界

本次已完成 README、许可和维护记录读取；四个重点候选还读取了真实源码/测试/示例。所有软件均未安装或运行；未评估实际安装时长、运行内存、十万文件性能、长时间多用户稳定性或完整 UI 使用感。各工具的产品适配结论应通过后续原型核心任务验证，而不能由功能表直接推出。

结构化来源见 `lineage-sources.json`。本地保留读取到的公开源文件与 API 回包，用于核验引用；对外发布只需使用本报告与紧凑来源索引，不需要打包完整第三方源码。

[dvc-readme]: https://github.com/treeverse/dvc/blob/56e59829512ff134aa269099a2099587b810b4dd/README.rst
[dvc-license]: https://github.com/treeverse/dvc/blob/56e59829512ff134aa269099a2099587b810b4dd/LICENSE
[dvc-code]: https://github.com/treeverse/dvc/blob/56e59829512ff134aa269099a2099587b810b4dd/dvc/dvcfile.py
[dvc-output]: https://github.com/treeverse/dvc/blob/56e59829512ff134aa269099a2099587b810b4dd/dvc/output.py
[dvc-test]: https://github.com/treeverse/dvc/blob/56e59829512ff134aa269099a2099587b810b4dd/tests/func/test_dvcfile.py
[dvc-release]: https://github.com/treeverse/dvc/releases/tag/3.67.1
[mlflow-readme]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/README.md
[mlflow-license]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/LICENSE.txt
[mlflow-code]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/mlflow/data/dataset.py
[mlflow-digest]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/mlflow/data/digest_utils.py
[mlflow-example]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/examples/quickstart/mlflow_tracking.py
[mlflow-docker]: https://github.com/mlflow/mlflow/blob/1246a5c8baf81dce7fe06fa83f4cad873411e9fe/docker-compose/README.md
[mlflow-release]: https://github.com/mlflow/mlflow/releases/tag/v3.16.0
[datalad-readme]: https://github.com/datalad/datalad/blob/28dc8b16519690bf0c00c3a0a63f84445829652d/README.md
[datalad-license]: https://github.com/datalad/datalad/blob/28dc8b16519690bf0c00c3a0a63f84445829652d/COPYING
[datalad-code]: https://github.com/datalad/datalad/blob/28dc8b16519690bf0c00c3a0a63f84445829652d/datalad/core/local/run.py
[datalad-test]: https://github.com/datalad/datalad/blob/28dc8b16519690bf0c00c3a0a63f84445829652d/datalad/core/local/tests/test_run.py
[datalad-release]: https://github.com/datalad/datalad/releases/tag/1.6.2
[ol-readme]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/README.md
[ol-license]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/LICENSE
[ol-spec]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/spec/OpenLineage.md
[ol-schema]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/spec/OpenLineage.json
[ol-code]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/client/python/src/openlineage/client/generated/base.py
[ol-example]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/client/python/tests/serde_example_run_event.json
[ol-version]: https://github.com/OpenLineage/OpenLineage/blob/aab43df6c425d6998ce0683ddc7a10dc3e15d205/spec/facets/DatasetVersionDatasetFacet.json
[ol-release]: https://github.com/OpenLineage/OpenLineage/releases/tag/1.53.0
[lakefs-readme]: https://github.com/treeverse/lakeFS/blob/4bb11638e95637e853d9680abf072b14f09e32fb/README.md
[lakefs-license]: https://github.com/treeverse/lakeFS/blob/4bb11638e95637e853d9680abf072b14f09e32fb/LICENSE
[lakefs-release]: https://github.com/treeverse/lakeFS/releases/tag/v1.86.0
[aim-readme]: https://github.com/aimhubio/aim/blob/6e098e38065364c76b2bb7c028f266e53b647642/README.md
[aim-license]: https://github.com/aimhubio/aim/blob/6e098e38065364c76b2bb7c028f266e53b647642/LICENSE
[aim-code]: https://github.com/aimhubio/aim/blob/6e098e38065364c76b2bb7c028f266e53b647642/aim/sdk/run.py
[aim-release]: https://github.com/aimhubio/aim/releases/tag/v3.29.1
[marquez-readme]: https://github.com/MarquezProject/marquez/blob/180f37b22387146187af1ef0279e3ee1d1ccd789/README.md
[marquez-license]: https://github.com/MarquezProject/marquez/blob/180f37b22387146187af1ef0279e3ee1d1ccd789/LICENSE
[marquez-code]: https://github.com/MarquezProject/marquez/blob/180f37b22387146187af1ef0279e3ee1d1ccd789/docker-compose.yml
[marquez-release]: https://github.com/MarquezProject/marquez/releases/tag/0.50.0
[renku-readme]: https://github.com/SwissDataScienceCenter/renku/blob/e5608308d1a62bafd2c6d7dd00c4a269ce6c009c/README.md
[renku-license]: https://github.com/SwissDataScienceCenter/renku/blob/e5608308d1a62bafd2c6d7dd00c4a269ce6c009c/LICENSE
[renku-code]: https://github.com/SwissDataScienceCenter/renku/blob/e5608308d1a62bafd2c6d7dd00c4a269ce6c009c/docs/docs/20-admins/10-architecture/10-services.md
[renku-release]: https://github.com/SwissDataScienceCenter/renku/releases/tag/2.20.0
[logseq-readme]: https://github.com/logseq/logseq/blob/263fd97cbde87b747712f3d2de7d8b12c774ce23/README.md
[logseq-license]: https://github.com/logseq/logseq/blob/263fd97cbde87b747712f3d2de7d8b12c774ce23/LICENSE.md
[logseq-code]: https://github.com/logseq/logseq/blob/263fd97cbde87b747712f3d2de7d8b12c774ce23/deps/db/src/logseq/db/frontend/schema.cljs
[logseq-release]: https://github.com/logseq/logseq/releases/tag/2.0.1
