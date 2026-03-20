@echo off
REM Windows 批处理示例 - 拖放MP3文件到这个bat文件上直接处理

REM 检查是否有拖放的文件
if "%~1" == "" (
    echo 请将MP3文件拖放到这个批处理文件上
    pause
    exit /b 1
)

REM 获取输入文件
set INPUT_FILE=%~1
echo 正在处理: %INPUT_FILE%

REM 运行人声去除
python ..\vocal_remover_demucs.py "%INPUT_FILE%" --mp3

echo.
echo 处理完成！伴奏保存在output目录下
pause
