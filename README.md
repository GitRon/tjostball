# Tjostball
Agent-based game simulation using Mesa framework

## Quick Start

Install dependencies:
```bash
pip install -r requirements.txt
```

Run headless simulation (no visualization):
```bash
python3 run_headless.py
```

Run with web visualization:
```bash
python3 run_simulation.py
# Open browser to http://localhost:8521
```

## Project Structure

```
tjostball/
├── agents/
│   └── player.py          # TjostballPlayer agent with FSM states
├── models/
│   └── game.py            # TjostballModel simulation
└── visualization/
    └── server.py          # Mesa web visualization server
```

## Current Implementation

### Player Agents (Issue #1)
- Basic FSM with states: DEFENDING, ATTACKING, SUPPORTING, POSITIONING
- Perception system (can see ball, nearby teammates/opponents)
- Simple movement AI (moves toward ball)
- Attributes: speed, strength, stamina

### Game Simulation (Issue #2)
- 100x70 continuous space field
- Ball physics with velocity and friction
- Ball possession detection
- 7 players per team (configurable)
- Data collection for game statistics

## Next Steps

This is a basic setup that runs. The framework is ready for:
- Implementing full gameplay rules from docs/gameplay
- Enhancing player AI and decision-making
- Adding tackling, passing, and scoring mechanics
- Improving visualization
