# 通用工具库，包含所有基本必要的Window应用层的操作（必须导入）
import re
from itertools import combinations
# 键盘鼠标事件控制库。
# import KeyBoardEvent as ky
import UtilityModuleClass as alan
# OCR文字识别库，快速截屏。
import OCRViewModule as ocr,json
# AI调用，可以调用多款AI解析问题。
import OpenAITool as ai

# 初始化一个空列表，用于存放转换后的坐标，网页翻页
coordinates = []
index = 0

# 当前这道题已经答错的次数（答对、换题后清零）
# 用于多选题的"前两次都答错，第三次直接全选"策略
wrong_count = 0

# 当前这道题在屏幕上检测到的选项按钮（如 "ABCD" 或 "ABCDE"）
# 必须在这道题刚出现、还没点过任何选项时检测：选项被点选后按钮样式会变，事后检测会漏选项
current_options = ""

# 多选题蒙题最多提交几次（第3次是全选，全选也错之后最多再试几次就放弃，别在一道题上耗太久）
MAX_MENG_TIMES = 6


def detect_options():
    """
    检测当前屏幕上实际存在哪些选项按钮，返回如 "ABCD" 或 "ABCDE"

    注意：选项个数不固定（有的题ABCD四个，有的题ABCDE五个），
    所以"全选"必须按这里检测到的实际结果来，不能写死ABCD。
    """
    options = ""
    for option in ["A", "B", "C", "D", "E"]:
        try:
            # 这里安静地检测，不打印日志，避免刷屏
            if alan.pyautogui.locateOnScreen(alan.lod_img(f"{option}.png"), confidence=0.8) is not None:
                options += option
        except Exception:
            pass
    return options

def is_timu():
    """
    判断屏幕上是否存在题目图标istimu.png
    :return: bool，存在题目返回True，不存在返回False
    """
    tempStr = alan.lod_img('istimu.png')
    image_position = alan.find_image_on_screen(tempStr)
    if image_position is not None:
        print(f"找到{tempStr}！坐标是：{image_position}")
        # alan.hover_to_image(tempStr)
        # alan.time.sleep(1)
        return True
    else:
        print(f"未找到{tempStr}，无法执行后续操作")
        return False

def is_play():
    """
    :return: bool，存在题目返回True，不存在返回False
    """
    tempStr = alan.lod_img('play.png')
    image_position = alan.find_image_on_screen(tempStr,0.9)
    if image_position is not None:
        print(f"找到{tempStr}！坐标是：{image_position}")
        alan.hover_to_image(tempStr)
        alan.pyautogui.click()
        return True
    else:
        print(f"没有找到播放图标 {tempStr} Play")
        return False

def is_renlianshibie():
    """
    人脸识别点击，遇到了就点
    """
    tempStr = alan.lod_img('kaishishibie.png')
    image_position = alan.find_image_on_screen(tempStr)
    if image_position is not None:
        print(f"找到{tempStr}！坐标是：{image_position}")
        alan.hover_to_image(tempStr)
        alan.pyautogui.click()
        return True
    else:
        print(f"未找到{tempStr}")
        return False

def jietu_timu():
    """
    题目截图专用函数
    """
    tempStr = alan.lod_img('istimu.png')
    image_position = alan.find_image_on_screen(tempStr)
    if image_position is not None:
        print(f"找到{tempStr}！起始坐标是：{image_position}")
        # 自动增加额外得坐标作用域结束作保，其中横向x+1200 / 竖向y+500
        # 采用区域截图
        x, y = image_position
        x -= 100
        y += 30
        # 终点坐标：横向 +1200，竖向 +500
        x1 = x + 1190

        # Y根据确定按钮计算，结束点得Y轴坐标。
        tempStr = alan.lod_img('ok.png')
        image_position = alan.find_image_on_screen(tempStr)
        x2, y2 = image_position

        y1 = y + (y2-y) - 40

        alan.move_to(x,y)
        alan.time.sleep(1)
        alan.move_to(x1,y1)
        alan.time.sleep(1)

        full_img = alan.capture_screen(x,y,x1,y1) # 区域截图
        full_save_path = alan.os.path.join(alan.WORK_FILE_DIR, "timu.png")
        full_img.save(full_save_path)
        print(f"题目截图已保存至: {full_save_path}\n")
    else:
        print(f"未找到{tempStr}，无法执行后续操作")

