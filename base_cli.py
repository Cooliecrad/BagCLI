class BaseCLI:
    def __init__(self, context):
        self.context = context
    
    def parse_args(self, args):
        for k, v in args._get_kwargs():
            if v and hasattr(self, k):
                getattr(self, k)(v)

    def set_context(self, context: str):
        """设置上下文

        Args:
            context (str): 上下文名称
        """
        self.context = context