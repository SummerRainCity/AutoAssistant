import subprocess
from datetime import time as datetime_time
from tkinter import Image
import coordinates as coordinates
from PIL import ImageGrab
from PIL import Image, ImageOps
import cv2
import numpy as np
import pyperclip
import pynput
import pyautogui
import time
import os

# 定义全局变量，
from greenlet import platform

CURRENT_EXE_DIR = None
WORK_FILE_DIR = None


def lod_img(p):
    """返回资源路径"""
    # 👇 增加防错判断
    if not p:
        raise Exception("lod_img 错误：传入的图片路径不能为空！")
    str1 = os.path.join(WORK_FILE_DIR, p)
    # 👇 增加文件是否存在判断
    if not os.path.exists(str1):
        print(f"⚠警告：图片文件不存在！路径：{str1}")
    # print(f"✅资源路径是：{str1}")
    return str1


def p(s):
    """简易打印函数"""
    print(s)


def init2():
    """初始化全局路径变量"""
    # 声明使用全局变量（关键步骤）
    global CURRENT_EXE_DIR, WORK_FILE_DIR
    # 获取并赋值给全局变量
    CURRENT_EXE_DIR = os.getcwd()
    # 使用 os.sep 替代硬编码的 \，保证跨平台兼容性（Windows用\，Linux/Mac用/）
    WORK_FILE_DIR = os.path.join(CURRENT_EXE_DIR, "WorkFile" + os.sep)
    # 打印验证
    p(f"■、当前程序目录：{CURRENT_EXE_DIR}")
    p(f"■、当前工作目录是：{WORK_FILE_DIR}")


def init():
    """初始化全局路径变量，并处理WorkFile文件夹（不存在则创建，存在则打开）"""
    # 声明使用全局变量
    global CURRENT_EXE_DIR, WORK_FILE_DIR

    # 获取当前程序目录（绝对路径）
    CURRENT_EXE_DIR = os.path.abspath(os.getcwd())
    # 拼接工作文件夹路径（规范化路径，避免\和/混用问题）
    WORK_FILE_DIR = os.path.normpath(os.path.join(CURRENT_EXE_DIR, "../WorkFile"))

    # 1. 判断并创建文件夹（不存在则创建）
    if not os.path.exists(WORK_FILE_DIR):
        try:
            os.makedirs(WORK_FILE_DIR, exist_ok=True)
            p(f"■、WorkFile文件夹不存在，已创建：{WORK_FILE_DIR}")
        except PermissionError:
            p(f"■、创建文件夹失败：权限不足，请以管理员身份运行！")
            return
        except Exception as e:
            p(f"■、创建文件夹失败：{str(e)}")
            return

    # 2. 打开文件夹（Windows专用稳定方案）
    try:
        # 核心：调用Windows原生资源管理器explorer.exe
        # /e 参数：以资源管理器模式打开；/root 参数：精准定位到目标文件夹
        # subprocess.run(
        #     ['explorer.exe', '/e,/root,', WORK_FILE_DIR],
        #     shell=True,
        #     check=True,
        #     # 隐藏子进程的输出，避免控制台乱码/多余窗口
        #     stdout=subprocess.DEVNULL,
        #     stderr=subprocess.DEVNULL
        # )
        p(f"■、已成功打开文件夹：{WORK_FILE_DIR}")
    except subprocess.CalledProcessError as e:
        p(f"■、打开文件夹失败：系统调用错误（错误码：{e.returncode}）")
    except FileNotFoundError:
        p(f"■、打开文件夹失败：未找到explorer.exe（系统异常）")
    except Exception as e:
        p(f"■、打开文件夹失败：{str(e)}")
        # 兜底方案：尝试用start命令打开
        try:
            subprocess.run(f'start "" "{WORK_FILE_DIR}"', shell=True)
            p(f"■、已通过兜底方案打开文件夹：{WORK_FILE_DIR}")
        except:
            p(f"■、所有打开方式均失败，请手动打开：{WORK_FILE_DIR}")

    # 打印最终路径信息
    p(f"■、当前程序目录：{CURRENT_EXE_DIR}")
    p(f"■、当前工作目录：{WORK_FILE_DIR}")


