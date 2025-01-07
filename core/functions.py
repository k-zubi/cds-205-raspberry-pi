from typing import Callable
from datetime import datetime
import yaml
import threading
import time
import pygame
from pathlib import Path
import os


from core.function_interface import FunctionInterface


class AlarmState:
    def __init__(self):
        self.alarm_time: str | None = None
        self.is_enabled: bool = False
        self.is_playing: bool = False
        self.monitor_thread: threading.Thread | None = None

        pygame.mixer.init()
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.alarm_sound = pygame.mixer.Sound(str(script_dir / "alarm.mp3"))


class FunctionParameter:
    def __init__(self, name: str, description: str, required: bool = False):
        self.name: str = name
        self.description: str = description
        self.required: bool = required


class Function:
    def __init__(self,
                 reference: Callable[[dict[str, object]], str],
                 description: str,
                 parameters: list[FunctionParameter] | None = None):
        self.reference: Callable[[dict[str, object]], str] = reference
        self.description: str = description
        self.parameters: list[FunctionParameter] | None = parameters


class Functions(FunctionInterface):

    def __init__(self):
        super().__init__()
        self.functions: list[Function] = [
            Function(
                reference=self.get_current_datetime,
                description="Get the current date and time"
            ),
            Function(
                reference=self.enable_alarm,
                description="Enable the alarm at a specific time",
                parameters=[
                    FunctionParameter(
                        name="time",
                        description="Provide the time here in exactly the \"HH:MM\" military time format without AM/PM as a string.",
                        required=True
                    )
                ]
            ),
            Function(
                reference=self.disable_alarm,
                description="Disable the alarm"
            ),
            Function(
                reference=self.check_alarm,
                description="Check whether and at which time the alarm is enabled"
            )
        ]
        self.alarm_state = AlarmState()

    def call_functions(self, function_calls_section_text: str) -> str:
        try:
            parsed_function_calls = yaml.safe_load(function_calls_section_text.strip())
            if not isinstance(parsed_function_calls, list):
                return "Failed to parse 'Function Calls'. Make sure to use proper parseable YAML!"
            function_responses: str = ""
            for function_call in parsed_function_calls:
                if not isinstance(function_call, dict):
                    return "Failed to parse 'Function Calls': Each entry must be a dictionary. Make sure to use proper parseable YAML!"
                function_name: str | None = function_call.get("function_name")
                if not function_name:
                    return "Failed to parse 'Function Calls': Missing 'function_name'. Make sure to use proper parseable YAML!"
                function: Function | None = self.get_function_by_name(function_name)
                if not function:
                    return f"Function '{function_name}' could not be found. Make sure to only use the available functions given!"
                parameters: dict[str, object] = function_call.get("parameters") or {}
                print(f"Calling function '{function.reference.__name__}' with parameters '{str(parameters)}' ...")
                function_return_value: str = function.reference(parameters)
                function_responses += f"Response from Function '{function.reference.__name__}':\n```\n{function_return_value}\n```\n\n"
            print(function_responses.strip())
            return function_responses.strip()
        except yaml.YAMLError as e:
            return f"Failed to parse 'Function Calls': {str(e)}. Make sure to use proper parseable YAML!"

    def get_formatted_list_of_functions(self) -> str:
        formatted_list: str = ""
        for function in self.functions:
            formatted_list += f"- function_name: {function.reference.__name__} # {function.description}\n"
            if not function.parameters is None and not function.parameters == []:
                formatted_list += f"parameters:\n"
                for parameter in function.parameters:
                    if parameter.required:
                        required_hint: str = "Required"
                    else:
                        required_hint: str = "Optional"
                    formatted_list += f"{parameter.name}: # {parameter.description} ({required_hint})\n"
        return formatted_list

    def get_function_by_name(self, function_name: str) -> Function | None:
        for function in self.functions:
            if function.reference.__name__ == function_name:
                return function
        return None

    @staticmethod
    def get_current_datetime(parameters: dict[str, object]) -> str:
        return str(datetime.now())

    def monitor_alarm(self):
        while self.alarm_state.is_enabled:
            current_time = datetime.now().strftime("%H:%M")
            if current_time == self.alarm_state.alarm_time and not self.alarm_state.is_playing:
                # Start alarm in a separate thread
                alarm_thread = threading.Thread(target=self.play_alarm)
                alarm_thread.start()
            time.sleep(1)  # Check every second

    def play_alarm(self):
        self.alarm_state.is_playing = True
        self.alarm_state.alarm_sound.play(1)  # Number of repetitions to play
        self.alarm_state.alarm_sound.stop()
        self.alarm_state.is_playing = False

    def enable_alarm(self, parameters: dict[str, object]) -> str:
        try:
            alarm_time = str(parameters.get("time", ""))
            datetime.strptime(alarm_time, "%H:%M")

            if self.alarm_state.monitor_thread and self.alarm_state.monitor_thread.is_alive():
                self.alarm_state.is_enabled = False
                self.alarm_state.monitor_thread.join()

            self.alarm_state.alarm_time = alarm_time
            self.alarm_state.is_enabled = True

            self.alarm_state.monitor_thread = threading.Thread(target=self.monitor_alarm)
            self.alarm_state.monitor_thread.daemon = True  # Thread will stop when main program exits
            self.alarm_state.monitor_thread.start()

            return f"Alarm enabled for {alarm_time}"
        except ValueError:
            return "Invalid time format. Please use HH:MM format (e.g., 09:30)"
        except Exception as e:
            return f"Error enabling alarm: {str(e)}"

    def disable_alarm(self, parameters: dict[str, object]) -> str:
        try:
            if self.alarm_state.is_enabled:
                self.alarm_state.is_enabled = False
                if self.alarm_state.monitor_thread:
                    self.alarm_state.monitor_thread.join()
                self.alarm_state.alarm_time = None
                return "Alarm disabled successfully"
            return "Alarm was already disabled"
        except Exception as e:
            return f"Error disabling alarm: {str(e)}"

    def check_alarm(self, parameters: dict[str, object]) -> str:
        if self.alarm_state.is_enabled:
            return f"Alarm is enabled for {self.alarm_state.alarm_time}"
        return "No alarm is currently enabled"
