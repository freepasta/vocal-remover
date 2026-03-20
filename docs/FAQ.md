# 常见问题 FAQ

## Q: 第一次运行提示下载模型，需要等多久？
A: 模型大小约300MB，根据网络速度，一般需要几分钟。模型只会下载一次，后续运行不需要再下载。

## Q: 处理速度很慢正常吗？
A: 正常。Demucs是深度学习模型，CPU处理一首3分钟歌曲通常需要2-5分钟。如果有NVIDIA GPU，PyTorch会自动使用CUDA加速，速度会快很多。

## Q: 分离效果不好怎么办？
A:
1. 尝试不同模型：`--model mdx_extra` 或 `--model htdemucs_ft`，不同模型对不同类型音乐效果不同
2. 原音频质量差、人声和伴奏混音太深会影响效果，这是正常的
3. 可以试试在参数中加入 `--two-stems` 已经默认分离人声和伴奏，不需要修改

## Q: 可以直接输出MP3吗？
A: 可以。加上 `--mp3` 参数即可，但需要先安装ffmpeg。
```bash
python vocal_remover_demucs.py input.mp3 --mp3
```

## Q: 输出文件在哪里？
A: 默认输出结构：
```
output/
  htdemucs/
    歌曲名/
      no_vocals.wav  ← 这是伴奏（去除人声）
      vocals.wav     ← 这是人声
```

如果指定了自定义输出目录：
```
your_output_dir/
  htdemucs/
    歌曲名/
      no_vocals.wav
      vocals.wav
```

## Q: ModuleNotFoundError: No module named 'demucs'
A: 需要先安装依赖：
```bash
pip install -r requirements.txt
```

## Q: 报错缺少ffmpeg？
A:
- Windows: 下载ffmpeg.exe，放到PATH，或者使用 `choco install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

如果你不需要输出MP3，不加 `--mp3` 参数也可以使用，输出是WAV格式。

## Q: 支持哪些输入格式？
A: Demucs支持大多数音频格式，包括：MP3, WAV, FLAC, M4A, AAC等。本工具专门针对MP3做了适配。

## Q: 可以批量处理吗？
A: 可以。参考 `docs/test_example.py` 中的 `test_batch_processing` 示例。

## Q: 和Spleeter比哪个好？
A:
- Demucs（本工具使用）：更新更好的模型，分离质量更高，支持最新Python，本项目使用它
- Spleeter：较老的模型，对新版本Python兼容性不好，依赖旧版本numpy

## Q: GPU加速需要做什么？
A: 如果你的Python安装了CUDA版本的PyTorch，Demucs会自动使用GPU，不需要额外配置。速度会比CPU快5-10倍。

## Q: 占用很多内存正常吗？
A: 正常，深度学习模型需要一定内存。处理长音频可能占用1-2GB内存，这是正常的。
