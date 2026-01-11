from starlette.requests import Request

from app.middleware.function_context import FunctionContext


def function_context(request: Request) -> FunctionContext:
    return FunctionContext(
        function_name=request.scope["azure_functions.function_name"],
        invocation_id=request.scope["azure_functions.invocation_id"],
        function_directory=request.scope["azure_functions.function_directory"]
    )