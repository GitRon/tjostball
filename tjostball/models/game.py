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
        n_players_per_team=12,
        field_width=100,
        field_height=70,
        seed=None
    ):
        """
        Initialize the Tjostball game model.

        Args:
            n_players_per_team: Number of players per team (default 12)
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

        # Goal zones (positioned at each end of the field)
        # Team 0 defends left goal (x=0), attacks right goal (x=field_width)
        # Team 1 defends right goal (x=field_width), attacks left goal (x=0)
        self.goal_width = 20  # Goal width (centered vertically)
        self.goal_depth = 5   # Goal depth (how far into the end zone)

        # Left goal (Team 0 defends, Team 1 attacks)
        self.left_goal = {
            "x_min": 0,
            "x_max": self.goal_depth,
            "y_min": (field_height - self.goal_width) / 2,
            "y_max": (field_height + self.goal_width) / 2,
            "defending_team": 0
        }

        # Right goal (Team 1 defends, Team 0 attacks)
        self.right_goal = {
            "x_min": field_width - self.goal_depth,
            "x_max": field_width,
            "y_min": (field_height - self.goal_width) / 2,
            "y_max": (field_height + self.goal_width) / 2,
            "defending_team": 1
        }

        # Game state
        self.score = [0, 0]
        self.game_time = 0.0
        self.last_scorer = None

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
        """
        Create player agents for both teams and position them on the field.

        Team composition (12 players as per rules):
        - 2 Front Fighters
        - 3 Heavy Hitters
        - 1 Runner
        - 6 Supporters
        """
        # Define roles for 12-player teams (simplified from 27 in full rules)
        roles = (
            ["front_fighter"] * 2 +
            ["heavy_hitter"] * 3 +
            ["runner"] * 1 +
            ["supporter"] * 6
        )

        for team in [0, 1]:
            # Starting positions: team 0 on left, team 1 on right
            start_x = self.field_width * 0.25 if team == 0 else self.field_width * 0.75

            for i in range(min(self.n_players_per_team, len(roles))):
                # Spread players vertically
                y_pos = (i + 1) * self.field_height / (self.n_players_per_team + 1)

                # Create player with role-based attributes
                role = roles[i] if i < len(roles) else "supporter"
                player = TjostballPlayer.create_with_role(
                    model=self,
                    team=team,
                    role=role,
                    random_generator=self.random
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

    def check_goal_scored(self):
        """
        Check if a goal has been scored.
        A goal is scored when a player carries the ball into the opponent's goal zone.
        Returns True if a goal was scored, False otherwise.
        """
        if self.ball_holder is None:
            return False

        player = self.ball_holder
        ball_x, ball_y = self.ball_position

        # Check left goal (Team 1 scores here)
        if (self.left_goal["x_min"] <= ball_x <= self.left_goal["x_max"] and
            self.left_goal["y_min"] <= ball_y <= self.left_goal["y_max"]):
            # Ball is in left goal zone
            if player.team == 1:  # Team 1 is attacking this goal
                self.score[1] += 1
                self.last_scorer = player
                print(f"GOAL! Team 1 scores! Player {player.unique_id} (role: {player.role})")
                print(f"Score: Team 0: {self.score[0]}, Team 1: {self.score[1]}")
                self.reset_after_goal()
                return True

        # Check right goal (Team 0 scores here)
        if (self.right_goal["x_min"] <= ball_x <= self.right_goal["x_max"] and
            self.right_goal["y_min"] <= ball_y <= self.right_goal["y_max"]):
            # Ball is in right goal zone
            if player.team == 0:  # Team 0 is attacking this goal
                self.score[0] += 1
                self.last_scorer = player
                print(f"GOAL! Team 0 scores! Player {player.unique_id} (role: {player.role})")
                print(f"Score: Team 0: {self.score[0]}, Team 1: {self.score[1]}")
                self.reset_after_goal()
                return True

        return False

    def reset_after_goal(self):
        """Reset ball and players to starting positions after a goal."""
        # Reset ball to center
        self.ball_position = (self.field_width / 2, self.field_height / 2)
        self.ball_velocity = (0.0, 0.0)
        self.ball_holder = None

        # Reset players to starting positions
        team_0_players = [a for a in self.agents if isinstance(a, TjostballPlayer) and a.team == 0]
        team_1_players = [a for a in self.agents if isinstance(a, TjostballPlayer) and a.team == 1]

        # Team 0 starts on left
        for i, player in enumerate(team_0_players):
            y_pos = (i + 1) * self.field_height / (len(team_0_players) + 1)
            self.grid.move_agent(player, (self.field_width * 0.25, y_pos))

        # Team 1 starts on right
        for i, player in enumerate(team_1_players):
            y_pos = (i + 1) * self.field_height / (len(team_1_players) + 1)
            self.grid.move_agent(player, (self.field_width * 0.75, y_pos))

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

        # Check if a goal was scored
        self.check_goal_scored()

        # Advance all agents (Mesa 3.x uses built-in agent management)
        for agent in self.agents:
            agent.step()

        # Collect data
        self.datacollector.collect(self)
