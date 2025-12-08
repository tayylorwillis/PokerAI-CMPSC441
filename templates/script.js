// Get your buttons
const raiseButton = document.getElementById('raiseButton');
const holdButton = document.getElementById('holdButton');
const foldButton = document.getElementById('foldButton');
const overlay = document.getElementById("overlay");
const confirmRaise = document.getElementById("confirmRaise");
const resetButton = document.getElementById("resetRaise");


// Add click events
raiseButton.addEventListener('click', () => {
    console.log("Raise pressed!");
});

holdButton.addEventListener('click', () => {
    console.log("Hold pressed!");
});

foldButton.addEventListener('click', () => {
    console.log("Fold pressed!");
});

raiseButton.addEventListener("click", () => {
    overlay.classList.remove("hidden");  // Show overlay
});

confirmRaise.addEventListener("click", () => {
    const amount = document.getElementById("raiseInput").value;
    console.log("Raise:", amount);
    // Hide overlay again after confirming
    overlay.classList.add("hidden");
});

resetButton.addEventListener("click", () => {
    raiseInput.value = 0;
});