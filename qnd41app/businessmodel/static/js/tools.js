const buttons = document.querySelectorAll('.tab-button, .database-button');

function togglePopup(popupId) {
    const popup = document.getElementById(popupId);
    popup.style.display = (popup.style.display === "block") ? "none" : "block";
}

window.onclick = event => {
    const popups = ["filterPopup", "resultsPopup"];
    popups.forEach(popupId => {
        const popup = document.getElementById(popupId);
        if (popup && event.target === popup) {
            popup.style.display = "none";
        }
    });
};

function toggleNavbar() {
    const navbar = document.querySelector(".navbar");
    const toggleButton = document.getElementById("toggleButton");
    const isVisible = navbar.style.display === "flex";

    navbar.style.display = isVisible ? "none" : "flex";
    toggleButton.textContent = isVisible ? "Menú de Opciones" : "Abierto";
}

