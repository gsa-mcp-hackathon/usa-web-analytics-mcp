{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      #       ↑ Swap it for your system if needed
      #       "aarch64-linux" / "x86_64-darwin" / "aarch64-darwin"
      pkgs = nixpkgs.legacyPackages.${system};
      runmpc = pkgs.writeShellScriptBin "runmpc" "";

      ingestme = pkgs.writeShellScriptBin "ingestme" ''
        cd "$(git rev-parse --show-toplevel)" &&
        duckdb demo.ddb < analytics-gov-ingestme.sql
      '';

    in
    {
      devShells.${system}.default =
        let
          pythonpkgs =
            ps: with ps; [
              numpy
              uv
              pandas
              duckdb
              boto3
            ];
          pythonEnv = pkgs.python3.withPackages pythonpkgs;
        in
        pkgs.mkShell {
          packages = with pkgs; [
            #postman
            cowsay
            pythonEnv
            ingestme
            duckdb
            curl
            runmpc
          ];
          shellHook = ''
            LC_ALL=C LANGUAGE=C LANG=C
             echo "hello welcome the MCP flake dev shell
                    ingestme <-- this command will read and build a duckdb database
                    " | fold -w 40 -s | cowsay
          '';
        };
    };
}
