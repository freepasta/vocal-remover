#!/usr/bin/env python3
"""
人声去除工具 - 从MP3文件中分离出伴奏
使用Meta AI的Demucs预训练模型进行音频分离
使用Python API，绕过torchcodec加载问题
"""

import argparse
import os
import sys
import subprocess
import torch
import soundfile as sf
from demucs.pretrained import get_model
from demucs.audio import convert_audio
from demucs.apply import apply_model


def safe_print(message, file=sys.stdout):
    """安全打印，处理Windows编码问题"""
    try:
        print(message, file=file)
    except UnicodeEncodeError:
        # 如果编码失败，替换不可编码字符再打印
        encoding = getattr(file, 'encoding', 'utf-8')
        cleaned = message.encode(encoding, errors='replace').decode(encoding)
        print(cleaned, file=file)


def remove_vocals(input_file, output_dir="output", model_name="htdemucs"):
    """
    从输入音频文件中去除人声，保留伴奏
    使用Demucs Python API，自己处理加载绕过torchcodec问题

    Args:
        input_file (str): 输入MP3文件路径
        output_dir (str): 输出目录
        model_name (str): 模型名称

    Returns:
        str: 伴奏文件的输出路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    safe_print(f"正在处理: {input_file}")
    safe_print(f"使用模型: {model_name}")
    safe_print("这可能需要几分钟时间，请耐心等待...")

    # 如果输入是MP3，先用ffmpeg转换为WAV，我们再用soundfile读取
    ext = os.path.splitext(input_file)[1].lower()
    if ext == '.mp3':
        safe_print("检测到MP3格式，使用ffmpeg转换为WAV...")
        temp_wav = os.path.join(output_dir, f"temp_input_{os.path.splitext(os.path.basename(input_file))[0]}.wav")
        convert_cmd = ["ffmpeg", "-y", "-analyzeduration", "100M", "-probesize", "100M", "-i", input_file, temp_wav]
        result = subprocess.run(convert_cmd)
        if result.returncode != 0:
            safe_print(f"错误: MP3转WAV失败，请检查ffmpeg是否正确安装", file=sys.stderr)
            sys.exit(1)
        input_file = temp_wav

    # 使用soundfile读取音频（绕过torchaudio/torchcodec问题）
    safe_print(f"读取音频文件: {input_file}")
    wav, sr = sf.read(input_file)
    # 转换为 (channels, samples) 格式
    if len(wav.shape) == 2:
        wav = wav.T
    else:
        wav = wav[None, :]
    wav = torch.from_numpy(wav).float()

    # 获取模型
    safe_print(f"加载模型 {model_name}...")
    model = get_model(model_name)
    model.eval()

    # 转换音频到模型要求的采样率和声道
    wav = convert_audio(wav, sr, model.samplerate, model.audio_channels)
    wav = wav[None, :, :]  # 添加batch维度

    # 分离
    safe_print("正在分离人声和伴奏...")
    with torch.no_grad():
        estimates = apply_model(model, wav, device='cpu')
    estimates = estimates[0]  # 移除batch维度

    # 获取结果
    # 我们需要把除了vocals之外的所有源加起来作为伴奏
    if 'vocals' in model.sources:
        vocals = estimates[model.sources.index('vocals')]
        # 伴奏是其他所有源的和
        accompaniment = torch.zeros_like(vocals)
        for i, source in enumerate(model.sources):
            if source != 'vocals':
                accompaniment += estimates[i]
    else:
        # 已经是two stems，假设第一个是vocals
        vocals = estimates[0]
        accompaniment = estimates[1]

    # 获取输出文件名
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    if base_name.startswith('temp_input_'):
        base_name = base_name[len('temp_input_'):]

    output_model_dir = os.path.join(output_dir, model_name)
    os.makedirs(output_model_dir, exist_ok=True)
    output_file_dir = os.path.join(output_model_dir, base_name)
    os.makedirs(output_file_dir, exist_ok=True)

    # 保存结果
    accompaniment_path = os.path.join(output_file_dir, "no_vocals.wav")
    vocals_path = os.path.join(output_file_dir, "vocals.wav")
    accompaniment_mp3_path = os.path.join(output_file_dir, "no_vocals.mp3")
    vocals_mp3_path = os.path.join(output_file_dir, "vocals.mp3")

    safe_print(f"保存WAV结果...")
    # 转换回numpy保存
    sf.write(accompaniment_path, accompaniment.cpu().numpy().T, model.samplerate)
    sf.write(vocals_path, vocals.cpu().numpy().T, model.samplerate)

    # 同时输出MP3格式，320kbps高质量
    safe_print(f"转换输出MP3...")
    convert_to_mp3(accompaniment_path, accompaniment_mp3_path, bitrate='320k')
    convert_to_mp3(vocals_path, vocals_mp3_path, bitrate='320k')

    # 删除临时文件
    if ext == '.mp3' and os.path.exists(input_file):
        os.unlink(input_file)

    safe_print(f"\n处理完成！")
    safe_print(f"WAV伴奏: {accompaniment_path}")
    safe_print(f"MP3伴奏: {accompaniment_mp3_path}")
    safe_print(f"WAV人声: {vocals_path}")
    safe_print(f"MP3人声: {vocals_mp3_path}")

    return accompaniment_path


def convert_to_mp3(wav_file, mp3_file, bitrate='320k'):
    """
    将WAV文件转换为MP3格式，需要ffmpeg
    """
    try:
        cmd = ["ffmpeg", "-y", "-i", wav_file, "-b:a", bitrate, mp3_file]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            safe_print(f"  ✓ {mp3_file}")
            return mp3_file
        else:
            safe_print(f"  ✗ 转换失败 {wav_file}", file=sys.stderr)
            return None
    except Exception as e:
        safe_print(f"  ✗ 转换失败 {wav_file}: {e}", file=sys.stderr)
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
        safe_print(f"错误: 输入文件 {args.input} 不存在", file=sys.stderr)
        sys.exit(1)

    # 检查ffmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if result.returncode != 0:
            safe_print("错误: ffmpeg未找到，请确保ffmpeg在PATH中", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        safe_print("错误: ffmpeg未找到，请确保ffmpeg在PATH中", file=sys.stderr)
        sys.exit(1)

    # 执行人声去除
    accompaniment_path = remove_vocals(args.input, args.output_dir, args.model)

    # 如果需要转换为MP3
    if args.mp3 and os.path.exists(accompaniment_path):
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        mp3_path = os.path.join(args.output_dir, f"{base_name}_伴奏.mp3")
        convert_to_mp3(accompaniment_path, mp3_path)

    safe_print("\n使用说明:")
    safe_print("- no_vocals.wav 就是伴奏文件 (去除了人声) ← 这是你需要的")
    safe_print("- vocals.wav 是提取出的人声")


if __name__ == "__main__":
    main()
