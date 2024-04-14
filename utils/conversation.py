import tiktoken
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List
from openai import OpenAI

from utils.logger_config import create_logger

LOGGER = create_logger('../logs/app.log', __name__)

_ = load_dotenv((find_dotenv()))


class Conversation:
    def __init__(self, system_prompt: str, model: str = "gpt-4-0613", tool_choice: str ="auto", max_tokens=256,
                 functions: List = None, temperature: float = 0):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.system_prompt = system_prompt
        self.messages = []
        self.model = model
        self.functions = functions
        self.tool_choice = tool_choice
        if system_prompt:
            self.add_sys_prompt()
        self.usage = {}
        self.response = {}
        self.max_tokens = max_tokens
        self.temperature = temperature

    def add_sys_prompt(self):
        return self.messages.append({"role": "system", "content": self.system_prompt})

    def add_user_message(self, message):
        return self.messages.append({"role": "user", "content": message})

    def send_completion_request(self):
        LOGGER.info(
            f"Sending completion request to chatGPT with the following:\n "
            f"Message: {json.dumps(self.messages, indent=4)}\n"
            f"Model: {self.model}\n"
            f"Tools: {self.functions}\n"
            f"ToolChoice: {self.tool_choice}\n"
        )
        res = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.functions,
            tool_choice=self.tool_choice,
            temperature=self.temperature,
            top_p=0,
            max_tokens=self.max_tokens
        )
        self.usage = res.usage.model_dump()
        self.response = res.choices[0].message.model_dump()  # Returns dictionary
        if not self.response.get('function_call'):
            self.response.pop('function_call')
        LOGGER.info(f"chatGPT responded: {json.dumps(self.response, indent=4)}")
        # each time we get a response back, we need to add the message to the context
        self.messages.append(self.response)
        return self.response