# LION Agent 规范

> 本文件是 LION 仓库中 AI Agent、贡献者和维护者共同遵守的工作规范。
> 任何 Agent 在修改代码、文档、构建配置或打包产物之前，必须先完整阅读本文件。
> 本文件不是用户手册，也不替代 NVDA 官方开发者文档；若与 README、NVDA 官方规范冲突，以本文件的“强制约束”为底线，并在提交说明中指出冲突来源。

## 1. 项目事实基线

LION 是一个 NVDA 全局插件（global plugin）与附加组件（add-on），基于 NVDA addonTemplate 构建，使用 PaddleOCR-json 在本地对屏幕区域进行定时 OCR，并将“与上次结果差异足够大”的新文本朗读给用户。

仓库关键事实：

- 包名/内部标识：`LION`
- 插件入口：`addon/globalPlugins/lion/__init__.py`
- 设置面板：`addon/globalPlugins/lion/lionGui.py`
- OCR 引擎：`addon/globalPlugins/lion/PaddleOCR/PaddleOCR-json.exe`
- 文本块后处理：`addon/globalPlugins/lion/tbpu/`
- 构建配置：`buildVars.py`、`sconstruct`、`manifest.ini.tpl`
- 当前版本：`3.3.0`
- 最低兼容 NVDA：`2026.1`
- 最后测试 NVDA：`2026.1`

核心运行链路：

1. 用户在设置面板选择识别目标、间隔、裁剪区域、相似度阈值和正则过滤器。
2. 触发 `NVDA+ALT+N` 后，插件启动后台线程。
3. 后台线程周期性抓取屏幕区域，保存为 PNG，通过 PaddleOCR-json 的管道/Base64 接口识别。
4. 识别结果经过正则过滤后，与上一轮结果计算相似度；超过阈值才朗读。

Agent 不得把 LION 当作独立的桌面应用、网络服务或通用 OCR SDK 来重构。它的边界是 NVDA 附加组件。

## 2. 强制约束

### 2.1 身份与边界

- 不得把 `addonTemplate`、`NV Access`、`info@nvaccess.org` 等模板残留信息当作本项目身份继续沿用。新建或维护时，应使用 LION 的真实作者、仓库地址和项目说明。
- 不得修改或删除 `COPYING.txt`，除非法律或维护者明确要求。
- 不得在插件内部加入广告、捐赠弹窗、遥测、自动联网上传或绕过 NVDA 的更新渠道，除非该行为在用户界面中显式说明并默认关闭。
- 不得把插件名改为包含 `NVDA`、`plugin`、`appmodule`、`globalPlugin` 等实现性词汇；用户不应从名称中感知实现方式。

### 2.2 无障碍与用户价值优先

- 所有交互必须可由键盘完成，设置面板不得依赖鼠标。
- 朗读内容必须简洁、可中断、可配置，并避免重复朗读相同文本。
- 新功能不得以牺牲响应速度、NVDA 主线程稳定性或电池/CPU 消耗为代价。
- 任何面向用户的可见文本都必须可翻译；不能写死中文、英文或第三方语言。

### 2.3 隐私与安全

- OCR 必须默认在本地完成。不得把屏幕图像、识别文本、正则表达式或用户配置发送到网络，除非用户明确开启且界面清楚说明。
- 不得在普通日志或调试输出中记录识别到的完整文本、屏幕截图、密码、剪贴板内容或其他敏感信息。
- 启动识别前必须检查 NVDA 屏幕遮蔽（screen curtain）；识别过程中若屏幕遮蔽开启，应停止后续 OCR，并向用户说明。
- 不得在安全桌面、UAC 提升界面或其他安全屏幕执行 OCR，除非经过明确的风险评估且默认禁止。
- 对 PaddleOCR-json 及随附 DLL/模型文件的升级，必须核验来源、记录版本、保留许可证与校验信息；不得随手替换二进制文件。

### 2.4 许可证与版权

