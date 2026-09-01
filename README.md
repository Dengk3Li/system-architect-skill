# System Architect Skill

把一个产品拆成可独立修改的模块，并让负责单个功能的 Agent 留在自己的边界内。

System Architect is an Agent Skill for assigning product changes to owned modules, protecting shared surfaces, and checking file scope before integration.

## 项目背景

这个 Skill 来自 Personal AI OS 的内部开发实践。Personal AI OS 是一个面向长期、多轮、多 Agent 工作的个人 AI 工作控制面。它需要同时处理产品规划、模块开发、跨会话验收和旧功能整合。

实际开发中反复出现两类问题。

第一类发生在产品层。一个对话同时接管许多历史项目后，很容易把不同优先级的工作混在一起。小改动被扩写成完整重构，旧需求和新需求也缺少清楚的边界。

第二类发生在代码层。多个前端功能共用 `app.js`、全局样式、主导航或同一个服务入口时，负责单个页面的对话实际上拥有了整站写权限。它可能为了接入一个模块，顺手改掉共享外壳，甚至覆盖已有页面。

产品经理可以决定做什么、先做什么，却不适合决定每个功能落在哪个代码模块、谁可以修改共享区域、上下游接口如何保持兼容。这个仓库补上了系统架构师角色。

私有 Personal AI OS 实现不在本仓库中。这里保留的是通用工作方法、模块清单模板和边界检查器。

## 它负责什么

系统架构师位于产品规划和模块开发之间。它接收已经明确的产品目标，然后回答五个问题：

1. 这项改动属于哪个模块？
2. 用户会在哪里看到它，页面中应该占多少位置？
3. 这个模块可以修改哪些文件？
4. 它通过什么接口连接上下游？
5. 哪些共享区域必须保留，只有集成者才能改？

它不负责决定产品优先级，也不代替模块开发者写完所有功能。

## 角色分工

```text
产品问题
  ↓
产品经理：目标、优先级、范围、验收结果
  ↓
系统架构师：模块落点、展示预算、文件归属、接口合同
  ↓
模块开发者：只实现一个登记模块
  ↓
集成者：通过登记接口接入共享外壳
```

| 角色 | 对结果负责 | 不应越过的边界 |
|---|---|---|
| 产品负责人或产品经理 | 用户问题、优先级、发布范围、验收标准 | 不直接分配代码所有权 |
| 系统架构师 | 模块落点、共享区域、接口版本、整合顺序 | 不接管所有功能实现 |
| 模块开发者 | 一个模块内的功能和测试 | 不修改兄弟模块与共享外壳 |
| 集成者 | 通过合同连接已完成的模块 | 不重写模块内部实现 |

## 提供的能力

### 给每个文件一个明确所有者

仓库使用 `.system-architect/module-boundaries.json` 登记模块。每个受管理文件必须匹配一个且只能匹配一个模块。

新文件没有所有者时，检查会失败。两个模块同时声明同一文件时，检查也会失败。Agent 不能靠文件名或目录印象猜测归属。

### 保护共享外壳

主导航、全局布局、设计变量、公共 API 入口和跨模块适配器可以登记为 protected module。普通模块开发者无法修改这些路径。

系统架构师或集成者需要得到真实授权，并显式使用 `--architecture-change`。这个参数只记录架构变更意图，不提供授权。

### 把联动写成接口合同

模块联动需要登记 provider、consumer、接口版本和合同说明。具体任务还要说明加载、空状态、错误、不可用状态以及写入权归属。

消费者依赖公开合同，不读取另一个模块的私有 DOM、存储、文件或内部函数。

### 在写代码前后检查范围

边界检查器覆盖四个时点：

- 先检查模块清单是否完整；
- 动手前检查计划修改的文件；
- 交付前检查相对某个 Git 基线的全部改动和未跟踪文件；
- 提交前只检查暂存区。

违规时脚本返回退出码 `2`，可以直接接入本地 hook 或 CI。

### 逐步拆解旧前端

如果旧功能都堆在一个共享文件中，系统架构师会先冻结这个文件，避免普通功能继续写入。新功能进入独立目录，通过一个窄接口接入。旧代码随后按真实需求逐块迁出。

这是一条渐进路径，不要求为了模块化先重写整站。

## 一个典型例子

