const raiseButton = document.getElementById('raiseButton');
const holdButton = document.getElementById('holdButton');
const foldButton = document.getElementById('foldButton');
const overlay = document.getElementById('overlay');
const confirmRaise = document.getElementById('confirmRaise');
const raiseInput = document.getElementById('raiseInput');

const communityContainer = document.getElementById('communityCards');
const playerHandContainer = document.getElementById('playerHandCards');
const rightMiniContainer = document.getElementById('rightMini');

function createCardImg(card, size = 'md') {
    const img = document.createElement('img');
    img.className = `card-img ${size === 'sm' ? 'sm' : ''}`.trim();
    if (card?.hidden) {
        img.src = 'https://www.deckofcardsapi.com/static/img/back.png';
        img.alt = 'Hidden card';
    } else {
        img.src = card?.image || '';
        img.alt = `${card?.rank ?? ''}${card?.suit ?? ''}`;
    }
    img.loading = 'lazy';
    return img;
}

function renderCards(container, cards, size = 'md') {
    if (!container || !cards) return;
    container.innerHTML = '';
    cards.forEach(card => container.appendChild(createCardImg(card, size)));
}

function updateText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

async function fetchJson(url, opts = {}) {
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
    return res.json();
}

async function loadGame() {
    const state = await fetchJson('/api/new-game', { method: 'POST' });
    renderState(state);
}

function renderState(state) {
    if (!state) return;
    renderCards(communityContainer, state.player.hole, 'md');
    renderCards(rightMiniContainer, state.opponent.hole, 'sm');

    updateText('potValue', state.pot ?? '0');
    updateText('statTotal', state.player.money ?? '');
    updateText('statRound', state.player.current_bet ?? '');
    updateText('statWins', state.player.best?.hand ?? '');
    updateText('rightTotal', state.opponent.money ?? '');
    updateText('rightBet', state.opponent.current_bet ?? '');

    const holdStatus = state.player.held ? ' (HELD)' : '';
    const oppHoldStatus = state.opponent.held ? ' (HELD)' : '';
    if (state.status === 'finished' && state.result) {
        const resultText = state.result === 'player' ? 'You win!' : state.result === 'opponent' ? 'Opponent wins' : 'Tie';
        updateText('potValue', `${state.pot} • ${resultText}`);
        newHandButton?.classList.remove('hidden');
    } else {
        newHandButton?.classList.add('hidden');
    }
}

async function sendAction(action, amount = 0) {
    const state = await fetchJson('/api/action', {
        method: 'POST',
        body: JSON.stringify({ action, amount })
    });
    renderState(state);
}

async function startNewHand() {
    const state = await fetchJson('/api/new-hand', { method: 'POST' });
    renderState(state);
}

const showOverlay = () => overlay?.classList.remove('hidden');
const hideOverlay = () => overlay?.classList.add('hidden');

raiseButton?.addEventListener('click', showOverlay);
holdButton?.addEventListener('click', () => sendAction('hold'));
foldButton?.addEventListener('click', () => sendAction('fold'));
newHandButton?.addEventListener('click', () => loadGame());

confirmRaise?.addEventListener('click', () => {
    const amount = Number(raiseInput?.value ?? 0);
    hideOverlay();
    sendAction('raise', amount);
});

document.querySelectorAll('.adjust').forEach(btn => {
    btn.addEventListener('click', () => {
        const { value } = btn.dataset;
        if (!raiseInput) return;
        if (value === 'reset') {
            raiseInput.value = 0;
            return;
        }
        const current = Number(raiseInput.value) || 0;
        raiseInput.value = Math.max(0, current + Number(value));
    });
});

overlay?.addEventListener('click', (e) => {
    if (e.target === overlay) hideOverlay();
});

window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideOverlay();
});

loadGame();
