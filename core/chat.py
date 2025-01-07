from typing import Iterator

from core.function_interface import FunctionInterface
from core.functions import Functions
from lm.base_lm_client import BaseLMClient
from lm.cerebras_lm_client import CerebrasLMClient


class Chat:

    def __init__(self):
        self.lm_client: BaseLMClient = CerebrasLMClient()
        self.functions: FunctionInterface = Functions()
        self.conversation: list[dict[str, str]] = [
            {
                "role": "system",
                "content": self.get_system_prompt()
            }
        ]

    def send_user_message(self, user_message: str, stream: bool = False) -> str | Iterator[str]:
        message: str = f"Message from User:\n```\n{user_message}\n```"
        if stream:
            for response_chunk in self.send_message(message=message, stream=True):
                yield response_chunk
        else:
            return self.send_message(message=message, stream=False)

    def send_message(self, message: str, stream: bool = False) -> str | Iterator[str]:
        self.conversation.append(
            {
                "role": "user",
                "content": message
            }
        )
        markdown_sections: dict = {}
        if stream:
            response_to_user: str = ""
            response_to_user_chunk: str = ""
            for response_chunk in self.lm_client.do_streaming_chat_completion(messages=self.conversation):
                if self.conversation[-1]["role"] == "assistant":
                    self.conversation[-1]["content"] = self.conversation[-1]["content"] + response_chunk
                    markdown_sections = self.parse_markdown_sections(self.conversation[-1]["content"])
                    if "Response to User" in markdown_sections:
                        response_to_user_chunk: str = self.get_text_after(markdown_sections["Response to User"], response_to_user)
                        response_to_user = markdown_sections["Response to User"]
                else:
                    self.conversation.append(
                        {
                            "role": "assistant",
                            "content": response_chunk
                        }
                    )
                    markdown_sections = self.parse_markdown_sections(response_chunk)
                    if "Response to User" in markdown_sections:
                        response_to_user_chunk: str = self.get_text_after(markdown_sections["Response to User"], response_to_user)
                        response_to_user = markdown_sections["Response to User"]
                if not response_to_user_chunk == "" and not response_to_user_chunk[-1] == "#":
                    yield response_to_user_chunk
            if "Function Calls" in markdown_sections and markdown_sections["Function Calls"].strip() != "" and markdown_sections["Function Calls"].strip() != "None" and markdown_sections["Function Calls"].strip() != "\"None\"":
                function_calls_response: str = self.functions.call_functions(markdown_sections["Function Calls"])
                for response_chunk in self.send_message(message=function_calls_response, stream=True):
                    yield response_chunk
        else:
            response: str = self.lm_client.do_chat_completion(messages=self.conversation)
            self.conversation.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )
            markdown_sections = self.parse_markdown_sections(self.conversation[-1]["content"])
            response_to_user: str = ""
            if "Response to User" in markdown_sections:
                response_to_user = markdown_sections["Response to User"]
            if "Function Calls" in markdown_sections:
                function_calls_response: str = self.functions.call_functions(markdown_sections["Function Calls"])
                return self.send_message(message=function_calls_response, stream=False)
            return response_to_user

    def get_system_prompt(self) -> str:
        return f"""You are a helpful assistant built into an alarm clock. You are responsible for managing all the functions that the alarm clock supports. When conversing with the user, you have a uniquely exciting, warm and colloquial conversation style.

Your job is to always determine whether any of the below given functions need to be called given the request from the user. First, write a response to the user. If you need to call a function, just tell the user in a single short sentence to wait for a second. If you want to call a function, then write the function call in the given YAML format. If you don't want to call a function, then leave "Function Calls" section away entirely or just write "None" in it. You have the following functions available:
```
{self.functions.get_formatted_list_of_functions()}
```

ALWAYS respond ONLY using EXACTLY the following format:
```
## Thinking

[Think here about what the user has said, what you should respond and whether you have to use one of the available functions. For complex tasks, such as tasks requiring reasoning or calculation, use this space as a scratchpad to dissect the task and solve it step by step.]

## Response to User

[Respond to the user here is a uniquely exciting, warm and colloquial conversation style. If you want to call one or multiple functions, announce it to the user in a single short sentence, e.g. by saying "Sure, I will create a timer of 10 minutes for you."]

## Function Calls (optional)

- function_name: [Provide the name of the function here]
  parameters:
    [Name of parameter]: [Value]
    [Name of parameter]: [Value]
  ...
```"""

    @staticmethod
    def parse_markdown_sections(markdown_text: str) -> dict:
        sections: dict = {}
        lines: list[str] = markdown_text.strip().split('\n')
        current_section: str | None = None
        current_content: list[str] = []
        for line in lines:
            if line.startswith('## '):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = line[3:].strip()
            elif current_section and line.strip():
                current_content.append(line)
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        return sections

    @staticmethod
    def get_text_after(full_string: str, search_text: str) -> str:
        if search_text is None or search_text == "":
            return full_string
        try:
            return full_string.split(search_text, 1)[1]
        except IndexError:
            return ""
