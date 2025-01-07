from abc import ABC, abstractmethod


class FunctionInterface(ABC):

    @abstractmethod
    def call_functions(self, function_calls_section_text: str) -> str:
        pass

    @abstractmethod
    def get_formatted_list_of_functions(self) -> str:
        pass
