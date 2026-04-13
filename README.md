# Clan Management Pro MCP

MCP server for [Clan](https://github.com/clan-lol/clan-core). Manage NixOS machines via LLM.

## Features

- **Machine Management**: List, create, and update NixOS machines.
- **Hardware Detection**: Initialize hardware configs remotely.
- **Secret Management**: Generate, list, and retrieve Clan vars (secrets).
- **Templates**: List and apply Clan templates for disk configs and services.
- **Validation**: Check Clan configuration integrity.

## Usage

### Nix Run

Run directly with Nix:

```bash
nix run github:utensils/mcp-clan -- [args]
```

### NixOS / Home Manager Configuration

Add to your MCP server configuration:

```json
{
  "mcpServers": {
    "clan": {
      "command": "nix",
      "args": ["run", "github:utensils/mcp-clan", "--"]
    }
  }
}
```

### Local Development

Enter development shell:

```bash
nix develop
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
