# 开发回顾总结 - Vocal Remover 人声分离伴奏提取工具

这个文档记录了整个项目的开发过程，包括遇到的问题和解决方案，方便后人参考。

---

## 项目目标

创建一个**简单易用**的人声分离工具，要求：

- ✅ 输入支持 MP3 格式
- ✅ 输出伴奏（去除人声），同时输出 WAV 无损和 MP3 320kbps 两种格式
- ✅ 提供**图形用户界面**，不需要命令行知识就能用
- ✅ 代码整理干净，推送到 GitHub 开源
- ✅ 解决依赖兼容性问题

---

## 技术选型

| 组件 | 选择 | 原因 |
|------|------|------|
| **分离模型** | Meta AI Demucs (htdemucs) | 当前开源最好的音乐分离模型之一，效果出色 |
| **GUI 框架** | Python tkinter | Python 内置，不需要额外安装依赖，跨平台 |
| **MP3 处理** | ffmpeg + soundfile | 绕过 torchcodec 兼容性问题 |
| **输出格式** | 同时输出 WAV + MP3 | WAV 供进一步编辑，MP3 直接可用 |

---

## 开发过程 & 踩坑记录

### 问题 1: torchcodec / ffmpeg 兼容性

**问题**: 最新版 torchaudio 依赖 torchcodec，而 torchcodec 对新版 ffmpeg (v8.x) 没有预编译包，直接运行会报错。

**解决方法**:
> 先用 ffmpeg 将 MP3 转换为临时 WAV 文件，然后用 soundfile 读取 WAV。完全绕过 torchaudio / torchcodec 的加载过程。

```python
# 核心思路
if ext == '.mp3':
    temp_wav = ...
    subprocess.run(["ffmpeg", "-y", "-i", input_file, temp_wav])
    input_file = temp_wav
# 然后 sf.read(input_file) 读取
```

---

### 问题 2: GUI 布局 - 开始按钮看不见

**问题**: 最初设计是：标题 → 输入 → 输出 → 日志区域 → 按钮。日志占用了所有剩余空间，按钮被挤到窗口外面了。用户必须最大化才能看到按钮。

**用户反馈**:
> "还是不行，我必须把窗口最大化才显示的出来。这样吧，你把开始处理的按钮调整到日志上面吧"

**解决方法**:
> 重新排列布局顺序，把**按钮放在日志区域上方**。无论窗口大小，按钮一定可见。

```
正确顺序:
标题
  ↓
输入文件选择
  ↓
输出目录选择
  ↓
模型选择
  ↓
选项 (自动打开文件夹)
  ↓
[开始处理] 按钮  ← 这里！放在日志上方
  ↓
运行日志区域 (占用剩余空间)
```

---

### 问题 3: Windows 中文编码崩溃

**问题**: 当文件名包含中文，输出包含 emoji (✓ ✓) 时，Windows CMD 默认 GBK 编码会抛出 `UnicodeEncodeError`。

**错误信息**:
```
'gbk' codec can't encode character '\u2713' in position 2: illegal multibyte sequence
```

**解决方法**:
> 添加 `safe_print` 包装函数，捕获编码错误，自动替换不可编码字符。

```python
def safe_print(message, file=sys.stdout):
    """安全打印，处理Windows编码问题"""
    try:
        print(message, file=file)
    except UnicodeEncodeError:
        encoding = getattr(file, 'encoding', 'utf-8')
        cleaned = message.encode(encoding, errors='replace').decode(encoding)
        print(cleaned, file=file)
```

这样即使显示乱码，程序也不会崩溃，文件都能正常生成。

---

### 问题 4: 默认输出目录

**需求**: 用户只选择输入文件，不指定输出目录时，应该自动设置一个合理的默认输出位置。

**解决方法**:
> 默认输出到 `输入文件所在目录/output/`，用户不用自己选。

```python
if not output_dir:
    input_dir = os.path.dirname(input_file)
    output_dir = os.path.join(input_dir, "output")
```

---

### 问题 5: 中英文 README 同步

**问题**: 中英文内容结构不一致，英文 README 图片路径不对。

**解决方法**:
- 保持中英文 README 结构完全一致
- 截图放在 `docs/gui-screenshot.png`，英文 README 中引用路径正确
- 两边都包含 GUI 使用说明

---

## 最终功能清单

- [x] **MP3 输入** - 支持任意 MP3 文件
- [x] **双格式输出** - 默认同时输出 `no_vocals.wav` (无损) 和 `no_vocals.mp3` (320kbps)
- [x] **图形界面** - 不需要命令行，点点鼠标就能用
- [x] **自动默认输出** - 不指定目录时自动输出到 `输入目录/output/`
- [x] **多模型支持** - 可选 `htdemucs` / `htdemucs_ft` / `mdx_extra` / `mdx_q`
- [x] **处理完成自动打开输出文件夹**
- [x] **兼容最新 Python** - 支持 Python 3.8 ~ 3.14
- [x] **Windows 拖放运行** - 把 MP3 拖到 `run.bat` 上自动处理

---

## 项目结构

```
vocal-remover/
├── gui.py                    # 图形界面入口
├── vocal_remover_api.py      # 命令行API (主处理程序)
├── requirements.txt          # Python依赖
├── README.md                 # 英文说明
├── README.zh-CN.md          # 中文说明
├── .gitignore
└── docs/
    ├── development_summary.md # 这份开发总结
    ├── gui-screenshot.png     # GUI截图
    ├── usage_examples.md      # 使用示例
    ├── run.bat                # Windows拖放运行脚本
    └── test_input/            # 测试文件目录
```

---

## 使用方式

### 图形界面 (推荐)

```bash
python gui.py
```

三步操作：
1. 点击「选择文件」选MP3
2. 输出目录自动设置好
3. 点击「开始处理」等待完成 → 自动打开输出文件夹

### 命令行

```bash
python vocal_remover_api.py 你的歌曲.mp3
```

输出位置：
```
output/htdemucs/你的歌曲/
├── no_vocals.wav    # 无损伴奏
├── no_vocals.mp3    # 320kbps MP3伴奏 (直接用)
├── vocals.wav       # 提取出的人声
└── vocals.mp3       # 提取出的人声 (MP3)
```

---

## 效果测试

使用 `司南 - 苏州人家_502611916.mp3` 测试:

| 指标 | 结果 |
|------|------|
| 输入 | 8.4MB MP3 (3分30秒) |
| 处理时间 (CPU) | ~2分钟 |
| 输出 no_vocals.wav | 36MB 无损 |
| 输出 no_vocals.mp3 | 8.1MB 320kbps |
| 人声去除效果 | 良好，伴奏干净 |

---

## 经验总结

1. **GUI布局**: 重要的操作按钮（如"开始处理"）一定要放在靠前位置，保证任何窗口大小都能看见
2. **Windows兼容性**: 中文文件名 + emoji输出容易触发编码问题，一定要提前处理
3. **依赖性问题**: 当库有兼容性问题时，"绕"过去有时候比修复更简单。本案中用ffmpeg预转WAV绕过torchcodec问题，省时省力
4. **默认值设计**: 尽量帮用户填好默认值，用户能少填一步就少填一步。本项目自动设置输出目录体验好很多
5. **双格式输出**: 同时输出无损WAV和高质量MP3，满足不同需求，用户体验更好

---

## GitHub 仓库

https://github.com/freepasta/vocal-remover

---

*更新于: 2026-03-20*
