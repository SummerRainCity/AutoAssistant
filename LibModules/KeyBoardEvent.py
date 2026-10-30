import subprocess
import pyperclip
import pyautogui
from pynput import keyboard
from pynput.keyboard import Key

"""
此函数库主要功能:
复制粘贴,键盘事件,截图,区域截图
"""

def copy_text(text_to_copy):
    """
    将指定文本复制到系统剪贴板
    :param text_to_copy: 要复制到剪贴板的文本内容
    """
    try:
        # 将传入的文本复制到剪贴板
        pyperclip.copy(text_to_copy)
        print(f"文本已成功复制到剪贴板：{text_to_copy}")
        return True
    except Exception as e:
        # 捕获可能出现的异常（如 pyperclip 未正确安装、系统剪贴板权限问题等）
        print(f"复制失败：{str(e)}")
        return False


# 复制
def copy_ctrl_c():
    pyautogui.hotkey('ctrl', 'c')


# 粘贴
def copy_ctrl_v():
    pyautogui.hotkey('ctrl', 'v')


# 2. 模拟 Ctrl+V 粘贴
def copy_ctrl_v_moni():
    with keyboard.pressed(Key.ctrl):
        keyboard.press('v')
        keyboard.release('v')


def _handle_exit_code(code):
    """
    内部辅助函数：处理 ScreenCapture 的退出码
    """
    messages = {
        0: "未定义 (Undefined)",
        1: "用户点击关闭按钮退出",
        2: "用户右键点击退出",
        3: "用户按下 ESC 键退出",
        4: "复制 RGB 颜色后退出",
        5: "复制 HEX 颜色后退出",
        6: "复制 CMYK 颜色后退出",
        7: "复制鼠标位置后退出",
        8: "保存到文件后退出",
        9: "成功保存到剪贴板"
    }

    msg = messages.get(code, f"未知错误码: {code}")
    print(f"[ScreenCapture] {msg}")
    return code == 9  # 只有 Code 9 才是我们想要的“成功”


def copy_screen_capture():
    """
    截取全屏并保存到剪贴板（警⚠告：如果当前程序直接关闭，截图后的剪切板将失效！）
    """
    exe_path = r"/ScreenCapture_API/ScreenCapture.exe"

    try:
        # 执行命令，不使用 check=True，以便我们手动检查 returncode
        result = subprocess.run(
            [exe_path, "--cap:fullscreen,clipboard"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return _handle_exit_code(result.returncode)

    except FileNotFoundError:
        print(f"[错误] 未找到程序：{exe_path}")
        return False
    except Exception as e:
        print(f"[错误] 发生未知错误：{str(e)}")
        return False


def copy_screen_capture_xy(x1, y1, x2, y2):
    """
    截取指定区域并保存到剪贴板（警⚠告：如果当前程序直接关闭，截图后的剪切板将失效！）
    :param x1: 左上角 X 坐标
    :param y1: 左上角 Y 坐标
    :param x2: 右下角 X 坐标
    :param y2: 右下角 Y 坐标
    """
    exe_path = r"/ScreenCapture_API/ScreenCapture.exe"

    width = x2 - x1
    height = y2 - y1

    if width <= 0 or height <= 0:
        print("[错误] 坐标错误：右下角坐标必须大于左上角坐标")
        return False

    try:
        cap_param = f"--cap:area,{x1},{y1},{width},{height},clipboard"

        result = subprocess.run(
            [exe_path, cap_param],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return _handle_exit_code(result.returncode)

    except FileNotFoundError:
        print(f"[错误] 未找到程序：{exe_path}")
        return False
    except Exception as e:
        print(f"[错误] 发生未知错误：{str(e)}")
        return False