- 新增 Python 源文件必须包含与项目一致的 GPL 版权头；对外分发应使用与 NVDA 兼容的 GPL 2 或更新版本。
- 引用的第三方组件必须可追溯到原始项目并保留其许可证信息。
- 不得引入与 GPL 2+ 不兼容的许可证，不得引入需要用户付费才能使用的专有依赖。

## 3. NVDA 插件工程规范

以下规则以 NVDA Code Standards、NVDA Add-on Development Overview、Global Plugins 文档和 Add-on 社区实践为准。

### 3.1 目录与构建

必须保留 addonTemplate 的标准目录：

- 全局插件放 `addon/globalPlugins/<plugin_name>/`
- 可翻译文本放 `addon/locale/`
- 文档放 `addon/doc/`
- 构建变量集中在 `buildVars.py`

构建命令：

```powershell
uv sync
uv run pre-commit run --all-files
uv run pyright
uv run ruff check .
uv run ruff format --check .
uv run scons
uv run scons pot
```

Agent 不得直接提交 `.nvda-addon`、`.pot`、`.mo`、`*.html`、`manifest.ini`、`addon/doc/<baseLanguage>/` 等构建生成物，除非发布流程明确要求。

### 3.2 编码风格

- Python 文件使用 UTF-8，无 BOM。
- 文本文件使用 LF 行尾；本地 Windows 开发可通过 `core.autocrlf` 检出 CRLF。
- 缩进使用制表符（tab），不使用空格；多行语句不进行垂直对齐。
- 行宽遵循 `pyproject.toml` 中的 `line-length = 110`。
- 遵循 PEP 8，除非与上述 NVDA 规范冲突。
- 使用 Ruff 与 Pyright 作为统一格式、静态检查和类型检查工具。

### 3.3 命名

- 函数、变量、属性：`mixedCase` 且首字母小写，例如 `getDynamicTargetRect`、`prevString`。
- 布尔值：使用肯定表达，并以 `should`、`is`、`has` 等词开头，例如 `isScreenCurtainRunning`。
- 类：`CamelCase`，例如 `LIONSettingsPanel`、`PPOCR_pipe` 这类历史命名不要在新代码中复制。
- 常量：`UPPER_SNAKE_CASE`。
- 脚本：以 `script_` 开头，后接 camelCase，例如 `script_readLiveOcr`。
- 事件处理器：以 `event_` 开头，后接 camelCase，例如 `event_gainFocus`。
- 枚举：枚举类用 PascalCase，成员用 `UPPER_SNAKE_CASE`。

历史代码中出现的 `PPOCR_pipe`、`tbpuName` 等命名属于第三方或旧式代码，不构成新代码的命名依据。

### 3.4 类型、文档与导入

- 所有新代码必须使用 PEP 484 类型标注，覆盖参数、返回值、变量、属性和集合类型。
- 联合类型使用 `X | Y`，不要使用 `typing.Union`；可选类型使用 `T | None`，不要使用 `typing.Optional`。
- 公开函数、类和方法必须使用 Sphinx 格式 docstring，且不要在 docstring 中重复类型信息；类型信息应通过类型标注表达。
- 删除未使用导入；如果导入是用于再导出，则加入 `__all__`，否则添加 `# noqa: <原因>`。
- 避免模块级全局变量。若确需模块级变量，应加下划线前缀并用 getter/setter 封装。
- 避免在 import 时执行有副作用或昂贵逻辑；应改为显式初始化函数，并在 `__init__` 中调用。
- 调用 Windows API 时使用 `ctypes`，外部函数/结构的类型命名应尽量与原始 C 声明一致，例如 `GetSystemMetrics`。

### 3.5 可翻译字符串

- 遵循 NVDA 翻译规范：所有面向用户的字符串必须用翻译函数包裹。
- 普通字符串使用 `_()`；涉及复数使用 `ngettext()`；需要上下文区分时使用 `pgettext()` 或 `npgettext()`。
- 每个可翻译字符串前必须有 `# Translators:` 注释，说明用途和上下文。
- 新增、修改或删除用户可见字符串时，同步维护 `pot`/`po` 流程。

### 3.6 线程与 UI

