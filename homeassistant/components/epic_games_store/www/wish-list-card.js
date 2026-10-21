const EGS_DOMAIN = "epic_games_store";

function openWishlistDialog(hass, entityId) {
  const stateObj = hass.states[entityId];
  const dialog = document.createElement("dialog");
  dialog.className = "egs-dialog";
  dialog.innerHTML = `
    <style>
      .egs-dialog {
        background: var(--card-background-color);
        color: var(--primary-text-color);
        border: none;
        border-radius: var(--ha-card-border-radius, 12px);
        padding: 0;
        min-width: min(400px, 90vw);
      }
      .egs-dialog::backdrop { background: rgba(0, 0, 0, 0.5); }
      .egs-dialog .content { padding: 24px; }
    </style>
    <div class="content">
      <h2 class="title"></h2>
      <div class="body"></div>
      <button class="close">Close</button>
    </div>
  `;
  dialog.querySelector(".title").textContent =
    stateObj?.attributes.friendly_name ?? entityId;

  dialog.querySelector(".body").textContent =
    `Show game search and saved info here in the .body`;

  dialog
    .querySelector(".close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => dialog.remove());
  document.body.append(dialog);
  dialog.showModal();
}

// Capture the press for the wishlist and override it with our own screen
window.addEventListener(
  "hass-more-info",
  (ev) => {
    const entityId = ev.detail?.entityId;
    const hass = document.querySelector("home-assistant")?.hass;
    const entry = hass?.entities[entityId];
    if (
      !entityId ||
      entry?.platform !== EGS_DOMAIN ||
      entry.translation_key !== "wish_list"
    ) {
      return;
    }
    ev.stopImmediatePropagation();
    openWishlistDialog(hass, entityId);
  },
  { capture: true },
);
