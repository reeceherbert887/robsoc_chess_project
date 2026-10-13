# Robotic Chess System — Phase 1 Project Specification

#### This project aims to build a hybrid physical–digital chess system where:

- The human plays on a physical 3D‑printed board

- The board detects human moves (RFID or alternative sensors)

- The AI plays digitally inside a ROS2 + Gazebo/RViz digital twin

- No robotic arm is used in Phase 1

- Stockfish (or another engine) generates AI moves

- The digital twin mirrors the game state in real time

- This creates a clean, achievable foundation for later expansion into robotic actuation.

## System Architecture

- The system is divided into hardware, software, and AI/game logic layers.

- Hardware Components

- 3D‑printed chess board

- 3D‑printed pieces

- RFID tags (or magnets, or CV markers)

- RFID reader array (or alternative sensors)

- Microcontroller (ESP32 / Arduino / Pi Pico)

- Processing body (Raspberry Pi 4/5)

## Software Components

- ROS2 

- Gazebo or RViz for digital twin

### Custom ROS2 nodes:

- Board state publisher

- Move validator

- AI move subscriber

- Digital twin synchroniser

- Stockfish chess engine

## Stockfish Idea

#### Stockfish is a classical chess engine, not an LLM. It uses:

- Minimax search

- Alpha–beta pruning

- Heuristic evaluation functions

- Opening books

- Endgame tablebases

#### It does not hallucinate; it calculates. It outputs moves in UCI format, e.g.:

- bestmove e2e4


This diagram shows the full Phase 1 system, including hardware, software, and Stockfish.

```mermaid
flowchart TD
  A[Physical Chess Board] --> B["Piece Detection Layer\n(RFID / Hall Sensors / CV)"]
  B --> C["Microcontroller\n(ESP32 / Pico)"]

  %% Data to SBC
  C --> D["SBC (Jetson / Pi)\nROS2 Node: Board State Publisher"]

  %% ROS2 Core
  D --> E["ROS2 Topic: /board_state"]
  E --> F[Move Validator Node]
  F --> G["Stockfish Engine\nUCI Protocol"]

  %% AI Move Output
  G --> H["ROS2 Topic: /ai_move"]
  H --> I[Digital Twin Sync Node]

  %% Digital Twin
  I --> J["Gazebo / RViz\nDigital Chessboard"]

  %% Human Feedback
  J --> K["User Display\n(Screen / GUI / LEDs)"]

  %% Loop Back
  K --> A

  %% Notes
  subgraph Physical System
    A
    B
    C
  end

  subgraph Compute System
    D
    E
    F
    G
    H
    I
  end

  subgraph Digital Twin
    J
    K
  end
```

Data Flow Summary

```mermaid
flowchart TD
  A["Human moves a piece physically\nSensors detect the piece + square"] --> B["Microcontroller sends data to SBC\nBoard state is published to ROS2"]
  B --> C["ROS2 validates the move\nEnsures legality and updates internal state"]
  C --> D["Stockfish calculates AI move\nReturns best move via UCI"]
  D --> E["Digital twin updates\nGazebo/RViz shows AI move"]
  E --> F["Human sees AI move\nOn screen or via LEDs"]
```