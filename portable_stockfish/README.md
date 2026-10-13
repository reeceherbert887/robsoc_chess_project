# RobSoc Portable Stockfish — Version 1

An isolated desktop chess app built using Tkinter and `python-chess`, with a local Stockfish UCI executable.

## Install (Ubuntu)

From the `portable_stockfish` directory:

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

You need internet access for the first installation and sudo access for Ubuntu prerequisites. After setup, the app can run offline, although the initial setup uses a system-installed Stockfish executable and therefore targets compatible Linux desktops.

## Play

Select **New Game — Play White** or **New Game — Play Black**. Click a piece and then a highlighted destination square. Stockfish replies automatically. Save your game as `.pgn` using **Save Game**. Pawn promotion currently defaults to a queen.

## Portability

The engine executable is copied to `engine/stockfish`. The `.venv` is machine-specific; after cloning to another Ubuntu PC, run `./setup.sh` there to recreate dependencies. Future versions can add downloadable official release builds, cross-platform installation, robotics interfaces, and enhanced GUI features.

## Licensing

Stockfish is licensed under GPL-3.0. If you distribute its executable in this repository, comply with the Stockfish licensing obligations, including supplying the applicable source code or a source-code link for the exact distributed binary and its licence. See https://github.com/official-stockfish/Stockfish. `python-chess` is separately licensed; follow its project licence as well.