假设团队要增加订单退款看板。产品目标已经明确，但实现需要退款页面、订单事件和主导航入口。

系统架构师会把 `refund-board` 定为主模块。模块开发者只能修改退款目录和对应测试。订单事件使用已经登记的 `orders.events.v2`。主导航由受保护的 `app-shell` 管理，最后由集成者通过 `shell.slot.v1` 接入。

如果订单事件没有 payload、错误语义或写入权限说明，任务停在 `UNKNOWN`。系统不会为了继续开发而临时发明一个接口。

## 安装

使用兼容 Agent Skills 的安装器安装完整的 `skills/system-architect` 目录。也可以把该目录复制到所用 Agent 工具的 skills 目录。

仓库根目录同时提供 Codex 插件清单：`.codex-plugin/plugin.json`。

## 在项目中启用

复制模板：

```bash
mkdir -p .system-architect
cp skills/system-architect/assets/module-boundaries.template.json \
  .system-architect/module-boundaries.json
```

把示例模块、路径和接口替换为目标仓库的真实信息，然后检查完整性：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --check-manifest
```

检查计划修改的文件：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --files src/catalog/view.ts tests/catalog_view_test.ts
```

检查当前工作区，包括未跟踪文件：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --base HEAD
```

检查暂存区：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module catalog \
  --role module-developer \
  --staged
```

受保护模块需要相应角色和显式架构变更：

```bash
python3 skills/system-architect/scripts/check_module_scope.py \
  --module app-shell \
  --role system-architect \
  --architecture-change \
  --files src/shell/navigation.ts
```

## 适用范围

这个 Skill 适合以下仓库：

- 多个 Agent 或多条开发对话同时工作；
- 前端功能共用主导航、全局样式或大型入口文件；
- 模块需要独立开发，但最终组合成一个产品；
- 旧系统需要逐步拆分，又不能停下来整体重写；
- 团队已经有 PRD，却缺少文件所有权和接口责任人。

单人维护的小型脚本通常不需要这套边界。边界成本应当小于误改共享代码的成本。

## 它不替代什么

- CODEOWNERS 负责把 Pull Request 交给正确的人审查，本工具负责检查 Agent 的文件范围。
- Nx、dependency-cruiser、ArchUnit 等工具检查 import 和依赖方向，本工具检查任务是否跨越模块所有权。
- 单元测试和合同测试检查行为，本工具检查谁可以修改哪些文件。
- Git 分支保护控制合并条件，本工具不会自动合并、推送或发布。

## 仓库结构

```text
.codex-plugin/plugin.json
skills/system-architect/
  SKILL.md
  agents/openai.yaml
  assets/module-boundaries.template.json
  references/architecture-sources.md
  references/change-contract.md
  scripts/check_module_scope.py
tests/test_check_module_scope.py
```

## 参考资料

这个项目主要吸收了以下公开资料：

- [Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)：按用户可见的垂直功能切分前端，由一个团队端到端负责。
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)：登记代码负责人，并与分支保护配合使用。
- [Nx module boundaries](https://nx.dev/docs/guides/enforce-module-boundaries)：用标签和规则约束项目依赖。
- [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md)：把禁止依赖写成可在 CI 中失败的规则。
- [Building Evolutionary Architectures](https://www.thoughtworks.com/content/dam/thoughtworks/documents/books/bk_building_evolutionary_architectures_second_edition_free_chapter.pdf)：用自动化适应度函数持续保护架构特征。
- [MADR](https://adr.github.io/madr/)：用轻量决策记录保存重要架构选择和取舍。

完整的资料说明和相关公开 Skill 对比见 [architecture-sources.md](skills/system-architect/references/architecture-sources.md)。

## 配套 Skill

[Product Manager Skill](https://github.com/Dengk3Li/product-manager-skill) 负责确认问题、优先级、产品范围和验收结果。本 Skill 接手已经明确的产品目标，把它放进一个可独立开发和安全整合的模块。

## 开发与验证

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

检查 Skill 和插件结构：

```bash
python3 <skill-creator>/scripts/quick_validate.py skills/system-architect
python3 <plugin-creator>/scripts/validate_plugin.py .
```

当前版本使用 Python 标准库，不需要安装额外运行依赖。

## License

仓库当前公开可见，但尚未授予开源许可证。
