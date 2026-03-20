#!/usr/bin/env python3
"""
Vocal Remover - Graphical User Interface
去除人声提取伴奏 - 图形界面版本
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess


class VocalRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Vocal Remover - 人声去除伴奏提取")
        self.root.geometry("650x800")
        self.root.minsize(550, 700)

        # 处理状态
        self.is_processing = False
        self.process_thread = None

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="🎵 Vocal Remover", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 输入文件 Frame
        input_frame = tk.LabelFrame(self.root, text="输入 MP3 文件", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        self.input_path_var = tk.StringVar()
        input_entry = tk.Entry(input_frame, textvariable=self.input_path_var, width=50)
        input_entry.grid(row=0, column=0, padx=5, sticky="ew")

        input_btn = tk.Button(input_frame, text="📁 选择文件", command=self.select_input_file)
        input_btn.grid(row=0, column=1, padx=5)

        input_frame.grid_columnconfigure(0, weight=1)

        # 默认提示
        hint_label = tk.Label(input_frame, text="提示: 默认输出 → 输入文件所在目录/output/", fg="gray")
        hint_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # 输出目录 Frame
        output_frame = tk.LabelFrame(self.root, text="输出目录 (留空使用默认)", padx=10, pady=10)
        output_frame.pack(fill="x", padx=10, pady=5)

        self.output_path_var = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        output_entry.grid(row=0, column=0, padx=5, sticky="ew")

        output_btn = tk.Button(output_frame, text="📁 选择目录", command=self.select_output_dir)
        output_btn.grid(row=0, column=1, padx=5)

        output_frame.grid_columnconfigure(0, weight=1)

        # 模型选择 Frame
        model_frame = tk.LabelFrame(self.root, text="选择模型", padx=10, pady=10)
        model_frame.pack(fill="x", padx=10, pady=5)

        self.model_var = tk.StringVar(value="htdemucs")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, state="readonly")
        model_combo['values'] = ("htdemucs", "htdemucs_ft", "mdx_extra", "mdx_q")
        model_combo.pack(fill="x")

        model_hint = tk.Label(model_frame, text="htdemucs: 推荐，平衡速度和质量", fg="gray")
        model_hint.pack(anchor="w")

        # 选项 Frame
        options_frame = tk.Frame(self.root, padx=10, pady=5)
        options_frame.pack(fill="x", padx=10)

        self.auto_open_var = tk.BooleanVar(value=True)
        auto_open_check = tk.Checkbutton(options_frame, text="处理完成后自动打开输出文件夹", variable=self.auto_open_var)
        auto_open_check.pack(anchor="w")

        # 日志 Frame - 使用固定高度，不抢占按钮空间
        log_frame = tk.LabelFrame(self.root, text="运行日志", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 日志文本框 - 深色背景
        self.log_text = tk.Text(log_frame, bg="#1e1e1e", fg="#d4d4d4", state="disabled")
        self.log_text.pack(fill="both", expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

        # 底部按钮
        btn_frame = tk.Frame(self.root, padx=10, pady=10)
        btn_frame.pack(fill="x")

        self.start_btn = tk.Button(btn_frame, text="🚀 开始处理", command=self.start_processing, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.start_btn.pack(expand=True)

    def select_input_file(self):
        file_path = filedialog.askopenfilename(
            title="选择输入MP3文件",
            filetypes=[("MP3 音频文件", "*.mp3"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_path_var.set(file_path)
            # 如果输出为空，自动设置默认输出
            if not self.output_path_var.get():
                input_dir = os.path.dirname(file_path)
                default_output = os.path.join(input_dir, "output")
                self.output_path_var.set(default_output)
                self.log(f"💡 自动设置默认输出目录: {default_output}")

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_path_var.set(dir_path)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()

    def start_processing(self):
        if self.is_processing:
            messagebox.showwarning("提示", "正在处理中，请等待...")
            return

        input_file = self.input_path_var.get().strip()
        output_dir = self.output_path_var.get().strip()
        model = self.model_var.get()

        # 验证
        if not input_file:
            messagebox.showerror("错误", "请先选择输入MP3文件！")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件不存在: {input_file}")
            return

        if not input_file.lower().endswith('.mp3'):
            messagebox.showwarning("警告", "输入文件不是MP3格式，仍会尝试处理")

        # 默认输出处理
        if not output_dir:
            input_dir = os.path.dirname(input_file)
            output_dir = os.path.join(input_dir, "output")

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        self.is_processing = True
        self.start_btn.config(state="disabled", text="处理中...")

        # 在后台线程处理
        self.process_thread = threading.Thread(
            target=self.processing_thread,
            args=(input_file, output_dir, model, self.auto_open_var.get())
        )
        self.process_thread.start()

    def processing_thread(self, input_file, output_dir, model, auto_open):
        try:
            self.log(f"➤ 输入文件: {os.path.basename(input_file)}")
            self.log(f"➤ 输出目录: {output_dir}")
            self.log(f"➤ 使用模型: {model}")
            self.log("")

            # 构建命令
            cmd = [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "vocal_remover_api.py"),
                input_file,
                "-o", output_dir,
                "--model", model
            ]

            self.log(f"执行命令: {' '.join(cmd)}")
            self.log("")

            # 运行并捕获输出
            env = os.environ.copy()
            # 确保ffmpeg在PATH中
            ffmpeg_path = os.path.join(os.path.dirname(__file__), "bin", "ffmpeg-master-latest-win64-gpl", "bin")
            if os.path.exists(ffmpeg_path):
                if 'PATH' in env:
                    env['PATH'] = ffmpeg_path + os.pathsep + env['PATH']
                else:
                    env['PATH'] = ffmpeg_path

            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in process.stdout:
                line = line.rstrip()
                if line:
                    self.log(line)

            exit_code = process.wait()

            if exit_code == 0:
                self.log("")
                self.log("✅ 处理完成！")

                # 获取输出路径
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                mp3_path = os.path.join(output_dir, model, base_name, "no_vocals.mp3")
                if os.path.exists(mp3_path):
                    self.log(f"🎯 MP3伴奏: {mp3_path}")

                if auto_open:
                    # 打开输出文件夹
                    open_dir = os.path.join(output_dir, model, base_name)
                    if os.path.exists(open_dir):
                        if sys.platform == 'win32':
                            os.startfile(open_dir)
                        elif sys.platform == 'darwin':
                            subprocess.run(['open', open_dir])
                        else:
                            subprocess.run(['xdg-open', open_dir])
                        self.log(f"📂 已打开输出文件夹")

                messagebox.showinfo("完成", "✅ 人声去除完成！\n伴奏已经生成好了。")
            else:
                self.log("")
                self.log(f"❌ 处理失败，退出码: {exit_code}")
                messagebox.showerror("失败", f"处理失败，请查看日志了解详情。\n退出码: {exit_code}")

        except Exception as e:
            self.log("")
            self.log(f"❌ 异常: {str(e)}")
            messagebox.showerror("异常", f"处理发生异常:\n{str(e)}")

        finally:
            self.is_processing = False
            self.start_btn.config(state="normal", text="🚀 开始处理")

    def on_closing(self):
        if self.is_processing:
            if not messagebox.askokcancel("退出", "正在处理中，确定要退出吗？"):
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    app = VocalRemoverGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
