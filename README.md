# Clan Management (Pro AI Slop) MCP

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
nix run github:MylesBolton/clan-mcp -- [args]
```

### NixOS / Home Manager Configuration

Add to your MCP server configuration:

```json
{
  "mcpServers": {
    "clan": {
      "command": "nix",
      "args": ["run", "github:MylesBolton/clan-mcp", "--"]
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
| `vars_check`            | Check if vars are up to date for a machine.       |
| `clan_select`           | Query Nix values from the flake using patterns.   |
| `nix_eval`              | Evaluate any Nix attribute in the flake (as JSON).|
| `docs_list`            | List all documentation files.                     |
| `docs_read`            | Read specific documentation file.                 |
| `docs_search`          | Search for query in documentation markdown files. |

## Resources

- `clan://config/main`: Reads `clan.nix` or `flake.nix` in the current directory.
- `clan://docs/{path}`: Reads documentation by its relative path.
