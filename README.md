# RobSoc Chess — Modular Robotic Chess System

**University of Hull Robotics Society | Project prototype and long-term development plan**

A modular **physical–digital chess project** intended to combine chess software, embedded electronics, 3D printing, sensors, ROS 2, digital-twin visualisation and—eventually—automatic movement of physical pieces.

The project is designed so society members can contribute to different subsystems independently. The first software prototype is a **local graphical chess application powered by the official Stockfish 19 engine**. The physical board, sensor network, ROS 2 integration and actuation remain planned development work.

## Current status (13 October 2026)

| Area | Status |
| --- | --- |
| Project proposals and architecture | Documented |
| Stockfish 19 UCI executable (Linux x86-64) | Verified: `id name Stockfish 19` / `uciok` |
| Python virtual environment and `python-chess` | Installed and verified on the development PC |
| Basic Tkinter graphical chessboard | Opened successfully (screenshot supplied) |
| Play-as-white / play-as-black controls | Implemented in prototype; end-to-end gameplay not formally tested |
| PGN saving | Available in prototype; not separately verified |
| Updated installation script | Drafted to handle the official archive; successful rerun not yet confirmed |
| Physical board, sensors, ROS 2 and digital twin | Planned, not implemented in the portable prototype |
| Automatic physical piece movement | Long-term objective, not implemented |

## Project vision

The original proposals describe **Phase 1** as a hybrid board: a person moves real pieces, sensors identify the move, the software validates it and Stockfish selects a response. A digital representation displays the reply, and the person manually places the AI piece. **No robotic arm is required for Phase 1.** Later phases may investigate a magnetic under-board XY mechanism, a gantry, or other robotic actuation.

```text
Planned physical chessboard (3D printed)
       |
       v
Piece/square sensing (RFID / Hall sensors / vision)
       |
       v
Microcontroller (ESP32 / Pico)
       |
       v
Board-state and rules software
       |
       +----> Stockfish (UCI chess engine)
       |               |
       +<--------------+
       |
       v
ROS 2 / digital twin / chess interface
       |
       v
Display AI move to human (Phase 1)
       |
       +----> Physical piece actuation (future)
```

The **current prototype** is simpler and deliberately standalone:

```text
Human clicks Tkinter chessboard
          |
          v
Python application + python-chess
          |
          v
Official Stockfish 19 binary (UCI)
          |
          v
AI move displayed on Tkinter board
```

## Getting started — current Ubuntu/Linux desktop prototype

**Tested environment:** Ubuntu desktop on Linux x86-64, Python 3.14.4, `python-chess` 1.999, Stockfish 19. Tkinter is provided by the OS. The official `stockfish-linux-x86-64-universal.tar.gz` archive was downloaded separately and placed at repository root; it is not inherently part of a Git clone.

From a configured working copy:

```bash
cd ~/Repos/robsoc_chess_project
./portable_stockfish/run.sh
```

If a root launcher has been created, `./run.sh` opens the same GUI. To launch Stockfish **without** a chessboard:

```bash
./portable_stockfish/engine/stockfish
```

To test the UCI engine without entering interactive mode:

```bash
printf 'uci\nquit\n' | ./portable_stockfish/engine/stockfish | grep -E 'id name|uciok'
```

Expected installed-engine identification:

```text
id name Stockfish 19
uciok
```

### Installation on a fresh Ubuntu x86-64 PC

