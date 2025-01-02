import json
import argparse as ap
import sys
import pprint
from functools import partial
import base_cli

ARGUMENTS = {
    "model": {
        "wanx-v1": "万相大模型"
    },
    "prompt": "str",
    "negative": "str",
    "ref_img": "URL",
    "style": {
        "<auto>": "默认值，由模型随机输出图像风格",
        "<photography>": "摄影",
        "<portrait>": "人像写真",
        "<3d_cartoon>": "3D卡通",
        "<anime>": "动画",
        "<oil_painting>": "油画",
        "<watercolor>": "水彩",
        "<sketch>": "素描",
        "<chinese> painting": "中国画",
        "<flat_illustration>": "扁平插画"
    },
    "ref_strength": "float",
    "ref_mode": {
        "repaint": "默认值，基于参考图的内容生成图像",
        "refonly": "基于参考图的风格生成图像"
    }
}


class Prompt(base_cli.BaseCLI):
    def __init__(self, context = base_cli.ContextConfig, parser = None):
        super().__init__(context)
        
        self.params = {
            "model": "wanx-v1",
            "prompt": "绘制在香包上的图样",
            "negative": None,
            "ref_img": None,
            "style": None,
            "ref_strength": None,
            "ref_mode": None
        }
        self.parser = parser if parser else ap.ArgumentParser()

        self.parser.add_argument("--savep", action="store_true",
                                   help = "保存当前的prompt")
        self.parser.add_argument("--loadp",
                                   help="从指定文件加载prompt")
        self.parser.add_argument("-lp", "--list_prompt", action="store_true",
                                   help="返回所有可用设置的参数")
        self.parser.add_argument("-qp", "--query_prompt",
                                   help="返回特定参数所设置的值")
        self.parser.add_argument("-m", "--model",
                                   help = "设置使用的文生图模型")
        self.parser.add_argument("-p", "--prompt",
                                   help = "设置使用的提示词")
        self.parser.add_argument("-n", "--negative",
                                   help = "设置使用的反向提示词")
        self.parser.add_argument("-s", "--style",
                                   help = "设置图像的风格")
        self.parser.add_argument("-ri", "--ref_img",
                                   help = "设置参考图像的URL地址")
        self.parser.add_argument("-rs", "--ref_strength", type=float,
                                   help = "设置参考图像的相似度(0~1)")
        self.parser.add_argument("-rm", "--ref_mode",
                                   help = "设置基于参考图生成图像的模式")
        # 枚举类参数
        for arg in ["model", "style", "ref_mode"]:
            setattr(self, arg, partial(self.set_value_enum, arg))

        # 非枚举类
        for arg in ['prompt', 'negative', 'ref_img', "ref_strength"]:
            setattr(self, arg, partial(self.set_value, arg))

    def save(self, _):
        with open(str(self.context)+'.i', 'w', encoding='utf-8') as fp:
            json.dump(self.params, fp)

    def load(self, load):
        try:
            with open(load, "r") as fp:
                self.params = json.load(fp)
        except FileNotFoundError as e:
            print(f"无法打开文件 '{str(self.context)}.prompt'")

    def list_prompt(self, _):
        pprint.pprint(ARGUMENTS)

    def query_prompt(self, name):
        ret = self.params.get(name)
        if ret is None:
            print(f"无效的参数名称{name}")
        else:
            print(f"{name}: {ret}")

    def set_value_enum(self, _key, value):
        value = value.replace("_", " ")
        if value in ARGUMENTS[_key]:
            self.params[_key] = value
        else:
            print(f"参数'{_key}'值错误, 值为'{value}', 预期为 {list(ARGUMENTS[_key].keys())}")

    def set_value(self, _key, value):
        self.params[_key] = value

            
if __name__ == "__main__":
    prompt = Prompt("global")
    argv = sys.argv[1:]
    while len(argv) < 1:
        ret = input().split()
        for arg in ret:
            if arg != '':
                argv.append(arg)

    prompt.parse_args(argv)