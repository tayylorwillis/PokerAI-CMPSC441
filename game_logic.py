""""
Goals for game_logic:
generate player hands
assign hands to players
detect hand types (ace high)
get_hand()
initiate who starts (not our agent for now)
operate the changing of turns
take_turn() func
call()
fold()
raise()
user prompting for user turn
mode setting for bot v bot or bot v user?
initialize starting money, will use a var for now,
take prompt from user later
ace 14 for now, add is_ace later

NOT: (this is a note to self because I Stew 
struggle to remember what goes where and will
start putting everything here otherwise)
win likelihood for bot logic
turn logic/decision making for bot
"""

"""
A:14
K:13
Q:12
J:11
10:10...
"""

import random
import array

#class for card objects
class Card:
    def __init__(self):
        self.suit = 0
        self.rank = 0
        self.id = 0
        #self.is_ace = false

#generate a random card
def gen_card():
    card = Card()
    #every card in deck has unique id through 52, decipher which is which accordingly:
    card_num = random.randint(1, 52)
    card.id = card_num
    # modulo 13 to get rank, +1 to adjust for ace high
    card.rank = (card_num % 13) + 1
    #rank order irrelevant, but divided evenly
    if ( card_num >= 1 and card_num <= 13):
        card.suit = "hearts"
    if ( card_num >= 14 and card_num <= 26):
        card.suit = "diamonds"
    if ( card_num >= 27 and card_num <= 39):
        card.suit = "spades"
    if ( card_num >= 40 and card_num <= 52):
        card.suit = "clubs"
    '''
    if (card.rank == 14):
        card.is_ace = true
    '''
    return card

#generate a specific card (only used for testing)
def create_card(card_num):
    card = Card()
    card.id = card_num
    # modulo 13 to get rank, +1 to adjust for ace high
    card.rank = (card_num % 13) + 1
    #rank order irrelevant, but divided evenly
    if ( card_num >= 1 and card_num <= 13):
        card.suit = "hearts"
    if ( card_num >= 14 and card_num <= 26):
        card.suit = "diamonds"
    if ( card_num >= 27 and card_num <= 39):
        card.suit = "spades"
    if ( card_num >= 40 and card_num <= 52):
        card.suit = "clubs"
    '''
    if (card.rank == 14):
        card.is_ace = true
    '''
    return card


#hand generation func
def create_hands():
    #track undealt cards
    #deck = list(range(1, 53))
    dealt_cards = []
    hand1 = []
    hand2 = []
    i = 0
    #generate first hand
    while (i < 5):
        c = gen_card()
        #if new card has already been dealt, generate a new card until it is unique
        while (c.id in dealt_cards):
            c = gen_card()
        #deck.remove(c.id)
        dealt_cards.append(c.id)
        hand1.append(c)
        i = i + 1

    i = 0
    while (i < 5):
        c = gen_card()
        while (c.id in dealt_cards):
            c = gen_card()
        #deck.remove(c.id)
        dealt_cards.append(c.id)
        hand2.append(c)
        i = i + 1
    
    return hand1, hand2

def print_hand(hand):
    print(hand[0].suit, hand[0].rank, ", ", hand[1].suit, hand[1].rank, ", ", hand[2].suit, hand[2].rank,
           ", ", hand[3].suit, hand[3].rank, ", ", hand[4].suit, hand[4].rank)


