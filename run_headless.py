#!/usr/bin/env python3
"""
Run the Tjostball simulation in headless mode (no visualization).

This script runs the simulation without the web interface,
useful for batch simulations and testing.
"""

from tjostball.models.game import TjostballModel


def main():
    """Run a headless simulation."""
    print("Running Tjostball simulation (headless mode)...")

    # Create model
    model = TjostballModel(
        n_players_per_team=7,
        field_width=100,
        field_height=70
    )

    # Run for 100 steps
    print("Running 100 simulation steps...")
    for i in range(100):
        model.step()

        if i % 10 == 0:
            print(f"Step {i}: Ball at {model.ball_position}, "
                  f"Time: {model.game_time:.1f}s, "
                  f"Score: {model.score[0]}-{model.score[1]}")

    print("\nSimulation complete!")
    print(f"Final score: Team 0: {model.score[0]}, Team 1: {model.score[1]}")
    print(f"Total game time: {model.game_time:.1f} seconds")

    # Get final data
    data = model.datacollector.get_model_vars_dataframe()
    print(f"\nCollected {len(data)} data points")


if __name__ == "__main__":
    main()
