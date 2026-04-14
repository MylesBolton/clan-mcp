import asyncio
import os
import json
from typing import Optional, Dict, Any, Union
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("Clan Management Pro")

# Documentation root: check ENV, then fall back to local dev path
DOCS_ROOT = Path(os.environ.get("CLAN_DOCS_ROOT", Path(__file__).parent.parent / "src")).resolve()

async def run_command(cmd: str, args: list[str], parse_json: bool = False) -> Union[str, Any]:
    """Run any command asynchronously and return output."""
    try:
        process = await asyncio.create_subprocess_exec(
            cmd, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            err_msg = stderr.decode().strip() or stdout.decode().strip() or "Unknown error"
            return f"Error ({cmd} exit {process.returncode}): {err_msg}"
        
        output = stdout.decode().strip()
        if parse_json and output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return output
        return output
    except FileNotFoundError:
        return f"Error: Command '{cmd}' not found in PATH."
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

async def run_clan(args: list[str], parse_json: bool = False) -> Union[str, Any]:
    """Run clan CLI asynchronously and return output."""
    # The clan CLI does not support --json for most subcommands yet.
    # We remove the blind addition of --json and handle the output as text.
    return await run_command("clan", args, parse_json=parse_json)

@mcp.tool()
async def clan_info(flake_path: str = "."):
    """Get Clan metadata and Nix version information."""
    clan_v = await run_command("clan", ["show", "--flake", flake_path])
    nix_v = await run_command("nix", ["--version"])
    return f"Clan Info:\n{clan_v}\n\nNix: {nix_v}"

# --- Nix & Flake Tools ---

@mcp.tool()
async def nix_flake_show(flake_path: str = "."):
    """Show flake outputs."""
    return await run_command("nix", ["flake", "show", flake_path])

@mcp.tool()
async def nix_flake_check(flake_path: str = "."):
    """Check flake for errors."""
    return await run_command("nix", ["flake", "check", flake_path])

@mcp.tool()
async def nix_build(attr: str, flake_path: str = "."):
    """Build a nix attribute."""
    return await run_command("nix", ["build", f"{flake_path}#{attr}", "--no-link"])

@mcp.tool()
async def nix_eval(attr: str, flake_path: str = ".", apply: Optional[str] = None):
    """Evaluate a nix attribute and return JSON. (e.g. attr='nixosConfigurations.machine1.config.services.nginx.enable')"""
    args = ["eval", f"{flake_path}#{attr}", "--json"]
    if apply:
        args.extend(["--apply", apply])
    return await run_command("nix", args, parse_json=True)

@mcp.resource("clan://config/main")
async def get_clan_config() -> str:
    """Read primary clan config (clan.nix or flake.nix)."""
    for name in ["clan.nix", "flake.nix"]:
        path = Path(name)
        if path.exists():
            return await asyncio.to_thread(path.read_text)
    return "Error: No clan.nix or flake.nix found."

# --- Inventory & Machines ---

@mcp.tool()
async def machine_list(flake_path: str = "."):
    """List all machines in clan."""
    return await run_clan(["machines", "list", "--flake", flake_path])

@mcp.tool()
async def machine_create(name: str, flake_path: str = "."):
    """Create new machine configuration."""
    return await run_clan(["machines", "create", name, "--flake", flake_path])

@mcp.tool()
async def machine_init_hardware(machine: str, target_host: str, flake_path: str = "."):
    """Detect hardware and save config from target host."""
    return await run_clan(["machines", "init-hardware-config", machine, "--target-host", target_host, "--flake", flake_path])

@mcp.tool()
async def machine_update(machine: str, flake_path: str = ".", target_host: Optional[str] = None, build_host: Optional[str] = None):
    """Deploy configuration changes to machine."""
    args = ["machines", "update", machine, "--flake", flake_path]
    if target_host: args.extend(["--target-host", target_host])
    if build_host: args.extend(["--build-host", build_host])
    return await run_clan(args)

@mcp.tool()
async def machine_install(machine: str, target_host: str, flake_path: str = "."):
    """Install Clan NixOS on target machine."""
    return await run_clan(["machines", "install", machine, "--target-host", target_host, "--flake", flake_path])

# --- Vars (Secrets) ---

@mcp.tool()
async def vars_generate(machine: Optional[str] = None, flake_path: str = ".", regenerate: bool = False):
    """Generate missing secrets/vars."""
    args = ["vars", "generate"]
    if machine: args.append(machine)
    args.extend(["--flake", flake_path])
    if regenerate: args.append("--regenerate")
    return await run_clan(args)

@mcp.tool()
async def vars_list(machine: str, flake_path: str = "."):
    """List vars for specific machine."""
    return await run_clan(["vars", "list", machine, "--flake", flake_path])

@mcp.tool()
async def vars_get(machine: str, var_id: str, flake_path: str = "."):
    """Retrieve decrypted var value."""
    return await run_clan(["vars", "get", machine, var_id, "--flake", flake_path])

@mcp.tool()
async def vars_upload(machine: str, flake_path: str = "."):
    """Upload vars to target machine (useful before manual rebuild)."""
    return await run_clan(["vars", "upload", machine, "--flake", flake_path])

# --- Templates ---

@mcp.tool()
async def template_list():
    """List available clan templates."""
    return await run_clan(["templates", "list"])

@mcp.tool()
async def template_apply(template: str, machine: str, settings: Optional[Dict[str, str]] = None, flake_path: str = "."):
    """Apply template (e.g. disk config) to machine."""
    args = ["templates", "apply", template, machine, "--flake", flake_path]
    if settings:
        for k, v in settings.items():
            args.extend(["--set", f"{k}={v}"])
    return await run_clan(args)

# --- Backups ---

@mcp.tool()
async def backups_list(machine: str, flake_path: str = "."):
    """List backups for a machine."""
    return await run_clan(["backups", "list", machine, "--flake", flake_path])

@mcp.tool()
async def backups_restore(machine: str, backup_id: str, flake_path: str = "."):
    """Restore a backup to a machine."""
    return await run_clan(["backups", "restore", machine, backup_id, "--flake", flake_path])

# --- Validation ---

@mcp.tool()
async def vars_check(machine: Optional[str] = None, flake_path: str = "."):
    """Check if vars are up to date."""
    args = ["vars", "check"]
    if machine:
        args.append(machine)
    args.extend(["--flake", flake_path])
    return await run_clan(args)

@mcp.tool()
async def clan_select(pattern: str, flake_path: str = "."):
    """Select nixos values from the flake using a pattern (e.g. nixosConfigurations.*.config.networking.hostName)."""
    return await run_clan(["select", pattern, "--flake", flake_path])

# --- Documentation ---

@mcp.tool()
async def docs_list() -> str:
    """List all documentation files."""
    if not DOCS_ROOT.exists():
        return f"Error: Documentation directory not found at {DOCS_ROOT}."
    
    docs = []
    for p in DOCS_ROOT.rglob("*.md"):
        docs.append(str(p.relative_to(DOCS_ROOT)))
    return "\n".join(sorted(docs))

@mcp.tool()
async def docs_read(path: str) -> str:
    """Read specific documentation file."""
    doc_path = (DOCS_ROOT / path).resolve()
    # Security check: ensure path is within DOCS_ROOT
    if not doc_path.exists() or not str(doc_path).startswith(str(DOCS_ROOT.resolve())):
        return f"Error: Documentation file '{path}' not found."
    
    # Use to_thread for blocking IO in async function
    return await asyncio.to_thread(doc_path.read_text)

@mcp.tool()
async def docs_search(query: str) -> str:
    """Search for query in documentation markdown files."""
    if not DOCS_ROOT.exists():
        return f"Error: Documentation directory not found at {DOCS_ROOT}."
    
    def search():
        results = []
        for p in DOCS_ROOT.rglob("*.md"):
            try:
                content = p.read_text()
                if query.lower() in content.lower():
                    results.append(str(p.relative_to(DOCS_ROOT)))
            except Exception:
                continue
        return results

    results = await asyncio.to_thread(search)
    
    if not results:
        return f"No results found for '{query}'."
    return "Matches found in:\n" + "\n".join(sorted(results))

@mcp.resource("clan://docs/{path}")
async def get_doc(path: str) -> str:
    """Read documentation by its relative path (e.g. guides/inventory/intro-to-inventory.md)."""
    return await docs_read(path)

def main():
    mcp.run("stdio")

if __name__ == "__main__":
    main()
