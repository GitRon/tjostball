# Tjostball
Agent-based game simulation using Mesa 3.x framework with Solara visualization

## Quick Start

Install dependencies using `uv`:
```bash
uv sync
```

Run headless simulation (no visualization):
```bash
uv run python run_headless.py
```

Run with web visualization:
```bash
# Option 1: Using the run script
uv run python run_simulation.py

# Option 2: Using solara directly
uv run solara run tjostball.visualization.server:page

# Open browser to http://localhost:8765
```

## Project Structure

```
tjostball/
├── agents/
│   └── player.py          # TjostballPlayer agent with FSM states
├── models/
│   └── game.py            # TjostballModel simulation
└── visualization/
    └── server.py          # Mesa 3.x Solara visualization
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
