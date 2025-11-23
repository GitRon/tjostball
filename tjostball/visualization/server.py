"""Visualization server for Tjostball simulation using Mesa 3.x Solara interface."""

from mesa.visualization import SolaraViz, Slider
from mesa.visualization import make_plot_component
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

    # Color by team
    if agent.team == 0:
        color = "blue"
    else:
        color = "red"

    # Size based on stamina
    stamina_ratio = agent.stamina / agent.max_stamina
    size = 15 + (stamina_ratio * 15)  # Size between 15-30

    return {
        "color": color,
        "size": size,
        "marker": "o",  # circle
    }


# Model parameters that can be adjusted in the UI
model_params = {
    "n_players_per_team": Slider(
        "Players per team",
        value=7,
        min=3,
        max=11,
        step=1,
    ),
    "field_width": 100,
    "field_height": 70,
}


# Create score plot
def make_score_plot(model):
    return make_plot_component(
        {
            "Score Team 0": "blue",
            "Score Team 1": "red",
        }
    )


# Create the visualization page - this is the module-level variable that Solara looks for
page = SolaraViz(
    TjostballModel,
    model_params,
    measures=[make_score_plot],
    name="Tjostball Simulation",
    agent_portrayal=agent_portrayal,
)
