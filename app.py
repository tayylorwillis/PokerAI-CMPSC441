from flask import Flask, jsonify, render_template, request
from deck import Deck
from player import Player
from hand_evaluator import HandEvaluator

app = Flask(__name__)


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


@app.post('/api/new-game')
def api_new_game():
    global GAME_STATE
    GAME_STATE = make_state()
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
