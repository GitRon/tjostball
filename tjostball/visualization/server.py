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
            "edgecolors": "orange",
            "linewidths": 2,
        }

    # Players
    if isinstance(agent, TjostballPlayer):
        # Team color
        color = "tab:blue" if agent.team == 0 else "tab:red"

        # Size based on stamina (larger = more stamina)
        stamina_ratio = agent.stamina / agent.max_stamina
        base_size = 50 + (stamina_ratio * 100)  # Size between 50-150

        # Highlight player with ball possession
        if agent.model.ball_holder == agent:
            # Ball holder: larger size and bright lime border to stand out
            size = base_size * 1.3  # 30% larger
            edgecolor = "lime"
            linewidth = 4
        else:
            # Regular players: subtle team-colored border
            size = base_size
            edgecolor = color
            linewidth = 1

        return {
            "color": color,
            "size": size,
            "edgecolors": edgecolor,
            "linewidths": linewidth,
        }

    # Unknown agent type
    return {}


def draw_goals(model):
    """
    Custom drawing function to draw goal zones on the field.
    Returns Altair chart layer for the goals.
    """
    import altair as alt
    import pandas as pd

    # Create rectangles for the two goals
    goals_df = pd.DataFrame([
        {
            "x": model.left_goal["x_min"],
            "y": model.left_goal["y_min"],
            "x2": model.left_goal["x_max"],
            "y2": model.left_goal["y_max"],
            "goal": "Team 0 Goal (defended)"
        },
        {
            "x": model.right_goal["x_min"],
            "y": model.right_goal["y_min"],
            "x2": model.right_goal["x_max"],
            "y2": model.right_goal["y_max"],
            "goal": "Team 1 Goal (defended)"
        }
    ])

    # Draw goal zones as rectangles
    goals_chart = alt.Chart(goals_df).mark_rect(
        opacity=0.3,
        stroke="black",
        strokeWidth=2
    ).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[0, model.field_width])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, model.field_height])),
        x2="x2:Q",
        y2="y2:Q",
        color=alt.Color("goal:N", scale=alt.Scale(
            domain=["Team 0 Goal (defended)", "Team 1 Goal (defended)"],
            range=["blue", "red"]
        )),
        tooltip=["goal:N"]
    )

    return goals_chart


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

def space_drawer(model):
    """
    Custom space drawing function that combines goals, agents, and ball.
    """
    import altair as alt
    import pandas as pd
    from tjostball.agents.player import TjostballPlayer
    from tjostball.agents.ball import Ball

    # Draw goals first (background layer)
    goals_layer = draw_goals(model)

    # Draw agents (players)
    agent_records = []
    for agent in model.agents:
        if isinstance(agent, TjostballPlayer) and agent.pos:
            portrayal = agent_portrayal(agent)
            agent_records.append({
                "x": agent.pos[0],
                "y": agent.pos[1],
                "size": portrayal.get("size", 50),
                "color": portrayal.get("color", "gray"),
                "edge_color": portrayal.get("edgecolors", "black"),
                "edge_width": portrayal.get("linewidths", 1),
                "team": f"Team {agent.team}",
                "role": agent.role or "unknown"
            })

    if agent_records:
        agents_df = pd.DataFrame(agent_records)
        agents_layer = alt.Chart(agents_df).mark_circle().encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[0, model.field_width])),
            y=alt.Y("y:Q", scale=alt.Scale(domain=[0, model.field_height])),
            size=alt.Size("size:Q", legend=None),
            color=alt.Color("color:N", scale=None, legend=alt.Legend(title="Team")),
            stroke=alt.Stroke("edge_color:N", scale=None, legend=None),
            strokeWidth=alt.StrokeWidth("edge_width:Q", legend=None),
            tooltip=["team:N", "role:N"]
        )
    else:
        agents_layer = alt.Chart(pd.DataFrame()).mark_circle()

    # Draw ball on top
    ball_layer = draw_ball(model)

    # Combine all layers
    combined = alt.layer(goals_layer, agents_layer, ball_layer).properties(
        width=600,
        height=420,
        title=f"Tjostball Game - Score: Team 0: {model.score[0]} | Team 1: {model.score[1]}"
    )

    return combined


# Create an initial model instance
model = TjostballModel()

# Use custom space drawer instead of default
space_component = space_drawer

# Create the visualization page
page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Tjostball Simulation",
)
