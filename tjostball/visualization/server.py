"""Visualization server for Tjostball simulation using Mesa 3.x Solara interface."""

from mesa.visualization import SolaraViz, Slider, make_space_component
from tjostball.models.game import TjostballModel
from tjostball.agents.player import TjostballPlayer
from tjostball.agents.ball import Ball


def agent_portrayal(agent):
    """
    Portrayal function for agents in the visualization.

    Returns a dictionary with agent visual properties for rendering.
    """
    # Ball
    if isinstance(agent, Ball):
        return {
            "color": "yellow",
            "size": 200,
            "marker": "o",
            "zorder": 10,  # Draw ball on top
        }

    # Players
    if isinstance(agent, TjostballPlayer):
        # Color by team
        color = "tab:blue" if agent.team == 0 else "tab:red"

        # Size based on stamina (larger = more stamina)
        stamina_ratio = agent.stamina / agent.max_stamina
        size = 50 + (stamina_ratio * 100)  # Size between 50-150

        return {
            "color": color,
            "size": size,
        }

    # Unknown agent type
    return {}


def draw_ball(model):
    """
    Custom drawing function to add the ball to the visualization.
    Returns Altair chart layer for the ball.
    """
    import altair as alt
    import pandas as pd

    # Create a dataframe with the ball position
    ball_df = pd.DataFrame([{
        "x": model.ball_position[0],
        "y": model.ball_position[1],
    }])

    # Create Altair chart for the ball
    ball_chart = alt.Chart(ball_df).mark_circle(
        size=200,
        color="yellow",
        stroke="orange",
        strokeWidth=2
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[0, model.field_width])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, model.field_height])),
    )

    return ball_chart


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

# Create space visualization component with matplotlib backend
# Configure to not draw property layers (which don't exist for ContinuousSpace)
space_component = make_space_component(
    agent_portrayal,
    propertylayer_portrayal=None,  # Disable property layers for ContinuousSpace
)

# Create the visualization page
page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Tjostball Simulation",
)
