import os
from openai import OpenAI

# 打开CMD和PowerShell执行命令为：
# setx ARK_API_KEY "ark-key"
# $env:ARK_API_KEY = "ark-key"
# print("环境变量 ARK_API_KEY =", os.getenv("ARK_API_KEY"))
# C:\Users\Alan>echo %ARK_API_KEY%
# Pro模型！
# ark-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 选择：doubao-seed-2-0-pro-260215

# 初始化DeepSeek（同时作为降级链的最后一道保险）
clientdp = OpenAI(
api_key='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
base_url="https://api.deepseek.com",
max_retries=0)   # 重试统一交给下面的降级链处理，不让SDK自己重试拖慢答题节奏

# 初始豆包
# 注意：没配置 ARK_API_KEY 时，OpenAI() 构造就会直接抛异常导致整个脚本起不来，
# 所以这里给个占位key，真正调用失败后由下面的降级链自动切到其它模型。
_ARK_API_KEY = os.environ.get("ARK_API_KEY")
if not _ARK_API_KEY:
    print("[AI降级] 警告：环境变量 ARK_API_KEY 未设置，豆包模型将不可用，会自动走备用模型。")

clientdb = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=_ARK_API_KEY or "ARK_API_KEY_NOT_SET",
    max_retries=0,
)

def open_ai_deepseek(question):
    """
    调用DeepSeek API获取回答（最终稳定版：仅输出纯答案字母）

    参数:
        question (str): 用户输入的问题

    返回:
        str: 仅包含 A/B/C/D/E 的连续大写字母答案，无任何多余内容
    """

    response = clientdp.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "严格指令：只做数理化答题。选择题、多选题、判断题直接输出连续大写字母，判断题A=对/B=错。禁止输出任何汉字、空格、标点、解释、换行，只允许输出ABCDE等连续性的字母。"
            },
            {"role": "user", "content": question},
        ],
        stream=False,
        temperature=0.0,    # 核心：固定答案，不随机发挥
        max_tokens=15,       # 限制长度，只输出答案
        top_p=1.0
    )

    # 🔥 终极过滤：只保留大写A-E字母，彻底杜绝多余内容
    answer = response.choices[0].message.content.strip()
    # final_answer = ''.join([c for c in answer if c.isupper() and c in 'ABCDE'])

    return answer


def open_ai_doubao(question):
    """
    调用DeepSeek API获取回答（最终稳定版：仅输出纯答案字母）

    参数:
        question (str): 用户输入的问题

    返回:
        str: 仅包含 A/B/C/D/E 的连续大写字母答案，无任何多余内容
    """
    # 调用接口
    response = clientdb.chat.completions.create(
        model="doubao-seed-2-0-mini-260428",
        messages=[
            # 全局系统提示词（人设、规则、输出要求，优先级最高）
            {"role": "system",
             "content": "你是严谨的答题助手，你必须多思考很久，不要给我答错了。但是回答精简，只回答大写字符ABC等。答案只答A或ABC或AD，禁止有多余的符号。你只答选择题、单选题、多选题；禁止答填空题！遇到填空题严格返回字符NONE，前端好做判断。"},
            {"role": "user", "content": question}
        ],
        temperature=0,  # 零随机，常识固定答案
        top_p=0.1,
        max_tokens=10  # 限制输出长度，只能输出1~3个字母，杜绝多余文字
    )

    # ✅ 只输出纯中文回答内容
    return response.choices[0].message.content


# 答题用的系统提示词（选择题、多选题、判断题、填空题都走这一套）
SYS_TIMU = "你是XXXXXXXXXX学生，你是学霸，你必须全网搜索相关知识。但回答精简，填空题以外的题目只回答大写字符ABC等，答案只答A或ABC或AD，禁止有多余的符号。你需要回答选择题、单选题、多选题、填空题！但是填空题我们会告诉你答案是几个字，填空题严格按照要求的回答字符个数来！"

# 模型降级链：(模型名, 客户端, 模型ID)，按顺序尝试，前一个失败自动换下一个
# 典型场景：豆包 pro 触发 SetLimitExceeded（安心体验模式额度用尽，服务被暂停）→ 自动切 mini → 再切 DeepSeek
TIMU_MODEL_CHAIN = [
    ("豆包pro", clientdb, "doubao-seed-2-0-pro-260215"),
    ("豆包mini", clientdb, "doubao-seed-2-0-mini-260428"),
    ("DeepSeek", clientdp, "deepseek-chat"),
]


def open_ai_doubao_pro(question):
    """
    按【豆包pro → 豆包mini → DeepSeek】的降级链获取答案。
    任何一个模型报错（额度用尽429、被暂停、超时、网络异常等）都会自动换下一个，
    避免单个模型不可用时整个答题脚本崩溃退出。

    参数:
        question (str): 用户输入的问题

    返回:
        str: 模型给出的答案（仅 A/B/C/D/E 字母或填空题文字）；
             三个模型全部失败时返回 "NONE" 兜底
    """
    last_err = None
    for name, client, model in TIMU_MODEL_CHAIN:
        try:
            # 调用接口
            response = client.chat.completions.create(
                model=model,
                messages=[
                    # 全局系统提示词（人设、规则、输出要求，优先级最高）
                    {"role": "system", "content": SYS_TIMU},
                    {"role": "user", "content": question}
                ],
                temperature=0,  # 零随机，常识固定答案
                top_p=0.1,
                max_tokens=20,  # 限制输出长度，只能输出1~3个字母，杜绝多余文字
                timeout=30      # 单次最多等30秒，卡住了就换下一个模型
            )

            answer = (response.choices[0].message.content or "").strip()
            if not answer:
                raise ValueError("模型返回了空内容")

            if name != "豆包pro":
                print(f"[AI降级] 已改用 {name}({model}) 作答：{answer}")
            return answer

        except Exception as e:  # noqa: BLE001 单个模型失败不能影响答题，统一降级
            last_err = e
            print(f"[AI降级] {name}({model}) 调用失败：{type(e).__name__}: {str(e)[:150]}")

    # 三个模型全部失败：不抛异常中断脚本，返回NONE让上层按“答错”逻辑继续（蒙题/跳过）
    print(f"[AI降级] 所有模型均不可用，返回NONE兜底。最后一个错误：{last_err}")
    return "NONE"