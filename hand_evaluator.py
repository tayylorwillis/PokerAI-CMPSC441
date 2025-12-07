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