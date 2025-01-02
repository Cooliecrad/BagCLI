
import argparse as ap
import sys
import os
from prompt_cfg import Prompt
from request_cfg import PromptRequest
import base_cli


class Manager(base_cli.BaseCLI):
    def __init__(self, context="global"):
        super().__init__(context)

        self.context = context
        self.__parser = ap.ArgumentParser(exit_on_error=False)
        self.__parser.add_argument("-c", "--context", help="设置上下文")

        sp = self.__parser.add_subparsers(title="pmt", description="prompt设置")
        pmt = sp.add_parser("pmt", help="prompt设置")
        req = sp.add_parser("req", help="文生图请求管理")

        self.__pmt = Prompt(self.context, pmt)
        self.__req = PromptRequest(self.context, req)
        self.__subparsers: list[base_cli.BaseCLI] = [
            self.__pmt, self.__req
        ]

    def set_context(self, context):
        self.context = context
        for p in self.__subparsers:
            p.set_context(context)

    def parse(self, args):
        args = self.__parser.parse_args(args)

        if args.context:
            self.set_context(args.context)
        if args.request:
            self.__req.request_generate_image(self.__pmt.params)

        for p in self.__subparsers:
            p.parse_args(args)


if __name__ == "__main__":
    mng = Manager()
    while True:
        try:
            cmd = input(f"({mng.context}) ").split()
            mng.parse(cmd)
        except SystemExit as ex:
            pass
        except KeyboardInterrupt as ex:
            break
        except EOFError as ex:
            break