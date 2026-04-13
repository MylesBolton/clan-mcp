{
  description = "MCP-Clan - Model Context Protocol server for Clan management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      flake-parts,
      ...
    }:
    let
      mkClanMcp =
        {
          pkgs,
          python3Packages ? pkgs.python3Packages,
        }:
        let
          pyproject = pkgs.lib.importTOML ./pyproject.toml;
        in
        python3Packages.buildPythonApplication {
          pname = pyproject.project.name;
          inherit (pyproject.project) version;
          pyproject = true;
          src = ./.;

          build-system = [ python3Packages.hatchling ];
          dependencies = with python3Packages; [
            fastmcp
          ];

          pythonRelaxDeps = true;
          dontCheckRuntimeDeps = true;
          # Adjust if you have actual tests later
          doCheck = false;

          meta = {
            inherit (pyproject.project) description;
            license = pkgs.lib.licenses.mit;
            mainProgram = "clan-mcp";
          };
        };
    in
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      flake = {
        overlays.default = final: _: {
          clan-mcp = mkClanMcp { pkgs = final; };
        };
      };

      perSystem =
        { system, ... }:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [
              (final: prev: {
                pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
                  (pyFinal: pyPrev: {
                    fastmcp = pyPrev.fastmcp.overridePythonAttrs (_: {
                      dontCheckRuntimeDeps = true;
                      doCheck = false;
                    });
                  })
                ];
              })
            ];
          };
        in
        {
          packages = rec {
            clan-mcp = mkClanMcp { inherit pkgs; };
            default = clan-mcp;
          };

          apps = rec {
            clan-mcp = {
              type = "app";
              program = pkgs.lib.getExe self.packages.${system}.clan-mcp;
              meta.description = "Clan Management Pro MCP server";
            };
            default = clan-mcp;
          };

          devShells.default = pkgs.mkShell {
            inputsFrom = [ self.packages.${system}.clan-mcp ];
            packages = [ pkgs.python3 ];
          };
        };
    };
}
