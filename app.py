from flask import Flask, render_template, jsonify, request
from game_logic import Pot, gen_card
from player import Player
from deck import Deck
from hand_evaluator import HandEvaluator

app = Flask(__name__)

game_pot = Pot()
player = Player("You", 1000, is_bot=False)
opponent = Player("Opponent", 1000, is_bot=True)
deck = Deck()
evaluator = HandEvaluator()
game_status = "waiting"
player_held = False
opponent_held = False


def card_to_dict(card):
    rank_names = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
    rank_str = rank_names.get(card.rank, str(card.rank))
    suit_codes = {
        'hearts': 'H',
        'diamonds': 'D',
        'spades': 'S',
        'clubs': 'C'
    }
    suit_code = suit_codes.get(card.suit.lower(), 'S')
    if rank_str == '10':
        card_code = f"0{suit_code}"
    else:
        card_code = f"{rank_str}{suit_code}"
    
    image_url = f"https://deckofcardsapi.com/static/img/{card_code}.png"
    
    return {
        'rank': rank_str,
        'suit': card.suit,
        'image': image_url,
        'id': card.id
    }


def get_game_state():
    """Return current game state as JSON."""
    player_best = evaluator.evaluate_hand(player.hand) if player.hand else None
    opponent_best = evaluator.evaluate_hand(opponent.hand) if opponent.hand else None
    
    state = {
        'pot': game_pot.get_total(),
        'status': game_status,
        'player': {
            'name': player.name,
            'money': player.money,
            'current_bet': player.current_bet,
            'hole': [card_to_dict(c) for c in player.hand],
            'best': {
                'hand': player_best[0] if player_best else None,
                'rank': player_best[1] if player_best else None
            } if player_best else None
        },
        'opponent': {
            'name': opponent.name,
            'money': opponent.money,
            'current_bet': opponent.current_bet,
            'hole': [card_to_dict(c) for c in opponent.hand],
            'best': {
                'hand': opponent_best[0] if opponent_best else None,
                'rank': opponent_best[1] if opponent_best else None
            } if opponent_best else None
        },
        'board': []
    }
    
    return state


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game and deal initial hands."""
    global game_status, player_held, opponent_held
    game_pot.reset()
    player.reset_for_new_round()
    opponent.reset_for_new_round()
    deck.reset()
    game_status = "playing"
    player_held = False
    opponent_held = False
    
    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))
    
    return jsonify(get_game_state())


@app.route('/api/new-hand', methods=['POST'])
def new_hand():
    """Start a new hand (keeps balances from previous game)."""
    global game_status, player_held, opponent_held
    
    game_pot.reset()
    player.reset_for_new_round()
    opponent.reset_for_new_round()
    deck.reset()
    game_status = "playing"
    player_held = False
    opponent_held = False
    
    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))
    
    return jsonify(get_game_state())


@app.route('/api/action', methods=['POST'])
def action():
    """Handle player actions: raise, hold, fold."""
    global game_status, player_held, opponent_held
    
    data = request.get_json()
    action_type = data.get('action')
    amount = data.get('amount', 0)
    
    if action_type == 'raise':
        if player.can_bet(amount):
            player.place_bet(amount, game_pot)
            player_held = False
            opponent.call(game_pot)
            opponent_held = True
    
    elif action_type == 'hold':
        player_held = True
        if not opponent_held:
            if game_pot.player_chips_in == game_pot.opponent_chips_in:
                opponent_held = True
    
    elif action_type == 'fold':
        player.is_folded = True
        opponent.win_pot(game_pot.get_total())
        game_status = "finished"
    
    state = get_game_state()
    
    if (player_held and opponent_held) or player.is_folded or opponent.is_folded:
        if not player.is_folded and not opponent.is_folded:
            player_result = evaluator.evaluate_hand(player.hand)
            opponent_result = evaluator.evaluate_hand(opponent.hand)
            player_hand_rank = evaluator.HAND_RANKINGS.get(player_result[0], 0)
            opponent_hand_rank = evaluator.HAND_RANKINGS.get(opponent_result[0], 0)
            if player_hand_rank > opponent_hand_rank:
                player.win_pot(game_pot.get_total())
                state['result'] = 'player'
            elif opponent_hand_rank > player_hand_rank:
                opponent.win_pot(game_pot.get_total())
                state['result'] = 'opponent'
            elif player_result[1] > opponent_result[1]:
                player.win_pot(game_pot.get_total())
                state['result'] = 'player'
            elif opponent_result[1] > player_result[1]:
                opponent.win_pot(game_pot.get_total())
                state['result'] = 'opponent'
            else:
                half_pot = game_pot.get_total() // 2
                player.win_pot(half_pot)
                opponent.win_pot(half_pot)
                state['result'] = 'tie'
        
        game_status = "finished"
        state['status'] = "finished"
    
    return jsonify(state)


if __name__ == '__main__':
    app.run(debug=True)
