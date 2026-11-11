# Mini AI Coding Agent

A small command-line AI assistant that can answer questions and help with
files and shell commands on your computer. It uses OpenAI's API and keeps
running so you can have a conversation until you type `exit` or `quit`.

## What it can do

- Answer prompts using an OpenAI GPT-4 model.
- List files in a directory and read or write text files.
- Run a shell command only after you confirm it.
- Keep the conversation going across multiple prompts.
- Report missing API keys and recoverable errors without abruptly ending the chat.

> **Use care:** The assistant can read and write files and run shell commands.
> Review each command before approving it, and only use the assistant in
> directories and environments where you are comfortable granting that access.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- An OpenAI API key

## Run the app

Open a terminal in the project directory and set your API key for the current
terminal session.

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

**macOS or Linux**

```sh
export OPENAI_API_KEY="your-api-key"
```

Then install the project dependencies and start the assistant:

```sh
uv sync
uv run main
```

Enter a prompt when you see `You:`. Type `exit` or `quit` to end the session.
The API key is not stored by the app; do not commit it to the repository.

## Project structure

```text
src/
  ai_agent.py                    # Agent, file helpers, command helper, and tool schemas
  mini_ai_coding_agent/
    __init__.py                  # Application entry point
```"# ai-coding-agent" 
