(all code generated with gemini inculding readme)

# Clan Management Pro MCP

MCP server for [Clan](https://github.com/clan-lol/clan-core). Manage NixOS machines via LLM.

## Prerequisites

- `clan` CLI installed and in PATH.
- Python 3.10+.
- `mcp` Python package.

## Features

- **Machine Management**: List, create, and update NixOS machines.
- **Hardware Detection**: Initialize hardware configs remotely.
- **Secret Management**: Generate, list, and retrieve Clan vars (secrets).
- **Templates**: List and apply Clan templates for disk configs and services.
- **Validation**: Check Clan configuration integrity.

## Usage

### Local Development

```bash
python clan-mcp.py
```

### Gemini CLI Integration

Run with `gemini-cli`:

```bash
gemini --mcp python clan-mcp.py
```

Or add to `~/.config/gemini/config.json`:

```json
{
  "mcpServers": {
    "clan": {
      "command": "python",
      "args": ["/absolute/path/to/clan-mcp/clan-mcp.py"]
    }
  }
}
```

## Tools

| Tool                    | Description                                       |
| ----------------------- | ------------------------------------------------- |
| `machine_list`          | List all machines in the clan flake.              |
| `machine_create`        | Create a new machine configuration.               |
| `machine_init_hardware` | Detect hardware and save config from target host. |
| `machine_update`        | Deploy configuration changes to a machine.        |
| `machine_install`       | Install Clan NixOS on a target machine.           |
| `vars_generate`         | Generate missing secrets/vars.                    |
| `vars_list`             | List vars for a specific machine.                 |
| `vars_get`              | Retrieve decrypted var value.                     |
| `template_list`         | List available clan templates.                    |
| `template_apply`        | Apply a template to a machine.                    |
| `config_check`          | Validate clan configuration.                      |

## Resources

- `clan://config/main`: Reads `clan.nix` or `flake.nix` in the current directory.
