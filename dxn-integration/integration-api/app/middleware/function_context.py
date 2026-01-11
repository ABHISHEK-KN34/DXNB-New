from dataclasses import dataclass

@dataclass
class FunctionContext:
    function_name: str
    invocation_id: str
    function_directory: str