def get_daan():
    """
    获取答案
    """
    result = ocr.call_paddle_ocr(alan.lod_img("timu.png"))
    print("题目内容：") # 控制台打印结果集（不重要，只是测试使用）
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    final_text = ""
    for item in result["data"]:
        final_text += item["text"]
    # 只保留中文汉字（去除字母、数字、符号、标点）
    final_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\.\+\-\*【】；‘，。/！!]', '', final_text)
    # 输出最终结果（只有一段纯汉字）
    print(final_text)

    # 首先判断是那种类型的题目？（判断题、单选题、多选题）保存到变量strTiMu中
    if "多选题" in final_text[:10]:  # 只在前10个字符中查找
        strTiMu = "多选题"
    elif "单选题" in final_text[:10]:
        strTiMu = "单选题"
    elif "判断题" in final_text[:10]:
        strTiMu = "判断题"
    else:
        strTiMu = "填空题"

    # print(f"题目类型：{strTiMu}")

    daan = ai.open_ai_doubao_pro(final_text)
    print("AI回答为：" + daan)

    # 返回结果为['题目类型', '答案']
    return [strTiMu,final_text, daan]


def set_daan(daan, timu_type):
    """
    提交答案并返回是否成功
    :param daan: 要提交的答案（如 "A", "BC" 等）
    :param timu_type: 题目类型
    :return: True表示答案正确（题目已消失），False表示答案错误（题目还在）
    """
    global wrong_count

    # 点击答案
    for char in daan:
        if char in ["A", "B", "C", "D", "E"]:
            # 关键：只有真的在屏幕上找到了这个选项按钮才点击。
            # 否则hover失败鼠标会停在原地，一点就点到别的地方（比如ABCD的题里点到不存在的E）
            if alan.hover_to_image(alan.lod_img(f"{char}.png")):
                alan.time.sleep(0.1)
                alan.pyautogui.click()
            else:
                print(f"⚠ 屏幕上没有找到选项 {char}，跳过不点（避免误点其它位置）")
    alan.time.sleep(0.2)

    # 提交答案
    alan.hover_to_image(alan.lod_img("ok.png"))
    alan.pyautogui.click()
    alan.time.sleep(1.5)

    # 判断答案是否正确（题目是否消失）
    if is_timu():
        # 题目还在，说明答错了，累计答错次数（多选题第三次全选要用到）
        wrong_count += 1
        print(f"本题已答错 {wrong_count} 次")
        return False

    # 答对了，本题结束，计数清零
    wrong_count = 0
    return True


