"""Visualization server for Tjostball simulation using Mesa 3.x Solara interface."""

from mesa.visualization import SolaraViz, Slider
from tjostball.models.game import TjostballModel


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

# Create the visualization page - this is the module-level variable that Solara looks for
# Mesa 3.x will automatically render the space with default settings
page = SolaraViz(
    model,
    model_params=model_params,
    name="Tjostball Simulation",
)
