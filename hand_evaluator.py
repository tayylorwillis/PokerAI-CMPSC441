class HandEvaluator:
    """Evaluates poker hands and determines hand rankings."""

    # (higher = better)
    HAND_RANKINGS = {
        "High Card": 1,
        "One Pair": 2,
        "Two Pair": 3,
        "Three of a Kind": 4,
        "Straight": 5,
        "Flush": 6,
        "Full House": 7,
        "Four of a Kind": 8,
        "Straight Flush": 9,
        "Royal Flush": 10
    }

    @staticmethod
    def evaluate_hand(hand):
        """
        Evaluate a poker hand and return its type and rank.
        Args:
            hand: List of 5 Card objects
        Returns:
            tuple: (hand_type_string, rank_value)
        """
        ranks = [card.rank for card in hand]
        suits = [card.suit for card in hand]
        max_rank = max(ranks)

        # check for flush and straight
        is_flush = HandEvaluator._is_flush(suits)
        is_straight = HandEvaluator._is_straight(ranks, max_rank)

        rank_counts = HandEvaluator._count_ranks(hand)

        # check for pairs or three of a kind or four of a kind
        has_pair, pair_rank = HandEvaluator._has_pair(rank_counts)
        has_two_pair, second_pair_rank = HandEvaluator._has_two_pair(rank_counts, pair_rank)
        has_three, three_rank = HandEvaluator._has_three_of_kind(rank_counts)
        has_four, four_rank = HandEvaluator._has_four_of_kind(rank_counts)

        # determine hand type
        if is_flush and is_straight and max_rank == 14:
            return "Royal Flush", max_rank

        if is_flush and is_straight:
            return "Straight Flush", max_rank

        if has_four:
            return "Four of a Kind", four_rank

        if has_pair and has_three:
            return "Full House", three_rank

        if is_flush:
            return "Flush", max_rank

        if is_straight:
            return "Straight", max_rank

        if has_three:
            return "Three of a Kind", three_rank

        if has_two_pair:
            return "Two Pair", max(pair_rank, second_pair_rank)

        if has_pair:
            return "One Pair", pair_rank

        return "High Card", max_rank

    @staticmethod
    def _is_flush(suits):
        """Check if all cards have the same suit."""
        return all(suit == suits[0] for suit in suits)

    @staticmethod
    def _is_straight(ranks, max_rank):
        """Check if cards form a straight."""
        return (max_rank - 1 in ranks and
                max_rank - 2 in ranks and
                max_rank - 3 in ranks and
                max_rank - 4 in ranks)

    @staticmethod
    def _count_ranks(hand):
        """
        Count occurrences of each rank.
        Returns a list where index represents rank-1 and value is count.
        """
        rank_counts = [0] * 13
        for card in hand:
            rank_counts[card.rank - 1] += 1
        return rank_counts

    @staticmethod
    def _has_four_of_kind(rank_counts):
        """Check for four of a kind."""
        for rank, count in enumerate(rank_counts, start=1):
            if count == 4:
                return True, rank
        return False, 0

    @staticmethod
    def _has_three_of_kind(rank_counts):
        """Check for three of a kind."""
        for rank, count in enumerate(rank_counts, start=1):
            if count == 3:
                return True, rank
        return False, 0

    @staticmethod
    def _has_pair(rank_counts):
        """Check for a pair."""
        for rank, count in enumerate(rank_counts, start=1):
            if count == 2:
                return True, rank
        return False, 0

    @staticmethod
    def _has_two_pair(rank_counts, first_pair_rank):
        """Check for two pair."""
        for rank, count in enumerate(rank_counts, start=1):
            if count == 2 and rank != first_pair_rank:
                return True, rank
        return False, 0

    @staticmethod
    def compare_hands(hand1, hand2):
        """
        Compare two hands and return the winner.
        Args:
            hand1: List of 5 Card objects
            hand2: List of 5 Card objects
        Returns:
            int: 1 if hand1 wins, 2 if hand2 wins, 0 for tie
        """
        type1, rank1 = HandEvaluator.evaluate_hand(hand1)
        type2, rank2 = HandEvaluator.evaluate_hand(hand2)

        if HandEvaluator.HAND_RANKINGS[type1] > HandEvaluator.HAND_RANKINGS[type2]:
            return 1
        elif HandEvaluator.HAND_RANKINGS[type2] > HandEvaluator.HAND_RANKINGS[type1]:
            return 2

        if rank1 > rank2:
            return 1
        elif rank2 > rank1:
            return 2

        return 0  # Tie


