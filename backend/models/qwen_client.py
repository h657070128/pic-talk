import os
import json
import httpx
import random
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    raise RuntimeError("DASHSCOPE_API_KEY is not set")


class QwenClient:
    """
    通义千问客户端
    - 生成图片语义计划
    - 生成标准答案
    """

    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    MODEL = "qwen-max"  # 可改成 qwen-plus

    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json",
            },
        )

    # -------------------------
    # 通用调用
    # -------------------------
    def _chat(self, messages: list, temperature: float = 0.7) -> str:
        payload = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": temperature,
        }

        resp = self.client.post(self.BASE_URL, json=payload)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # -------------------------
    # 1️⃣ 生成图片语义计划
    # -------------------------
    def generate_semantic_plan(self, difficulty_level: str) -> Dict[str, Any]:

        scenes = [
            "在阳光明媚的社区公园里喂鸭子",
            "在现代图书馆的安静阅读区翻书",
            "在厨房流理台前用搅拌机做香蕉奶昔",
            "在地铁车厢内给老人让座",
            "在宠物诊所里轻抚刚打完疫苗的小猫",
            "在阳台小花园里用喷壶浇番茄苗",
            "在社区中心教爷爷奶奶用平板电脑视频通话",
            "在雨天共撑一把大伞走过人行道",
            "在旧货市集淘二手黑胶唱片",
            "在露营帐篷外用便携炉煮热巧克力",
            "在舞蹈教室镜前练习芭蕾手位",
            "在修车铺旁帮爸爸递扳手",
            "在海边用金属探测器寻找贝壳与古币",
            "在咖啡馆窗边手绘明信片寄给笔友",
            "在社区菜园里采摘紫茄子和罗勒叶",
            "在音乐教室用尤克里里弹《You Are My Sunshine》",
            "在博物馆儿童互动区拼青铜器拓片拼图",
            "在雪后街道上堆戴围巾和胡萝卜鼻子的雪人",
            "在屋顶小农场观察蜜蜂采蜜",
            "在深夜书房台灯下修改英文演讲稿",
            "在社区老年活动室用放大镜读报纸",
            "在植物园温室里记录凤梨科植物气生根生长",
            "在共享厨房里教国际学生包素馅饺子",
            "在天文台穹顶下调整小型望远镜对准木星",
            "在社区回收站分类塑料瓶与铝罐",
            "在传统药房里用铜秤称量金银花与菊花",
            "在无障碍游泳池边协助朋友戴浮力腰带",
            "在校园创客空间用3D打印机打印盲文字母模型",
            "在街角修鞋摊看老师傅缝补裂口皮鞋",
            "在社区花园长椅上用语音助手朗读电子诗集",
            "在少儿编程课上拖拽积木块让机器人绕过障碍",
            "在旧书店阁楼翻找泛黄的昆虫图鉴",
            "在社区烘焙坊用硅胶模具制作无麸质饼干",
            "在湿地观鸟屋透过双筒望远镜数白鹭数量",
            "在社区中心用投影仪播放手语版天气预报",
            "在阳台垂直种植架上修剪罗勒与薄荷嫩芽",
            "在社区健身房用阻力带做肩部康复训练",
            "在非遗工坊里用蓝印花布拓印棉麻手帕",
            "在社区图书漂流角贴新书二维码借阅标签",
            "在屋顶太阳能板旁用平板查看当日发电量",
            "在社区厨房用厨余垃圾处理器制作堆肥",
            "在儿童医院游戏室用毛绒玩具演示听诊器用法",
            "在社区广场用蓝牙音箱播放非洲鼓节奏教学",
            "在植物标本室用镊子将蕨类叶片固定于吸水纸",
            "在社区老年大学用触控屏练习汉字笔顺动画",
            "在社区菜市场用可重复布袋装四季豆与山药",
            "在校园生态池边用pH试纸检测水质酸碱度",
            "在社区缝纫角用脚踏缝纫机修补帆布书包",
            "在社区音乐角用陶笛吹奏《茉莉花》五声音阶",
            "在社区药房自助终端扫描处方码取药",
            "在社区共享工具屋归还电动螺丝刀与水平仪",
            "在社区墙绘现场用投影仪描摹环保主题线稿",
            "在社区托育中心用布偶演示洗手七步法",
            "在社区防灾演练中用扩音喇叭指导疏散路线",
            "在社区种子银行柜台登记交换番茄与向日葵种子",
            "在社区语言角用双语卡片教小朋友‘butterfly’和‘蝴蝶’",
            "在社区科技角用VR眼镜‘参观’国际空间站",
            "在社区旧衣改造工作坊剪裁牛仔裤成托特包",
            "在社区宠物友好咖啡馆用智能喂食器定时投粮",
            "在社区河岸清理行动中用长夹拾起塑料瓶与渔网",
            "在社区老年合唱团排练厅用节拍器跟唱《茉莉花》",
            "在社区智慧路灯柱旁用手机APP调节照明亮度",
            "在社区共享晾衣区用紫外线消毒灯照射婴儿衣物",
            "在社区故事角用布偶剧场演绎《龟兔赛跑》英文版",
            "在社区农艺师指导下用滴灌系统为辣椒苗供水",
            "在社区艺术疗愈室用陶土捏制减压小动物",
            "在社区数字扫盲班用大字体平板学习微信支付",
            "在社区无障碍步道上用盲杖轻敲地面辨识方向",
            "在社区旧物新生展柜前为改造的玻璃瓶花瓶贴标签",
            "在社区亲子厨房用食物模具压出星形苹果片",
            "在社区气象角读取百叶箱内温度与湿度数据",
            "在社区多语种导览屏前用手势选择西班牙语解说",
            "在社区昆虫旅馆旁用放大镜观察瓢虫爬行轨迹",
            "在社区共享钢琴角弹奏简化的《卡农》旋律",
            "在社区急救培训点用模拟人练习海姆立克急救法",
            "在社区苔藓微景观工作坊用喷雾瓶保湿鹿角蕨",
            "在社区方言保护项目中用录音笔采集阿公讲古",
            "在社区零废弃市集用蜂蜡布包裹自制燕麦饼干",
            "在社区星空观测夜用星图APP识别北斗七星",
            "在社区老年瑜伽角跟随视频做椅子辅助猫牛式",
            "在社区儿童安全教育角用AR识别交通标志含义",
            "在社区雨水收集桶旁用滤网清理落叶杂质",
            "在社区陶艺体验区用刮刀修整拉坯的茶杯口沿",
            "在社区多代同堂读书会用大字版共读《小王子》",
            "在社区植物染坊用洋葱皮煮制米色棉布",
            "在社区声景地图项目中用分贝仪记录鸟鸣分贝值",
            "在社区旧书修复角用日本纸修补泛黄童话书页",
            "在社区共享自习室用降噪耳机听英语播客",
            "在社区微型动物园用长柄勺喂食矮马",
            "在社区可持续时尚展用LED屏展示再生纤维流程",
            "在社区老年棋社用磁性象棋盘下盲棋",
            "在社区自然笔记角用彩铅绘制蒲公英种子飘散轨迹",
            "在社区数字遗产计划中扫描老照片存入云端相册",
            "在社区社区花园用蚯蚓堆肥箱处理厨余",
            "在社区手语故事会用指尖在空中拼写‘FAMILY’",
            "在社区旧物交换角用积分卡兑换手工编织坐垫",
            "在社区儿童工程角用乐高齿轮组搭建升降桥",
            "在社区生态监测站用红外相机回看貉夜间活动",
            "在社区多语种公告栏前用手机翻译功能读防疫通知",
            "在社区老年摄影班用三脚架拍摄银杏落叶特写",
            "在社区共享工具图书馆借出修枝剪与土壤测试仪",
            "在社区非遗剪纸角用刻刀在红纸上镂空‘福’字",
            "在社区零塑包装站用可重复玻璃罐装散装燕麦",
            "在社区跨代共学课堂用平板协作编辑家庭树PPT",
            "在社区城市农场用卷尺测量黄瓜藤蔓日生长长度",
            "在社区声音疗愈角用颂钵振动频率放松肩颈",
            "在社区旧物新生市集用3D打印配件修复断柄雨伞",
            "在社区社区记忆墙前为老照片添加语音注释"
        ]

        random_scene = random.choice(scenes)


        system_prompt = (
            "你是一名英语口语教学内容设计专家，"
            "擅长为“看图说话”设计稳定、可评估的教学图片。"
        )

        user_prompt = f"""
请为英语口语练习生成一份【图片语义计划】。

要求：
- 难度等级：{difficulty_level}
- 场景：{random_scene}
- 内容真实、具体、易于描述
- 不要抽象概念
- 不要出现文字、标志或品牌
- 画面元素数量适中
- 全部用英文输出

请严格按照以下 JSON 格式输出，不要添加任何多余文字：

{{
  "difficulty_level": "{difficulty_level}",
  "scene": "",
  "people": [
    {{
      "role": "",
      "appearance": "",
      "emotion": ""
    }}
  ],
  "main_actions": [],
  "key_objects": [],
  "background": ""
}}
"""

        content = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,  # 稍高一点，增加多样性
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse semantic plan JSON: {content}") from e

    # -------------------------
    # 2️⃣ 生成标准答案
    # -------------------------
    def generate_standard_answer(self, semantic_plan: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "你是一名英语口语评估专家，"
            "负责为看图说话练习生成标准答案。"
        )

        user_prompt = f"""
以下是某张教学图片的【语义计划】：

{json.dumps(semantic_plan, ensure_ascii=False, indent=2)}

请基于该语义计划，生成学习者在“看图说话”中应表达的【标准事实要点】。

要求：
- 只描述图片中明确可见的内容
- 不加入推测或背景故事
- 使用自然、简单的英文
- 适合 {semantic_plan.get("difficulty_level")} 水平
- 3 到 5 条要点

请严格按照以下 JSON 格式输出，不要添加任何多余文字：

{{
  "key_facts": [],
  "recommended_vocab": [],
  "example_full_answer": ""
}}
"""

        content = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,  # 标准答案要稳
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse standard answer JSON: {content}") from e

    # -------------------------
    # 3️⃣ 对用户的口语练习进行评估
    # -------------------------
    def evaluate_practice(
        self,
        semantic_plan: dict,
        standard_answer: str,
        user_text: str
    ) -> dict:
        """
        对用户口语（ASR 文本）进行语义 + 流畅度分析
        """

        system_prompt = (
            "你是一名英语口语评估专家，用户根据一张图片描述里其中的内容。"
            "请根据用户语音转录的文字和图片，对用户的描述给予细节评价和改进方向。"
        )
            
        user_prompt = f"""
【图片语义信息】
{json.dumps(semantic_plan, ensure_ascii=False)}

【标准参考描述】
{standard_answer}

【用户口语转写文本】
{user_text}

请你完成以下任务：
1. 判断用户的描述内容与图片语义的匹配程度（是否说对了主要人物、行为、场景）。
2. 判断用户英语表达的流畅度和自然程度（语法、用词、句子是否自然）。
3. 指出用户描述中缺失或不准确的关键信息。
4. 给出具体、可执行的改进建议，适合英语学习者理解。
5. 回答使用中文，但是在具体建议部分，用“标准参考描述”里的英文原文。

【评分要求】
- relevance_score：0-100，表示内容相关性
- fluency_score：0-100，表示语言流畅度

【返回格式要求】
你必须只返回一个 JSON，对象格式如下，不要输出任何额外说明文字：

{{
  "relevance_score": 0,
  "fluency_score": 0,
  "summary": "",
  "strengths": [],
  "issues": [],
  "suggestions": []
}}
"""

        content = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse practice evaluation JSON: {content}") from e