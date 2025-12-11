import React, { useEffect, useRef, useState } from 'react';
import './App.css';

const cardBack = 'https://i.pinimg.com/originals/ce/ac/76/ceac7651e78ef135370a8a236580201a.png';

const suitSymbols = {
  hearts: '♥',
  diamonds: '♦',
  clubs: '♣',
  spades: '♠',
};

const faceCardImages = {
  1: '/Taylor.png', // Ace
  13: '/Dylan.png', // King
  12: '/Alex.png',  // Queen
  11: '/Stew.png',  // Jack
  10: '/Sam.png',   // Ten
};

function App() {
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState(0);
  const [log, setLog] = useState([]);
  const [gameState, setGameState] = useState(null);
  const logRef = useRef(null);
  const audioRef = useRef(null);

  const fetchJson = async (url, opts = {}) => {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    });
    return res.json();
  };

  const loadNewGame = async () => {
    const state = await fetchJson('/api/new-game', { method: 'POST' });
    setGameState(state);
    setLog(['--- New game ---']);
    setOverlayVisible(false);
    setRaiseAmount(0);
  };

  const startNewHand = async () => {
    const state = await fetchJson('/api/new-hand', { method: 'POST' });
    setGameState(state);
    setLog(prev => [...prev, '--- New hand ---']);
    setOverlayVisible(false);
    setRaiseAmount(0);
  };

  const sendAction = async (action, amount = 0) => {
    const state = await fetchJson('/api/action', {
      method: 'POST',
      body: JSON.stringify({ action, amount }),
    });
    setGameState(state);
    const resultMsg = state.result ? ` - ${state.result}` : '';
    const geminiMsg = state.gemini_bot ? ` | Gemini: $${state.gemini_bot.money}` : '';
    setLog(prev => [...prev, `You ${action}${amount ? ` ${amount}` : ''}`, `Your Balance: $${state.player?.money ?? 0} | Opponent: $${state.opponent?.money ?? 0}${geminiMsg}${resultMsg}`]);
  };

  const handleRaiseConfirm = () => {
    const highestBet = Math.max(
      gameState?.opponent?.current_bet ?? 0,
      gameState?.gemini_bot?.current_bet ?? 0
    );
    const minRaise = Math.max(0, highestBet - (gameState?.player?.current_bet ?? 0));
    const finalAmount = Math.max(minRaise, Number(raiseAmount) || 0);
    sendAction('raise', finalAmount);
    setOverlayVisible(false);
    setRaiseAmount(0);
  };

  const adjustRaise = (value) => {
    const highestBet = Math.max(
      gameState?.opponent?.current_bet ?? 0,
      gameState?.gemini_bot?.current_bet ?? 0
    );
    const minRaise = Math.max(0, highestBet - (gameState?.player?.current_bet ?? 0));
    if (value === 'reset') setRaiseAmount(minRaise);
    else setRaiseAmount(prev => Math.max(minRaise, prev + parseInt(value, 10)));
  };

  const handleCall = () => sendAction('call');
  const handleHold = () => sendAction('hold');
  const handleFold = () => sendAction('fold');

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log]);

  useEffect(() => {
    loadNewGame();
  }, []);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.loop = true;
      audioRef.current.volume = 0.3;
      audioRef.current.play().catch(() => {
        // Autoplay prevented by browser; user interaction required
      });
    }
  }, []);

  const playerCards = gameState?.player?.hole ?? [];
  const opponentCards = gameState?.opponent?.hole ?? [];
  const geminiCards = gameState?.gemini_bot?.hole ?? [];

  const renderCard = (card, idx, size = 'md') => {
    const hidden = card?.hidden;
    if (hidden) {
      return <img key={idx} src={cardBack} alt="Card back" className={size === 'sm' ? 'sm' : ''} />;
    }

    const rank = card?.rank;
    const suit = card?.suit;
    const customImg = faceCardImages[rank];

    if (customImg) {
      const suitSymbol = suitSymbols[suit] || '';
      const suitClass = suit === 'hearts' || suit === 'diamonds' ? 'red' : 'black';
      const rankLabel = rank === 1 ? 'A' : rank === 13 ? 'K' : rank === 12 ? 'Q' : rank === 11 ? 'J' : '10';
      return (
        <div key={idx} className={`custom-card ${size === 'sm' ? 'sm' : 'md'}`}>
          <img src={customImg} alt={`Card ${rankLabel}`} />
          <div className={`corner-label top ${suitClass}`}>
            <span className="rank-text">{rankLabel}</span>
            <span className="suit-text">{suitSymbol}</span>
          </div>
          <div className={`corner-label bottom ${suitClass}`}>
            <span className="rank-text">{rankLabel}</span>
            <span className="suit-text">{suitSymbol}</span>
          </div>
        </div>
      );
    }

    const src = card?.image || cardBack;
    return <img key={idx} src={src} alt={`Card ${idx + 1}`} className={size === 'sm' ? 'sm' : ''} />;
  };

  const status = gameState?.status || 'loading';
  const isFinished = status === 'finished';
  const highestBet = Math.max(
    gameState?.opponent?.current_bet ?? 0,
    gameState?.gemini_bot?.current_bet ?? 0
  );
  const needsToCall = highestBet > (gameState?.player?.current_bet ?? 0);

  return (
    <div className="App">
      <audio ref={audioRef} src="/music.mp3" />
      <header>
        <h1>Let's Go Kambling!</h1>
      </header>

      <main>
        <div className="hand-log" ref={logRef}>
          {log.map((entry, idx) => (
            <p key={idx}>{entry}</p>
          ))}
        </div>

        <div className = "container">
          <div className = "back-stacks">
            <ChipStack count = {10} size = {30} color = "blue" borderColor = "white" borderWidth = {3} />
            <ChipStack count = {10} size = {30} color = "white" borderColor = "blue" borderWidth = {3} />
            <ChipStack count = {10} size = {30} color = "green" borderColor = "white" borderWidth = {3} />
            <ChipStack count = {10} size = {30} color = "black" borderColor = "gray" borderWidth = {3} />
            <ChipStack count = {10} size = {30} color = "red" borderColor = "white" borderWidth = {3} />
          </div>
          <div className = "front-stacks">
            <ChipStack count = {7} size = {30} color = "purple" borderColor = "white" borderWidth = {3} stackZ = {2000} />
            <ChipStack count = {7} size = {30} color = "purple" borderColor = "blue" borderWidth = {3} stackZ = {2000} />
          </div>
        </div> 

        <div className="action-buttons">
          <button onClick={() => {
            const minRaise = Math.max(0, highestBet - (gameState?.player?.current_bet ?? 0));
            setRaiseAmount(minRaise);
            setOverlayVisible(true);
          }} disabled={isFinished}>Raise</button>
          {needsToCall && !isFinished && (
            <button onClick={handleCall}>Call ${highestBet - (gameState?.player?.current_bet ?? 0)}</button>
          )}
          <button onClick={handleHold} disabled={isFinished || needsToCall}>Hold</button>
          <button onClick={handleFold} disabled={isFinished}>Fold</button>
          {isFinished && (
            <button onClick={startNewHand}>New Hand</button>
          )}
          <button onClick={loadNewGame}>New Game</button>
        </div>
      </main>

      {/* Player cards - large at bottom */}
      <div className="card-row">
        {playerCards.map((card, idx) => renderCard(card, idx, 'md'))}
      </div>

      <img
        src={cardBack}
        className="hand-card"
        alt="Hand Card"
      />

      {/* Player stats - bottom left */}
      <div className="bottom-left-texts">
        <div>Pot: ${gameState?.pot ?? 0}</div>
        <div>Your Total: ${gameState?.player?.money ?? 0}</div>
        <div>Your Bet: ${gameState?.player?.current_bet ?? 0}</div>
        <div>Best: {gameState?.player?.best?.hand ?? '—'}</div>
        <div>Status: {isFinished ? 'Winner!' : status}{gameState?.result ? ` (${gameState.result})` : ''}</div>
      </div>

      {/* Opponent - left side */}
      <div className="mini-card-column2">
        {opponentCards.map((card, idx) => renderCard(card, idx, 'sm'))}
      </div>

      <div className="opstats-circle">
        <div className="opstats-text">
          <div>Opponent Total: ${gameState?.opponent?.money ?? 0}</div>
          <div>Opponent Bet: ${gameState?.opponent?.current_bet ?? 0}</div>
        </div>
      </div>

      {/* Gemini - right side (mirror of opponent) */}
      {gameState?.gemini_bot && (
        <>
          <div className="mini-card-column">
            {geminiCards.map((card, idx) => renderCard(card, idx, 'sm'))}
          </div>

          <div className="opstats-circle2">
            <div className="opstats-text2">
              <div>Gemini Total: ${gameState.gemini_bot.money}</div>
              <div>Gemini Bet: ${gameState.gemini_bot.current_bet}</div>
            </div>
          </div>
        </>
      )}

      {overlayVisible && (
        <div id="overlay">
          <div className="overlay-content">
            <p>Enter your Raise Amount:</p>
            <input
              type="number"
              id="raiseInput"
              value={raiseAmount}
              min={Math.max(0, highestBet - (gameState?.player?.current_bet ?? 0))}
              onChange={(e) => {
                const minRaise = Math.max(0, highestBet - (gameState?.player?.current_bet ?? 0));
                setRaiseAmount(Math.max(minRaise, Number(e.target.value)));
              }}
            />
            <div className="buttons">
              {[-500, -100, -10, -1, 'reset', 1, 10, 100, 500].map((val, idx) => (
                <button key={idx} className="adjust" onClick={() => adjustRaise(val)}>
                  {val === 'reset' ? 0 : val > 0 ? `+${val}` : val}
                </button>
              ))}
            </div>
            <button className="confirm-button" onClick={handleRaiseConfirm}>
              Confirm
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;