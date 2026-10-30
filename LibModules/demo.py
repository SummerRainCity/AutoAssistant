# 通用工具库（必须导入）
import UtilityModuleClass as alan
# OCR文字识别库
import OCRViewModule as ocr,json
# 键盘事件控制库
import KeyBoardEvent as ky
# AI问题调用
import OpenAITool as ai

# 主函数入口-开始执行
if __name__ == '__main__':
    # 必须存在的初始化！！
    alan.init()

    ##############[通用模块]###############
    # 功能函数-在屏幕上查找图片，有则返回坐标x,y，无则返回None
    # image_position = alan.find_image_on_screen(alan.lod_img('cfr_ico.png'))
    # if image_position is not None:
    #     print(f"找到图片！坐标是：{image_position}")
    #     alan.hover_to_image(alan.lod_img('cfr_ico.png'))
    # else:
    #     print("未找到 del.png 图片，无法执行后续操作")

    # 鼠标操作为：移动到、单机鼠标
    # alan.hover_to_image(alan.lod_img('del.png'))
    # alan.time.sleep(1)
    # alan.hover_to_image(alan.lod_img('ico.png'))
    # alan.time.sleep(1)
    # alan.mouse_action_image(alan.lod_img('edit.png'), 'c')
    # alan.time.sleep(1)

    # 功能函数-获取指定图标在屏幕中的所有坐标位置
    # 调用修复后的函数（关键：降低阈值+合理设置最小间距）
    # matched_coords = alan.find_icons_coordinates(
    #     template_path=alan.lod_img('cfr_ico.png'),
    #     threshold=0.6,  # 阈值
    # )
    # # 遍历结果，拿来轮播页面使用
    # print(f"\n最终找到 {len(matched_coords)} 个匹配图标：")
    # results = []  # 换一个变量名，避免和 import 的 coordinates 冲突
    # for i, (x, y) in enumerate(matched_coords, 1):
    #     results.append((x, y))
    #     print(f"图标{i}：中心点坐标 (x={x}, y={y})")
    #     alan.pyautogui.moveTo(x, y)
    #     alan.time.sleep(0.1)
    #     alan.pyautogui.click()
    #     alan.time.sleep(1)


    # 功能函数-截图
    # full_img = capture_screen(500,400,1000,1080) # 区域截图
    # print("测试：正在进行全屏截图...")
    # full_img = alan.capture_screen()
    # full_save_path = alan.os.path.join(alan.WORK_FILE_DIR, "full_screen.png")
    # full_img.save(full_save_path)
    # print(f"全屏截图已保存至: {full_save_path}\n")

    #################################【OCR视觉识别模块】############################################

    # 一、OCR识别模块，返回JSON资源集合数据
    # result = ocr.call_paddle_ocr(alan.lod_img("text.png"))
    # print("返回的JSON结果：") # 控制台打印结果集（不重要，只是测试使用）
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    # 二、查找字符串返回box结果集
    # find_str = "苏打饼上"
    # ps = find_text_points_box(result, find_str)
    # print(f"\n包含「{find_str}」的文本坐标：")
    # for idx, point in enumerate(ps):
    #     print(f"第{idx + 1}个匹配项BOX坐标：{point}")

    # 查找字符串，返回中心坐标结果集x,y，然后点击，或者右击开始。
    # find_str = "大势浏览器"
    # x, y = ocr.find_text_point_single(result, find_str)
    # # 使用前建议先判断是否找到
    # if x is not None and y is not None:
    #     print(f"找到目标文本，中心坐标为：({x}, {y})")
    #     alan.time.sleep(0.1)
    #     alan.pyautogui.moveTo(x, y)
    #     alan.pyautogui.click()
    #     alan.pyautogui.doubleClick()
    #     # 点击当前鼠标位置的右键
    #     alan.pyautogui.click(button='right')
    # else:
    #     print("未找到包含指定字符串的文本")

    #######################【ky事件模块】#####################
    # ky.copy_ctrl_c()
    # ky.copy_ctrl_v()
    # 示例：全屏截图，自动复制到了剪切板中。
    # ky.copy_screen_capture()
    # 示例：区域截图 (10,10) 到 (510,610)
    # ky.copy_screen_capture_xy(10, 10, 1000, 1000)

    # 题目识别测试+AI回答
    result = ocr.call_paddle_ocr_text_contentTm(alan.lod_img("timu.png"))
    print("返回的JSON结果：\n" + result)
    daan = ai.open_ai_deepseek(result)
    print("DeepSeep AI回答为：" + daan)