def find_image_on_screen(image_path,tol=0.8):
    """
    在电脑屏幕上查找指定图片，并返回其中心点坐标

    参数:
        image_path (str): 待查找图片的文件路径（绝对路径/相对路径均可）

    返回值:
        tuple | None: 找到图片则返回中心点坐标 (x, y)，未找到/出错则返回 None
    """
    if not os.path.exists(image_path):
        print(f"Fun->找不到文件: {image_path}")
        return None

    try:
        # 尝试在屏幕上定位图片
        # confidence=0.8 是置信度（需要安装 opencv-python 才能使用此参数）
        # 如果没装 opencv，去掉 confidence 参数，但容错率会变低
        location = pyautogui.locateOnScreen(image_path, confidence=tol)

        if location:
            print(f"Fun->找到图片！位置: {location}")
            # 获取中心点坐标
            center = pyautogui.center(location)
            print(f"Fun->中心点坐标: {center}")
            x,y = center
            print(f"Fun->坐标是：{x}, {y}")
            return center
        else:
            print("Fun->未在屏幕中找到该图片。")
            return None
    except Exception as e:
        # print(f"Fun->发生错误: {e}")
        return None


def hover_to_image(image_path, confidence=0.8):
    """
    将鼠标移动到屏幕上指定图片的中心位置
    :param image_path: 要定位的图片路径
    :param confidence: 匹配置信度（0-1，需要安装opencv-python）
    """
    if not os.path.exists(image_path):
        print(f"错误：找不到图片文件 {image_path}")
        return False

    try:
        # 定位图片在屏幕上的位置
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)

        if location:
            # 计算中心点坐标
            center = pyautogui.center(location)
            print(f"找到图片，移动鼠标到坐标: {center.x}, {center.y}")

            # 移动鼠标到中心点
            pyautogui.moveTo(center.x, center.y)
            return True
        else:
            print("未在屏幕中找到该图片。")
            return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False


def mouse_action_image(image_path, action='hover', confidence=0.8, delay=0.2):
    """
    根据图片定位并执行鼠标操作
    :param image_path: 目标图片路径
    :param action: 操作类型，可选 'h'(悬停)、'c'(单击)、'd'(双击)
    :param confidence: 匹配置信度（0-1）
    :param delay: 移动鼠标后到执行点击的延迟（秒），模拟真人操作
    :return: 操作成功返回True，失败返回False
    """
    # 1. 检查图片文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：找不到图片文件 {image_path}")
        return False

    try:
        # 2. 定位图片在屏幕上的位置
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if not location:
            print(f"未在屏幕中找到图片：{image_path}")
            return False

        # 3. 计算图片中心点坐标
        center_x, center_y = pyautogui.center(location)
        print(f"找到图片，坐标：({center_x}, {center_y})")

        # 4. 移动鼠标到目标坐标
        pyautogui.moveTo(center_x, center_y, duration=0.3)  # duration=移动耗时，更平滑
        time.sleep(delay)  # 延迟，确保鼠标移动到位

        # 5. 根据指定操作执行鼠标动作
        if action == 'c':
            pyautogui.click(center_x, center_y)
            print("执行单击操作完成")
        elif action == 'd':
            pyautogui.doubleClick(center_x, center_y)
            print("执行双击操作完成")
        elif action == 'h':
            print("仅执行悬停操作，无点击")
        else:
            print(f"不支持的操作类型：{action}，仅支持 hover/click/double_click")
            return False

        return True

    except Exception as e:
        print(f"操作失败：{e}")
        return False


def find_icons_coordinates(template_path, threshold=0.8, min_dist=20):
    """
    在当前屏幕上查找所有与 template_path 图标匹配的位置，返回它们的左上角坐标列表。

    Args:
        template_path (str): 要匹配的小图标文件路径，如 'yemian.png'
        threshold (float): 匹配阈值，范围 0~1，越接近1匹配越严格，默认 0.8
        min_dist (int): 去重时两点之间的最小距离（像素），避免返回太近的重复点，默认 50

    Returns:
        List[Tuple[int, int]]: 所有匹配图标的左上角坐标 (x, y) 列表，如 [(x1, y1), (x2, y2), ...]
    """

    # 1. 检查模板文件是否存在
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板图片 '{template_path}' 不存在，请检查路径！")

    # 2. 加载模板图像（小图标）
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"无法加载模板图片 '{template_path}'，请检查文件格式是否为 JPG/PNG 等。")
    h, w = template.shape[:2]  # 模板的高度和宽度，后续用于画框或点击

    # 3. 截取当前整个屏幕
    screenshot = ImageGrab.grab()  # PIL 格式，RGB
    screenshot_np = np.array(screenshot)  # 转为 NumPy 数组
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)  # 转为 OpenCV 格式 (BGR)

    # 4. 使用模板匹配查找相似区域
    res = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)  # 找到所有匹配度大于阈值的点
    points = list(zip(*loc[::-1]))  # 注意：loc 是 (y, x)，我们转换为 (x, y)

    # 5. 去重：去掉太靠近的重复点
    unique_points = []
    seen = set()
    for pt in points:
        x, y = pt
        is_unique = True
        for seen_pt in seen:
            sx, sy = seen_pt
            if abs(sx - x) < min_dist and abs(sy - y) < min_dist:
                is_unique = False
                break
        if is_unique:
            seen.add((x, y))
            unique_points.append((x, y))

    # 6. 返回所有去重后的坐标
    return unique_points

