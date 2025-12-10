"""
Base AI player - Abstract base class for AI implementations

"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, List
from hand_evaluator import win_prob
from app import get_game_state


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
        #very naive, change later
        self.willing_to_bet = int(self.money * win_prob(hand))    #set max willing to bet as (prob of win)percent of remaining money

    @abstractmethod
    def decide_action(self, game_state, player) -> Tuple[str, Optional[int]]:
        """
        Decide what action to take based on current game state.

        Args:
            game_state: GameState object with full game information including:
                - Current pot size
                - Current betting round
                - Other players' states
                - Betting manager
            player: Player object representing this AI, containing:
                - Current hand
                - Current chip stack
                - Current bet amount
                - Status (folded, all-in, etc.)

        Returns:
            tuple: (action, amount) where:
                - action (str): 'call', 'raise', or 'fold'
                - amount (int|None): Raise amount if action is 'raise', None otherwise
        """
        '''
        Call when: cost to win <= remainder willing to bet
        Fold when: cost to win >= remainder willing to bet
        Raise when: cost to win <= remainder willing to bet (rand 50/50 chance whether to call or raise)
        Hold when: cost to win >= remainder willing to bet
        Willing to bet = win_prob
        amount_to_call is effectively cost of win at given turn
        '''
        state = json.loads(get_game_state())
        amount_bet = 
        curr_pot = state["pot"]
        if (state[player["held"]] == False):
            amount_to_call = state[player["current_bet"]] - state[opponent["current_bet"]]
        if (state[player["held"]] == True):
            amount_to_call = 0              #call is not appropriate here
        if (amount_to_call > 0 and amount_to_call
        
        pot_odds = _calculate_pot_odds(self, curr_pot, amount_to_call)

        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name/description of this AI strategy.

        This should return a human-readable description of the AI's
        approach or personality. Used for logging and display purposes.

        Returns:
            str: Strategy name or description
        """
        pass

    # ------------------- HELPER METHODS -------------------

    def _get_hand_strength(self, hand) -> int:
        """
        Evaluate hand strength using the HandEvaluator.

        This provides a quick way to get a numerical rating of hand strength
        without needing to understand the full evaluation system.

        Args:
            hand: Hand object containing cards

        Returns:
            int: Hand strength ranking (1-10) where:
                1 = High Card (weakest)
                2 = One Pair
                3 = Two Pair
                4 = Three of a Kind
                5 = Straight
                6 = Flush
                7 = Full House
                8 = Four of a Kind
                9 = Straight Flush
                10 = Royal Flush (strongest)
        """
        from hand_evaluator import HandEvaluator
        ranking, _, _ = HandEvaluator.evaluate(hand)
        return ranking

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
        if bet_to_call == 0:
            return float('inf')
        if pot == 0:
            return float('inf')
        return bet_to_call / pot

    def _get_available_actions(self, player, current_bet: int) -> List[str]:
        """
        Determine which actions are legally available to the player.

        Args:
            player: Player object to check
            current_bet: Current bet that must be matched

        Returns:
            list: Available actions, always includes 'fold', may include
                'call' and/or 'raise' depending on chip stack
        """
        actions = ['fold']  # Can always fold

        amount_to_call = current_bet - player.current_bet

        # Can call if has enough money
        if player.can_bet(amount_to_call):
            actions.append('call')

        # Can raise if has money beyond the call amount
        if player.money > amount_to_call:
            actions.append('raise')

        return actions

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
        standard = 1000                         #since players all start with 1000, use this as point of comparison
        prob_win = win_prob(hand)                   #find likelihood of winning hand
        max_bet = int(self.money * prob_win)    #set max willing to bet as prob of win percent of remaining money


        


        amount = int(random()*max_bet)          #amount is random num up to max_bet
        return amount

    def place_bet(self):
        """Place a bet (deduct from money, add to current_bet)"""
        amount = bet_amount()
        if amount > self.money:
            amount = self.money  # All-in
        self.money -= amount
        self.current_bet += amount
        return amount

    #win_prob can be used instead of this for greater accuracy
    def _estimate_win_probability_simple(self, hand_strength: int) -> float:
        """
        Get a rough estimate of win probability based on hand strength.

        This is a simplified heuristic. For more accurate probabilities,
        implement Monte Carlo simulation or use lookup tables.

        Args:
            hand_strength: Hand ranking (1-10)

        Returns:
            float: Estimated win probability (0.0 to 1.0)
        """
        # Simple lookup table for rough estimates
        probabilities = {
            10: 0.999,  # Royal Flush - almost always wins
            9: 0.95,  # Straight Flush
            8: 0.90,  # Four of a Kind
            7: 0.85,  # Full House
            6: 0.75,  # Flush
            5: 0.65,  # Straight
            4: 0.55,  # Three of a Kind
            3: 0.45,  # Two Pair
            2: 0.35,  # One Pair
            1: 0.20  # High Card
        }
        return probabilities.get(hand_strength, 0.5)

    def __repr__(self):
        """String representation of the AI player."""
        return f"{self.__class__.__name__}('{self.name}', ${self.money})"