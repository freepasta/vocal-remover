#!/usr/bin/env python3
"""
测试用例 - 人声去除工具演示

这个文件展示了如何以编程方式使用人声去除功能，
以及如何进行批量处理。
"""

import os
import subprocess
import sys


def test_single_file(input_file):
    """测试单个文件处理"""
    print("=" * 60)
    print("测试：单个文件人声去除")
    print(f"输入文件: {input_file}")
    print("=" * 60)

    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在: {input_file}")
        print("请将测试MP3文件放在此处，或者修改路径。")
        return False

    cmd = [
        sys.executable,
        "../vocal_remover_demucs.py",
        input_file,
        "-o", "../test_output",
    ]

    print(f"执行命令: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)
    return result.returncode == 0


def test_batch_processing(input_dir):
    """批量处理目录下所有MP3文件"""
    print("=" * 60)
    print("测试：批量处理目录下所有MP3文件")
    print(f"输入目录: {input_dir}")
    print("=" * 60)

    if not os.path.exists(input_dir):
        print(f"错误：输入目录不存在: {input_dir}")
        return False

    mp3_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.mp3')]

    if not mp3_files:
        print("目录中没有找到MP3文件")
        return False

    print(f"找到 {len(mp3_files)} 个MP3文件:")
    for f in mp3_files:
        print(f"  - {f}")
    print()

    success_count = 0
    for f in mp3_files:
        input_path = os.path.join(input_dir, f)
        print(f"正在处理: {f}")
        cmd = [
            sys.executable,
            "../vocal_remover_demucs.py",
            input_path,
            "-o", "../batch_output",
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            success_count += 1
            print(f"  ✓ 成功")
        else:
            print(f"  ✗ 失败")
        print()

    print(f"处理完成: {success_count}/{len(mp3_files)} 成功")
    return success_count == len(mp3_files)


def show_output_structure(base_dir="test_output"):
    """显示输出目录结构"""
    print("\n输出目录结构:")
    print("-" * 40)
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')


if __name__ == "__main__":
    # 示例1：处理单个文件
    # 请将你的测试MP3放在test_input目录下，或者修改这里的路径
    test_mp3 = "test_input/sample.mp3"
    test_single_file(test_mp3)

    # 示例2：批量处理（取消注释使用）
    # test_batch_processing("test_input")
