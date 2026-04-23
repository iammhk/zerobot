# CLI Reference

| Command | Description |
|---------|-------------|
| `zerobot onboard` | Initialize config & workspace at `~/.zerobot/` |
| `zerobot onboard --wizard` | Launch the interactive onboarding wizard |
| `zerobot onboard -c <config> -w <workspace>` | Initialize or refresh a specific instance config and workspace |
| `zerobot agent -m "..."` | Chat with the agent |
| `zerobot agent -w <workspace>` | Chat against a specific workspace |
| `zerobot agent -w <workspace> -c <config>` | Chat against a specific workspace/config |
| `zerobot agent` | Interactive chat mode |
| `zerobot agent --no-markdown` | Show plain-text replies |
| `zerobot agent --logs` | Show runtime logs during chat |
| `zerobot serve` | Start the OpenAI-compatible API |
| `zerobot gateway` | Start the gateway |
| `zerobot status` | Show status |
| `zerobot provider login openai-codex` | OAuth login for providers |
| `zerobot channels login <channel>` | Authenticate a channel interactively |
| `zerobot channels status` | Show channel status |

Interactive mode exits: `exit`, `quit`, `/exit`, `/quit`, `:q`, or `Ctrl+D`.

