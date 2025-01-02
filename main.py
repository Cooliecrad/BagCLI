import argparse as ap
from prompt_cfg import Prompt
from request_cfg import PromptRequest
import base_cli


class Manager:
    def __init__(self, context="global"):
        self.parser = ap.ArgumentParser(exit_on_error=False)
        sp = self.parser.add_subparsers(dest="subcommand", help="子命令")

        ctx_parser = sp.add_parser("ctx", help="上下文管理")
        pmt_parser = sp.add_parser("pmt", help="prompt设置")
        req_parser = sp.add_parser("req", help="文生图请求管理")

        self.__ctx = base_cli.ContextConfig(context, ctx_parser)
        self.__subp = {
            "ctx": self.__ctx,
            "pmt": Prompt(self.__ctx, pmt_parser),
            "req": PromptRequest(self.__ctx, req_parser),
        }

    @property
    def context(self) -> str:
        return str(self.__ctx)

    def parse(self, args):
        args = self.parser.parse_args(args)
        
        if hasattr(args, "subcommand"):
            subc = args.subcommand
            self.__subp[subc].parse_args(args)

        if hasattr(args, "request") and args.request:
            self.__subp["req"].request_generate_image(self.__subp["pmt"].params)


if __name__ == "__main__":
    mng = Manager()
    while True:
        try:
            cmd = input(f"\n({mng.context}) ").split()
            if len(cmd) > 0:
                mng.parse(cmd)
        except SystemExit as ex:
            pass
        except KeyboardInterrupt as ex:
            break
        except EOFError as ex:
            break