def print_hand(hand):
    """
    Print a hand of cards.
    Args:
        hand: List of Card objects
    """
    card_strs = [f"{card.suit} {card.rank}" for card in hand]
    print(", ".join(card_strs))


def hand_type(hand):
    """
    Legacy function for backward compatibility.
    Evaluates a hand using HandEvaluator.
    Args:
        hand: List of 5 Card objects
    Returns:
        tuple: (hand_type_string, rank_value)
    """
    return HandEvaluator.evaluate_hand(hand)

def win_prob(hand):
    type, rank = HandEvaluator.evaluate_hand(hand)
    if (type == "Royal Flush"):
        return 1
    
    if (type == "Straight Flush"):
        if (rank == 13): #K
            prob = (2598960-4)/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598960-8)/2598960
            return prob
        if (rank == 11): #J
            prob = (2598960-12)/2598960
            return prob
        if (rank == 10):
            prob = (2598960-16)/2598960
            return prob
        if (rank == 9):
            prob = (2598960-20)/2598960
            return prob
        if (rank == 8):
            prob = (2598960-24)/2598960
            return prob
        if (rank == 7):
            prob = (2598960-28)/2598960
            return prob
        if (rank == 6):
            prob = (2598960-32)/2598960
            return prob
        if (rank == 5):
            prob = (2598960-36)/2598960
            return prob
        
    if (type == "Four of a Kind"):
        if (rank == 14): #A
            prob = (2598960-40-48*0)/2598960
            return prob
        if (rank == 13): #K
            prob = (2598960-40-48*1)/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598960-40-48*2)/2598960
            return prob
        if (rank == 11): #J
            prob = (2598960-40-48*3)/2598960
            return prob
        if (rank == 10):
            prob = (2598960-40-48*4)/2598960
            return prob
        if (rank == 9):
            prob = (2598960-40-48*5)/2598960
            return prob
        if (rank == 8):
            prob = (2598960-40-48*6)/2598960
            return prob
        if (rank == 7):
            prob = (2598960-40-48*7)/2598960
            return prob
        if (rank == 6):
            prob = (2598960-40-48*8)/2598960
            return prob
        if (rank == 5):
            prob = (2598960-40-48*9)/2598960
            return prob
        if (rank == 4):
            prob = (2598960-40-48*10)/2598960
            return prob
        if (rank == 3):
            prob = (2598960-40-48*11)/2598960
            return prob
        if (rank == 2):
            prob = (2598960-40-48*12)/2598960
            return prob
           
    if (type == "Full House"):
        if (rank == 13): #A
            prob = (2598344 -(312*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2598344 -(312*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2598344 -(312*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2598344 -(312*4))/2598960
            return prob
        if (rank == 10):
            prob = (2598344 -(312*5))/2598960
            return prob
        if (rank == 9):
            prob = (2598344 -(312*6))/2598960
            return prob
        if (rank == 8):
            prob = (2598344 -(312*7))/2598960
            return prob
        if (rank == 7):
            prob = (2598344 -(312*8))/2598960
            return prob
        if (rank == 6):
            prob = (2598344 -(312*9))/2598960
            return prob
        if (rank == 5):
            prob = (2598344 -(312*10))/2598960
            return prob
        if (rank == 4):
            prob = (2598344 -(312*11))/2598960
            return prob
        if (rank == 3):
            prob = (2598344 -(312*12))/2598960
            return prob
    
    if (type == "Flush"):
        if (rank == 13): #A
            prob = (2594600 -(572*0))/2598960
            return prob
        if (rank == 13): #K
            prob = (2594600 -(572*1))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2594600 -(572*2))/2598960
            return prob
        if (rank == 11): #J
            prob = (2594600 -(572*3))/2598960
            return prob
        if (rank == 10):
            prob = (2594600 -(572*4))/2598960
            return prob
        if (rank == 9):
            prob = (2594600 -(572*5))/2598960
            return prob
        if (rank == 8):
            prob = (2594600 -(572*6))/2598960
            return prob
        if (rank == 7):
            prob = (2594600 -(572*7))/2598960
            return prob
        if (rank == 6):
            prob = (2594600 -(572*8))/2598960
            return prob
        
    
    if (type == "Straight"):
        if (rank == 13): #A
            prob = (2589444 - (1020*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2589444 - (1020*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2589444 - (1020*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2589444 - (1020*4))/2598960
            return prob
        if (rank == 10):
            prob = (2589444 - (1020*5))/2598960
            return prob
        if (rank == 9):
            prob = (2589444 - (1020*6))/2598960
            return prob
        if (rank == 8):
            prob = (2589444 - (1020*7))/2598960
            return prob
        if (rank == 7):
            prob = (2589444 - (1020*8))/2598960
            return prob
        if (rank == 6):
            prob = (2589444 - (1020*9))/2598960
            return prob
        if (rank == 5):
            prob = (2589444 - (1020*10))/2598960
            return prob
        
    
    if (type == "Three of a Kind"):
        if (rank == 14): #A
            prob = (2579244 - (4224*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2579244 - (4224*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2579244 - (4224*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2579244 - (4224*4))/2598960
            return prob
        if (rank == 10):
            prob = (2579244 - (4224*5))/2598960
            return prob
        if (rank == 9):
            prob = (2579244 - (4224*6))/2598960
            return prob
        if (rank == 8):
            prob = (2579244 - (4224*7))/2598960
            return prob
        if (rank == 7):
            prob = (2579244 - (4224*8))/2598960
            return prob
        if (rank == 6):
            prob = (2579244 - (4224*9))/2598960
            return prob
        if (rank == 5):
            prob = (2579244 - (4224*10))/2598960
            return prob
        if (rank == 4):
            prob = (2579244 - (4224*11))/2598960
            return prob
        if (rank == 3):
            prob = (2579244 - (4224*12))/2598960
            return prob
        if (rank == 2):
            prob = (2579244 - (4224*13))/2598960
            return prob
    
    if (type == "Two Pair"):
        if (rank == 14): #A
            prob = (2524332 - (10296*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2524332 - (10296*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2524332 - (10296*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2524332 - (10296*4))/2598960
            return prob
        if (rank == 10):
            prob = (2524332 - (10296*5))/2598960
            return prob
        if (rank == 9):
            prob = (2524332 - (10296*6))/2598960
            return prob
        if (rank == 8):
            prob = (2524332 - (10296*7))/2598960
            return prob
        if (rank == 7):
            prob = (2524332 - (10296*8))/2598960
            return prob
        if (rank == 6):
            prob = (2524332 - (10296*9))/2598960
            return prob
        if (rank == 5):
            prob = (2524332 - (10296*10))/2598960
            return prob
        if (rank == 4):
            prob = (2524332 - (10296*11))/2598960
            return prob
        if (rank == 3):
            prob = (2524332 - (10296*12))/2598960
            return prob
        
    
    if (type == "One Pair"):
        if (rank == 14): #A
            prob = (2400780 - (84480*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (2400780 - (84480*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (2400780 - (84480*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (2400780 - (84480*4))/2598960
            return prob
        if (rank == 10):
            prob = (2400780 - (84480*5))/2598960
            return prob
        if (rank == 9):
            prob = (2400780 - (84480*6))/2598960
            return prob
        if (rank == 8):
            prob = (2400780 - (84480*7))/2598960
            return prob
        if (rank == 7):
            prob = (2400780 - (84480*8))/2598960
            return prob
        if (rank == 6):
            prob = (2400780 - (84480*9))/2598960
            return prob
        if (rank == 5):
            prob = (2400780 - (84480*10))/2598960
            return prob
        if (rank == 4):
            prob = (2400780 - (84480*11))/2598960
            return prob
        if (rank == 3):
            prob = (2400780 - (84480*12))/2598960
            return prob
        if (rank == 2):
            prob = (2400780 - (84480*13))/2598960
            return prob
    
    if (type == "High Card"):
        if (rank == 14): #A
            prob = (1302540 - (108545*1))/2598960
            return prob
        if (rank == 13): #K
            prob = (1302540 - (108545*2))/2598960
            return prob
        if (rank == 12): #Q
            prob = (1302540 - (108545*3))/2598960
            return prob
        if (rank == 11): #J
            prob = (1302540 - (108545*4))/2598960
            return prob
        if (rank == 10):
            prob = (1302540 - (108545*5))/2598960
            return prob
        if (rank == 9):
            prob = (1302540 - (108545*6))/2598960
            return prob
        if (rank == 8):
            prob = (1302540 - (108545*7))/2598960
            return prob
        if (rank == 7):
            prob = (1302540 - (108545*8))/2598960
            return prob
        if (rank == 6):
            prob = (1302540 - (108545*9))/2598960
            return prob
        if (rank == 5):
            prob = (1302540 - (108545*10))/2598960
            return prob
        if (rank == 4):
            prob = (1302540 - (108545*11))/2598960
            return prob
        if (rank == 3):
            prob = (1302540 - (108545*12))/2598960
            return prob