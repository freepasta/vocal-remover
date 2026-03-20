# 人声去除工具 - 伴奏提取

[English README](README.md)

这是一个基于Meta AI Demucs预训练模型的人声去除工具，可以从MP3歌曲中提取出伴奏。

Demucs是目前效果最好的开源音频分离模型之一，兼容最新Python版本。

## 特性

- 🎵 从任意MP3歌曲中去除人声，只保留伴奏
- ✅ 支持MP3输入格式
- 📦 默认同时输出 **WAV无损** 和 **MP3 320kbps** 两种格式
- 🏆 使用 Demucs (htdemucs 模型) - 业界领先的开源分离效果
- 🐍 兼容 Python 3.8+ 包括 Python 3.14
- 🔧 绕过了 torchcodec/ffmpeg 版本兼容问题
- 🖥️ **图形界面** - 不需要命令行知识，点点鼠标就能用！

## 安装

```bash
git clone https://github.com/freepasta/vocal-remover.git
cd vocal-remover
pip install -r requirements.txt
```

**注意**: 第一次运行会自动下载预训练模型 (~300MB)。

你需要安装 **ffmpeg** 来解码/编码MP3:
- Windows: 下载ffmpeg解压到 `bin/` 目录，或者添加到PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## 使用方法

### 图形界面 (推荐)

直接运行:
```bash
python gui.py
```

打开GUI窗口后，只需要三步:
1. 点击 **[📁 选择文件]** 选择你的MP3
2. 输出目录会**自动设置**好，默认就是 `输入文件所在目录/output/`
3. 点击 **[🚀 开始处理]** 等待完成
4. 处理完会自动打开输出文件夹，可以直接拿到伴奏

### 命令行用法

```bash
# 添加ffmpeg到 PATH
export PATH="$PWD/bin/ffmpeg-master-latest-win64-gpl/bin:$PATH"

python vocal_remover_api.py 你的歌曲.mp3
```

输出:
```
output/htdemucs/你的歌曲/
├── no_vocals.wav    # 无损伴奏
├── no_vocals.mp3    # 320kbps MP3伴奏 ← 直接就能用
├── vocals.wav       # 提取出的人声
└── vocals.mp3       # 提取出的人声 (MP3)
```

### 指定输出目录

```bash
python vocal_remover_api.py 你的歌曲.mp3 -o ./my_output
```

### 更换模型

```bash
python vocal_remover_api.py 你的歌曲.mp3 --model mdx_extra
```

可用模型: `htdemucs` (默认), `htdemucs_ft`, `mdx_extra`, `mdx_q`

## Windows 拖放运行

复制 `docs/run.bat` 到桌面，直接把MP3文件拖放到 `run.bat` 图标上就会自动开始处理。

## 输出说明

处理完成后，默认同时输出两种格式:
- `no_vocals.wav` - 无损音质WAV伴奏
- `no_vocals.mp3` - 320kbps高质量MP3伴奏 ← 直接就能播放使用

## 技术原理

Demucs 是基于 Hybrid Transformer 架构的深度学习模型，在数千首歌曲上训练完成。它能把混合音频分离成不同音轨:
- `vocals` - 人声演唱
- `drums` - 鼓点
- `bass` - 贝斯
- `other` - 其他乐器 (吉他、钢琴、键盘等等)

本工具把除了人声之外的所有音轨加起来，得到完整的伴奏。

## 示例结果

对于一首3分钟的MP3歌曲 (~5MB):
- 输出: ~36MB WAV + ~5MB MP3
- CPU处理时间: 2-5分钟 (GPU更快)

## 感谢

- [Demucs](https://github.com/facebookresearch/demucs) - Meta AI 出品的顶尖音乐分离模型
- 所有预训练权重来自 Facebook Research

## 许可证

MIT License
