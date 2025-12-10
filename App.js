import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // We'll use your existing CSS with minor tweaks

function App() {
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState(0);
  const [log, setLog] = useState([]);
  const logRef = useRef(null); // Ref for the log container


  const handleRaise = () => {
    setLog(prev => [
      ...prev,
      `AI raised for ${Math.floor(Math.random() * 50 + 10)} coins`,
      `You raised for ${raiseAmount} coins`
    ]);
    setOverlayVisible(false);
    setRaiseAmount(0);
  };

  // Scroll log to bottom whenever it changes
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log]);

  const adjustRaise = (value) => {
  if (value === 'reset') setRaiseAmount(0);
  else setRaiseAmount(prev => Math.max(0, prev + parseInt(value)));
};

  const handleHold = () => {
    setLog(prev => [...prev, 'AI holds', 'You hold']);
  };

    //will need to change this to {player} with an identifier
  const handleFold = () => {
    setLog(prev => [...prev, 'AI folds', 'You fold']);
  };



  const cards = Array(5).fill(
    "https://opengameart.org/sites/default/files/oga-textures/92832/spades_2.png"
  );

  const miniCards = Array(5).fill(
    "https://opengameart.org/sites/default/files/oga-textures/92832/spades_2.png"
  );

  return (
    <div className="App">
      {/* Header */}
      <header>
        <h1>Let's Go Kambling!</h1>
      </header>

      {/* Main content */}
      <main>
        {/* Hand history log */}
        <div className="hand-log" ref={logRef}>
          {log.map((entry, idx) => (
            <p key={idx}>{entry}</p>
          ))}
        </div>

        <div className="action-buttons">
          <button onClick={() => setOverlayVisible(true)}>Raise</button>
          <button onClick={() => handleHold()}>Hold</button>
          <button onClick={() => handleFold()}>Fold</button>
        </div>
      </main>

      {/* Card row */}
      <div className="card-row">
        {cards.map((uri, idx) => (
          <img key={idx} src={uri} alt={`Card ${idx + 1}`} />
        ))}
      </div>

      {/* Hand card bottom-right */}
      <img
        src="https://i.pinimg.com/originals/ce/ac/76/ceac7651e78ef135370a8a236580201a.png"
        className="hand-card"
        alt="Hand Card"
      />

          {/* Bottom-left stats container */}
        <div className="bottom-left-texts">
          <div>Pot: #### </div>
          <div>Total: ####</div>
          <div>Round: ####</div>
          <div>Wins: ####</div>
          <div>Losses: ####</div>
        </div>

      {/* Mini card columns */}
      <div className="mini-card-column">
        {miniCards.map((uri, idx) => (
          <img key={idx} src={uri} alt={`Mini ${idx + 1}`} />
        ))}
      </div>

      <div className="mini-card-column2">
        {miniCards.map((uri, idx) => (
          <img key={idx} src={uri} alt={`Mini ${idx + 1}`} />
        ))}
      </div>

      {/* Semi-circle wager areas */}
      <div className="opstats-circle">
        <div className="opstats-text">
          <div>Total: ####</div>
          <div>Bet: ####</div>
        </div>
      </div>

      <div className="opstats-circle2">
        <div className="opstats-text2">
          <div>Total: ####</div>
          <div>Bet: ####</div>
        </div>
      </div>

      {/* Overlay */}
      {overlayVisible && (
        <div id="overlay">
          <div className="overlay-content">
            <p>Enter your Raise Amount:</p>
            <input
              type="number"
              id="raiseInput"
              value={raiseAmount}
              min={0}
              readOnly
            />
            <div className="buttons">
              {[-500, -100, -10, -1, 'reset', 1, 10, 100, 500].map((val, idx) => (
                <button key={idx} className="adjust" onClick={() => adjustRaise(val)}>
                  {val === 'reset' ? 0 : val > 0 ? `+${val}` : val}
                </button>
              ))}
            </div>
            <button className="confirm-button" onClick={() => setOverlayVisible(false)}>
              Confirm
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;