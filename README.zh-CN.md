# System Architect Skill

[English](README.md) | 简体中文

[![CI](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/Dengk3Li/system-architect-skill/actions/workflows/ci.yml)

一个用于登记模块归属、保护共享代码并在整合前检查文件范围的 Agent Skill。

## 快速开始

使用通用 Skills CLI 安装：

```bash
npx skills add Dengk3Li/system-architect-skill --skill system-architect
```

让 Agent 为改动确定模块边界：

```text
Use $system-architect to place this change in one owned module and define the
interfaces needed for integration.
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

- 让每个受管理文件只属于一个模块；
- 保护应用外壳、全局样式、共享 API 和设计变量；
- 为模块接口登记提供方、使用方、版本、错误、写入副作用和负责人；
- 按计划文件、工作区差异或暂存区差异检查修改范围；
- 在不重写整站的前提下，从前端单体中逐步拆出新功能；
- 模块归属、授权或接口没有证据时保留 `UNKNOWN`。

这个仓库同时提供架构指令和一个 Python 范围检查器。

## 为什么需要这个 Skill

多个 Agent 共用一个代码库时，功能任务的实际写入范围经常远大于产品范围。

负责一个页面的开发者，可能仍然可以修改主路由、全局样式、应用外壳、共享服务客户端和其他功能。一次局部改动可能替换导航、破坏兄弟模块的假设，或者把简单接入变成全站改版。

单靠提示词很难形成稳定边界。这个 Skill 把模块归属写进仓库，并检查真实 Git 改动。共享区域仍然可以整合，但它会成为一项明确的架构变更，而不是功能开发的附带结果。

## 架构模型

### 独立归属的模块

每个受管理文件必须匹配一个模块的 `owned_paths`。没有归属或被多个模块同时声明都会检查失败。

### 受保护的共享区域

应用外壳、全局变量、公共 API 适配器等共享区域可以标记为 protected。普通模块开发者不能修改。架构师或集成者需要真实授权，并明确声明架构变更。

### 带版本的接口

模块依赖公开合同，不读取其他模块的私有 DOM、存储、文件或内部函数。接口合同需要说明提供方、使用方、版本、行为和副作用负责人。

### 范围检查

检查器可以在开发前验证计划修改的文件，也可以在交付前检查真实 Git 差异。违规时返回退出码 `2`，可以直接阻断本地 hook 或 CI。

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

1. 阅读已经确认的产品范围和仓库规则。
2. 选择现有模块、新模块或受保护的共享合同变更。
3. 记录页面落点、展示占比、文件归属、接口、保留区域和测试。
4. 开发前检查计划文件。
5. 运行模块测试和合同测试。
6. 整合前检查完整差异。

系统架构师负责模块落点和接口，不会接管所有模块的开发。

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
  scripts/check_module_scope.py
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