def meng_ti(timu_type, attempted):
    """
    蒙题函数：按顺序尝试未试过的选项
    :param timu_type: 题目类型（判断题、单选题、多选题）
    :param attempted: AI已经答错的那个答案（如 "AB" 表示AI选了A和B）
    :return: True表示蒙题成功，False表示失败

    多选题规则：前面两次（AI答案 + 第一次蒙题）如果都答错，第三次就直接全选。
    全选按屏幕上实际检测到的选项来，ABCD四选项就是ABCD，ABCDE五选项就是ABCDE。
    """
    # 已经试过的答案：既记录单个字母，也记录整体组合，避免重复提交同一个答案
    tried = set()
    if attempted:
        tried.update(attempted.strip())
        tried.add(attempted.strip())

    while is_timu():
        meng_daan = None

        if timu_type == "判断题":
            # 判断题只有A(对)和B(错)两种可能
            if "A" not in tried:
                meng_daan = "A"
            elif "B" not in tried:
                meng_daan = "B"
            else:
                print("判断题AB都试过了还是错，放弃此题")
                return False

        elif timu_type == "单选题":
            # 单选题按顺序尝试：A->B->C->D
            if "A" not in tried:
                meng_daan = "A"
            elif "B" not in tried:
                meng_daan = "B"
            elif "C" not in tried:
                meng_daan = "C"
            elif "D" not in tried:
                meng_daan = "D"
            else:
                print("单选题ABCD都试过了还是错，放弃此题")
                return False

        elif timu_type == "多选题":
            # 选项个数不固定：有的是ABCD四个，有的是ABCDE五个，所以按实际检测结果来
            # 优先用题目刚出现时缓存下来的检测结果（现在再检测，已选中的按钮样式变了会漏选项）
            available_options = current_options or detect_options()
            if len(available_options) < 2:
                print(f"多选题没检测到足够的选项按钮（检测到：{available_options or '无'}），放弃此题")
                return False

            full_answer = "".join(available_options)
            next_times = wrong_count + 1  # 本次即将进行的是本题的第几次作答
            print(f"多选题：选项{available_options}，全选是{full_answer}；已答错{wrong_count}次，本次是第{next_times}次作答")

            if next_times >= 3 and full_answer not in tried:
                # 需求：前两次都答错，第三次直接全选
                meng_daan = full_answer
                print(f"前两次都答错了，第{next_times}次直接全选：{full_answer}")
            else:
                # 第二次（以及全选也试过之后）：从选项多的组合往少的试，先排除全选（全选留给第3次用）
                combos = ["".join(combo)
                          for r in range(len(available_options) - 1, 1, -1)
                          for combo in combinations(available_options, r)]
                combos = [combo for combo in combos if combo not in tried]

                if next_times > MAX_MENG_TIMES:
                    print(f"多选题已尝试{wrong_count}次仍未蒙对（上限{MAX_MENG_TIMES}次），放弃此题")
                    return False

                if combos:
                    meng_daan = combos[0]
                elif full_answer not in tried:
                    # 没有别的组合可试了（例如只有AB两个选项的多选题），那就直接全选
                    meng_daan = full_answer
                    print(f"没有其它组合可试了，直接全选：{full_answer}")
                else:
                    print("多选题所有组合都试过了还是错，放弃此题")
                    return False

        else:
            print(f"未知题目类型：{timu_type}，放弃此题")
            return False

        # 尝试蒙题答案
        print(f"{timu_type}蒙题：已试过{sorted(tried)}，现在选{meng_daan}")
        if set_daan(meng_daan, timu_type):
            print(f"蒙题成功！答案是{meng_daan}")
            return True

        tried.add(meng_daan)
        alan.time.sleep(1.5)  # 等待屏幕稳定

    return False


def NextPage():
    global index
    index = (index + 1) % len(coordinates)  # 关键：实现循环
    x, y = coordinates[index]
    alan.move_to(x, y)
    alan.pyautogui.click()


def tiankongti():
    print("Agent 思考中...")
    result = ocr.call_paddle_ocr(alan.lod_img("timu.png"))
    final_text = ""
    for item in result["data"]:
        final_text += item["text"]
    # 只保留中文
    # final_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\.\，。！？；：\+\-\*【】]', '', final_text)
    final_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\.\+\-\*【】；‘，。/！!]', '', final_text)
    
    # 判断内容中是否存在“填空题”三个字，有则继续，无则返回。
    if "填空题" not in final_text:
        print("不是填空题，tiankongti函数忽略！")
        return False

    # 填空题专项处理
    # 先获取填空题又几个答案框框
    daan_coords = alan.find_icons_coordinates_zhongxin(
        template_path=alan.lod_img('tiankongkuang.png'),
        threshold=0.6,  # 阈值
    )

    # 这里是找到了几个填空框框，可以传给AI，告诉AI答案是几个字。
    print(f"共找到 {len(daan_coords)} 个填空题框：")
    # for i, (x, y) in enumerate(daan_coords, 1):
    #     x = int(x)  # 强制转换为 Python int
    #     y = int(y)  # 强制转换为 Python int
    #     # 鼠标移动到这个位置
    #     alan.move_to(x, y)
    #     alan.pyautogui.click()
    #     # 延时一秒钟
    #     alan.time.sleep(0.5)

    # 是len(daan_coords)个字的答案，题目内容是final_text
    daanText = ai.open_ai_doubao_pro(f"答案是{len(daan_coords)}字，你的回答答案必须是这个字数！"+final_text)
    print("AI填空题答案是：" + daanText)

    # 兜底保护：AI返回的字数少于填空框数量时（例如三个模型都不可用返回NONE），避免索引越界崩溃
    if len(daanText) < len(daan_coords):
        print(f"⚠ AI答案「{daanText}」字数少于填空框数量（{len(daan_coords)}），缺口按空字符填入。")

    # 下面就是，按照第一个填空题坐标、第二个、第三个类似的变量，每次到某个框框的时候，先用鼠标单机激活，然后复制答案第一个汉字，粘贴到第一个框框中，然后下一个循环继续类似操作，知道答案全部粘贴完就行
    for i, (x, y) in enumerate(daan_coords, 1):
        x = int(x)  # 强制转换为 Python int
        y = int(y)  # 强制转换为 Python int

        # 拷贝daanText对应的字符到剪贴板（i超出答案长度时填空字符，防止越界）
        alan.copy_text(daanText[i-1] if i <= len(daanText) else "")
        
        # 鼠标移动到这个位置
        alan.move_to(x, y)
        alan.pyautogui.click()

        # 粘贴到这个框框中
        alan.copy_paste()

        # 延时一秒钟
        alan.time.sleep(0.5)

    alan.hover_to_image(alan.lod_img("ok.png"))
    alan.pyautogui.click()  # 提交答案了

    # 不断点击确定按钮，直到ok.png消失为止
    while True:
        alan.time.sleep(0.5)
        image_position = alan.find_image_on_screen(alan.lod_img("ok.png"))
        if image_position is None:
            break
        # 点击ok.png
        x,y = image_position
        alan.move_to(x,y)
        alan.pyautogui.click()

    print("Agent 思考完毕！")
    return "填空题" in final_text


