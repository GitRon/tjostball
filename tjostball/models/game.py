"""Game model implementation for Tjostball simulation."""

from mesa import Model, DataCollector
from mesa.space import ContinuousSpace
from tjostball.agents.player import TjostballPlayer
from tjostball.agents.ball import Ball


class TjostballModel(Model):
    """
    A model representing a Tjostball game simulation.

    The field is 100x70 units, with teams starting on opposite ends.
    Includes ball physics, player agents, and game state management.
    """

    def __init__(
        self,
        n_players_per_team=7,
        field_width=100,
        field_height=70,
        seed=None
    ):
        """
        Initialize the Tjostball game model.

        Args:
            n_players_per_team: Number of players per team (default 7)
            field_width: Width of the playing field (default 100)
            field_height: Height of the playing field (default 70)
            seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)

        self.field_width = field_width
        self.field_height = field_height
        self.n_players_per_team = n_players_per_team

        # Create continuous space for smooth movement
        self.grid = ContinuousSpace(
            field_width,
            field_height,
            torus=False
        )

        # Ball state
        self.ball_position = (field_width / 2, field_height / 2)
        self.ball_velocity = (0.0, 0.0)
        self.ball_holder = None

        # Game state
        self.score = [0, 0]
        self.game_time = 0.0

        # Create ball agent
        self.ball = Ball(self)
        self.grid.place_agent(self.ball, self.ball_position)

        # Create players for both teams
        self._create_teams()

        # Data collector for tracking game statistics
        self.datacollector = DataCollector(
            model_reporters={
                "Score Team 0": lambda m: m.score[0],
                "Score Team 1": lambda m: m.score[1],
                "Game Time": lambda m: m.game_time
            }
        )

    def _create_teams(self):
        """Create player agents for both teams and position them on the field."""
        for team in [0, 1]:
            # Starting positions: team 0 on left, team 1 on right
            start_x = self.field_width * 0.25 if team == 0 else self.field_width * 0.75

            for i in range(self.n_players_per_team):
                # Spread players vertically
                y_pos = (i + 1) * self.field_height / (self.n_players_per_team + 1)

                # Create player with some variation in attributes
                player = TjostballPlayer(
                    model=self,
                    team=team,
                    speed=4.0 + self.random.random() * 2.0,  # Speed: 4-6
                    strength=4.0 + self.random.random() * 2.0,  # Strength: 4-6
                    stamina=90.0 + self.random.random() * 20.0  # Stamina: 90-110
                )

                self.grid.place_agent(player, (start_x, y_pos))

    def update_ball_physics(self):
        """
        Update ball position based on velocity and apply friction.
        Simple physics model for the basic setup.
        """
        if self.ball_holder is None:
            # Ball is loose - apply physics
            vx, vy = self.ball_velocity
            bx, by = self.ball_position

            # Apply friction (slow down)
            friction = 0.95
            vx *= friction
            vy *= friction

            # Update position
            new_x = bx + vx
            new_y = by + vy

            # Bounce off boundaries
            if new_x <= 0 or new_x >= self.field_width:
                vx = -vx * 0.8  # Energy loss on bounce
                new_x = max(0, min(self.field_width, new_x))

            if new_y <= 0 or new_y >= self.field_height:
                vy = -vy * 0.8  # Energy loss on bounce
                new_y = max(0, min(self.field_height, new_y))

            self.ball_position = (new_x, new_y)
            self.ball_velocity = (vx, vy)

            # Stop ball if moving very slowly
            if abs(vx) < 0.1 and abs(vy) < 0.1:
                self.ball_velocity = (0.0, 0.0)
        else:
            # Ball follows the holder
            self.ball_position = self.ball_holder.pos

        # Update ball agent position
        self.grid.move_agent(self.ball, self.ball_position)

    def check_ball_possession(self):
        """Check if any player is close enough to possess the ball."""
        if self.ball_holder is None:
            # Find closest player to ball
            closest_player = None
            min_distance = 2.0  # Possession radius

            for agent in self.agents:
                if isinstance(agent, TjostballPlayer) and agent.pos:
                    dx = agent.pos[0] - self.ball_position[0]
                    dy = agent.pos[1] - self.ball_position[1]
                    distance = (dx**2 + dy**2)**0.5

                    if distance < min_distance:
                        min_distance = distance
                        closest_player = agent

            if closest_player and min_distance < 2.0:
                self.ball_holder = closest_player

    def step(self):
        """
        Advance the model by one step (0.1 seconds of game time).
        """
        # Update game time
        self.game_time += 0.1

        # Update ball physics
        self.update_ball_physics()

        # Check for ball possession
        self.check_ball_possession()

        # Advance all agents (Mesa 3.x uses built-in agent management)
        for agent in self.agents:
            agent.step()

        # Collect data
        self.datacollector.collect(self)
