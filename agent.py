import os
import json
from typing import Optional, Any, Dict, Callable
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, DEFAULT_MODEL, SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS, TOOL_DECLARATIONS

class VoiceAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key: Optional[str] = api_key or os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
        self.model: str = model
        self.client: Optional[genai.Client] = genai.Client(api_key=self.api_key) if self.api_key else None

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    async def run_agent_step(self, user_instruction: str, on_log_callback: Optional[Callable] = None) -> str:
        if not self.client:
            return "Please enter your Gemini API Key in the top right box and click Save."

        if on_log_callback:
            await on_log_callback("thought", f"Analyzing command: '{user_instruction}'")

        prompt = f"System Context:\n{SYSTEM_PROMPT}\n\nUser Request:\n{user_instruction}"

        try:
            # Use SDK chat session for automatic history and tool management
            chat = self.client.chats.create(
                model=self.model,
                config=types.GenerateContentConfig(
                    tools=TOOL_DECLARATIONS,
                    temperature=0.4
                )
            )

            response = chat.send_message(prompt)

            # Handle autonomous tool calls
            while response.function_calls:
                for call in response.function_calls:
                    # pyrefly: ignore [unnecessary-type-conversion]
                    fn_name: str = str(call.name or "")
                    fn_args: Dict[str, Any] = dict(call.args) if call.args else {}

                    if on_log_callback:
                        await on_log_callback("tool_call", f"⚡ Running `{fn_name}`: {json.dumps(fn_args)}")

                    if fn_name in TOOL_FUNCTIONS:
                        tool_fn = TOOL_FUNCTIONS[fn_name]
                        # pyrefly: ignore [unnecessary-type-conversion]
                        result: str = str(tool_fn(**fn_args))
                    else:
                        result = f"Error: Tool '{fn_name}' not found."

                    if on_log_callback:
                        await on_log_callback("tool_result", f"Result: {result[:250]}")

                    # Feed tool execution result back to the model
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name=fn_name,
                            response={"result": result}
                        )
                    )

            return response.text or "Task completed successfully."
        except Exception as e:
            return f"Execution error: {str(e)}"
