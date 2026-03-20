# 使用示例

## 1. 命令行基本用法

### 处理单个MP3文件（默认输出WAV）
```bash
python vocal_remover_demucs.py my_song.mp3
```

输出位置：`output/htdemucs/my_song/no_vocals.wav`

### 直接输出MP3格式（需要ffmpeg）
```bash
python vocal_remover_demucs.py my_song.mp3 --mp3
```

输出位置：`output/我的歌曲_伴奏.mp3`

### 指定自定义输出目录
```bash
python vocal_remover_demucs.py my_song.mp3 -o ~/my_accompaniments
```

### 使用不同模型
```bash
# 使用mdx_extra模型，有时候效果更好
python vocal_remover_demucs.py my_song.mp3 --model mdx_extra
```

可用模型：
- `htdemucs` (默认) - 推荐，平衡速度和质量
- `htdemucs_ft` - 更精细，速度更慢
- `mdx_extra` - 另一个高质量模型
- `mdx_q` - 量化版，更快

## 2. Windows拖放使用

1. 将 `docs/run.bat` 复制到你方便的位置
2. 直接把MP3文件拖放到 `run.bat` 文件图标上
3. 程序会自动运行，处理完成后会提示

## 3. 编程方式使用

```python
from vocal_remover_demucs import remove_vocals

# 去除人声，获取伴奏文件路径
accompaniment_path = remove_vocals("input.mp3", output_dir="output")
print(f"伴奏已保存到: {accompaniment_path}")
```

## 4. 批量处理示例

参考 `docs/test_example.py` 中的 `test_batch_processing` 函数：

```python
import os
import subprocess
import sys

def batch_process(mp3_dir, output_dir):
    """批量处理目录中所有MP3文件"""
    for filename in os.listdir(mp3_dir):
        if filename.lower().endswith('.mp3'):
            input_path = os.path.join(mp3_dir, filename)
            cmd = [
                sys.executable,
                'vocal_remover_demucs.py',
                input_path,
                '-o', output_dir
            ]
            subprocess.run(cmd)
```

## 5. 转换输出为MP3（手动）

如果你已经有了WAV文件，可以用ffmpeg手动转换：

```bash
ffmpeg -i output/htdemucs/my_song/no_vocals.wav -codec:a libmp3lame -qscale:a 2 my_song_accompaniment.mp3
```

## 6. 完整示例流程

```bash
# 1. 进入项目目录
cd d:/code/project/learn

# 2. 安装依赖
pip install -r requirements.txt

# 3. 放入你的MP3到docs/test_input目录
# 假设文件是 example.mp3

# 4. 运行处理
python vocal_remover_demucs.py docs/test_input/example.mp3 --mp3

# 5. 查看结果
# 伴奏在 output/docs/test_input/example_伴奏.mp3
# 或者 output/htdemucs/example/no_vocals.wav
```

## 输出文件说明

处理完成后，你会得到：

| 文件 | 内容 |
|------|------|
| `no_vocals.wav` | 伴奏（人声已去除）← **这是你需要的** |
| `vocals.wav` | 提取出的人声 |

如果使用 `--mp3` 参数，还会额外得到：
- `{歌曲名}_伴奏.mp3` - MP3格式的伴奏