1. Clone the repository.
2. Download the **official Linux x86-64 universal** Stockfish archive from the [Stockfish releases](https://github.com/official-stockfish/Stockfish/releases) and put the `.tar.gz` file at the repository root. Note that a clean clone may not include the archive/binary because large downloads are excluded from Git.
3. Run the updated local installer (the original installer would copy Ubuntu's packaged engine instead):

```bash
git clone https://github.com/reeceherbert887/robsoc_chess_project.git
cd robsoc_chess_project
chmod +x portable_stockfish/setup.sh portable_stockfish/run.sh
./portable_stockfish/setup.sh
./portable_stockfish/run.sh
```

**Caveat:** these instructions assume you have installed the **revised `setup.sh`** documented in [`Documentation/Portable-Stockfish-Setup.md`](Documentation/Portable-Stockfish-Setup.md). The revised script was proposed during development; verify your checked-out copy contains it. These commands are **not** a promise of universal, dependency-free portability. Python/Tkinter must be available and a compatible Stockfish build is needed for the target architecture.

### Using the GUI

The current Tkinter window is titled **RobSoc — Portable Stockfish**. Start a new game as White or Black, click your piece and then a legal destination, and wait for Stockfish's reply. The interface has a **Stockfish move time (seconds)** setting and a **Save Game (.pgn)** action. Promotion defaults to a queen in this prototype. A full game and all save paths should still be tested before release.

Stockfish itself has **no official desktop chess GUI**: the RobSoc Tkinter application is our custom interface. **PyChess** is a separate, optional chess GUI and is not required for this prototype.

## File structure

The tree below combines the **observed local repository layout** with the launchers/docs discussed during setup. Entries marked **optional** may not exist until you create them; generated files are not intended for Git.

```text
robsoc_chess_project/
├── README.md                              # This overview
├── Documentation/
│   ├── Robotic_Chess_System.md            # Project specification (local move reported)
│   ├── Robotic_Chess_System_Masterplan_Phase_1.md
│   ├── Robotic_Chess_system2.md
│   ├── Robotic_Chess_system3.md
│   └── Portable-Stockfish-Setup.md        # Separate build/install log (new)
├── portable_stockfish/
│   ├── app.py                             # Tkinter UI + game logic
│   ├── requirements.txt                   # python-chess
│   ├── setup.sh                           # OS/Python/engine installation
│   ├── run.sh                             # GUI launcher
│   ├── README.md                          # Existing subproject notes
│   ├── .gitignore
│   ├── .venv/                             # Generated Python environment, ignore in Git
│   ├── games/                             # Local PGN files
│   └── engine/
│       ├── stockfish                      # Stockfish 19 executable, local/untracked
│       ├── stockfish-official             # Local duplicate (can be removed later)
│       └── stockfish-source/             # Extracted official archive contents
├── stockfish-linux-x86-64-universal.tar.gz # Local download, normally ignored
├── run.sh                                 # Optional root GUI launcher
└── stockfish.sh                           # Optional root UCI launcher
```

The original four planning documents were seen under `Documentation/` in the local Git status; the public GitHub snapshot viewed during drafting still showed them at repository root. Confirm their final filenames before committing.

## Planned hardware and software

| Subsystem | Candidate technologies | Status |
| --- | --- | --- |
| Chessboard and pieces | Custom CAD / 3D printing | Planned |
| Piece detection | RFID tags/readers, Hall sensors, or computer vision | Under consideration |
| Sensor controller | ESP32 / Raspberry Pi Pico / Arduino | Planned |
| Main computer | Raspberry Pi 4/5; Jetson option for advanced vision | Proposed |
| Gameplay | Python, python-chess, Stockfish UCI | Initial desktop prototype |
| Communications | ROS 2 board-state and move topics | Planned |
| Digital twin | 2D board, RViz or Gazebo | Planned |
| Actuation | Under-board magnetic XY gantry or other mechanism | Future |

An RFID reader per square is **an idea**, not a final engineering decision: cost, interference, complexity and reliability need prototyping. A combined occupancy-detection/piece-identification approach is another proposal.

## Development roadmap

1. **Software foundation (underway):** verify full games, error handling, PGN saving and robust install/launch scripts.
2. **Smart physical board:** design the 3D-printed board; evaluate RFID/Hall/vision approaches; prototype sensing and move detection.
3. **Digital integration:** publish board state and player/AI moves to ROS 2; synchronise a 2D interface or RViz visualisation.
4. **Extended simulation:** investigate Gazebo, board feedback, diagnostics and a polished UI.
5. **Autonomous movement (later):** prototype a safe movement system, including captures, calibration and collision avoidance.

The roadmap reflects the proposals' phased intention; it is not a claim of completed hardware or ROS work.

## Collaboration

The project can be divided among CAD/3D-printing, electronics, embedded software, AI/chess logic, ROS 2, simulation, UI and mechanical teams. Contributors should document changes, test software independently where possible and separate implemented features from proposed designs.

## Original documentation

- [`Documentation/Robotic_Chess_System.md`](Documentation/Robotic_Chess_System.md) — initial Phase 1 hybrid board specification.
- [`Documentation/Robotic_Chess_System_Masterplan_Phase_1.md`](Documentation/Robotic_Chess_System_Masterplan_Phase_1.md) — modular architecture, sensing comparison and development phases.
- [`Documentation/Robotic_Chess_system2.md`](Documentation/Robotic_Chess_system2.md) — physical/digital Phase 1 proposal.
- [`Documentation/Robotic_Chess_system3.md`](Documentation/Robotic_Chess_system3.md) — society team structure and staged design.
- [`Documentation/Portable-Stockfish-Setup.md`](Documentation/Portable-Stockfish-Setup.md) — **separate** technical installation and troubleshooting record.

## Licensing and distribution

Stockfish is third-party GPL-licensed software. When redistributing a binary, comply with the relevant GPL obligations, including appropriate licensing and corresponding-source arrangements. Keep its copyright/licensing information intact; the chess GUI and project code need their own clear licence decision. `python-chess` is also third-party GPL-licensed software; review redistribution obligations before packaging a distributable release.

## Project links

- [GitHub repository](https://github.com/reeceherbert887/robsoc_chess_project)
- [Official Stockfish project](https://github.com/official-stockfish/Stockfish)
- [python-chess](https://python-chess.readthedocs.io/)

*README updated: 13 October 2026. Project documentation describes the intended design; current prototype status comes from development-terminal logs and GUI screenshots.*
