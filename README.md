# 人声去除工具 - 伴奏提取

这是一个基于Meta AI Demucs预训练模型的人声去除工具，可以从MP3歌曲中提取出伴奏。

Demucs是目前效果最好的开源音频分离模型之一，兼容最新Python版本。

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 第一次运行时会自动下载预训练模型，需要等一会儿，模型大小约300MB。

如果需要输出MP3格式，还需要安装ffmpeg:
- Windows: 下载ffmpeg并添加到PATH，或者使用 `choco install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## 使用方法

### 基本用法（输出WAV格式）

```bash
python vocal_remover_demucs.py 你的歌曲.mp3
```

伴奏会输出到 `output/htdemucs/你的歌曲/no_vocals.wav`

### 直接输出MP3格式

```bash
python vocal_remover_demucs.py 你的歌曲.mp3 --mp3
```

### 指定输出目录

```bash
python vocal_remover_demucs.py 你的歌曲.mp3 -o ./my_output
```

### 使用其他模型

Demucs提供多个模型可选：`htdemucs` (默认), `htdemucs_ft`, `mdx_extra`, `mdx_q`

```bash
python vocal_remover_demucs.py 你的歌曲.mp3 --model mdx_extra
```

## 参数说明

- `input`: 输入的MP3文件路径（必需）
- `-o, --output-dir`: 输出目录，默认为 `output`
- `--mp3`: 是否转换为MP3格式（需要ffmpeg和pydub）
- `--model`: 模型名称，默认为 `htdemucs`

## 输出文件

处理完成后会得到两个文件：
- `no_vocals.wav`: 伴奏部分（去除了人声，这就是你需要的）
- `vocals.wav`: 人声部分

## 原理

使用Meta AI开源的Demucs深度学习模型，它基于Hybrid Transformer架构，在大量音乐上预训练过，能够较好地分离人声和伴奏。

`--two-stems vocals` 模式会直接将音频分离为人声和其他（伴奏）两部分。

## 优点对比

相比Spleeter:
- Demucs分离质量更好
- 支持最新Python版本（包括3.14）
- 模型更新，效果更好

## 说明

- 分离效果取决于原音频，大部分流行歌曲效果不错
- 第一次运行需要下载模型，请耐心等待
- 处理时间取决于音频长度、电脑性能和是否使用GPU，一般一首3分钟歌曲CPU处理需要2-5分钟

## 示例

```bash
# 处理 example.mp3，输出到output目录，转换为MP3
python vocal_remover_demucs.py example.mp3 --mp3
```
