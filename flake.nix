{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = nixpkgs.legacyPackages.${system}; in
        {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python310
              python310Packages.caldav
              python310Packages.icalendar
              python310Packages.keyring
              python310Packages.requests
              python310Packages.google-api-core
              python310Packages.google-api-python-client
              python310Packages.google-auth-oauthlib
            ];
            shellHook = ''
            '';
          };
        }
      );
}