# had to make full house detection its own func due to discrepencies between how pairs are handled
#hand type detection func
def hand_type(hand):
    ranks = [hand[0].rank, hand[1].rank, hand[2].rank, hand[3].rank, hand[4].rank]
    suits = [hand[0].suit, hand[1].suit, hand[2].suit, hand[3].suit, hand[4].suit]
    max_rank = max(ranks)
    is_flush = False
    is_straight = False
    has_pair = False
    pair_rank = 0
    has_three = False
    three_rank = 0
    has_two_pair = False
    second_pair_rank = 0
    has_four = False
    four_rank = 0
    three_cards = []

    #check for straight
    if (max_rank - 1 in ranks and max_rank - 2 in ranks and max_rank - 3 in ranks and 
        max_rank - 4 in ranks):
        is_straight = True
    #check for flush
    if (suits[0] == suits[1] and suits[0] == suits[2] and suits[0] == suits[3] and
        suits[0] == suits[4]):
        is_flush = True

    #check to see if pair is present, tracking what rank the pair is
    #if pair found, check to see if a three can also be made from that pair
    #if three found, check for four
    #if one pair found, look for second
    #if three found, reset two pair in case three detected as two pair
    ###NOT DONE: prevent false full house, get rid of pair that is part of three
    if (ranks[0] == ranks[1] or ranks[0] == ranks[2] or ranks[0] == ranks[3] or ranks[0] == ranks[4]):
        has_pair = True
        pair_rank = ranks[0]
        #check for three
        if (has_pair and ranks[0] == ranks[1] == ranks[2] or ranks[0] == ranks[1] == ranks[3] or 
            ranks[0] == ranks[1] == ranks[4] or ranks[0] == ranks[2] == ranks[3] or 
            ranks[0] == ranks[2] == ranks[4] or ranks[0] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            pair_rank = 0
            three_rank = ranks[0]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[0])
            if (ranks[0] == ranks[1]):
                three_cards.append(hand[1])
            if (ranks[0] == ranks[2]):
                three_cards.append(hand[2])
            if (ranks[0] == ranks[3]):
                three_cards.append(hand[3])
            if (ranks[0] == ranks[4]):
                three_cards.append(hand[4])
            #check for four
            if (has_three and ranks[0] == ranks[1] == ranks[2] == ranks[3] or
                ranks[0] == ranks[1] == ranks[2] == ranks[4] or
                ranks[0] == ranks[1] == ranks[3] == ranks[4] or
                ranks[0] == ranks[2] == ranks[3] == ranks[4]):
                has_three = False
                three_rank = 0
                has_four = True
                four_rank = ranks[0]
    #make sure cards used for pair are not in three
    if (hand[1] not in three_cards and (ranks[1] == ranks[2] or ranks[1] == ranks[3] or ranks[1] == ranks[4])):
        #if one pair already found, make first pair be second pair and new pair is first pair
        if (has_pair == True):
            has_two_pair = True
            second_pair_rank = pair_rank
        has_pair = True
        pair_rank = ranks[1]
        #check for three
        if (has_pair and ranks[1] == ranks[2] == ranks[3] or ranks[1] == ranks[2] == ranks[4] or 
            ranks[1] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            pair_rank = 0
            three_rank = ranks[1]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[1])
            if (ranks[1] == ranks[2]):
                three_cards.append(hand[2])
            if (ranks[1] == ranks[3]):
                three_cards.append(hand[3])
            if (ranks[1] == ranks[4]):
                three_cards.append(hand[4])
            #reset two pair info in case three has triggered two pair
            has_two_pair = False
            second_pair_rank = 0
            #check for four
            if (has_three and ranks[1] == ranks[2] == ranks[3] == ranks[4]):
                has_three = False
                three_rank = 0
                has_four = True
                four_rank = ranks[1]
    #make sure cards used for pair are not in three
    if (hand[2] not in three_cards and (ranks[2] == ranks[3] or ranks[2] == ranks[4])):
        #if one pair already found, make first pair be second pair and new pair is first pair
        if (has_pair == True):
            has_two_pair = True
            second_pair_rank = pair_rank
        has_pair = True
        pair_rank = ranks[2]
        #check for three
        if (has_pair and ranks[2] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            pair_rank = 0
            three_rank = ranks[2]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[2])
            three_cards.append(hand[3])
            three_cards.append(hand[4])
            #reset two pair info in case three has triggered two pair
            has_two_pair = False
            second_pair_rank = 0
    #make sure cards used for pair are not in three
    if (hand[3] not in three_cards and hand[4] not in three_cards and (ranks[3] == ranks[4])):
        #if one pair already found, make first pair be second pair and new pair is first pair
        if (has_pair == True):
            has_two_pair = True
            second_pair_rank = pair_rank
        has_pair = True
        pair_rank = ranks[3]

    # return hand type and relevant val in case of tied hand type and 
    # needing to compare ranks to determine winner
    if (is_flush and is_straight and max_rank == 14):
        return "Royal Flush", max_rank
    
    if (is_flush and is_straight):
        return "Straight Flush", max_rank
    
    if (has_four):
        return "Four of a Kind", four_rank

    is_house, house_three_rank = has_house(hand)
