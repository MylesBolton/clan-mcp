import subprocess
import os
import json
from typing import Optional, Dict, Any
from fastmcp import FastMCP

mcp = FastMCP("Clan Management Pro")

def run_clan(args: list[str]) -> str:
    """Run clan CLI and return output."""
    try:
        # Prefer JSON output for programmatic use where supported
        # (Assuming clan supports --json for most list/show commands)
        result = subprocess.run(
            ["clan"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Clan Error (Exit {e.returncode}):\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"

@mcp.resource("clan://config/main")
def get_clan_config() -> str:
    """Read primary clan config (clan.nix or flake.nix)."""
    for path in ["clan.nix", "flake.nix"]:
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
    return "Error: No clan.nix or flake.nix found."

# --- Inventory & Machines ---

@mcp.tool()
def machine_list(flake_path: str = "."):
    """List all machines in clan."""
    return run_clan(["machines", "list", "--flake", flake_path])

@mcp.tool()
def machine_create(name: str, flake_path: str = "."):
    """Create new machine configuration."""
    return run_clan(["machines", "create", name, "--flake", flake_path])

@mcp.tool()
def machine_init_hardware(machine: str, target_host: str, flake_path: str = "."):
    """Detect hardware and save config from target host."""
    return run_clan(["machines", "init-hardware-config", machine, "--target-host", target_host, "--flake", flake_path])

@mcp.tool()
def machine_update(machine: str, flake_path: str = ".", target_host: Optional[str] = None, build_host: Optional[str] = None):
    """Deploy configuration changes to machine."""
    args = ["machines", "update", machine, "--flake", flake_path]
    if target_host: args.extend(["--target-host", target_host])
    if build_host: args.extend(["--build-host", build_host])
    return run_clan(args)

@mcp.tool()
def machine_install(machine: str, target_host: str, flake_path: str = "."):
    """Install Clan NixOS on target machine."""
    return run_clan(["machines", "install", machine, "--target-host", target_host, "--flake", flake_path])

# --- Vars (Secrets) ---

@mcp.tool()
def vars_generate(machine: Optional[str] = None, flake_path: str = ".", regenerate: bool = False):
    """Generate missing secrets/vars."""
    args = ["vars", "generate"]
    if machine: args.append(machine)
    args.extend(["--flake", flake_path])
    if regenerate: args.append("--regenerate")
    return run_clan(args)

@mcp.tool()
def vars_list(machine: str, flake_path: str = "."):
    """List vars for specific machine."""
    return run_clan(["vars", "list", machine, "--flake", flake_path])

@mcp.tool()
def vars_get(machine: str, var_id: str, flake_path: str = "."):
    """Retrieve decrypted var value."""
    return run_clan(["vars", "get", machine, var_id, "--flake", flake_path])

@mcp.tool()
def vars_upload(machine: str, flake_path: str = "."):
    """Upload vars to target machine (useful before manual rebuild)."""
    return run_clan(["vars", "upload", machine, "--flake", flake_path])

# --- Templates ---

@mcp.tool()
def template_list():
    """List available clan templates."""
    return run_clan(["templates", "list"])

@mcp.tool()
def template_apply(template: str, machine: str, settings: Optional[Dict[str, str]] = None, flake_path: str = "."):
    """Apply template (e.g. disk config) to machine."""
    args = ["templates", "apply", template, machine, "--flake", flake_path]
    if settings:
        for k, v in settings.items():
            args.extend(["--set", f"{k}={v}"])
    return run_clan(args)

# --- Validation ---

@mcp.tool()
def config_check(flake_path: str = "."):
    """Validate clan configuration."""
    return run_clan(["config", "check", "--flake", flake_path])

def main():
    mcp.run("stdio")

if __name__ == "__main__":
    main()
