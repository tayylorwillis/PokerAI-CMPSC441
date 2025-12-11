const raiseButton = document.getElementById('raiseButton');
const holdButton = document.getElementById('holdButton');
const foldButton = document.getElementById('foldButton');
const overlay = document.getElementById('overlay');
const confirmRaise = document.getElementById('confirmRaise');
const raiseInput = document.getElementById('raiseInput');

const communityContainer = document.getElementById('communityCards');
const leftMiniContainer = document.getElementById('leftMini');
const rightMiniContainer = document.getElementById('rightMini');
const handCardSlot = document.getElementById('handCardSlot');

const cardBack = 'https://i.pinimg.com/originals/ce/ac/76/ceac7651e78ef135370a8a236580201a.png';

function createCardImg(card, size = 'md') {
    const img = document.createElement('img');
    img.className = `card-img ${size === 'sm' ? 'sm' : ''}`.trim();
    img.src = card?.image || cardBack;
    img.alt = `${card?.rank ?? ''}${card?.suit ?? ''}`;
    img.loading = 'lazy';
    return img;
}

function renderCards(container, cards, size = 'md') {
    if (!container || !cards) return;
    container.innerHTML = '';
    cards.forEach(card => container.appendChild(createCardImg(card, size)));
}

function setHandCard(card) {
    if (!handCardSlot || !card) return;
    handCardSlot.src = card.image || cardBack;
    handCardSlot.alt = `${card.rank ?? ''}${card.suit ?? ''}`;
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
    renderCards(communityContainer, state.board, 'md');
    renderCards(leftMiniContainer, state.player.hole, 'sm');
    renderCards(rightMiniContainer, state.opponent.hole, 'sm');
    setHandCard(state.player.hole?.[0] || {});

    updateText('potValue', state.pot ?? '0');
    updateText('statTotal', state.player.money ?? '');
    updateText('statRound', state.player.current_bet ?? '');
    updateText('statWins', state.player.best?.hand ?? '');
    updateText('statLosses', state.opponent.best?.hand ?? '');

    if (state.status === 'finished' && state.result) {
        const resultText = state.result === 'player' ? 'You win!' : state.result === 'opponent' ? 'Opponent wins' : 'Tie';
        updateText('potValue', `${state.pot} • ${resultText}`);
    }
}

async function sendAction(action, amount = 0) {
    const state = await fetchJson('/api/action', {
        method: 'POST',
        body: JSON.stringify({ action, amount })
    });
    renderState(state);
}

const showOverlay = () => overlay?.classList.remove('hidden');
const hideOverlay = () => overlay?.classList.add('hidden');

raiseButton?.addEventListener('click', showOverlay);
holdButton?.addEventListener('click', () => sendAction('hold'));
foldButton?.addEventListener('click', () => sendAction('fold'));

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

// Kick off
loadGame();