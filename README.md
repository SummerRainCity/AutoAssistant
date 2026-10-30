# AutoAssistant 开源说明

## 一、项目简介

**AutoAssistant** 是一个模块化的自动化助手项目。它通过识别屏幕信息，将截图中的文字内容交给 OCR 或 AI 进行二次处理，再根据业务规则执行鼠标、键盘等自动化操作。

你可以用它实现一些流程化的自动化操作，例如：

- 按流程操作浏览器，完成视频播放等操作；
- 按指定步骤打开软件并执行操作；
- 截图后识别文字，根据文字内容决定下一步动作；
- 将 OCR 结果传入 AI，由 AI 辅助判断或生成下一步业务逻辑。

项目本身只提供基础能力模块，**每个人的需求不同，具体业务代码需要由你自己实现**。

> 注意：本项目对“功能图标”类界面的识别不是很友好。被操作的组件最好由**英文或汉字文字**显示，这样 OCR 识别和流程判断会更稳定。

---

## 二、工作原理

AutoAssistant 的核心流程是一个循环：

```text
截图
  ↓
OCR 分析 / 信息捕获
  ↓
按照业务逻辑判断
  ↓
执行鼠标 / 键盘事件
  ↓
再次截图
  ↓
再次 OCR 分析
  ↓
继续执行下一步……
```

也就是：

```text
截图 → OCR分析 → 业务动作 → 截图 → OCR分析 → 业务动作 → 循环
```

你可以把 OCR 识别结果直接用于业务判断，也可以传入 AI 进行二次处理，例如让 AI 判断当前界面状态、提取关键信息或辅助生成操作决策。

---

## 三、项目目录结构

```text
├── LibModules/
│   ├── demo.py                  // 延时代码
│   ├── KeyBoardEvent.py         // 键盘事件
│   ├── OCRViewModule.py         // OCR 文字识别
│   ├── OpenAITool.py            // AI 接入
│   └── UtilityModuleClass.py    // 鼠标事件 + 信息捕获
├── PaddleOCR/                   // OCR 程序模块
├── WorkFile/                    // 资源文件，用于图像对比等
└── main.py                      // 业务代码入口
```

### 各目录说明

#### `LibModules/`

基础能力模块目录，提供自动化流程所需的通用能力。

- `demo.py`：延时代码，可用于控制流程节奏；
- `KeyBoardEvent.py`：键盘事件相关能力；
- `OCRViewModule.py`：OCR 文字识别模块；
- `OpenAITool.py`：AI 接入模块，可用于将 OCR 结果交给 AI 二次处理；
- `UtilityModuleClass.py`：鼠标事件与信息捕获相关能力。

#### `PaddleOCR/`

OCR 程序模块目录。

本项目使用 PaddleOCR-json 作为 OCR 能力来源，参考原作者项目：

```text
https://github.com/hiroi-sora/PaddleOCR-json
```

使用前请先下载 PaddleOCR-json，并将其放入当前项目的 `PaddleOCR/` 目录中，然后通过命令行方式调用即可。

#### `WorkFile/`

资源文件目录，用于存放图像对比所需的图片等资源。

例如，业务中需要点击某个固定图片区域时，可以将目标图片放在：

```text
WorkFile/xxxx.png
```

然后在业务代码中读取该图片并进行对比或定位。

#### `main.py`

业务代码入口。

为避免一些不必要的麻烦，项目中已删除部分业务代码，仅保留部分代码供参考。你应当根据自己的实际需求，在 `main.py` 中编写自己的自动化业务流程。

---

## 四、环境准备

### 1. 准备 Python 环境

建议使用 Python 3.10.11 环境运行项目。具体依赖请根据 `LibModules/` 中各模块的 `import` 内容安装。

### 2. 下载并配置 PaddleOCR-json

1. 访问 PaddleOCR-json 原项目：

   ```text
   https://github.com/hiroi-sora/PaddleOCR-json
   ```

2. 下载对应平台的 PaddleOCR-json 程序；
3. 将其放入本项目的 `PaddleOCR/` 目录；
4. 确认可以通过命令行调用 OCR 程序；
5. 根据你的实际路径，在 `OCRViewModule.py` 或业务代码中配置 OCR 调用命令。

### 3. 准备资源文件

如果需要使用图像对比、图标定位等功能，请将相关图片放入 `WorkFile/` 目录。

例如：

```text
WorkFile/button.png
WorkFile/logo.png
```

业务代码中可通过这些图片进行匹配或辅助定位。

### 4. 配置 AI 接入

如果需要使用 AI 二次处理能力，请在 `OpenAITool.py` 中配置对应的 API Key、接口地址和模型信息。

请不要将真实 API Key 直接提交到公开仓库中，建议使用环境变量或本地配置文件管理密钥。

---

## 五、模块说明

### 1. `demo.py` —— 演示代码

用于控制自动化流程中的等待时间。

自动化操作中，界面加载、页面跳转、OCR 识别都需要时间，合理使用延时可以提高流程稳定性。

### 2. `KeyBoardEvent.py` —— 键盘事件

提供键盘输入、按键触发等能力，可用于：

- 输入文字；
- 按下快捷键；
- 回车确认；
- 组合键操作等。

### 3. `OCRViewModule.py` —— 文字识别