if __name__ == '__main__':

    print("-[Agent Auto]-")
    print("-输入任意字符开始-")
    input()

    alan.init2()

    # 全部页面下标初始化为0
    index = 0
    # 假设你已经得到了匹配坐标列表
    matched_coords = alan.find_icons_coordinates(
        template_path=alan.lod_img('cfr_ico.png'),
        threshold=0.6,  # 阈值
    )

    # 遍历并打印每个坐标
    print(f"共找到 {len(matched_coords)} 个匹配图标：")
    for i, (x, y) in enumerate(matched_coords, 1):
        x = int(x)  # 强制转换为 Python int
        y = int(y)  # 强制转换为 Python int
        coordinates.append((x, y))  # 添加到 coordinates 列表中
        print(f"  {i}. 坐标 (x={x}, y={y})")

    while True:
        is_renlianshibie()
        alan.time.sleep(1.0)

        if is_timu(): # 题目是否存在？
            jietu_timu() # 截取题目图片
            alan.time.sleep(2)

            # 新题出现时先检测选项（wrong_count为0说明这道题还没答过）
            # 必须在点任何选项之前检测：选项被选中后按钮样式会变，之后再检测会漏掉选项
            if wrong_count == 0:
                current_options = detect_options()
                print(f"本题检测到选项：{current_options or '（没检测到，蒙题时会再检测一次）'}")

            # 直接单独处理填空题的问题
            if tiankongti():
                # 如果是填空题且已处理完成，跳过后续逻辑
                wrong_count = 0  # 本题结束，答错计数清零
                continue

            print("Agent AI (DeepSeek) 思考中...")
            # 获取答案
            timu_type, timu_content, daan = get_daan()
            print(f"题目类型：{timu_type}")
            print(f"题目内容：{timu_content}")
            print("Agent AI (DeepSeek) 思结束！")
            print(f"AI回答为：{daan}")

            # 提交AI答案
            if set_daan(daan, timu_type):
                print("AI已完成答题！")
                continue

            # AI答案错误，进入蒙题模式
            print("AI答题错误，开始蒙题！")
            meng_ti(timu_type, daan)
        else:
            is_play()
            wrong_count = 0  # 换题/翻页了，答错计数清零
            NextPage()

# 打包命令：
# cd PyMainProject
# pyinstaller -c --paths "./LibModules" --hidden-import UtilityModuleClass --hidden-import OCRViewModule --hidden-import KeyBoardEvent --hidden-import OpenAITool --distpath "C:\AgentAuto_EXE\" CFR_Main.py
