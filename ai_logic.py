"""
AI bot - Basic AI implementation with random decisions
"""

import random
from ai_player import BaseAIPlayer


class AIBot(BaseAIPlayer):
    """
    AI bot that makes decisions based on basic hand strength
    with some randomness added.
    """

    def __init__(self, money=1000, aggression=0.5):
        """
        Initialize bot.

        Args:
            money: Starting money
            aggression: Aggression level 0.0-1.0 (higher = more likely to raise)
        """
        super().__init__(money)
        self.aggression = max(0.0, min(1.0, aggression))

    def decide_action(self, game_state, player):
        """
        Decide action based on hand strength and randomness.

        Args:
            game_state: GameState object
            player: This player's Player object

        Returns:
            tuple: (action, amount)
        """
        hand_strength = self._get_hand_strength(player.hand)
        pot = game_state.betting_manager.get_pot()
        current_bet = game_state.betting_manager.current_round.current_bet
        amount_to_call = current_bet - player.current_bet

        available_actions = self._get_available_actions(player, current_bet)

        if hand_strength >= 7:  # full house or better
            if 'raise' in available_actions and random.random() < 0.8:
                raise_amount = self._calculate_raise_amount(player, pot, 'strong')
                return 'raise', raise_amount
            elif 'call' in available_actions:
                return 'call', None

        elif hand_strength >= 4:  # three of a kind or better
            if 'raise' in available_actions and random.random() < (0.5 + self.aggression * 0.3):
                raise_amount = self._calculate_raise_amount(player, pot, 'medium')
                return 'raise', raise_amount
            elif 'call' in available_actions:
                return 'call', None

        elif hand_strength >= 2:  # pair or better
            if 'call' in available_actions and random.random() < 0.6:
                return 'call', None
            elif 'raise' in available_actions and random.random() < self.aggression:
                # Bluff
                raise_amount = self._calculate_raise_amount(player, pot, 'weak')
                return 'raise', raise_amount

        else:  # high card
            if 'call' in available_actions and amount_to_call == 0:
                return 'call', None
            elif 'raise' in available_actions and random.random() < (self.aggression * 0.3):
                raise_amount = self._calculate_raise_amount(player, pot, 'bluff')
                return 'raise', raise_amount

        if amount_to_call == 0 and 'call' in available_actions:
            return 'call', None
        return 'fold', None

    def _calculate_raise_amount(self, player, pot, strength):
        """
        Calculate how much to raise based on situation.

        Args:
            player: Player object
            pot: Current pot size
            strength: 'strong', 'medium', 'weak', or 'bluff'

        Returns:
            int: Raise amount
        """
        max_raise = player.money // 4  # never raise more than 1/4 of stack

        if strength == 'strong':
            # raise 30-50% of pot
            base_raise = int(pot * random.uniform(0.3, 0.5))
        elif strength == 'medium':
            # raise 20-40% of pot
            base_raise = int(pot * random.uniform(0.2, 0.4))
        elif strength == 'weak':
            # raise 10-25% of pot
            base_raise = int(pot * random.uniform(0.1, 0.25))
        else:  # bluff
            # small raise 5-15% of pot
            base_raise = int(pot * random.uniform(0.05, 0.15))

        raise_amount = max(10, base_raise)

        raise_amount = min(raise_amount, max_raise)

        return raise_amount

    def get_strategy_name(self):
        """Get strategy description."""
        return f"AI Bot (Aggression: {self.aggression:.1f})"