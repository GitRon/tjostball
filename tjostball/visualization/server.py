"""Visualization server for Tjostball simulation using Mesa's web interface."""

from mesa.visualization import CanvasGrid, ChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider
from tjostball.models.game import TjostballModel
from tjostball.agents.player import TjostballPlayer


def agent_portrayal(agent):
    """
    Define how agents are portrayed in the visualization.

    Args:
        agent: The agent to portray

    Returns:
        Dictionary describing the visual representation
    """
    if not isinstance(agent, TjostballPlayer):
        return {}

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.8,
        "Layer": 1
    }

    # Color by team
    if agent.team == 0:
        portrayal["Color"] = "blue"
    else:
        portrayal["Color"] = "red"

    # Size based on stamina
    stamina_ratio = agent.stamina / agent.max_stamina
    portrayal["r"] = 0.5 + (stamina_ratio * 0.5)

    return portrayal


def ball_portrayal(model):
    """
    Create a portrayal for the ball.

    Args:
        model: The model containing ball state

    Returns:
        List of portrayal dictionaries
    """
    ball_x, ball_y = model.ball_position

    return [{
        "Shape": "circle",
        "Filled": "true",
        "Color": "yellow",
        "r": 0.5,
        "Layer": 2,
        "x": ball_x,
        "y": ball_y
    }]


def create_server():
    """
    Create and configure the Mesa visualization server.

    Returns:
        ModularServer instance ready to run
    """
    # Canvas for the field
    canvas = CanvasGrid(
        agent_portrayal,
        100,  # field width
        70,   # field height
        500,  # canvas width in pixels
        350   # canvas height in pixels
    )

    # Chart for scores
    score_chart = ChartModule(
        [
            {"Label": "Score Team 0", "Color": "Blue"},
            {"Label": "Score Team 1", "Color": "Red"}
        ],
        data_collector_name="datacollector"
    )

    # Model parameters that can be adjusted in the UI
    model_params = {
        "n_players_per_team": Slider(
            "Players per team",
            7,
            3,
            11,
            1,
            description="Number of players on each team"
        ),
        "field_width": 100,
        "field_height": 70,
    }

    # Create server
    server = ModularServer(
        TjostballModel,
        [canvas, score_chart],
        "Tjostball Simulation",
        model_params
    )

    return server


if __name__ == "__main__":
    server = create_server()
    server.port = 8521
    server.launch()
