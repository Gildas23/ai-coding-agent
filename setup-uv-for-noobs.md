windows
install python then
winget install --id=astral-sh.uv -e
or
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh | iex"
or
winget install --id=astral-sh.uv -e

on mac / linux
curl -LsSf https://astral.sh | sh

exclusively on mac if you have home brew
brew install uv

uv python pin [ the version e.g 3.12 ]

to run your code
Set your OpenAI API key in the environment first.

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

On macOS or Linux, use:

```sh
export OPENAI_API_KEY="your-api-key"
```

Then run the app:

```sh
uv run main
```

If the API key is missing, the app explains how to set it and exits without
starting. If an API request or tool fails, it reports the error and lets you
try another prompt.
