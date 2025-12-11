from flask import Flask, render_template, jsonify, request
from game_logic import Pot, gen_card
from player import Player
from deck import Deck
from hand_evaluator import HandEvaluator
from ai_player import BaseAIPlayer

app = Flask(__name__)

game_pot = Pot()
player = Player("You", 1000, is_bot=False)
opponent = BaseAIPlayer("Opponent", 1000, is_bot=True)
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
            'held': player_held,
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
            'held': opponent_held,
            'hole': [card_to_dict(c) for c in opponent.hand],
            'best': {
                'hand': opponent_best[0] if opponent_best else None,
                'rank': opponent_best[1] if opponent_best else None
            } if opponent_best else None
        },
        'board': []
    }
    
    return state


def card_to_dict(card, hidden=False):
    if hidden:
        return {"hidden": True}
    rank_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K', 10: '0'}
    rank_code = rank_map.get(card.rank, str(card.rank))
    
    suit_map = {'hearts': 'H', 'diamonds': 'D', 'spades': 'S', 'clubs': 'C'}
    suit_letter = suit_map.get(card.suit, 'H')
    
    img_url = f"https://deckofcardsapi.com/static/img/{rank_code}{suit_letter}.png"
    return {
        "rank": card.rank,
        "suit": card.suit,
        "image": img_url,
    }
def evaluate_winner(state):
    player = state["player"]
    opponent = state["opponent"]
    result = HandEvaluator.compare_hands(player.hand, opponent.hand)
    
    p_best = HandEvaluator.evaluate_hand(player.hand)
    o_best = HandEvaluator.evaluate_hand(opponent.hand)
    
    if result == 1:
        winner = "player"
    elif result == 2:
        winner = "opponent"
    else:
        winner = "tie"

    return winner, p_best, o_best

def make_state():
    deck = Deck()
    deck.reset()

    player = Player("You", starting_money=1000, is_bot=False)
    opponent = Player("Opponent", starting_money=1000, is_bot=True)
    
    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))

    state = {
        "deck": deck,
        "player": player,
        "opponent": opponent,
        "pot": 0,
        "player_held": False,
        "opponent_held": False,
        "status": "playing",
        "result": None,
    }
    return state


GAME_STATE = make_state()


def reset_hand_keep_balances():
    """Reset hand/pot but keep player balances intact."""
    global GAME_STATE
    if not GAME_STATE:
        GAME_STATE = make_state()
        return GAME_STATE

    deck = Deck()
    deck.reset()
    GAME_STATE["deck"] = deck

    player = GAME_STATE["player"]
    opponent = GAME_STATE["opponent"]

    player.reset_for_new_round()
    opponent.reset_for_new_round()

    GAME_STATE.update({
        "pot": 0,
        "player_held": False,
        "opponent_held": False,
        "status": "playing",
        "result": None,
    })

    player.receive_hand(deck.deal_hand(5))
    opponent.receive_hand(deck.deal_hand(5))
    return GAME_STATE


def serialize_state(state, reveal_opponent=False):
    player = state["player"]
    opponent = state["opponent"]

    if len(player.hand) == 5 and len(opponent.hand) == 5:
        winner, p_best, o_best = evaluate_winner(state)
    else:
        winner = None
        p_best = ("—", 0)
        o_best = ("—", 0)

    return {
        "pot": state["pot"],
        "status": state["status"],
        "result": state["result"],
        "player": {
            "money": player.money,
            "current_bet": player.current_bet,
            "hole": [card_to_dict(c) for c in player.hand],
            "best": {"hand": p_best[0], "rank": p_best[1]},
            "held": state.get("player_held", False),
        },
        "opponent": {
            "money": opponent.money,
            "current_bet": opponent.current_bet,
            "hole": [card_to_dict(c, hidden=not reveal_opponent) for c in opponent.hand],
            "best": {"hand": o_best[0], "rank": o_best[1]},
            "held": state.get("opponent_held", False),
        },
        "winner_preview": winner,
    }


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

@app.route('/api/ai_action', methods=['POST'])
def ai_action():
    """Handle ai_player actions: raise, hold, fold, call"""
    global game_status, player_held, opponent_held
    
    #data = request.get_json()
    action_type, amount = opponent.decide_action(game_status)
    
    if action_type == 'raise':
        opponent.place_bet(amount, game_pot)
        opponent_held = False
        player.call(game_pot)           #does this force player to call??? what if they don't want to
        player_held = True
    
    elif action_type == 'hold':
        opponent_held = True
        if not player_held:
            if game_pot.opponent_chips_in == game_pot.player_chips_in:
                player_held = True
    
    elif action_type == 'fold':
        opponent.is_folded = True
        player.win_pot(game_pot.get_total())
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

@app.post('/api/new-game')
def api_new_game():
    global GAME_STATE
    GAME_STATE = make_state()
    return jsonify(serialize_state(GAME_STATE))


@app.post('/api/new-hand')
def api_new_hand():
    """Start a new hand but keep player balances."""
    global GAME_STATE
    GAME_STATE = reset_hand_keep_balances()
    return jsonify(serialize_state(GAME_STATE))


@app.get('/api/state')
def api_state():
    return jsonify(serialize_state(GAME_STATE, reveal_opponent=GAME_STATE.get("status") == "finished"))

@app.post('/api/action')
def api_action():
    global GAME_STATE
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action")
    amount = int(data.get("amount", 0))

    if GAME_STATE["status"] != "playing":
        return jsonify(serialize_state(GAME_STATE, reveal_opponent=True))

    player = GAME_STATE["player"]
    opponent = GAME_STATE["opponent"]

    if action == "raise":
        bet = player.place_bet(max(0, amount))
        GAME_STATE["pot"] += bet
        GAME_STATE["player_held"] = False
    elif action == "fold":
        GAME_STATE["status"] = "finished"
        GAME_STATE["result"] = "opponent"
        opponent.win_pot(GAME_STATE["pot"])
        GAME_STATE["pot"] = 0
        return jsonify(serialize_state(GAME_STATE, reveal_opponent=True))
    elif action == "hold":
        GAME_STATE["player_held"] = True
    if GAME_STATE.get("player_held", False):
        GAME_STATE["opponent_held"] = True
    else:
        call_needed = player.current_bet - opponent.current_bet
        if call_needed > 0 and opponent.money > 0:
            call_amt = opponent.place_bet(min(call_needed, opponent.money))
            GAME_STATE["pot"] += call_amt
        GAME_STATE["opponent_held"] = False
    if GAME_STATE.get("player_held", False) and GAME_STATE.get("opponent_held", False):
        winner, _, _ = evaluate_winner(GAME_STATE)
        GAME_STATE["status"] = "finished"
        GAME_STATE["result"] = winner

        if winner == "player":
            player.win_pot(GAME_STATE["pot"])
        elif winner == "opponent":
            opponent.win_pot(GAME_STATE["pot"])
        else:
            player.win_pot(GAME_STATE["pot"] // 2)
            opponent.win_pot(GAME_STATE["pot"] - GAME_STATE["pot"] // 2)
        GAME_STATE["pot"] = 0
        return jsonify(serialize_state(GAME_STATE, reveal_opponent=True))

    return jsonify(serialize_state(GAME_STATE, reveal_opponent=False))


if __name__ == '__main__':
    app.run(debug=True)
