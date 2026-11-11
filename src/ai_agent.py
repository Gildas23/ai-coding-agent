import json
import os
import subprocess
from pathlib import Path
from typing import Any

MODEL = "gpt-4"
MAX_TOOL_ROUNDS = 8
SYSTEM_PROMPT = (
    "You are a helpful assistant. Give concise, accurate answers, "
    "and explain your responses clearly. Use the provided tools when needed. "
    "Ask for confirmation before running shell commands. If a tool reports an "
    "error, explain it and suggest a safe next step."
)


def run_agent() -> None:
    """Keep chatting with the agent until the user enters 'exit' or 'quit'."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print(
            "OPENAI_API_KEY is not set. Set your OpenAI API key in the "
            "environment, then run the app again."
        )
        return

    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        print("The OpenAI package is missing. Install the project dependencies with `uv sync`.")
        return

    try:
        client = OpenAI(api_key=api_key)
    except OpenAIError as error:
        print(f"Could not initialize the OpenAI client: {error}")
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            return
        if not prompt:
            print("Please enter a prompt, or type 'exit' to quit.")
            continue

        prompt_start = len(messages)
        messages.append({"role": "user", "content": prompt})

        try:
            for _ in range(MAX_TOOL_ROUNDS):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )
                if not response.choices:
                    raise RuntimeError("The model returned no choices.")

                message = response.choices[0].message
                if not message.tool_calls:
                    if message.content is None:
                        raise RuntimeError("The model returned no response text.")
                    print(f"Agent: {message.content}")
                    messages.append({"role": "assistant", "content": message.content})
                    break

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            tool_call.model_dump(exclude_none=True)
                            for tool_call in message.tool_calls
                        ],
                    }
                )
                for tool_call in message.tool_calls:
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                        if not isinstance(arguments, dict):
                            raise ValueError("Tool arguments must be a JSON object.")
                        result = run_tool(tool_call.function.name, arguments)
                        result_text = (
                            result if isinstance(result, str) else json.dumps(result)
                        )
                    except (
                        json.JSONDecodeError,
                        EOFError,
                        OSError,
                        subprocess.SubprocessError,
                        TypeError,
                        ValueError,
                    ) as error:
                        result_text = f"Tool error: {error}"

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        }
                    )
            else:
                raise RuntimeError(
                    f"The model exceeded the {MAX_TOOL_ROUNDS}-round tool limit."
                )
        except KeyboardInterrupt:
            del messages[prompt_start:]
            print("\nRequest canceled. You can try another prompt or type 'exit'.")
        except (OpenAIError, RuntimeError, TypeError) as error:
            del messages[prompt_start:]
            print(f"Request failed: {error}\nYou can try another prompt.")

def list_files_in_directory(directory: str) -> list[str]:
    """List files directly inside a directory."""
    return [
        path.name
        for path in Path(directory).iterdir()
        if path.is_file()
    ]


def read_file(file_path: str) -> str:
    """Read a UTF-8 text file."""
    return Path(file_path).read_text(encoding="utf-8")


def write_file(file_path: str, content: str) -> str:
    """Write text to a UTF-8 file."""
    Path(file_path).write_text(content, encoding="utf-8")
    return f"Saved {file_path}"


def run_command(command: str) -> str:
    """Run a shell command only after the user confirms it."""
    confirmation = input(f"Run this command? {command!r} (yes/no): ").strip().lower()
    if confirmation != "yes":
        return "Command execution canceled by user."

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout
    if result.stderr:
        output = f"{output}\n{result.stderr}".strip()
    if result.returncode:
        output = f"Command exited with status {result.returncode}.\n{output}".strip()
    return output or "Command completed with no output."


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files_in_directory",
            "description": "List files directly inside a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Path to the directory to list.",
                    }
                },
                "required": ["directory"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read.",
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text to a UTF-8 file, replacing its contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text to write to the file.",
                    },
                },
                "required": ["file_path", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command. The user must confirm before it executes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run.",
                    }
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    },
]

TOOL_INSTANCES: dict[str, Any] = {
    "list_files_in_directory": list_files_in_directory,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

def run_tool(name: str, arguments: dict[str, Any]) -> object:
    """Call a tool function by name with the provided arguments."""
    name = name.lower()
    print(f"Calling tool: {name} with arguments: {arguments}") 
    if name not in TOOL_INSTANCES:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_INSTANCES[name](**arguments)