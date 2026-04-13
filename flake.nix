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

        lib.mkClanMcp = mkClanMcp;
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

            docker = pkgs.dockerTools.buildLayeredImage {
              name = "ghcr.io/clan-project/clan-mcp";
              tag = clan-mcp.version;
              created =
                let
                  d = self.lastModifiedDate;
                in
                "${builtins.substring 0 4 d}-${builtins.substring 4 2 d}-${builtins.substring 6 2 d}T${builtins.substring 8 2 d}:${builtins.substring 10 2 d}:${builtins.substring 12 2 d}Z";
              contents = [
                clan-mcp
                pkgs.cacert
              ];
              config = {
                Entrypoint = [ (pkgs.lib.getExe clan-mcp) ];
                Env = [
                  "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
                ];
              };
            };
          };

          apps = rec {
            clan-mcp = {
              type = "app";
              program = pkgs.lib.getExe self.packages.${system}.clan-mcp;
              meta.description = "MCP server for Clan management";
            };
            default = clan-mcp;
          };

          formatter = pkgs.nixfmt-rfc-style;

          devShells.default = pkgs.mkShell {
            inputsFrom = [ self.packages.${system}.clan-mcp ];
            packages = with pkgs.python3Packages; [
              pkgs.python3
              hatchling
              build
              ruff
              mypy
            ];
          };
        };
    };
}