- NVDA 不是完全线程安全的。耗时 OCR 必须放在后台线程。
- 按 NVDA Global Plugins 文档，耗时任务放在后台线程；涉及 UI、语音或 NVDA 对象的更新，优先通过 `wx.CallAfter` 或 `queueHandler.queueFunction(queueHandler.eventQueue, ...)` 回到主线程执行。
- 不得使用无限忙等循环。周期任务应使用可中断的 `Event.wait(timeout)` 或队列，并支持退出。
- `interval` 必须设置大于 0 的下限，防止 0 秒间隔形成空转循环。
- 事件处理器中不要执行重任务；需要 `nextHandler()` 时，除非有明确理由，否则必须调用。

### 3.7 配置管理

- 配置项统一注册到 `config.conf.spec["lion"]`，并在设置面板中读写。
- 配置 spec 应给出合理默认值、范围和类型，且与设置面板的显示、保存逻辑保持一致。
- 不得在模块导入时写入 `config.conf.spec`；应放入插件初始化阶段。
- 新配置项必须有可翻译说明、用户可见反馈，并写入英文与中文文档。

### 3.8 设置面板

- 设置面板继续使用 NVDA 设置对话框中的 category panel，不要另起独立顶层窗口，除非有充分理由。
- 标签使用助记符（`&`），并确保不重复、可翻译。
- 正则过滤器等自定义输入必须处理回车、焦点和错误输入，不能导致对话框异常关闭。
- 无效正则表达式必须在保存或运行时给出明确反馈，而不是静默忽略。

### 3.9 生命周期与资源清理

- `__init__` 中创建的资源必须在 `terminate` 中清理，并调用 `super().terminate()`。
- 后台线程在插件终止时应设置停止标志并等待合理超时。
- PaddleOCR-json 子进程必须在插件卸载时可靠退出；不得留下孤儿进程。
- 不得在 `terminate` 之后继续捕获屏幕或朗读文本。

## 4. 版本、发布与文档同步

- 版本号使用 `major.minor.patch`，且三部分必须为整数，符合 NV Access Add-on Store 要求。
- 修改版本时，必须同步以下位置，避免漂移：
  - `buildVars.py` 中的 `addon_version`、`addon_changelog`、兼容版本字段
  - `changelog.md`
  - `readme.md`
  - `addon/doc/zh_CN/readme.md`
  - 必要时更新 `pyproject.toml` 的项目元数据
- `addon_minimumNVDAVersion` 与 `addon_lastTestedNVDAVersion` 必须真实反映测试情况；不要随意提高或降低。
- 英文本应作为基础语言文档（`baseLanguage = "en"`）维护；中文文档应与英文保持内容一致，不能只更新一侧。
- 发布前确认 `addon_license`/`addon_licenseURL`、`addon_author`、`addon_url`、`addon_sourceURL` 均已正确填写。
- 发布到 Add-on Store 或社区时，遵循 NV Access 提交指南和社区代码审核要求；`nvda-addon` 的 SHA256 不应被发布后篡改。

## 5. Agent 验证清单

任何代码或文档修改完成前，Agent 必须逐项确认：

- [ ] 已阅读本文件、`readme.md`、`addon/doc/zh_CN/readme.md` 和相关 NVDA 文档。
- [ ] 新代码符合命名、缩进、类型标注和 docstring 规则。
- [ ] 用户可见字符串均已标记翻译并带 `# Translators:` 注释。
- [ ] 没有引入新的模块级副作用或 import 时初始化。
- [ ] 线程与 UI/朗读更新方式符合第 3.6 节规则。
- [ ] 资源在 `terminate` 中清理，线程和子进程可退出。
- [ ] 隐私保护已落实：本地处理、不记录识别内容、不捕获安全屏幕。
- [ ] 配置、文档、changelog、版本号同步更新。
- [ ] `uv run pre-commit run --all-files`、`uv run pyright` 通过。
- [ ] `uv run scons` 和 `uv run scons pot` 成功，且生成物未被误提交。
- [ ] 未新增超过 500 KB 的大文件、二进制文件或模型文件；确有必要时先在 PR 中说明。

## 6. 社区规则与同类项目参考

