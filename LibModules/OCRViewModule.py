import subprocess
import json
import shutil
import os
from typing import Dict, Any


def call_paddle_ocr(image_path: str,exe_path: str = None) -> Dict[str, Any]:
    """
    调用 PaddleOCR-json 程序进行 OCR 识别。
    """

    target_exe = exe_path
    exe_dir = None

    if not target_exe:
        for name in ["PaddleOCR", "PaddleOCR.exe", "PaddleOCR-json.exe"]:
            if shutil.which(name):
                target_exe = shutil.which(name)
                break
        if not target_exe:
            target_exe = r"C:\Python_Project\Agent_RPA_2026\OCR\PaddleOCR\PaddleOCR.exe"

    if os.path.isabs(target_exe):
        exe_dir = os.path.dirname(target_exe)

    cmd = [target_exe, f'-image_path={image_path}']

    try:
        result = subprocess.run(
            cmd,
            cwd=exe_dir,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # ========== 核心修复：清洗输出内容 ==========
        json_str = ""
        lines = result.stdout.splitlines()

        # 遍历每一行，找到看起来像是 JSON 的那一行（通常以 '{' 开头）
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('{'):
                json_str = stripped_line
                break

        if not json_str:
            return {"code": -1, "data": "未在输出中找到JSON数据"}

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return {
                "code": -1,
                "data": f"JSON解析失败: {str(e)}\n尝试解析的内容: {json_str}"
            }

    except Exception as e:
        return {"code": -1, "data": f"调用异常: {str(e)}"}


def call_paddle_ocr_text_content(image_path: str, exe_path: str = None) -> str:
    """
    调用 PaddleOCR 程序进行 OCR 识别，直接返回纯文本内容（自动换行）。
    """
    target_exe = exe_path
    exe_dir = None

    if not target_exe:
        for name in ["PaddleOCR", "PaddleOCR.exe", "PaddleOCR-json.exe"]:
            if shutil.which(name):
                target_exe = shutil.which(name)
                break
        if not target_exe:
            target_exe = r"C:\Python_Project\Agent_RPA_2026\OCR\PaddleOCR\PaddleOCR.exe"

    if os.path.isabs(target_exe):
        exe_dir = os.path.dirname(target_exe)

    cmd = [target_exe, f'-image_path={image_path}']

    try:
        result = subprocess.run(
            cmd,
            cwd=exe_dir,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # 清洗输出内容，提取 JSON
        json_str = ""
        lines = result.stdout.splitlines()
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('{'):
                json_str = stripped_line
                break

        if not json_str:
            return ""

        ocr_result = json.loads(json_str)

        # 提取并拼接文本内容
        if ocr_result.get("code") == 100:
            text_list = [item["text"] for item in ocr_result.get("data", [])]
            return "\n".join(text_list)
        else:
            return ""

    except Exception as e:
        return ""


def call_paddle_ocr_text_contentTm(image_path: str, exe_path: str = None) -> str:
    """
    【题目专用函数】调用 PaddleOCR 程序进行 OCR 识别，返回过滤后的纯净文本。（过滤版）
    """
    target_exe = exe_path
    exe_dir = None

    if not target_exe:
        for name in ["PaddleOCR", "PaddleOCR.exe", "PaddleOCR-json.exe"]:
            if shutil.which(name):
                target_exe = shutil.which(name)
                break
        if not target_exe:
            target_exe = r"C:\Python_Project\Agent_RPA_2026\OCR\PaddleOCR\PaddleOCR.exe"

    if os.path.isabs(target_exe):
        exe_dir = os.path.dirname(target_exe)

    cmd = [target_exe, f'-image_path={image_path}']

    try:
        result = subprocess.run(
            cmd,
            cwd=exe_dir,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # 清洗输出内容，提取 JSON
        json_str = ""
        lines = result.stdout.splitlines()
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('{'):
                json_str = stripped_line
                break

        if not json_str:
            return ""

        ocr_result = json.loads(json_str)

        # 提取、过滤并拼接文本内容
        if ocr_result.get("code") == 100:
            filtered_texts = []
            for item in ocr_result.get("data", []):
                text = item["text"].strip()

                # ========== 核心过滤逻辑 ==========
                # 1. 过滤掉空字符串
                if not text:
                    continue

                # 2. 过滤掉长度太短（<=1）且通常无意义的字符
                if len(text) <= 1:
                    # 可以在这里定义你想保留的单字符（如果有的话），目前全部过滤
                    continue

                # 3. (可选) 如果你还想过滤特定的垃圾词，可以加在这里
                garbage_words = ["确定", "得分规则"]
                if text in garbage_words:
                    continue

                filtered_texts.append(text)

            return "\n".join(filtered_texts)
        else:
            return ""

    except Exception as e:
        return ""


def find_text_points_box(orc_json, find_str):
    """
    在OCR结果中查找包含指定子串的文本，并返回对应坐标BOX集合
    :param orc_json: OCR识别结果的字典对象
    :param find_str: 需要查找的子字符串
    :return: 匹配到的坐标列表，格式为 [[x1,y1,x2,y2,x3,y3,x4,y4], ...]
    """
    matched_points = []

    # 检查识别状态码是否成功且包含数据
    if orc_json.get("code") == 100 and "data" in orc_json:
        for item in orc_json["data"]:
            # 检查文本是否包含目标子串
            if find_str in item.get("text", ""):
                # 将box坐标展平为一维数组方便遍历
                flat_box = [coord for point in item["box"] for coord in point]
                matched_points.append(flat_box)

    return matched_points


def find_text_point_single(orc_json, find_str):
    """
    在OCR结果中查找包含指定子串的文本，并返回第一个匹配BOX的中心坐标
    :param orc_json: OCR识别结果的字典对象
    :param find_str: 需要查找的子字符串
    :return: 第一个匹配BOX的中心坐标元组 (x, y)，未找到返回 (None, None)
    """
    # 检查识别状态码是否成功且包含数据
    if orc_json.get("code") == 100 and "data" in orc_json:
        for item in orc_json["data"]:
            # 检查文本是否包含目标子串
            if find_str in item.get("text", ""):
                # 获取当前box的四个顶点
                box = item["box"]
                # 提取所有x和y坐标
                x_coords = [point[0] for point in box]
                y_coords = [point[1] for point in box]
                # 计算中心坐标（取四个顶点的平均值）
                center_x = sum(x_coords) / 4
                center_y = sum(y_coords) / 4
                # 返回中心坐标元组，支持直接 x, y = 赋值
                return (center_x, center_y)
    # 未找到匹配项时返回None元组
    return None, None
