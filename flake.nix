{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = [
          (pkgs.python314.withPackages (
            python-pkgs: with python-pkgs; [
              fastapi
              fastapi-cli
              matplotlib
              numpy
              sympy
            ]
          ))
        ];
      };
    };
}
