import React, { useEffect, useRef, useState } from 'react';
import './App.css';

const cardBack = 'https://i.pinimg.com/originals/ce/ac/76/ceac7651e78ef135370a8a236580201a.png';

function App() {
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState(0);
  const [log, setLog] = useState([]);
  const [gameState, setGameState] = useState(null);
  const logRef = useRef(null);

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
    setLog(prev => [...prev, `You ${action}${amount ? ` ${amount}` : ''}`, `Your Balance: $${state.player?.money ?? 0} | Opponent: $${state.opponent?.money ?? 0}${resultMsg}`]);
  };

  const handleRaiseConfirm = () => {
    sendAction('raise', Math.max(0, Number(raiseAmount) || 0));
    setOverlayVisible(false);
    setRaiseAmount(0);
  };

  const adjustRaise = (value) => {
    if (value === 'reset') setRaiseAmount(0);
    else setRaiseAmount(prev => Math.max(0, prev + parseInt(value, 10)));
  };

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

  const playerCards = gameState?.player?.hole ?? [];
  const opponentCards = gameState?.opponent?.hole ?? [];

  const renderCard = (card, idx, size = 'md') => {
    const hidden = card?.hidden;
    const src = hidden ? cardBack : card?.image || cardBack;
    return <img key={idx} src={src} alt={`Card ${idx + 1}`} className={size === 'sm' ? 'sm' : ''} />;
  };

  const status = gameState?.status || 'loading';
  const isFinished = status === 'finished';

  return (
    <div className="App">
      <header>
        <h1>Let's Go Kambling!</h1>
      </header>

      <main>
        <div className="hand-log" ref={logRef}>
          {log.map((entry, idx) => (
            <p key={idx}>{entry}</p>
          ))}
        </div>

        <div className="action-buttons">
          <button onClick={() => setOverlayVisible(true)} disabled={isFinished}>Raise</button>
          <button onClick={handleHold} disabled={isFinished}>Hold</button>
          <button onClick={handleFold} disabled={isFinished}>Fold</button>
          {isFinished && (
            <button onClick={startNewHand}>New Hand</button>
          )}
          <button onClick={loadNewGame}>New Game</button>
        </div>
      </main>

      <div className="card-row">
        {playerCards.map((card, idx) => renderCard(card, idx, 'md'))}
      </div>

      <img
        src={cardBack}
        className="hand-card"
        alt="Hand Card"
      />

      <div className="bottom-left-texts">
        <div>Pot: ${gameState?.pot ?? 0}</div>
        <div>Your Total: ${gameState?.player?.money ?? 0}</div>
        <div>Your Bet: ${gameState?.player?.current_bet ?? 0}</div>
        <div>Best: {gameState?.player?.best?.hand ?? '—'}</div>
        <div>Status: {isFinished ? 'Winner!' : status}{gameState?.result ? ` (${gameState.result})` : ''}</div>
      </div>

      <div className="mini-card-column">
        {playerCards.map((card, idx) => renderCard(card, idx, 'sm'))}
      </div>

      <div className="mini-card-column2">
        {opponentCards.map((card, idx) => renderCard(card, idx, 'sm'))}
      </div>

      <div className="opstats-circle">
        <div className="opstats-text">
          <div>Opponent Total: ${gameState?.opponent?.money ?? 0}</div>
          <div>Opponent Bet: ${gameState?.opponent?.current_bet ?? 0}</div>
        </div>
      </div>

      {overlayVisible && (
        <div id="overlay">
          <div className="overlay-content">
            <p>Enter your Raise Amount:</p>
            <input
              type="number"
              id="raiseInput"
              value={raiseAmount}
              min={0}
              onChange={(e) => setRaiseAmount(Number(e.target.value))}
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