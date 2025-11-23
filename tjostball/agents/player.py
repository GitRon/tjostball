"""Player agent implementation for Tjostball simulation."""

from mesa import Agent
from enum import Enum


class PlayerState(Enum):
    """Finite State Machine states for player behavior."""
    DEFENDING = "defending"
    ATTACKING = "attacking"
    SUPPORTING = "supporting"
    POSITIONING = "positioning"


class TjostballPlayer(Agent):
    """
    A player agent in the Tjostball game.

    Attributes:
        team: Team identifier (0 or 1)
        state: Current FSM state
        speed: Player speed attribute
        strength: Player strength attribute
        stamina: Player stamina attribute
        position: Current position on the field (handled by Mesa grid)
    """

    def __init__(self, unique_id, model, team, speed=5.0, strength=5.0, stamina=100.0):
        """
        Initialize a Tjostball player agent.

        Args:
            unique_id: Unique identifier for the agent
            model: The model instance the agent belongs to
            team: Team identifier (0 or 1)
            speed: Player speed (default 5.0)
            strength: Player strength (default 5.0)
            stamina: Current stamina level (default 100.0)
        """
        super().__init__(unique_id, model)
        self.team = team
        self.state = PlayerState.POSITIONING
        self.speed = speed
        self.strength = strength
        self.stamina = stamina
        self.max_stamina = stamina

    def perceive(self):
        """
        Perceive the environment (ball location, nearby players).
        Returns basic perception data.
        """
        perception = {
            "ball_pos": self.model.ball_position,
            "my_pos": self.pos,
            "teammates": [],
            "opponents": []
        }

        # Get nearby agents
        if self.pos:
            neighbors = self.model.grid.get_neighbors(
                self.pos,
                moore=True,
                include_center=False,
                radius=10
            )

            for agent in neighbors:
                if isinstance(agent, TjostballPlayer):
                    if agent.team == self.team:
                        perception["teammates"].append(agent)
                    else:
                        perception["opponents"].append(agent)

        return perception

    def decide(self, perception):
        """
        Decide next action based on FSM state and perception.

        Args:
            perception: Dictionary of perceived environment data

        Returns:
            Action to take (simplified for basic setup)
        """
        # Simple decision logic - move toward ball
        if perception["ball_pos"] and self.pos:
            ball_x, ball_y = perception["ball_pos"]
            my_x, my_y = self.pos

            # Calculate direction toward ball
            dx = ball_x - my_x
            dy = ball_y - my_y

            return {"type": "move", "direction": (dx, dy)}

        return {"type": "idle"}

    def execute_action(self, action):
        """
        Execute the decided action.

        Args:
            action: Dictionary describing the action to take
        """
        if action["type"] == "move" and self.pos:
            dx, dy = action["direction"]

            # Normalize and scale by speed
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                move_x = dx / dist * min(self.speed, dist)
                move_y = dy / dist * min(self.speed, dist)

                new_x = self.pos[0] + move_x
                new_y = self.pos[1] + move_y

                # Clamp to field boundaries
                new_x = max(0, min(self.model.field_width, new_x))
                new_y = max(0, min(self.model.field_height, new_y))

                self.model.grid.move_agent(self, (new_x, new_y))

    def step(self):
        """
        Agent step function - called each simulation step.
        Implements the perception-decision-action cycle.
        """
        # Reduce stamina slightly each step
        self.stamina = max(0, self.stamina - 0.1)

        # Perception -> Decision -> Action cycle
        perception = self.perceive()
        action = self.decide(perception)
        self.execute_action(action)