负责调用 PaddleOCR-json 对截图进行文字识别。

典型用途：

- 识别当前界面文字；
- 判断按钮或菜单是否存在；
- 提取页面中的关键信息；
- 将识别结果交给业务逻辑或 AI 处理。

### 4. `OpenAITool.py` —— AI 接入

用于接入 OpenAI 或兼容接口的 AI 服务。

你可以将 OCR 识别出的文字、当前界面信息、业务上下文传入 AI，让 AI 进行二次处理，例如：

- 判断当前页面处于哪个步骤；
- 从 OCR 文本中提取关键信息；
- 根据规则生成下一步操作建议；
- 辅助处理非固定格式的文本内容。

### 5. `UtilityModuleClass.py` —— 鼠标事件与信息捕获

提供鼠标操作和屏幕信息捕获能力，可用于：

- 鼠标移动、点击；
- 截取屏幕区域；
- 获取界面信息；
- 配合 OCR 或图像对比完成自动化操作。

---

## 六、快速开始

### 第一步：克隆项目

```bash
git clone <你的项目仓库地址>
cd AutoAssistant
```

### 第二步：下载 PaddleOCR-json

前往：

```text
https://github.com/hiroi-sora/PaddleOCR-json
```

下载后放入：

```text
AutoAssistant/PaddleOCR/
```

并确认命令行调用正常。

### 第三步：安装依赖

根据 `LibModules/` 中各模块的导入情况安装依赖。建议先运行：

```bash
python main.py
```

根据报错信息安装缺失的 Python 包。

### 第四步：准备业务资源

将需要对比或定位的图片放入：

```text
WorkFile/
```

例如：

```text
WorkFile/start_button.png
```

### 第五步：编写业务代码

在 `main.py` 中实现你的业务流程。

下面是一个伪代码示例，仅用于说明整体思路，具体函数名请以项目实际模块为准：

```python
from LibModules.OCRViewModule import OCRViewModule
from LibModules.UtilityModuleClass import UtilityModuleClass
from LibModules.KeyBoardEvent import KeyBoardEvent
from LibModules.demo import sleep_time

ocr = OCRViewModule()
utility = UtilityModuleClass()
keyboard = KeyBoardEvent()

while True:
    # 1. 截图
    image = utility.capture_screen()

    # 2. OCR 识别
    text = ocr.recognize(image)

    # 3. 根据业务逻辑判断
    if "登录" in text:
        utility.click(x=100, y=200)
        sleep_time(1)
    elif "搜索" in text:
        keyboard.input_text("AutoAssistant")
        keyboard.press_enter()
        sleep_time(2)
    else:
        sleep_time(1)
```

实际业务中，你可以将 OCR 结果继续传入 `OpenAITool.py` 进行二次处理，再决定下一步动作。

## 七、适用场景

AutoAssistant 适合用于一些相对固定、流程化的自动化操作，例如：

- 浏览器流程化操作；
- 打开指定软件并执行固定步骤；
- 根据屏幕文字判断当前状态；
- 截图后 OCR 识别并自动点击；
- OCR 结果交由 AI 分析后执行下一步；
- 结合 `WorkFile/` 中的图片做简单图像对比。

---

## 八、使用注意事项

1. **业务代码需要自己实现**  
   本项目是模块化基础能力集合，不提供完整业务成品。不同人的需求不同，请根据实际场景编写业务逻辑。

2. **对图标类界面不友好**  
   本项目更适合识别由英文或汉字显示的组件。纯图标、复杂图形按钮的识别稳定性有限，建议优先使用文字作为判断依据。

3. **保持界面环境稳定**  
   建议固定窗口大小、窗口位置和屏幕分辨率，避免截图区域变化导致 OCR 或图像对比失败。

4. **合理设置延时**  
   页面加载、软件响应和 OCR 识别都需要时间，必要时使用 `demo.py` 中的延时能力或自行增加等待逻辑。

5. **OCR 调用路径要正确**  
   请确认 `PaddleOCR/` 目录中的程序可以正常通过命令行调用，否则 OCR 模块无法工作。

6. **保护 API Key**  
   使用 `OpenAITool.py` 接入 AI 时，不要将真实密钥提交到公开仓库。

7. **遵守软件使用条款**  
   请勿将本项目用于违反法律法规、软件服务条款或侵犯他人权益的自动化操作。


## 九、参考与致谢

OCR 能力参考 PaddleOCR-json 项目：

```text
https://github.com/hiroi-sora/PaddleOCR-json
```

感谢原作者提供 OCR 程序模块。使用前请先下载并按照其说明完成配置，然后在 AutoAssistant 中通过命令行方式调用。

---

## 十、注明

AutoAssistant 是一个通过“截图 → OCR 分析 → 业务动作 → 循环”实现流程自动化的模块化助手。

它适合做流程化浏览器操作、软件操作、文字识别判断和 AI 辅助决策等场景。项目保留了基础模块和参考业务代码，删除了部分业务实现，目的是让你根据自己的需求自由扩展。

如果你希望自动化流程更稳定，建议优先操作带有英文或汉字文字的组件，并保持界面、分辨率和操作流程相对固定。

它已在一些生产中稳定运行，此次上传作为备份，如果您觉得他有用可以点个⭐。