### 6.1 必须遵守的社区规则

- NVDA Citizen and Contributor Code of Conduct：所有贡献者必须保持包容、尊重，保护隐私，不发布个人或敏感信息，不进行歧视、骚扰、威胁或政治/宗教布道。
- NV Access Add-on Store 提交规则：元数据必须与 manifest 一致，发布文件不可变，SHA256 用于校验，插件不得恶意或违反行为准则。
- 社区基础审查（若适用）：许可证与版权、安全性、用户体验、文档、NVDA 兼容性五类均需通过，且许可证必须与 NVDA 的 GPL 2 兼容。
- 隐私要求：GitHub 是公开论坛；提交 issue 或日志前必须仔细移除屏幕截图中的个人信息和 OCR 内容。

### 6.2 同类无障碍项目参考

以下项目可用于对齐“本地 OCR + NVDA 插件”的成熟实践，但不得直接复制其未授权代码：

- [nvdaaddons/devguide](https://github.com/nvdaaddons/devguide)：NVDA Add-on Development Guide，涵盖组件类型、命令冲突、发布和审查。
- [nvaccess/addonTemplate](https://github.com/nvaccess/addonTemplate)：本项目模板来源，用于核对构建与本地化流程。
- [nvdacn/xyOCR](https://github.com/nvdacn/xyOCR)：同样基于 PaddleOCR-json 的 NVDA 离线/在线 OCR 插件，可参考其黑屏检测、进程清理和设置组织。
- [nidza07/nao](https://github.com/nidza07/nao)：NVDA Advanced OCR，可参考识别结果窗口、取消长时间识别和安全屏幕处理。
- [davidedec/nvda-ocr](https://github.com/davidedec/nvda-ocr)：使用 Tesseract 的 NVDA OCR 插件，可参考设置集成和不可见对象处理。
- [ip3rfra/AI-content-describer](https://github.com/ip3rfra/AI-content-describer)：NVDA 图像描述插件，可参考 AI/OCR 类插件的隐私边界与用户提示。
- [Fanfulla/OCR-buddy](https://github.com/Fanfulla/OCR-buddy)：完全本地 OCR 的浏览器扩展，可作为“无服务器、不离开设备”的隐私原则参照。

## 7. Agent 操作规范

- 先读文档，再读代码；不得仅凭文件名或猜测修改。
- 新增功能或调用新的 NVDA API 前，必须先查阅当前兼容版本的官方开发者指南、源码或 API 文档，确认该 API 仍存在且参数/返回值未变，并把依据写进提交说明或 PR 描述。
- 搜索优先使用 `rg`，修改文件使用补丁工具；不得用 shell 重定向或脚本批量写入源码文件。
- 不得跨模块进行无依据的大重构；先提交最小、可验证的变更。
- 二进制文件、模型文件、DLL、第三方代码默认冻结。确需变更时，必须在 PR 中说明来源、版本、许可证和校验值。
- 不得在未完成验证的情况下声称“已完成、已通过、已修复”。必须运行对应命令并保留输出证据。
- 处理 issue 或 PR 时，先协作后冲突；不要用攻击性语言，不要泄露他人隐私。
- 若用户要求的行为与本规范、NVDA 官方规范或社区行为准则冲突，应明确指出冲突并说明风险，而不是盲从。

## 8. 参考链接

- [NVDA Code Standards](https://mintlify.wiki/nvaccess/nvda/development/code-standards)
- [NVDA Add-on Development Overview](https://mintlify.wiki/nvaccess/nvda/development/addons/overview)
- [NVDA Global Plugins](https://mintlify.wiki/nvaccess/nvda/development/addons/global-plugins)
- [NVDA Code of Conduct](https://mintlify.wiki/nvaccess/nvda/community/code-of-conduct)
- [NVDA Add-on Development Guide](https://github.com/nvdaaddons/devguide/wiki/nvda-add-on-development-guide)
- [NV Access Add-on Datastore](https://github.com/jscholes/addon-datastore)
- [NV Access addonTemplate](https://github.com/nvaccess/addonTemplate)