######COME BACK
    if (is_house):
        return "Full House", house_three_rank

    if (is_flush):
        return "Flush", max_rank

    if (is_straight):
        return "Straight", max_rank
    
    if (has_three):
        return "Three of a Kind", three_rank

    if (has_two_pair):
        return "Two Pair", max(pair_rank, second_pair_rank)

    if (has_pair):
        return "One Pair", pair_rank

    return "High Card", max_rank

def has_house(hand):
    ranks = [hand[0].rank, hand[1].rank, hand[2].rank, hand[3].rank, hand[4].rank]
    has_pair = False
    has_three = False
    three_rank = 0
    three_cards = []
    #check to see if pair is present
    #if pair found, check to see if a three can also be made from that pair
    ###NOT DONE: prevent false full house, get rid of pair that is part of three
    if (ranks[0] == ranks[1] or ranks[0] == ranks[2] or ranks[0] == ranks[3] or ranks[0] == ranks[4]):
        has_pair = True
        #check for three
        if (has_pair and ranks[0] == ranks[1] == ranks[2] or ranks[0] == ranks[1] == ranks[3] or 
            ranks[0] == ranks[1] == ranks[4] or ranks[0] == ranks[2] == ranks[3] or 
            ranks[0] == ranks[2] == ranks[4] or ranks[0] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            three_rank = ranks[0]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[0])
            if (ranks[0] == ranks[1]):
                three_cards.append(hand[1])
            if (ranks[0] == ranks[2]):
                three_cards.append(hand[2])
            if (ranks[0] == ranks[3]):
                three_cards.append(hand[3])
            if (ranks[0] == ranks[4]):
                three_cards.append(hand[4])
    #make sure cards used for pair are not in three
    if (hand[1] not in three_cards and (ranks[1] == ranks[2] or ranks[1] == ranks[3] or ranks[1] == ranks[4])):
        #check for three
        if (has_pair and ranks[1] == ranks[2] == ranks[3] or ranks[1] == ranks[2] == ranks[4] or 
            ranks[1] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            three_rank = ranks[1]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[1])
            if (ranks[1] == ranks[2]):
                three_cards.append(hand[2])
            if (ranks[1] == ranks[3]):
                three_cards.append(hand[3])
            if (ranks[1] == ranks[4]):
                three_cards.append(hand[4])
        # this section moved to after three check to prevent making has_pair false due to having 3,
        # in case that both true for house
        #if one pair already found, make first pair be second pair and new pair is first pair
        has_pair = True
    #make sure cards used for pair are not in three
    if (hand[2] not in three_cards and (ranks[2] == ranks[3] or ranks[2] == ranks[4])):
        #check for three
        if (has_pair and ranks[2] == ranks[3] == ranks[4]):
            has_pair = False
            has_three = True
            three_rank = ranks[2]
            #add cards to list of cards that make up three, to prevent false full houses
            three_cards.append(hand[2])
            three_cards.append(hand[3])
            three_cards.append(hand[4])
        #if one pair already found, make first pair be second pair and new pair is first pair
        # this section moved to after three check to prevent making has_pair false due to having 3,
        # in case that both true for house
        has_pair = True
    #make sure cards used for pair are not in three
    if (hand[3] not in three_cards and hand[4] not in three_cards and (ranks[3] == ranks[4])):
        #if one pair already found, make first pair be second pair and new pair is first pair
        has_pair = True

    if (has_three and has_pair):
        return True, three_rank
    else:
        return False, 0

    


