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

      ingestme = pkgs.writeShellScriptBin "ingestme" ''
        cd "$(git rev-parse --show-toplevel)" &&
        duckdb demo.ddb < analytics-gov-ingestme.sql
      '';

      mcp_run = pkgs.writeShellScriptBin "run_mcp" ''
        cd "$(git rev-parse --show-toplevel)" &&

        $env:ANALYTICS_API_KEY="DEMO_KEY1"
        uv run analytics-server

            fastmpc list ./src/analytics_server/app.py
            fastmpc call ./src/analytics_server/app.py get_anlytic_report report_name=language
            fastmpc call ./src/analytics_server/app.py get_top_pages_realtime agaency=commerce
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
            firefox
            uv
            mcp_run
            cowsay
            pythonEnv
            ingestme
            duckdb
            mcp-language-server
            curl
          ];
          shellHook =
            #bash
            ''
              LC_ALL=C LANGUAGE=C LANG=C
               echo "hello welcome the MCP flake dev shell
                      ingestme <-- this command will read from analytics.gov and build a duckdb database
                      " | fold -w 40 -s | cowsay
            '';
        };
    };
}
