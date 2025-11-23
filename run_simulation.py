#!/usr/bin/env python3
"""
Run the Tjostball simulation with visualization.

This script starts the Mesa 3.x Solara visualization server
and opens the simulation in a web browser.
"""

import subprocess
import sys


def main():
    """Start the Tjostball simulation server."""
    print("Starting Tjostball simulation with Solara...")
    print("The server will start on http://localhost:8765")
    print("Your browser should open automatically")
    print("Press Ctrl+C to stop the server\n")

    # Use solara run to start the visualization server
    # This is the correct way to run Solara apps in Mesa 3.x
    try:
        subprocess.run(
            ["solara", "run", "tjostball.visualization.server:page"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\nError running Solara server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
