#!/usr/bin/env python3
"""
人声去除工具 - 从MP3文件中分离出伴奏
使用Meta AI的Demucs预训练模型进行音频分离
支持Python 3.8+，包括Python 3.14
"""

import argparse
import os
import sys
import subprocess


def remove_vocals(input_file, output_dir="output", model="htdemucs"):
    """
    从输入音频文件中去除人声，保留伴奏

    Args:
        input_file (str): 输入MP3文件路径
        output_dir (str): 输出目录
        model (str): 模型名称

    Returns:
        str: 伴奏文件的输出路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    input_abs = os.path.abspath(input_file)
    output_abs = os.path.abspath(output_dir)

    print(f"正在处理: {input_file}")
    print(f"使用模型: {model}")
    print("这可能需要几分钟时间，请耐心等待...")

    # 如果输入是MP3，先转换为WAV绕过torchcodec问题
    ext = os.path.splitext(input_file)[1].lower()
    if ext == '.mp3':
        print("检测到MP3格式，先转换为WAV...")
        temp_wav = os.path.join(output_dir, "temp_input.wav")
        # 使用ffmpeg转换，增加探测参数解决VBR MP3问题
        convert_cmd = ["ffmpeg", "-y", "-analyzeduration", "100M", "-probesize", "100M", "-i", input_abs, temp_wav]
        result = subprocess.run(convert_cmd)
        if result.returncode != 0:
            print(f"错误: MP3转WAV失败，请检查ffmpeg是否正确安装", file=sys.stderr)
            sys.exit(1)
        input_abs = temp_wav

    # 使用demucs命令行工具进行分离
    cmd = [
        sys.executable, "-m", "demucs",
    ]
    # 指定模型
    if model:
        cmd.extend(["--name", model])
    # 添加分离参数
    cmd.extend([
        "--two-stems", "vocals",  # 只分离人声和其他(伴奏)
        "-o", output_abs,
        input_abs
    ])

    print(f"执行命令: {' '.join(cmd)}")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"错误: 处理失败", file=sys.stderr)
        sys.exit(1)

    # 获取输出路径
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    # demucs 输出结构: output/model_name/file_name/no_vocals.wav
    accompaniment_path = os.path.join(output_abs, model, base_name, "no_vocals.wav")

    if not os.path.exists(accompaniment_path):
        # 尝试其他可能的输出路径
        alternative_path = os.path.join(output_abs, base_name, "no_vocals.wav")
        if os.path.exists(alternative_path):
            accompaniment_path = alternative_path
        else:
            print(f"警告: 找不到输出文件，请检查输出目录: {output_abs}", file=sys.stderr)

    print(f"\n处理完成！")
    print(f"伴奏文件已保存到: {accompaniment_path}")

    return accompaniment_path


def convert_to_mp3(wav_file, mp3_file):
    """
    将WAV文件转换为MP3格式，需要ffmpeg
    """
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format="mp3", bitrate="320k")
        print(f"已转换为MP3: {mp3_file}")
        return mp3_file
    except ImportError:
        print("提示: 需要安装pydub才能转换为MP3", file=sys.stderr)
        print("可以手动使用ffmpeg转换: ffmpeg -i {} -codec:a libmp3lame -qscale:a 2 {}".format(wav_file, mp3_file))
        return None
    except Exception as e:
        print(f"转换失败: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='去除音频中的人声，提取伴奏')
    parser.add_argument('input', help='输入MP3文件路径')
    parser.add_argument('-o', '--output-dir', default='output', help='输出目录 (默认: output)')
    parser.add_argument('--mp3', action='store_true', help='是否输出为MP3格式 (需要ffmpeg)')
    parser.add_argument('--model', default='htdemucs', help='模型名称 (默认: htdemucs)')

    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件 {args.input} 不存在", file=sys.stderr)
        sys.exit(1)

    # 检查文件扩展名
    ext = os.path.splitext(args.input)[1].lower()
    if ext != '.mp3':
        print(f"警告: 输入文件不是MP3格式，但仍会尝试处理", file=sys.stderr)

    try:
        import demucs
    except ImportError:
        print("错误: demucs未安装，请先安装: pip install demucs", file=sys.stderr)
        sys.exit(1)

    # 执行人声去除
    accompaniment_path = remove_vocals(args.input, args.output_dir, args.model)

    # 如果需要转换为MP3
    if args.mp3 and os.path.exists(accompaniment_path):
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        mp3_path = os.path.join(args.output_dir, f"{base_name}_伴奏.mp3")
        convert_to_mp3(accompaniment_path, mp3_path)

    print("\n使用说明:")
    print("- 分离后得到的 no_vocals.wav 就是伴奏文件 (去除了人声)")
    print("- vocals.wav 是提取出的人声")
    print("- 如果需要MP3格式，请使用 --mp3 参数，或者手动用ffmpeg转换")


if __name__ == "__main__":
    main()
