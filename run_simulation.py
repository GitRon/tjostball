#!/usr/bin/env python3
"""
Run the Tjostball simulation with visualization.

This script starts the Mesa 3.x Solara visualization server
and opens the simulation in a web browser.
"""

from tjostball.visualization.server import create_server


def main():
    """Start the Tjostball simulation server."""
    print("Starting Tjostball simulation with Solara...")
    print("The server will start on http://localhost:8765")
    print("Your browser should open automatically")
    print("Press Ctrl+C to stop the server")

    # Create the visualization page
    page = create_server()

    # In Mesa 3.x with Solara, we use the page's built-in display
    page.show()


if __name__ == "__main__":
    main()
