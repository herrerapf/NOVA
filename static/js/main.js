console.log('NOVA loaded');
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");





  if (flashes.length > 0) {
    setTimeout(() => {
      flashes.forEach(f => f.classList.add("hide"));
    }, 3000); // ⏳

    setTimeout(() => {
      flashes.forEach(f => f.remove());
    }, 3800);
  }
});

// ==============================
//  BUSCADOR EN PANEL ADMIN
// ==============================
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchUser");
    if (!searchInput) return; // Si no estamos en el admin, no se ejecuta

    searchInput.addEventListener("keyup", function () {
        let filter = this.value.toLowerCase();
        let cards = document.querySelectorAll(".admin-user-card");

        cards.forEach(card => {
            let name = card.querySelector(".user-name")?.innerText.toLowerCase() || "";
            let email = card.querySelector(".user-email")?.innerText.toLowerCase() || "";

            if (name.includes(filter) || email.includes(filter)) {
                card.style.display = "flex";
            } else {
                card.style.display = "none";
            }
        });
    });
});



