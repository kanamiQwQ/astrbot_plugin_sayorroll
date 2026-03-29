import re
import random
import difflib
import string
import unicodedata
from astrbot.api.all import *
from astrbot.api.event import AstrMessageEvent
from astrbot.api.event.filter import command, regex
from astrbot.api.star import Context, Star, register

@register("sayoroll", "mas-alone", "随机数字或随机事件", "1.0.0")
class SayoRoll(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    def normalize_str(self, s: str) -> str:
        return unicodedata.normalize('NFKC', s)
    @regex(r"^(.*?)概率$")
    async def on_probability(self, event: AstrMessageEvent):
        """处理后缀为“概率”的消息"""
        user_input = event.message_str.strip()

        replaced_input = user_input.replace('我', '你')
        probability = random.uniform(0.01, 100.00)
        msg = f'{replaced_input}为：{probability:.2f}%'
        yield event.plain_result(msg)

    @command("roll")
    async def on_roll(self, event: AstrMessageEvent, message: str = ""):
        """处理 /roll 指令"""
        args_text = message.strip()
        if not args_text:
            msg = f'{random.randint(1, 100)}'
            
        elif args_text.isdigit():
            num = int(args_text)
            if num > 99999:
                msg = '数字太大了，你真的需要这么大的随机数吗？'
            else:
                msg = f'{random.randint(1, num)}'
                
        elif re.search(r'([\u4e00-\u9fff])[不没].*?\1(.*?)', args_text):
            result = re.search(r'([\u4e00-\u9fff])[不没].*?\1(.*?)', args_text)
            options = [result.group()[:1], result.group()[1:]]
            
            first_params = args_text[:result.span()[0]].replace('我', 'temp').replace('temp', '你')
            second_params = args_text[result.span()[1]:].replace('我', 'temp').replace('temp', '你')
            
            similarity = difflib.SequenceMatcher(None, first_params.lower(), second_params.lower()).ratio()
            if similarity > 0.8:
                msg = f'总共就{len(options)}个参数..还这么相似..怎么roll都一样啊'
            else:
                msg = '我觉得' + first_params + random.choice(options) + second_params
                
        elif re.search(r'(.+)还是(.+)', args_text):
            options = re.split(r'还是', args_text)
            similarity = difflib.SequenceMatcher(None, options[0].lower(), options[1].lower()).ratio()
            if similarity > 0.8:
                msg = '总共就2个参数..还这么相似..怎么roll都一样啊'
            else:
                msg = f'当然是{random.choice(options)}咯'
                msg = msg.replace('我', 'temp').replace('temp', '你')
                
        else:
            args_text = self.normalize_str(args_text)
            args_without_punctuation = args_text.translate(str.maketrans('', '', string.punctuation))
            
            if len(args_without_punctuation.split(' ')) == 1:
                msg = '未匹配到参数！'
            else:
                options = [x for x in args_text.split(' ') if x.strip()]
                if len(options) > 1:
                    similarities = [
                        difflib.SequenceMatcher(None, option1.lower(), option2.lower()).ratio() 
                        for i, option1 in enumerate(options) 
                        for option2 in options[i+1:]
                    ]
                    if any(similarity > 0.8 for similarity in similarities):
                        msg = f'总共就{len(options)}个参数..还这么相似..怎么roll都一样啊'
                    else:
                        msg = f'当然是{random.choice(options)}咯'
                else:
                    msg = '未匹配到参数！'

        yield event.plain_result(msg)