##test four
'''
#four of a kind, 5th spot irrelevant
hand = [create_card(1), create_card(14), create_card(27), create_card(40), create_card(2)]
print(hand_type(hand))
#four of a kind, 4th spot irrelevant
hand = [create_card(1), create_card(14), create_card(27), create_card(2), create_card(40)]
print(hand_type(hand))
#four of a kind, 3th spot irrelevant
hand = [create_card(1), create_card(14), create_card(2), create_card(27), create_card(40)]
print(hand_type(hand))
#four of a kind, 2th spot irrelevant
hand = [create_card(1), create_card(2), create_card(14), create_card(27), create_card(40)]
print(hand_type(hand))
#four of a kind, 1th spot irrelevant
hand = [create_card(2), create_card(1), create_card(14), create_card(27), create_card(40)]
print(hand_type(hand))
'''
##test three

#three, 4th 5th irr
hand = [create_card(1), create_card(14), create_card(27), create_card(3), create_card(2)]
print(hand_type(hand))
#three, 3th 5th irr
hand = [create_card(1), create_card(14), create_card(2), create_card(27), create_card(3)]
print(hand_type(hand))
#three, 3th 4th irr
hand = [create_card(1), create_card(14), create_card(2), create_card(3), create_card(27)]
print(hand_type(hand))
#three, 2th 5th irr
hand = [create_card(1), create_card(2), create_card(14), create_card(27), create_card(3)]
print(hand_type(hand))
#three, 2th 4th irr
hand = [create_card(1), create_card(2), create_card(14), create_card(3), create_card(27)]
print(hand_type(hand))
#three, 2th 3th irr
hand = [create_card(1), create_card(2), create_card(3), create_card(14), create_card(27)]
print(hand_type(hand))
#three, 1th 5th irr
hand = [create_card(2), create_card(1), create_card(14), create_card(27), create_card(3)]
print(hand_type(hand))
#three, 1th 4th irr -----CURR FULL HOUSE
hand = [create_card(2), create_card(1), create_card(14), create_card(3), create_card(27)]
print(hand_type(hand))
#three, 1th 3th irr -----CURR FULL HOUSE
hand = [create_card(2), create_card(1), create_card(3), create_card(14), create_card(27)]
print(hand_type(hand))
#three, 1th 2th irr
hand = [create_card(2), create_card(3), create_card(1), create_card(14), create_card(27)]
print(hand_type(hand))

##test FULL HOUSE

#house, 4th 5th pair
hand = [create_card(1), create_card(14), create_card(27), create_card(15), create_card(2)]
print(hand_type(hand))
#house, 3th 5th pair
hand = [create_card(1), create_card(14), create_card(2), create_card(27), create_card(15)]
print(hand_type(hand))
#house, 3th 4th pair
hand = [create_card(1), create_card(14), create_card(2), create_card(15), create_card(27)]
print(hand_type(hand))
#house, 2th 5th pair
hand = [create_card(1), create_card(2), create_card(14), create_card(27), create_card(15)]
print(hand_type(hand))
#house, 2th 4th pair
hand = [create_card(1), create_card(2), create_card(14), create_card(15), create_card(27)]
print(hand_type(hand))
#house, 2th 3th pair
hand = [create_card(1), create_card(2), create_card(15), create_card(14), create_card(27)]
print(hand_type(hand))
#house, 1th 5th pair
hand = [create_card(2), create_card(1), create_card(14), create_card(27), create_card(15)]
print(hand_type(hand))
#house, 1th 4th pair
hand = [create_card(2), create_card(1), create_card(14), create_card(15), create_card(27)]
print(hand_type(hand))
#house, 1th 3th pair
hand = [create_card(2), create_card(1), create_card(15), create_card(14), create_card(27)]
print(hand_type(hand))
#house, 1th 2th pair
hand = [create_card(2), create_card(15), create_card(1), create_card(14), create_card(27)]
print(hand_type(hand))




