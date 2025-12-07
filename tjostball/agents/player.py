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
        role: Player role (e.g., "runner", "fighter", etc.)

        Physical attributes:
            speed: Movement speed
            strength: Physical power for tackles and holding ball
            stamina: Energy level (0-100)
            agility: Maneuverability and dodge ability

        Technical attributes:
            passing: Accuracy when passing the ball
            catching: Ability to receive passes
            kicking: Power and accuracy when kicking
            tackling: Ability to steal ball from opponents

        Mental attributes:
            decision_making: Quality of tactical decisions
            positioning: Ability to find good field positions
            awareness: Perception of game state

        position: Current position on the field (handled by Mesa grid)
        memory: List of recent events for decision making
    """

    def __init__(self, model, team, role=None,
                 speed=5.0, strength=5.0, stamina=100.0, agility=5.0,
                 passing=5.0, catching=5.0, kicking=5.0, tackling=5.0,
                 decision_making=5.0, positioning=5.0, awareness=5.0):
        """
        Initialize a Tjostball player agent.

        Args:
            model: The model instance the agent belongs to
            team: Team identifier (0 or 1)
            role: Player role (optional, e.g., "runner", "fighter")

            Physical:
                speed: Movement speed (default 5.0)
                strength: Physical power (default 5.0)
                stamina: Energy level (default 100.0)
                agility: Maneuverability (default 5.0)

            Technical:
                passing: Pass accuracy (default 5.0)
                catching: Receive ability (default 5.0)
                kicking: Kick power/accuracy (default 5.0)
                tackling: Steal ability (default 5.0)

            Mental:
                decision_making: Decision quality (default 5.0)
                positioning: Positioning ability (default 5.0)
                awareness: Game state perception (default 5.0)
        """
        super().__init__(model)
        self.team = team
        self.role = role
        self.state = PlayerState.POSITIONING

        # Physical attributes
        self.speed = speed
        self.strength = strength
        self.stamina = stamina
        self.max_stamina = stamina
        self.agility = agility

        # Technical attributes
        self.passing = passing
        self.catching = catching
        self.kicking = kicking
        self.tackling = tackling

        # Mental attributes
        self.decision_making = decision_making
        self.positioning = positioning
        self.awareness = awareness

        # Memory for decision making (extensible)
        self.memory = []

    @classmethod
    def create_with_role(cls, model, team, role, random_generator=None):
        """
        Create a player with role-based attribute presets.

        Roles based on Tjostball game rules:
        - front_fighter: High strength and tackling
        - heavy_hitter: Balanced strength, kicking
        - runner: High speed and agility
        - supporter: Balanced attributes

        Args:
            model: The model instance
            team: Team identifier (0 or 1)
            role: Role name string
            random_generator: Random number generator for variation

        Returns:
            TjostballPlayer instance with role-appropriate attributes
        """
        import random as rand
        rng = random_generator if random_generator else rand

        # Base attributes with some random variation
        def vary(base, variation=1.0):
            return base + rng.random() * variation - variation / 2

        if role == "front_fighter":
            return cls(
                model=model,
                team=team,
                role=role,
                # Physical - high strength, moderate speed
                speed=vary(4.5, 1.0),
                strength=vary(7.5, 1.0),
                stamina=vary(95, 10),
                agility=vary(4.0, 1.0),
                # Technical - excellent tackling
                passing=vary(4.0, 1.0),
                catching=vary(5.0, 1.0),
                kicking=vary(4.0, 1.0),
                tackling=vary(8.0, 1.0),
                # Mental
                decision_making=vary(5.0, 1.0),
                positioning=vary(6.0, 1.0),
                awareness=vary(5.0, 1.0)
            )
        elif role == "heavy_hitter":
            return cls(
                model=model,
                team=team,
                role=role,
                # Physical - strong and fairly fast
                speed=vary(5.5, 1.0),
                strength=vary(7.0, 1.0),
                stamina=vary(90, 10),
                agility=vary(5.0, 1.0),
                # Technical - good kicking
                passing=vary(5.0, 1.0),
                catching=vary(5.5, 1.0),
                kicking=vary(7.5, 1.0),
                tackling=vary(6.0, 1.0),
                # Mental
                decision_making=vary(5.5, 1.0),
                positioning=vary(5.5, 1.0),
                awareness=vary(5.0, 1.0)
            )
        elif role == "runner":
            return cls(
                model=model,
                team=team,
                role=role,
                # Physical - very fast and agile
                speed=vary(8.0, 1.0),
                strength=vary(4.0, 1.0),
                stamina=vary(85, 10),
                agility=vary(8.0, 1.0),
                # Technical - good catching
                passing=vary(6.0, 1.0),
                catching=vary(7.5, 1.0),
                kicking=vary(5.0, 1.0),
                tackling=vary(4.0, 1.0),
                # Mental
                decision_making=vary(6.5, 1.0),
                positioning=vary(6.0, 1.0),
                awareness=vary(7.0, 1.0)
            )
        elif role == "supporter":
            return cls(
                model=model,
                team=team,
                role=role,
                # Physical - balanced
                speed=vary(5.5, 1.0),
                strength=vary(5.5, 1.0),
                stamina=vary(100, 10),
                agility=vary(5.5, 1.0),
                # Technical - balanced
                passing=vary(6.0, 1.0),
                catching=vary(6.0, 1.0),
                kicking=vary(5.5, 1.0),
                tackling=vary(5.5, 1.0),
                # Mental - good awareness and positioning
                decision_making=vary(6.0, 1.0),
                positioning=vary(7.0, 1.0),
                awareness=vary(6.5, 1.0)
            )
        else:
            # Default balanced player
            return cls(
                model=model,
                team=team,
                role=role
            )

    def perceive(self):
        """
        Perceive the environment (ball location, nearby players).
        Returns detailed perception data including distances and game state.

        Returns:
            Dictionary with:
                - ball_pos: Ball position (x, y)
                - ball_distance: Distance to ball
                - ball_direction: Normalized direction to ball (dx, dy)
                - my_pos: Player's current position
                - has_ball: Whether this player has the ball
                - ball_holder: Which player has the ball (if any)
                - teammates: List of nearby teammates
                - opponents: List of nearby opponents
                - nearest_teammate: Closest teammate (or None)
                - nearest_opponent: Closest opponent (or None)
                - goal_pos: Position of opponent's goal
                - own_goal_pos: Position of own goal
        """
        perception = {
            "ball_pos": self.model.ball_position,
            "my_pos": self.pos,
            "has_ball": self.model.ball_holder == self,
            "ball_holder": self.model.ball_holder,
            "teammates": [],
            "opponents": [],
            "nearest_teammate": None,
            "nearest_opponent": None
        }

        # Calculate ball distance and direction
        if self.pos and self.model.ball_position:
            bx, by = self.model.ball_position
            mx, my = self.pos
            dx = bx - mx
            dy = by - my
            distance = (dx**2 + dy**2)**0.5

            perception["ball_distance"] = distance
            if distance > 0:
                perception["ball_direction"] = (dx / distance, dy / distance)
            else:
                perception["ball_direction"] = (0, 0)
        else:
            perception["ball_distance"] = float('inf')
            perception["ball_direction"] = (0, 0)

        # Goal positions (team 0 attacks right, team 1 attacks left)
        if self.team == 0:
            perception["goal_pos"] = (self.model.field_width, self.model.field_height / 2)
            perception["own_goal_pos"] = (0, self.model.field_height / 2)
        else:
            perception["goal_pos"] = (0, self.model.field_height / 2)
            perception["own_goal_pos"] = (self.model.field_width, self.model.field_height / 2)

        # Get nearby agents (vision radius based on awareness)
        vision_radius = 10 + self.awareness * 2  # Base 10, +2 per awareness point
        if self.pos:
            neighbors = self.model.grid.get_neighbors(
                self.pos,
                radius=vision_radius,
                include_center=False
            )

            min_teammate_dist = float('inf')
            min_opponent_dist = float('inf')

            for agent in neighbors:
                if isinstance(agent, TjostballPlayer):
                    # Calculate distance
                    dx = agent.pos[0] - self.pos[0]
                    dy = agent.pos[1] - self.pos[1]
                    dist = (dx**2 + dy**2)**0.5

                    if agent.team == self.team:
                        perception["teammates"].append(agent)
                        if dist < min_teammate_dist:
                            min_teammate_dist = dist
                            perception["nearest_teammate"] = agent
                    else:
                        perception["opponents"].append(agent)
                        if dist < min_opponent_dist:
                            min_opponent_dist = dist
                            perception["nearest_opponent"] = agent

        return perception

    def update_state(self, perception):
        """
        Update FSM state based on current perception.

        State transitions:
        - DEFENDING: Opponent has ball or ball is in defensive zone
        - ATTACKING: Team has ball and player is advancing
        - SUPPORTING: Team has ball but player doesn't have it
        - POSITIONING: Default state, no clear threat or opportunity
        """
        ball_holder = perception["ball_holder"]
        has_ball = perception["has_ball"]
        ball_distance = perception["ball_distance"]

        if ball_holder:
            if ball_holder.team == self.team:
                # Teammate has ball
                if has_ball:
                    self.state = PlayerState.ATTACKING
                else:
                    self.state = PlayerState.SUPPORTING
            else:
                # Opponent has ball
                self.state = PlayerState.DEFENDING
        else:
            # Ball is loose - always try to attack it
            # This ensures players actively pursue the ball
            self.state = PlayerState.ATTACKING

    def decide(self, perception):
        """
        Decide next action based on FSM state and perception.

        Args:
            perception: Dictionary of perceived environment data

        Returns:
            Action dictionary with type and parameters
        """
        # Update state based on perception
        self.update_state(perception)

        # Decide action based on current state
        if self.state == PlayerState.DEFENDING:
            return self._decide_defending(perception)
        elif self.state == PlayerState.ATTACKING:
            return self._decide_attacking(perception)
        elif self.state == PlayerState.SUPPORTING:
            return self._decide_supporting(perception)
        else:  # POSITIONING
            return self._decide_positioning(perception)

    def _decide_defending(self, perception):
        """Decide action when in DEFENDING state."""
        ball_holder = perception["ball_holder"]
        nearest_opponent = perception["nearest_opponent"]

        # If opponent has ball and is close, try to tackle
        if ball_holder and ball_holder.team != self.team:
            if self.pos:
                dx = ball_holder.pos[0] - self.pos[0]
                dy = ball_holder.pos[1] - self.pos[1]
                distance = (dx**2 + dy**2)**0.5

                if distance < 3.0:
                    return {"type": "tackle", "target": ball_holder}
                else:
                    # Move toward ball carrier
                    return {"type": "move", "direction": (dx, dy)}

        # Otherwise, move to intercept ball
        if perception["ball_pos"] and self.pos:
            dx, dy = perception["ball_direction"]
            return {"type": "move", "direction": (dx * perception["ball_distance"],
                                                  dy * perception["ball_distance"])}

        return {"type": "idle"}

    def _decide_attacking(self, perception):
        """Decide action when in ATTACKING state."""
        has_ball = perception["has_ball"]
        goal_pos = perception["goal_pos"]

        if has_ball and self.pos:
            # Player has the ball
            gx, gy = goal_pos
            mx, my = self.pos
            goal_distance = ((gx - mx)**2 + (gy - my)**2)**0.5

            # If close to goal, kick it
            if goal_distance < 20:
                return {"type": "kick", "target": goal_pos}

            # If teammate is in better position, pass
            nearest_teammate = perception["nearest_teammate"]
            if nearest_teammate and nearest_teammate.pos:
                tx, ty = nearest_teammate.pos
                teammate_goal_dist = ((gx - tx)**2 + (gy - ty)**2)**0.5

                # Pass if teammate is closer to goal and within range
                if teammate_goal_dist < goal_distance - 10:
                    teammate_dist = ((tx - mx)**2 + (ty - my)**2)**0.5
                    if teammate_dist < 20:
                        return {"type": "pass", "target": nearest_teammate}

            # Otherwise, move toward goal
            return {"type": "move", "direction": (gx - mx, gy - my)}
        else:
            # Don't have ball, move toward it
            if perception["ball_pos"] and self.pos:
                dx, dy = perception["ball_direction"]
                return {"type": "move", "direction": (dx * perception["ball_distance"],
                                                      dy * perception["ball_distance"])}

        return {"type": "idle"}

    def _decide_supporting(self, perception):
        """Decide action when in SUPPORTING state."""
        ball_holder = perception["ball_holder"]
        goal_pos = perception["goal_pos"]

        if self.pos and ball_holder and ball_holder.pos:
            # Move to open space between ball carrier and goal
            bx, by = ball_holder.pos
            gx, gy = goal_pos

            # Position ahead of ball carrier toward goal
            target_x = bx + (gx - bx) * 0.4
            target_y = by + (gy - by) * 0.4

            dx = target_x - self.pos[0]
            dy = target_y - self.pos[1]

            return {"type": "move", "direction": (dx, dy)}

        return {"type": "idle"}

    def _decide_positioning(self, perception):
        """Decide action when in POSITIONING state."""
        goal_pos = perception["goal_pos"]
        own_goal_pos = perception["own_goal_pos"]

        if self.pos:
            # Move to defensive position between own goal and center field
            ogx, ogy = own_goal_pos
            center_x = self.model.field_width / 2
            center_y = self.model.field_height / 2

            # Position at 2/3 between own goal and center
            target_x = ogx + (center_x - ogx) * 0.66
            target_y = ogy + (center_y - ogy) * 0.66

            dx = target_x - self.pos[0]
            dy = target_y - self.pos[1]

            # Only move if far from target position
            distance = (dx**2 + dy**2)**0.5
            if distance > 5.0:
                return {"type": "move", "direction": (dx, dy)}

        return {"type": "idle"}

    def would_collide(self, new_pos, min_distance=3.0):
        """
        Check if moving to new_pos would cause a collision with other players.

        Args:
            new_pos: Tuple (x, y) of the proposed new position
            min_distance: Minimum allowed distance between players

        Returns:
            True if collision would occur, False otherwise
        """
        new_x, new_y = new_pos

        # Check all other players
        for agent in self.model.agents:
            if isinstance(agent, TjostballPlayer) and agent != self:
                other_x, other_y = agent.pos
                dx = new_x - other_x
                dy = new_y - other_y
                distance = (dx**2 + dy**2)**0.5

                if distance < min_distance:
                    return True

        return False

    def execute_action(self, action):
        """
        Execute the decided action.

        Args:
            action: Dictionary describing the action to take
        """
        action_type = action["type"]

        if action_type == "move":
            self._execute_move(action)
        elif action_type == "pass":
            self._execute_pass(action)
        elif action_type == "kick":
            self._execute_kick(action)
        elif action_type == "tackle":
            self._execute_tackle(action)
        # "idle" or unknown actions do nothing

    def _execute_move(self, action):
        """Execute a movement action."""
        if not self.pos:
            return

        dx, dy = action["direction"]

        # Normalize and scale by speed (modified by agility)
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            effective_speed = self.speed * (1 + self.agility / 20)  # Agility bonus
            move_x = dx / dist * min(effective_speed, dist)
            move_y = dy / dist * min(effective_speed, dist)

            new_x = self.pos[0] + move_x
            new_y = self.pos[1] + move_y

            # Clamp to field boundaries (positions must be strictly less than width/height)
            new_x = max(0.01, min(self.model.field_width - 0.01, new_x))
            new_y = max(0.01, min(self.model.field_height - 0.01, new_y))

            # Only move if it won't cause a collision
            if not self.would_collide((new_x, new_y)):
                self.model.grid.move_agent(self, (new_x, new_y))

    def _execute_pass(self, action):
        """Execute a pass action."""
        if not self.pos or self.model.ball_holder != self:
            return

        target = action["target"]
        if not target or not target.pos:
            return

        # Calculate distance to target
        dx = target.pos[0] - self.pos[0]
        dy = target.pos[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5

        # Pass accuracy based on passing skill and distance
        base_accuracy = self.passing / 10.0  # 0-1 scale
        distance_penalty = max(0, 1 - distance / 50.0)  # Penalty for long passes
        success_chance = base_accuracy * distance_penalty

        # Add randomness
        if self.model.random.random() < success_chance:
            # Successful pass
            self.model.ball_holder = None
            # Set ball velocity toward target
            speed_factor = 3.0
            self.model.ball_velocity = (dx / distance * speed_factor,
                                       dy / distance * speed_factor)
            # Store event in memory
            self.memory.append({"type": "pass", "success": True, "target": target})
        else:
            # Failed pass - ball goes in random direction
            self.model.ball_holder = None
            angle = self.model.random.random() * 6.28  # Random angle
            import math
            self.model.ball_velocity = (math.cos(angle) * 2.0, math.sin(angle) * 2.0)
            self.memory.append({"type": "pass", "success": False})

    def _execute_kick(self, action):
        """Execute a kick action."""
        if not self.pos or self.model.ball_holder != self:
            return

        target_pos = action["target"]
        if not target_pos:
            return

        # Calculate direction to target
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5

        if distance == 0:
            return

        # Kick power and accuracy based on kicking skill
        kick_power = 2.0 + self.kicking / 5.0  # Higher skill = faster kick
        accuracy = self.kicking / 10.0  # 0-1 scale

        # Add inaccuracy based on skill
        import math
        angle_error = (self.model.random.random() - 0.5) * (1 - accuracy) * 0.5
        base_angle = math.atan2(dy, dx)
        actual_angle = base_angle + angle_error

        # Release ball and set velocity
        self.model.ball_holder = None
        self.model.ball_velocity = (math.cos(actual_angle) * kick_power,
                                   math.sin(actual_angle) * kick_power)

        self.memory.append({"type": "kick", "target": target_pos})

    def _execute_tackle(self, action):
        """Execute a tackle action."""
        if not self.pos:
            return

        target = action["target"]
        if not target or not target.pos:
            return

        # Check if target has the ball
        if self.model.ball_holder != target:
            return

        # Calculate distance
        dx = target.pos[0] - self.pos[0]
        dy = target.pos[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5

        # Must be very close to tackle
        if distance > 3.0:
            return

        # Tackle success based on tackling skill vs target's strength
        attacker_skill = self.tackling + self.strength / 2
        defender_skill = target.strength + target.agility / 2

        success_chance = attacker_skill / (attacker_skill + defender_skill)

        if self.model.random.random() < success_chance:
            # Successful tackle - steal the ball
            self.model.ball_holder = self
            self.memory.append({"type": "tackle", "success": True, "target": target})
        else:
            # Failed tackle - ball becomes loose
            self.model.ball_holder = None
            # Ball bounces away
            import math
            angle = self.model.random.random() * 6.28
            self.model.ball_velocity = (math.cos(angle) * 1.5, math.sin(angle) * 1.5)
            self.memory.append({"type": "tackle", "success": False})

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
