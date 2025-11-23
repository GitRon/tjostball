"""Ball agent for Tjostball simulation."""

from mesa import Agent


class Ball(Agent):
    """
    A ball agent in the Tjostball game.

    The ball is a passive agent - it doesn't make decisions or take actions.
    Its position is updated by the model's physics system.
    """

    def __init__(self, model):
        """
        Initialize the ball agent.

        Args:
            model: The model instance the agent belongs to
        """
        super().__init__(model)
        self.is_ball = True  # Easy identifier for rendering

    def step(self):
        """
        Ball doesn't take actions - its position is controlled by model physics.
        """
        pass  # Ball has no agency
