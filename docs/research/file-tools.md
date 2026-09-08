# 文件组织、存储占用与 Agent 工作区：产品借鉴研究

研究截止：2026-09-08 03:41:27 UTC。本报告覆盖 12 个定向核查项目，重点核查 Spacedrive、TagSpaces、organize、dua 和 Repomix。这是一份有证据的广泛扫描，覆盖文件工具与工作区相关类别，不代表穷尽 GitHub。架构工具与实验追溯工具见同目录的分领域研究。

## 结论

首版应成为“看懂目录职责、找到产物来历”的只读工作台。以一个可携带的数据模型连接目录、模块、文件版本与运行记录，让使用者回答：这个目录负责什么、哪个版本产生了这个结果、占用集中在哪里。扫描、校验、统计与关系验证用确定性代码完成；AI 可以提出目录职责和业务性质的候选解释。

本次没有找到需要首版直接嵌入的整套文件平台。建议自行实现小型只读扫描器、模型与交互视图。未来确有规模需求时，优先评估 gdu 报告导入；上下文分享可以评估 Repomix 可选导出。目录治理、同步、删除、去重执行与 Agent 调度均不进入首版。

这一取舍来自功能与代价的比较：文件平台的丰富元数据可借鉴，但同时带来守护进程、同步和写权限；磁盘工具的扫描与快照已成熟，但尚不能说明实验因果；Agent 工作区保留任务上下文，但任务日志不能证明产物由何种输入生成。

## 搜索方式与证据边界

- 公共网页检索共 5 个查询：`site:github.com file organization disk usage Spacedrive TagSpaces organize`；`site:github.com Agent workspace Trellis Repomix Backstage`；`site:github.com file organizer organize rules dry-run`；`site:github.com disk usage analyzer dua gdu dust QDirStat WinDirStat`；`site:github.com mindfold Trellis AI workflows`。
- GitHub REST `GET /search/repositories` 共 8 个查询，默认相关度，每个取前 10 条，没有按 Star 排名。四组词为 `file organizer`、`disk usage analyzer`、`agent workspace`、`file tagging`；先查 name/description（文件组织首轮还含 README），再用带引号的精确短语查询。第二轮空间词为 `"disk usage"`。原始请求词、返回列表、返回总数均保存在 `github-search-results.json`。8 次结果中共出现 74 个不同仓库；这只是发现列表，不能当作已评估项目数。
- 通过已知候选和 README 的 alternatives/related links 补充，按“文件性质、目录大小、内容身份、可导出报告、Agent 上下文、软件所有权”补齐覆盖面。项目总数受检索窗口限制，搜索返回总数不用于市场规模或完备性结论。
- 同名仓库先核验作者与官方互链。TagSpaces 采用 `tagspaces/tagspaces`；Trellis 采用 `mindfold-ai/Trellis`，没有把搜索结果里的同名 OpenCnid 项目混入。
- 每个入选项目读取一手 README、当前许可、默认分支 HEAD、近期 5 条提交、GitHub Releases 与 tags；重点项目继续读取源码或测试。所有源码结论绑定下表固定提交。GitHub 的 latest release 字段只是平台标签，不能自动证明产品稳定性。
- 本次未安装、未启动候选工具，未执行第三方安装脚本或上游测试。代码验证仅指静态核查调用、字段和分支；作者提供的性能、截图和演示不能视为本机体验或性能测量。默认分支的新功能与已发布二进制分别说明。

## 覆盖矩阵

