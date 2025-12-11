"""
Base AI player - Abstract base class for AI implementations

"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, List
import random


class BaseAIPlayer(ABC):
    """
    Abstract base class for AI poker players.
    """

    def __init__(self, name: str, money: int = 1000):
        """
        Initialize the AI player.

        Args:
            name: Player name (displayed in game)
            money: Starting chip stack (default: 1000)
        """
        self.name = name
        self.money = money
        self.start_money = money
        self.is_bot = True
        self.hand = []
        self.current_bet = 0
        self.is_folded = False
        self.is_active = True  # Player is still in the game

    def _calculate_willing_to_bet(self):
        """Calculate how much AI is willing to bet based on hand strength."""
        if not self.hand or len(self.hand) < 5:
            return 0
        from hand_evaluator import win_prob
        prob = win_prob(self.hand)
        return int(self.money * prob)

    def decide_action(self, game_state, player) -> Tuple[str, Optional[int]]:
        """
        Decide what action to take based on current game state.

        Args:
            game_state: Dict with game information:
                - pot: Current pot size
                - player_bet: Human player's current bet
                - opponent_bet: AI opponent's current bet
            player: Player object representing this AI, containing:
                - hand: Current hand
                - money: Current chip stack
                - current_bet: Current bet amount
                - is_folded: Folded status

        Returns:
            tuple: (action, amount) where:
                - action (str): 'call', 'raise', or 'fold'
                - amount (int|None): Raise amount if action is 'raise', None otherwise
        
        Call when: cost to win <= remainder willing to bet
        Fold when: cost to win >= remainder willing to bet
        Raise when: cost to win <= remainder willing to bet (rand 50/50 chance whether to call or raise)
        Hold when: cost to win >= remainder willing to bet
        Willing to bet = win_prob * remaining money
        amount_to_call is effectively cost of win at given turn
        """
        # Calculate willing to bet based on hand strength
        willing_to_bet = self._calculate_willing_to_bet()
        already_bet = self.start_money - self.money
        remaining_willing_to_bet = willing_to_bet - already_bet

        if remaining_willing_to_bet <= 0:
            return ("fold", None)

        # Get pot and betting info from game_state
        curr_pot = game_state.get("pot", 0)
        player_bet = game_state.get("player_bet", 0)
        opponent_bet = game_state.get("opponent_bet", 0)
        
        # Calculate amount needed to call
        amount_to_call = player_bet - opponent_bet
        
        # If amount_to_call is negative, we're ahead in betting
        if amount_to_call < 0:
            amount_to_call = 0

        # If willing to keep playing and call is available
        if amount_to_call > 0 and amount_to_call <= remaining_willing_to_bet:
            choices = ["call", "raise"]
            decision = random.choice(choices)
            
            if decision == "call":
                return ("call", None)
            else:  # raise
                raise_amount = random.randint(1, remaining_willing_to_bet)
                return ("raise", raise_amount)
        
        # If no call needed (we're matched or ahead)
        elif amount_to_call == 0:
            choices = ["hold", "raise"]
            decision = random.choice(choices)
            
            if decision == "hold":
                return ("call", None)  # "hold" maps to "call" with no amount
            else:  # raise
                raise_amount = random.randint(1, remaining_willing_to_bet)
                return ("raise", raise_amount)
        
        # Amount to call exceeds what we're willing to bet
        else:
            return ("fold", None)
        

    def get_strategy_name(self) -> str:
        """
        Get the name/description of this AI strategy.

        This should return a human-readable description of the AI's
        approach or personality. Used for logging and display purposes.

        Returns:
            str: Strategy name or description
        """
        strategy = "This AI agent's strategy is to evaluate the likelihood that its hand will win and make bets corresponding to this likelihood."
        return strategy
#here to helper curr working on

    def receive_hand(self, hand):
        """Assign a hand to the player"""
        self.hand = hand

    def reset_for_new_round(self):
        """Reset ai_player state for a new round"""
        self.hand = []
        self.current_bet = 0
        self.is_folded = False

    def place_bet(self, amount, pot=None):
        """Place a bet (deduct from money, add to current_bet)"""
        self.money -= amount
        self.current_bet += amount
        # Add to pot if pot instance is provided
        if pot:
            who = "opponent" if self.is_bot else "player"
            pot.add_bet(amount, who)
        return amount

    def call(self, pot):
        """Call the current bet (match opponent's bet)."""
        who = "opponent" if self.is_bot else "player"
        call_amt = pot.get_call_amount(who)
        if call_amt > 0:
            return self.place_bet(call_amt, pot)
        return 0

    def win_pot(self, pot_amount):
        """Add winnings to player's money"""
        self.money += pot_amount

    def __str__(self):
        return f"{self.name}: ${self.money} (Current bet: ${self.current_bet})"

    # ------------------- HELPER METHODS -------------------

    def _calculate_pot_odds(self, pot: int, bet_to_call: int) -> float:
        """
        Calculate pot odds for calling decision.

        Pot odds represent the ratio of the current pot to the cost of calling.
        Higher pot odds mean you're getting a better price to call.

        Args:
            pot: Current pot size
            bet_to_call: Amount needed to call

        Returns:
            float: Pot odds ratio (bet_to_call:pot)
                - Returns infinity if bet_to_call is 0
        """
        #currently not being used
        if bet_to_call == 0:
            return float('inf')
        if pot == 0:
            return float('inf')
        return bet_to_call / pot


    def _calculate_expected_value(self, pot: int, bet_to_call: int,
                                  win_probability: float) -> float:
        """
        Calculate expected value (EV) of calling.

        EV helps determine if calling is mathematically profitable in the long run.
        Positive EV means calling is profitable, negative EV means it's not.

        Args:
            pot: Current pot size
            bet_to_call: Amount needed to call
            win_probability: Estimated probability of winning (0.0 to 1.0)

        Returns:
            float: Expected value in chips
                - Positive = profitable to call
                - Negative = not profitable to call
        """
        #currently not being used
        pot_after_call = pot + bet_to_call
        expected_winnings = win_probability * pot_after_call
        expected_loss = (1 - win_probability) * bet_to_call
        return expected_winnings - expected_loss

    def _get_full_hand_info(self, hand):
        """
        Get complete information about a hand.

        Convenience method that returns all evaluation details in one call.
        Useful for LLM-based bots that need full context.

        Args:
            hand: Hand object

        Returns:
            dict: Complete hand information including:
                - ranking: Numerical strength (1-10)
                - value: Tie-breaker value
                - name: Human-readable name (e.g., "Full House")
        """
        from hand_evaluator import HandEvaluator
        ranking, value, name = HandEvaluator.evaluate(hand)
        return {
            'ranking': ranking,
            'value': value,
            'name': name
        }

    def bet_amount():
        """Choose how much to bet"""
        #NOT CURRENTLY BEING USED
        standard = 1000                         #since players all start with 1000, use this as point of comparison
        prob_win = win_prob(hand)                   #find likelihood of winning hand
        max_bet = int(self.money * prob_win)    #set max willing to bet as prob of win percent of remaining money

        amount = int(random()*max_bet)          #amount is random num up to max_bet
        return amount



    def __repr__(self):
        """String representation of the AI player."""
        return f"{self.__class__.__name__}('{self.name}', ${self.money})"