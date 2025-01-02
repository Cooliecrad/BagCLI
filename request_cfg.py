import requests
import argparse as ap
import base_cli
import os


class PromptRequest(base_cli.BaseCLI):
    def __init__(self, context, parser = None):
        super().__init__(context)
        self.__task_id = ""
        self.__urls = []

        self.__parser = parser if parser else ap.ArgumentParser()

        self.__parser.add_argument("-r", "--request", action="store_true",
                                   help = "请求文生图，保存文生图的task_id")

        self.__parser.add_argument("-loadi", "--load_id", action="store_true",
                                   help="从指定文件加载task_id")
        self.__parser.add_argument("--taskid", action="store_true",
                                   help = "返回当前的task_id")

        self.__parser.add_argument("-ret", "--response", action="store_true",
                                   help = "获得task_id的结果，保存生成图像的URL")

        self.__parser.add_argument("-loadu", "--load_urls", action="store_true",
                                   help = "从指定文件加载URL列表")
    
        self.__parser.add_argument("-dl", "--download_image", action="store_true",
                                   help = "下载URL列表指向的图像")

    def get_apikey(self):
        ret = os.getenv("QWEN_APIKEY")
        if ret is None:
            raise Exception("缺少环境变量QWEN_APIKEY")
        return ret

    def request_generate_image(self, prompt) -> str:
        """
        生成图像，返回图像的task_id
        """
        api_key = self.get_apikey()
        api_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'X-DashScope-Async': 'enable',
        }

        data_input = {"prompt": prompt["prompt"]}
        data_param = {}

        if prompt["negative"] is not None:
            data_input["negative_prompt"] = prompt["negative"]
        if prompt["ref_img"] is not None:
            data_input["ref_img"] = prompt["ref_img"]

        if prompt["style"] is not None:
            data_param["style"] = prompt["style"]
        if prompt["ref_strength"] is not None:
            data_param["ref_strength"] = prompt["ref_strength"]
        if prompt["ref_mode"] is not None:
            data_param["ref_img"] = prompt["ref_mode"]

        data = {
            "model": prompt["model"],
            "input": data_input,
            "parameters": data_param
        }

        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            self.__task_id = result.get("output")['task_id']

            filename = f"{self.context}.id"
            with open(filename, "w", encoding='utf-8') as fp:
                fp.write(self.__task_id)
            print(f"已保存任务ID到{filename}")

            return self.__task_id

        return ""

    def taskid(self, _):
        print(f"当前任务ID: {self.__task_id}")

    def load_id(self, _):
        filename = f"{self.context}.id"
        try:
            with open(filename, "r", encoding='utf-8') as fp:
                self.__task_id = fp.read()
        except FileNotFoundError:
            print(f"无法打开文件 '{filename}'")

    def __get_response(self) -> tuple[str, list[str]]:
        """

        Args:
            task_id (_type_): _description_
            output_prefix (_type_): _description_

        Returns:
            list[str]: _description_
        """
        api_key = self.get_apikey()
        api_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{self.__task_id}'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'X-DashScope-Async': 'enable',
        }

        response = requests.get(api_url, headers=headers)

        status = "REQUEST_FAILED"
        if response.status_code == 200:
            output = response.json().get("output")
            if output is not None:
                status = output["task_status"]
                if status == "SUCCEEDED":
                    img_result = output["results"]
                    ret = [ result["url"] for result in img_result]
                    return status, ret

        return status, []

    def response(self, _):
        status, urls = self.__get_response()
        print(f"task_id: '{self.__task_id}', status: {status}")
        if status == "SUCCEEDED":
            self.__urls = urls
            
            print("URLs:")
            for x in urls:
                print(f"\t{x}")

            filename = f"{self.context}.result"
            with open(filename, "w", encoding='utf-8') as fp:
                fp.write(str(urls))
            print(f"已保存图片URL到{filename}")

    def load_urls(self, _):
        filename = f"{self.context}.result"
        try:
            with open(filename, "r", encoding='utf-8') as fp:
                self.__urls = eval(fp.read())
        except FileNotFoundError:
            print(f"无法打开文件 '{filename}'")

    def download_image(self, _):
        for index, url in enumerate(self.__urls):
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

            filename = f"{self.context}_{index}.jpg" 
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"成功下载图片，保存为{filename}")