| 项目 | 覆盖问题 | 取舍 | 当前许可 | 维护与发布证据 | 一手入口 |
|---|---|---|---|---|---|
| Spacedrive | 跨设备文件平台 | 采用位置与内容身份分离、离线状态；自行实现模型；不整包集成 | FSL-1.1-ALv2；当前版本两年后转 Apache-2.0 | v2.0.0-alpha.2（2026-02-07，预发布）；旧线 0.4.3 被 API 标作非预发布，但发布正文仍称 alpha；[HEAD 6dfeccf2](https://github.com/spacedriveapp/spacedrive/commit/6dfeccf2113039e35f2ce735f945e70dc3e4ea45) 2026-07-29 | [README](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/README.md) · [许可原文](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/LICENSE) |
| TagSpaces | 文件标签与详情 | 采用多维标签与详情交互；元数据存于工作台覆盖层；不使用文件名标签、不嵌入 Pro | AGPL-3.0；商业双许可；Pro 组件另有专有 EULA | v6.13.12（2026-07-20，非预发布）；[HEAD 7ec3a2e8](https://github.com/tagspaces/tagspaces/commit/7ec3a2e8632b8bf5db685436e6d2d8805977a880) 2026-07-24 | [README](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/README.md) · [许可原文](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/LICENSE.txt) |
| organize | 确定性文件组织规则 | 采用透明规则和预览；只读分类自行实现；首版不集成移动/删除引擎 | MIT | v3.3.0（2024-11-25，非预发布）；main 后续有提交；[HEAD 36a54572](https://github.com/tfeldmann/organize/commit/36a54572488d89dc9279d79848ecc067b632f1a5) 2026-03-15 | [README](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/README.md) · [许可原文](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/LICENSE.txt) |
| dua | 空间分析、快照与差异 | 采用快照/比较、占用口径、错误可见；默认扫描自行实现；有规模瓶颈后再评估适配器 | MIT | dua CLI v2.44.0（2026-08-30）有快照；2026-09-07 最新 release 为 dua-core-v4.0.0，不能当 CLI 版本；[HEAD 0e992386](https://github.com/Byron/dua-cli/commit/0e992386d15275d08b4e1ef40196edb2a30dd799) 2026-09-07 | [README](https://github.com/Byron/dua-cli/blob/0e992386d15275d08b4e1ef40196edb2a30dd799/README.md) · [许可原文](https://github.com/Byron/dua-cli/blob/0e992386d15275d08b4e1ef40196edb2a30dd799/LICENSE) |
| dust | 目录大小树 | 采用缩进树、相对比例条、深度控制；已有读写无关功能无需依赖 | Apache-2.0 | v1.2.5（2026-08-19）；[HEAD 8a846f66](https://github.com/bootandy/dust/commit/8a846f6689f2db6be6ef595239a21ec784d62b57) 2026-08-18 | [README](https://github.com/bootandy/dust/blob/8a846f6689f2db6be6ef595239a21ec784d62b57/README.md) · [许可原文](https://github.com/bootandy/dust/blob/8a846f6689f2db6be6ef595239a21ec784d62b57/LICENSE) |
| gdu | 空间扫描与可导入报告 | 最合适的后续空间报告导入候选；采用原始字节、错误标记与扫描范围；首版不内置依赖 | MIT | v5.37.0（2026-08-18）；[HEAD 0dd3ecb4](https://github.com/dundee/gdu/commit/0dd3ecb41e2814c41c289a5d95af36f50431c329) 2026-09-04 | [README](https://github.com/dundee/gdu/blob/0dd3ecb41e2814c41c289a5d95af36f50431c329/README.md) · [许可原文](https://github.com/dundee/gdu/blob/0dd3ecb41e2814c41c289a5d95af36f50431c329/LICENSE.md) |
| QDirStat | 类型分布与树图 | 采用目录/类型统计联动、尺寸分布；不采用清理命令或桌面依赖 | GPL-2.0 | 2.0（2026-01-18）；[HEAD f4a37d96](https://github.com/shundhammer/qdirstat/commit/f4a37d961da75acb1dc3f8ec9c935b34c35c8757) 2026-08-22 | [README](https://github.com/shundhammer/qdirstat/blob/f4a37d961da75acb1dc3f8ec9c935b34c35c8757/README.md) · [许可原文](https://github.com/shundhammer/qdirstat/blob/f4a37d961da75acb1dc3f8ec9c935b34c35c8757/LICENSE) |
| WinDirStat | Windows 占用与清理 | 采用逻辑/物理尺寸切换、扩展名联动；不带入系统维护与删除 | 应用 GPL-2.0；部分源码另许可；图标 CC BY 3.0 | release/v2.8.0（2026-08-02）；beta/v2.8.3/2026-09-07（预发布）；[HEAD 9e9b7222](https://github.com/windirstat/windirstat/commit/9e9b7222f8709ad6fd4d419156930212ac5129ad) 2026-09-07 | [README](https://github.com/windirstat/windirstat/blob/9e9b7222f8709ad6fd4d419156930212ac5129ad/README.md) · [许可原文](https://github.com/windirstat/windirstat/blob/9e9b7222f8709ad6fd4d419156930212ac5129ad/LICENSE.md) |
| Czkawka / Krokiet | 重复与文件异常诊断 | 后续可考虑只读诊断；首版不做清理、近似重复或自动去重 | 核心/CLI 代码 MIT；Krokiet/Cedinia 应用 GPL-3.0-only；媒体素材 CC BY 4.0 | 12.0.1（2026-07-29）；README 已说明旧 GTK GUI 停止新二进制，转向 Krokiet；[HEAD 499f15c7](https://github.com/qarmin/czkawka/commit/499f15c718fbf3a6baebbef75e8983d510eb6904) 2026-09-03 | [README](https://github.com/qarmin/czkawka/blob/499f15c718fbf3a6baebbef75e8983d510eb6904/README.md) · [许可原文](https://github.com/qarmin/czkawka/blob/499f15c718fbf3a6baebbef75e8983d510eb6904/LICENSE_CC_BY_4_ICONS) |
| Repomix | AI 上下文打包与分享 | 采用范围选择、跳过原因、可携带导出；未来可选上下文包；不作为版本或实验记录权威 | MIT | v1.18.0（2026-08-08）；本次代码核查 main HEAD，不能把 HEAD 新行为一概写成已发布行为；[HEAD dc40590d](https://github.com/yamadashy/repomix/commit/dc40590d5fe46069bae0cb6f40ba953992e618b5) 2026-09-07 | [README](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/README.md) · [许可原文](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/LICENSE) |
| Trellis | 任务与 Agent 上下文 | 采用有目的的上下文清单与字节预算；不引入任务状态机、hook 或固定目录模板 | AGPL-3.0-only（CLI 包声明） | GitHub Releases 列表为空；main/CLI 0.6.16，tag v0.6.16；另有 v0.7.0 beta 标签，未审查；[HEAD 88f48344](https://github.com/mindfold-ai/Trellis/commit/88f4834449da9b4f607ec05e322408a0aa66f2ce) 2026-08-27 | [README](https://github.com/mindfold-ai/Trellis/blob/88f4834449da9b4f607ec05e322408a0aa66f2ce/README.md) · [许可原文](https://github.com/mindfold-ai/Trellis/blob/88f4834449da9b4f607ec05e322408a0aa66f2ce/LICENSE) |
| Backstage | 软件目录与所有权关系 | 采用实体类型、owner、system、dependsOn 显式关系；不部署完整门户 | Apache-2.0 | v1.54.6（2026-08-28，稳定）；v1.55.0-next.1（2026-09-01，预发布）；[HEAD 97a7e8e7](https://github.com/backstage/backstage/commit/97a7e8e7b7c3d65d3a0a635289659420de618e32) 2026-09-07 | [README](https://github.com/backstage/backstage/blob/97a7e8e7b7c3d65d3a0a635289659420de618e32/README.md) · [许可原文](https://github.com/backstage/backstage/blob/97a7e8e7b7c3d65d3a0a635289659420de618e32/LICENSE) |

维护日期仅证明该次提交或发布存在，不代表响应速度、活跃用户数或商业可持续性。当前 12 个仓库的 API 均未标记 archived。

## 五个重点候选

### Spacedrive：借鉴位置与内容分离，不复制跨设备平台

作者将其定位为跨设备数据平台，提供索引、P2P、云卷、内容身份、多个文件视图和 Agent 访问面。当前源码区分文件条目与内容：entry 保存父目录、卷、大小、修改时间和可选 content_id；content_identity 另存快速 content_hash 与完整 integrity_hash。核查发现，大于 100 KiB 的快速摘要只读取首尾及四个中间片段，输出截断为 16 个十六进制字符；这是一种低成本候选身份策略。完整校验字段也已存在，不能把 Spacedrive 的所有身份处理都说成采样。[条目字段](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/core/src/infra/db/entities/entry.rs#L10-L30)；[双摘要字段](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/core/src/infra/db/entities/content_identity.rs#L10-L25)；[摘要实现](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/core/src/domain/content_identity.rs#L124-L253)。

**采用**：路径位置与内容身份分离；离线/可用状态独立于内容存在；派生产物单独建模。**自行实现**：实验版本使用完整摘要和明确算法，支持“尚未计算”；采样相同最多作为候选重复。**不采用**：P2P、云卷、权限代理、守护进程和整套平台依赖。当前 FSL 有 Competing Use 限制，两年后的许可转换不等于当前可任意复制竞品代码；本版只借鉴概念，保留独立实现。发布 v2 alpha.2 正文明确仍有功能未工作，main 的最新能力不能等同于该预发布体验。[许可原文](https://github.com/spacedriveapp/spacedrive/blob/6dfeccf2113039e35f2ce735f945e70dc3e4ea45/LICENSE)；[alpha.2 发布说明](https://github.com/spacedriveapp/spacedrive/releases/tag/v2.0.0-alpha.2)。

使用成本：下载预发布包可减少初始安装步骤；源码环境需要 Rust、Bun、just，部分适配器另需 Python。整合其后台、数据库与跨设备协议的成本明显高于本次只读本地范围。未实际启动产品。

### TagSpaces：借鉴多维性质，元数据与原目录分开保存

作者主张离线文件管理、标签、搜索和预览。静态代码能确认两条不同写入路径：标签可以编码进文件名并触发重命名，也可以写入旁置元数据；保存元数据会在条目所在位置创建元数据目录并写 JSON。详情保存逻辑检查只读 location，但整套产品仍包含文件写操作。[标签写入分支](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/src/renderer/hooks/TaggingActionsContextProvider.tsx#L521-L588)；[元数据写入](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/src/renderer/hooks/IOActionsContextProvider.tsx#L2154-L2227)；[只读详情保存判断](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/src/renderer/hooks/FilePropertiesContextProvider.tsx#L140-L161)。

**采用**：在目录之外添加可搜索的多维业务标签，文件详情集成说明和性质。**自行实现**：标签、注释和模块映射存入工作台的显式输出文件或用户指定元数据库，关联相对路径与版本 ID；对受观察目录保持只读。**不采用**：以改名持久化标签，以及默认在真实实验目录散布 sidecar。两者都会改变现有脚本、路径和快照。开源代码为 AGPL，Pro 是独立专有部分，本版没有复制组件。[许可组成](https://github.com/tagspaces/tagspaces/blob/7ec3a2e8632b8bf5db685436e6d2d8805977a880/LICENSING.md)。

使用成本：桌面包可直接试用；源码开发有 Electron、Node/npm 和本地服务。标签录入还需要使用者维护业务语义。当前 develop 与稳定发行应分别判断；未实际操作其 UI。

### organize：采用可解释的规则匹配，不引入文件动作引擎

作者提供 YAML 规则、模拟与移动/重命名/删除。代码表明 `sim` 和 `run` 分别传入 simulate 真/假，Move 和 Delete 在非模拟时执行实际文件动作。MIME 过滤器调用 Python `mimetypes.guess_type(path)`，它推测的是路径对应的媒体类型，不能证明文件内容，也不能识别“原始数据/中间产物/结论”。[CLI 模式](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/organize/cli.py#L270-L281)；[移动分支](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/organize/actions/move.py#L67-L99)；[删除分支](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/organize/actions/delete.py#L18-L45)；[MIME 规则](https://github.com/tfeldmann/organize/blob/36a54572488d89dc9279d79848ecc067b632f1a5/organize/filters/mimetype.py#L14-L59)。

**采用**：规则是可阅读数据，显示匹配理由与预览结果。**自行实现**：首版限定无副作用的规则，例如扩展名、相对路径、模块映射；字段标明规则来源。**不采用**：移动、覆盖、删除以及任意 Python/shell 扩展。单纯识别文件性质不需要通用规则执行器。MIT 许可允许在条件内复用，仍没有必要为几个分类规则新增整套依赖。

使用成本：Python 3.9+ 与一个包即可开始，但用户需要维护 YAML，任意脚本能力带来审查成本。最新 GitHub release 为 2024 年，main 在 2026 年仍有提交；不能只看旧 release 就判定废弃，也不能把 main 变化称为已发布。

### dua：历史快照已是基线，实验来源才是补充价值

作者已在 CLI v2.44.0 发布快照导出与比较。当前代码把扫描条目写成有版本的确定性快照，并用 SHA-256 校验快照数据流；条目包含名称、尺寸、修改时间和错误标志。这个校验说明保存的快照是否完整，不是每个源文件的内容哈希。目录的逻辑长度与磁盘分配尺寸走不同分支，读取失败会保留错误状态。[CLI 快照发布说明](https://github.com/Byron/dua-cli/releases/tag/v2.44.0)；[快照格式与校验](https://github.com/Byron/dua-cli/blob/0e992386d15275d08b4e1ef40196edb2a30dd799/src/snapshot/mod.rs#L291-L434)；[尺寸与错误处理](https://github.com/Byron/dua-cli/blob/0e992386d15275d08b4e1ef40196edb2a30dd799/src/traverse.rs#L1015-L1057)。

**采用**：保存可重开的扫描结果、比较新增/移除/占用变化、显示扫描范围与不完整状态。**自行实现**：运行记录明确引用输入和输出版本，用 run、configuration、artifact、conclusion 的显式关系解释“为什么变化”。**不采用**：把快照变化自动解释为实验关系或可回收空间。硬链接、APFS 克隆与逻辑长度有不同口径，源文件大小之和不能直接叫“真实可释放容量”。dua 自身也明确 APFS clone 去重是选择项，部分共享块不覆盖。[README](https://github.com/Byron/dua-cli/blob/0e992386d15275d08b4e1ef40196edb2a30dd799/README.md)。

使用成本：二进制入口轻，TUI 的高级操作和跨平台统计仍需要学习；代码适配与格式升级有持续成本。最新 API release 是 dua-core，不可拿核心库版本充当 CLI 发布号。上游 snapshot/diff 测试已阅读，未运行。

### Repomix：采用可携带上下文，保留事实与分享边界

作者让仓库能通过 CLI、MCP 和 Skill 变成 AI 易读的内容包。当前源码能确认读取并发有上限、被跳过文件记录原因，范围受限模式会比较真实路径，避免只看字符串路径造成符号链接越界；相应真实符号链接测试存在，但未在本次执行。普通 CLI 的范围限制开关默认关闭，不能声称所有入口天然受同样约束。[收集与跳过记录](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/src/core/file/fileCollect.ts#L9-L60)；[真实路径边界](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/src/core/file/fileSearch.ts#L291-L321)；[符号链接测试](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/tests/core/file/fileSearchConfineSymlink.test.ts#L8-L55)。

**采用**：先选择范围，告知跳过项，再导出可携带结果；为陌生人提供示例和可直接使用的出口。**可能集成**：经过用户选择的代码上下文包，作为可选适配器。**不采用**：把拼接文本当目录事实库，或自动把文件内容送入 AI。Secretlint 是已知模式检测，不能替代导出白名单；本机配置可调用外部处理命令，也须与只读模式分开。当前 package.json 要求 Node >=22。[运行要求](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/package.json#L127-L130)；[README](https://github.com/yamadashy/repomix/blob/dc40590d5fe46069bae0cb6f40ba953992e618b5/README.md)。

## 另外七项提供的约束

- **gdu** 提供 JSON 导出/导入，代码保存 Size、Usage、Mtime。适合作为后续离线报告接口候选；先写适配合同再选择依赖。导入旧报告应显示观察时间与来源，不能显示为“实时”。[导出字段](https://github.com/dundee/gdu/blob/0dd3ecb41e2814c41c289a5d95af36f50431c329/report/export.go#L165-L205)；[导入实现](https://github.com/dundee/gdu/blob/0dd3ecb41e2814c41c289a5d95af36f50431c329/report/import.go)。
- **dust、QDirStat、WinDirStat** 说明大小比例条、目录树、类型统计及选中联动都是成熟表达。首版用这些熟悉的语法即可。大面积矩形树图可作占用补充，但不能解释模块职责和实验关系。此项是依据官方示例提出的设计判断，未做 UI 可用性测量。[README](https://github.com/bootandy/dust/blob/8a846f6689f2db6be6ef595239a21ec784d62b57/README.md)；[README](https://github.com/shundhammer/qdirstat/blob/f4a37d961da75acb1dc3f8ec9c935b34c35c8757/README.md)；[README](https://github.com/windirstat/windirstat/blob/9e9b7222f8709ad6fd4d419156930212ac5129ad/README.md)。
- **Czkawka/Krokiet** 区分按内容发现重复、近似媒体匹配和扩展名异常，提醒“同名”“同尺寸”“相似”“相同内容”需要分开。其清理目的与本次追溯目的不同，首版不增加自动去重。许可也按核心、应用与媒体素材分别处理。[README](https://github.com/qarmin/czkawka/blob/499f15c718fbf3a6baebbef75e8983d510eb6904/README.md)；[核心清单](https://github.com/qarmin/czkawka/blob/499f15c718fbf3a6baebbef75e8983d510eb6904/czkawka_core/Cargo.toml)；[GUI 清单](https://github.com/qarmin/czkawka/blob/499f15c718fbf3a6baebbef75e8983d510eb6904/krokiet/Cargo.toml)。
- **Trellis** 把 implement/check 上下文组织为清单，实际代码校验条目、大小和可解析位置；注入器有每文件、每产物与总字节预算。适合借鉴“按目的选上下文”，任务日志仍是工作记录，不等同于数据或实验版本。整套任务创建、hook、状态机不适合普通文件查看。[清单校验](https://github.com/mindfold-ai/Trellis/blob/88f4834449da9b4f607ec05e322408a0aa66f2ce/packages/cli/src/templates/trellis/scripts/common/task_context.py#L270-L400)；[预算与路径边界](https://github.com/mindfold-ai/Trellis/blob/88f4834449da9b4f607ec05e322408a0aa66f2ce/packages/cli/src/templates/shared-hooks/inject-subagent-context.py#L170-L288)。
- **Backstage** 的实体 envelope 有 apiVersion/kind/metadata，Component 显式声明 owner、system、dependsOn、提供/消费 API。这证明架构语义应有独立模型，文件夹名称不能代替职责。采用关系约定即可；完整门户的开发和运维成本超出首版。[实体模型](https://github.com/backstage/backstage/blob/97a7e8e7b7c3d65d3a0a635289659420de618e32/packages/catalog-model/src/schema/Entity.schema.json#L26-L64)；[组件契约](https://github.com/backstage/backstage/blob/97a7e8e7b7c3d65d3a0a635289659420de618e32/packages/catalog-model/src/kinds/ComponentEntityV1alpha1.ts#L30-L44)；[安装成本](https://github.com/backstage/backstage/blob/97a7e8e7b7c3d65d3a0a635289659420de618e32/docs/getting-started/index.md#L68-L97)。

## 对首版模型与界面的建议

| 概念 | 确定性事实 | 可编辑解释或候选 | 需要保留的区别 |
|---|---|---|---|
| 路径条目 | root_id、相对路径、条目类型、观察时间、读取结果 | 显示名、说明 | 路径是位置；移动不必产生新内容 |
| 内容版本 | 算法、完整摘要、长度、计算状态 | 外部版本别名 | 未哈希、采样候选、完整校验分别表示 |
| 快照 | 扫描 ID、时间、范围/排除规则、条目引用、完整性 | 快照名称 | 扫描结果不是原子文件系统快照，也不是数据备份 |
| 模块 | 明确来源的路径覆盖、接口/依赖声明 | 职责、边界候选 | 扫描观察、人工声明、AI 建议分开 |
| 运行 | 输入/配置/输出的版本 ID、时间、状态、来源记录 | 运行说明 | 时间相近或同目录不足以推出 used/generated 关系 |
| 结论 | 引用的运行/产物/证据 | 人工陈述、AI 候选归纳 | 运行完成不等于结论获验证 |
| 格式与性质 | 扩展名、媒体类型及检测方法 | 原始数据、配置、中间结果、发布产物等业务角色 | `.csv` 是格式，`训练输入` 是角色；两者可独立过滤 |
| 存储 | 逻辑字节、可得时的分配字节、硬链接/读取错误 | 展示分组 | 全部尺寸之和不是独占占用；占用不是可回收量 |

范围边界采用明确根目录、相对路径与输出位置。读取失败保留 unknown/partial；符号链接默认只记录链接本身，跨根内容不读取。扫描报告排除规则和状态可见。完整内容哈希需要读取文件，支持按需计算、时间与大小预算；扫描中变化的文件标记不稳定，不能把两次状态拼成确定版本。公开导出需要独立的安全视图，默认只用合成样例；白名单字段比全量导出后屏蔽少量关键词更可靠。

建议三个主视图共享选中对象：

1. **目录与架构**：左侧目录树，中部模块/路径对应，右侧详情；模块职责与物理目录保持可关联的两种视角。颜色用于对象类别或状态，面积与条长用于尺寸。
2. **来源与历史**：选中一个产物后展示“输入版本 → 运行 → 输出版本 → 结论”，同时列出不同快照的变化。默认呈现小范围关系，不把全库堆成连线密集的图。
3. **文件详情与空间**：逻辑大小、分配大小（若可得）、格式、业务角色、摘要状态、来源及相关运行。总览可按模块、格式、角色聚合；选择占用区块时定位到同一文件列表。

AI 判断定位为 AI_ASSISTED：可根据受选范围提出目录职责、业务角色、关系候选和解释；结构化结果包含证据引用与不确定性。扫描、哈希、大小、版本关系校验和所有写入权限由普通代码处理。AI 不决定版本事实、文件删除、权限或实验结论是否成立。无 AI 时，扫描、浏览、过滤、显式运行登记和导出仍完整可用。

## 可体验成果的验证问题

这些是首版需要通过的任务，不是本次已经测得的产品表现：

- 陌生人打开合成示例后，能从一个目录找到对应模块、职责和关键文件。
- 从一个结果文件，找到所用输入版本、配置及运行，并识别缺失的来源记录。
- 对比两次扫描，解释增量来自哪些文件；对内容未知和读取失败不作伪精确结论。
- 在文件详情中区分格式、业务角色、逻辑大小和占用口径。
- 导出可重新打开的示例结果，保存模块和运行关联；导出物不含本机绝对路径或未经选择的内容。

“看懂 → 愿意试 → 得到结果 → 愿意分享”的具体入口可用一个零安装示例页、三个可完成的小任务和可携带 JSON/HTML。这个设计假设应在原型中验证；检索证据没有证明任一候选关注度的增长原因，也没有证明它们与本产品拥有相同体验。

## 证据文件

公开候选矩阵见 `file-candidates.json`，发现查询及结果见 `file-search-results.json`。正文源链接固定到本次读取的提交。完整第三方源码缓存不随产品分发。
