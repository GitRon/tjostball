"""Visualization server for Tjostball simulation using Mesa 3.x Solara interface."""

from mesa.visualization import SolaraViz, Slider, make_space_component
from tjostball.models.game import TjostballModel
from tjostball.agents.player import TjostballPlayer


def agent_portrayal(agent):
    """
    Portrayal function for agents in the visualization.

    Returns a dictionary with agent visual properties for Altair rendering.
    """
    if not isinstance(agent, TjostballPlayer):
        return {}

    # Color by team
    color = "tab:blue" if agent.team == 0 else "tab:red"

    # Size based on stamina (larger = more stamina)
    stamina_ratio = agent.stamina / agent.max_stamina
    size = 50 + (stamina_ratio * 100)  # Size between 50-150

    return {
        "color": color,
        "size": size,
    }


# Model parameters that can be adjusted in the UI
model_params = {
    "n_players_per_team": Slider(
        label="Players per team",
        value=7,
        min=3,
        max=11,
        step=1,
    ),
    "field_width": 100,
    "field_height": 70,
}

# Create an initial model instance
model = TjostballModel()

# Create space visualization component with agent portrayal
space_component = make_space_component(agent_portrayal)

# Create the visualization page
page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Tjostball Simulation",
)
