import argparse as ap

class ContextConfig:
    def __init__(self, context, parser = None):
        self.__context = context
        self.parser = parser if parser else ap.ArgumentParser()
        self.parser.add_argument("context", help="上下文名称")

    def __str__(self):
        return self.__context

    def set_context(self, ctx):
        self.__context = ctx
        
    def parse_args(self, value):
        self.__context = value.context


class BaseCLI:
    def __init__(self, context: ContextConfig):
        self.context = context
    
    def parse_args(self, args):
        for k, v in args._get_kwargs():
            if v and hasattr(self, k):
                getattr(self, k)(v)
                