def find_icons_coordinates_zhongxin(template_path, threshold=0.8, min_dist=20):
    """
    在当前屏幕上查找所有与 template_path 图标匹配的位置，返回它们的中心点坐标列表。

    Args:
        template_path (str): 要匹配的小图标文件路径，如 'yemian.png'
        threshold (float): 匹配阈值，范围 0~1，越接近1匹配越严格，默认 0.8
        min_dist (int): 去重时两点之间的最小距离（像素），避免返回太近的重复点，默认 20

    Returns:
        List[Tuple[int, int]]: 所有匹配图标的中心点坐标 (center_x, center_y) 列表
    """

    # 1. 检查模板文件是否存在
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板图片 '{template_path}' 不存在，请检查路径！")

    # 2. 加载模板图像（小图标）
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"无法加载模板图片 '{template_path}'，请检查文件格式是否为 JPG/PNG 等。")
    h, w = template.shape[:2]  # 模板的高度和宽度

    # 3. 截取当前整个屏幕
    screenshot = ImageGrab.grab()  # PIL 格式，RGB
    screenshot_np = np.array(screenshot)  # 转为 NumPy 数组
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)  # 转为 OpenCV 格式 (BGR)

    # 4. 使用模板匹配查找相似区域
    res = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)  # 找到所有匹配度大于阈值的点
    points = list(zip(*loc[::-1]))  # 转换为 (x, y) 左上角坐标

    # 5. 去重：去掉太靠近的重复点
    unique_points = []
    seen = set()
    for pt in points:
        x, y = pt
        is_unique = True
        for seen_pt in seen:
            sx, sy = seen_pt
            if abs(sx - x) < min_dist and abs(sy - y) < min_dist:
                is_unique = False
                break
        if is_unique:
            seen.add((x, y))
            unique_points.append((x, y))

    # 6. ✅ 关键修改：把左上角坐标转为中心点坐标
    center_points = []
    for (x, y) in unique_points:
        center_x = x + w // 2
        center_y = y + h // 2
        center_points.append((center_x, center_y))

    # 返回中心点坐标
    return center_points

def capture_screen(x1=None, y1=None, x2=None, y2=None):
    """
    截图函数，支持全屏截图和区域截图

    Args:
        x1 (int, optional): 区域截图起始点X坐标
        y1 (int, optional): 区域截图起始点Y坐标
        x2 (int, optional): 区域截图结束点X坐标
        y2 (int, optional): 区域截图结束点Y坐标

    Returns:
        PIL.Image.Image: 截图图像对象
    """
    # 如果提供了完整的区域坐标，则进行区域截图
    if all(param is not None for param in [x1, y1, x2, y2]):
        # 确保坐标顺序正确（处理起始点大于结束点的情况）
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)

        # 区域截图
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    else:
        # 全屏截图
        screenshot = ImageGrab.grab()

    full_save_path = os.path.join(WORK_FILE_DIR, "full_screen.png")
    screenshot.save(full_save_path)
    # print(f"debug全屏截图已保存至: {full_save_path}\n")

    return screenshot


def move_to(x, y=None, duration=0.3):
    """
    移动鼠标到指定坐标位置
    
    Args:
        x: 可以是X坐标(int)，Point对象，或坐标元组/列表(x, y)
        y (int): 目标Y坐标（当x为坐标时使用）
        duration (float): 移动耗时（秒），默认0.3秒，值越大移动越平滑
    
    Returns:
        bool: 移动成功返回True，失败返回False
    """
    try:
        # 处理不同的参数形式
        if y is None:
            # 可能是Point对象或元组/列表
            if hasattr(x, 'x') and hasattr(x, 'y'):
                # Point对象
                coord_x, coord_y = int(x.x), int(x.y)
            elif isinstance(x, (tuple, list)) and len(x) >= 2:
                # 元组或列表
                coord_x, coord_y = int(x[0]), int(x[1])
            else:
                raise ValueError(f"无法解析坐标: {x}")
        else:
            # 标准的两个参数形式
            coord_x, coord_y = int(x), int(y)
        
        pyautogui.moveTo(coord_x, coord_y, duration=duration)
        print(f"鼠标到坐标: ({coord_x}, {coord_y})")
        return True
    except Exception as e:
        print(f"移动鼠标失败: {e}")
        return False

def copy_text(text):
    # 程序复制文本到剪贴板
    pyperclip.copy(text)

def copy_paste():
    # 粘贴内容
    pyautogui.hotkey('ctrl', 'v')