#!/usr/bin/env python3
"""
Run the Tjostball simulation with visualization.

This script starts the Mesa visualization server and opens
the simulation in a web browser.
"""

from tjostball.visualization.server import create_server


def main():
    """Start the Tjostball simulation server."""
    print("Starting Tjostball simulation...")
    print("Open your browser to http://localhost:8521")
    print("Press Ctrl+C to stop the server")

    server = create_server()
    server.port = 8521
    server.launch(open_browser=True)


if __name__ == "__main__":
    main()
