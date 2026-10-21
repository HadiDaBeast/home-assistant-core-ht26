import "../coordinator.py";

const EGS_DOMAIN = "epic_games_store";

function openWishlistDialog(hass, entityId) {
  const stateObj = hass.states[entityId];
  const dialog = document.createElement("dialog");
  dialog.className = "egs-dialog";
  dialog.innerHTML = `
    <style>
      /* Mirrors the variables used by ha-more-info-dialog / wa-dialog */
      .egs-dialog {
        --egs-full-width: var(--ha-dialog-width-full, min(95vw, var(--safe-width, 100vw)));
        --egs-margin-top: var(--dialog-surface-margin-top, var(--ha-space-10, 40px));
        box-sizing: border-box;
        width: min(var(--ha-dialog-width-md, 580px), var(--egs-full-width));
        max-width: none;
        max-height: calc(
          100svh - var(--egs-margin-top) - var(--ha-space-2, 8px) -
            var(--safe-area-inset-y, 0px)
        );
        margin: var(--egs-margin-top) auto auto;
        padding: 0;
        border: none;
        border-radius: var(--ha-dialog-border-radius, var(--ha-border-radius-3xl, 28px));
        background: var(
          --ha-dialog-surface-background,
          var(--card-background-color, var(--ha-color-surface-default))
        );
        color: var(--primary-text-color);
        font-family: var(--ha-font-family-body, Roboto, Noto, sans-serif);
        box-shadow: var(--ha-box-shadow-l, 0 6px 12px -3px #0000001f, 0 16px 32px -6px #0003);
        overflow: hidden;
      }
      .egs-dialog[open] {
        display: flex;
        flex-direction: column;
        animation: egs-dialog-show var(--ha-dialog-show-duration, 0.2s) ease;
      }
      .egs-dialog::backdrop {
        background: var(--ha-dialog-scrim-color, rgba(0, 0, 0, 0.32));
        animation: egs-backdrop-show var(--ha-dialog-show-duration, 0.2s) ease;
      }
      @keyframes egs-dialog-show {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
      }
      @keyframes egs-backdrop-show {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      /* ha-dialog-header */
      .egs-dialog .header-bar {
        display: flex;
        flex-direction: row;
        align-items: center;
        box-sizing: border-box;
        padding: 0 var(--ha-space-1, 4px);
        flex-shrink: 0;
      }
      .egs-dialog .header-navigation-icon,
      .egs-dialog .header-action-items {
        flex: none;
        display: flex;
        flex-direction: row;
        min-width: var(--ha-space-2, 8px);
      }
      .egs-dialog .header-content {
        flex: 1;
        min-width: 0;
        min-height: var(--ha-space-12, 48px);
        padding: 10px var(--ha-space-1, 4px);
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-sizing: border-box;
      }
      .egs-dialog .breadcrumb {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: var(--ha-space-1, 4px);
        min-width: 0;
        margin-bottom: 2px;
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-s, 12px);
        line-height: 16px;
        white-space: nowrap;
      }
      .egs-dialog .breadcrumb[hidden] { display: none; }
      .egs-dialog .breadcrumb span {
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .egs-dialog .breadcrumb svg {
        flex: none;
        width: 16px;
        height: 16px;
        fill: currentColor;
      }
      .egs-dialog .title {
        margin: 0;
        font-size: var(--ha-font-size-xl, 20px);
        line-height: var(--ha-line-height-condensed, 1.2);
        font-weight: var(--ha-font-weight-normal, 400);
        color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      /* ha-icon-button */
      .egs-dialog .close {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        padding: 0;
        border: none;
        border-radius: 50%;
        background: none;
        color: var(--primary-text-color);
        cursor: pointer;
        position: relative;
        outline: none;
      }
      .egs-dialog .close::before {
        content: "";
        position: absolute;
        inset: 4px;
        border-radius: 50%;
        background: currentColor;
        opacity: 0;
        transition: opacity 15ms linear;
      }
      .egs-dialog .close:hover::before { opacity: 0.08; }
      .egs-dialog .close:focus-visible::before,
      .egs-dialog .close:active::before { opacity: 0.12; }
      .egs-dialog .close svg {
        width: 24px;
        height: 24px;
        fill: currentColor;
        position: relative;
      }

      .egs-dialog .body {
        flex: 1;
        overflow-y: auto;
        padding: 0 var(--ha-space-6, 24px) var(--ha-space-6, 24px);
      }

      @media (min-width: 450px) and (min-height: 500px) {
        .egs-dialog .header-bar { padding: 0 var(--ha-space-2, 8px); }
      }

      /* ha-adaptive-dialog switches to a bottom sheet on small screens */
      @media (max-width: 449px), (max-height: 499px) {
        .egs-dialog {
          width: 100%;
          max-height: var(
            --ha-bottom-sheet-max-height,
            calc(100dvh - max(var(--safe-area-inset-top, 0px), 48px))
          );
          margin: auto 0 0;
          border-bottom-left-radius: 0;
          border-bottom-right-radius: 0;
          padding-bottom: var(--safe-area-inset-bottom, 0px);
        }
        .egs-dialog[open] { animation-name: egs-sheet-show; }
        @keyframes egs-sheet-show {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
      }
    </style>
    <header class="header">
      <div class="header-bar">
        <section class="header-navigation-icon">
          <button class="close" aria-label="Close" title="Close">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
            </svg>
          </button>
        </section>
        <section class="header-content">
          <div class="breadcrumb" hidden></div>
          <h2 class="title"></h2>
        </section>
        <section class="header-action-items"></section>
      </div>
    </header>
    <div class="body"></div>
  `;
  const entry = hass.entities[entityId];
  const device = entry?.device_id ? hass.devices[entry.device_id] : undefined;
  const area = hass.areas[entry?.area_id ?? device?.area_id];
  const deviceName = device?.name_by_user ?? device?.name;
  let title = stateObj?.attributes.friendly_name ?? entityId;
  if (deviceName && title.startsWith(`${deviceName} `)) {
    title = title.slice(deviceName.length + 1);
  }
  dialog.querySelector(".title").textContent = title;

  const crumbs = [area?.name, deviceName].filter(Boolean);
  const breadcrumb = dialog.querySelector(".breadcrumb");
  crumbs.forEach((crumb, index) => {
    if (index > 0) {
      breadcrumb.insertAdjacentHTML(
        "beforeend",
        `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z" /></svg>`,
      );
    }
    const span = document.createElement("span");
    span.textContent = crumb;
    breadcrumb.append(span);
  });
  breadcrumb.hidden = crumbs.length === 0;

  dialog.querySelector(".body").innerHTML = `
    <div class="input-row">
      <label class="text-field">
        <input id="search-game" type="text" placeholder=" " autocomplete="off" />
        <span class="label">Add to wishlist</span>
        <span class="line"></span>
      </label>
      <ul class="suggestions" id="game-suggestions" role="listbox" hidden></ul>
    </div>
    <ul class="wish-list" id ="wishlisted-games">
    </ul>
`;
  // Copied over the style variables used to ensure the same style
  dialog.querySelector(".body").innerHTML += `
  <style>
    .modal {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      font-family: 'Roboto';
    }

    .modal.show {
      display: flex;
    }

    .input-row {
      position: relative;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* Matches the ha-combo-box dropdown */
    .suggestions {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      z-index: 1;
      max-height: 240px;
      margin: 0;
      padding: var(--ha-space-2, 8px) 0;
      overflow-y: auto;
      list-style: none;
      background: var(--card-background-color, var(--ha-color-surface-default));
      border-radius: var(--ha-border-radius-sm, 4px);
      box-shadow: var(--ha-box-shadow-m, 0 3px 6px -1px #0000001a, 0 8px 16px -2px #00000026);
    }
    .suggestions[hidden] {
      display: none;
    }
    .suggestions li {
      display: flex;
      align-items: center;
      min-height: 48px;
      padding: 0 var(--ha-space-4, 16px);
      color: var(--primary-text-color);
      font-size: var(--ha-font-size-l, 16px);
      cursor: pointer;
    }
    .suggestions li:hover,
    .suggestions li.active {
      background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.08);
    }
    .suggestions li.empty {
      color: var(--secondary-text-color);
      cursor: default;
      background: none;
    }

    /* Filled text field, matching ha-textfield on text entities */
    .text-field {
      position: relative;
      display: block;
      flex: 1;
      min-width: 0;
      height: 56px;
      box-sizing: border-box;
      background: var(--input-fill-color, var(--mdc-text-field-fill-color, whitesmoke));
      border-radius: var(--ha-border-radius-sm, 4px) var(--ha-border-radius-sm, 4px) 0 0;
      border-bottom: 1px solid var(--input-idle-line-color, rgba(0, 0, 0, 0.42));
      transition: border-bottom-color 150ms;
    }
    .text-field:hover {
      border-bottom-color: var(--input-hover-line-color, rgba(0, 0, 0, 0.87));
    }
    .text-field input {
      position: absolute;
      inset: 0;
      width: 100%;
      box-sizing: border-box;
      padding: 20px 16px 6px;
      border: none;
      outline: none;
      background: transparent;
      color: var(--input-ink-color, var(--primary-text-color));
      caret-color: var(--primary-color);
      font-family: inherit;
      font-size: var(--ha-font-size-l, 16px);
    }
    .text-field .label {
      position: absolute;
      left: 16px;
      right: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--input-label-ink-color, var(--secondary-text-color));
      font-size: var(--ha-font-size-l, 16px);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      pointer-events: none;
      transition: top 150ms, font-size 150ms, transform 150ms, color 150ms;
    }
    .text-field input:focus + .label,
    .text-field input:not(:placeholder-shown) + .label {
      top: 8px;
      transform: none;
      font-size: var(--ha-font-size-s, 12px);
    }
    .text-field input:focus + .label {
      color: var(--primary-color);
    }
    .text-field .line {
      position: absolute;
      left: 0;
      right: 0;
      bottom: -1px;
      height: 2px;
      background: var(--primary-color);
      transform: scaleX(0);
      transition: transform 180ms ease;
    }
    .text-field input:focus ~ .line {
      transform: scaleX(1);
    }

    .plus-button {
      flex-shrink: 0;
      width: 27px;
      height: 27px;
      background: #3c3c3c;
      color: white;
      font-size: 19px;
      line-height: 1;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 0px;
    }

    .plus-button:hover {
      background: white;
      color: black;
      border-radius: 50%;
    }

    /* Matches ha-md-list-item rows */
    .wish-list {
      min-height: calc(4 * 48px);
      margin: var(--ha-space-2, 8px) 0 0;
      padding: 0;
      list-style: none;
    }
    .wish-list li {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: var(--ha-space-4, 16px);
      min-height: 48px;
      padding: 0 0 0 var(--ha-space-4, 16px);
      border-bottom: 1px solid var(--divider-color);
      border-radius: var(--ha-border-radius-sm, 4px);
      transition: background-color 15ms linear;
    }
    .wish-list li:last-child {
      border-bottom: none;
    }
    .wish-list li:hover {
      background: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.04);
    }
    .wish-list li span {
      flex: 1;
      min-width: 0;
      color: var(--primary-text-color);
      font-size: var(--ha-font-size-l, 16px);
      line-height: 24px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* ha-icon-button */
    .minus-button {
      flex: none;
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      padding: 0;
      border: none;
      border-radius: 50%;
      background: none;
      color: var(--secondary-text-color);
      cursor: pointer;
      outline: none;
    }
    .minus-button::before {
      content: "";
      position: absolute;
      inset: 4px;
      border-radius: 50%;
      background: currentColor;
      opacity: 0;
      transition: opacity 15ms linear;
    }
    .minus-button:hover {
      color: var(--error-color, #db4437);
    }
    .minus-button:hover::before { opacity: 0.08; }
    .minus-button:focus-visible::before,
    .minus-button:active::before { opacity: 0.12; }
    .minus-button svg {
      position: relative;
      width: 24px;
      height: 24px;
      fill: currentColor;
    }

  </style>
`;
  const catalog = stateObj?.attributes.catalog ?? [];

  // Fetch stored games
  // TODO: Replace mock data with the stored wishlist
  let games = [];
  let wish_list = dialog.querySelector("#wishlisted-games");

  function addRow(game) {
    const item = document.createElement("li");
    item.dataset.gameId = game.id;
    item.innerHTML = `<span></span><button class="minus-button" aria-label="Remove" title="Remove"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19,13H5V11H19V13Z" /></svg></button>`;
    item.querySelector("span").textContent = game.title;
    item.querySelector(".minus-button").addEventListener("click", () => {
      games = games.filter((g) => g.id !== game.id);
      item.remove();
      //TODO Remove game from storage
    });
    wish_list.append(item);
  }
  // Add stored games to the wishlist
  games.forEach(addRow);

  const input = dialog.querySelector("#search-game");
  const suggestions = dialog.querySelector("#game-suggestions"); // Dropdown for searching games
  let matches = []; // Searched game matches
  let activeIndex = -1;

  function closeSuggestions() {
    // Close the suggestion dropdown
    suggestions.hidden = true;
    activeIndex = -1;
  }

  function addGame(game) {
    // Add game from suggestion
    games.push(game);
    addRow(game);
    input.value = "";
    closeSuggestions();
  }

  function renderSuggestions() {
    const query = input.value.trim().toLowerCase(); // Format the query to lowercase
    if (!query) {
      //If we have not written anything then we do not show the suggestion
      closeSuggestions();
      return;
    }
    // Remove games already wishlisted from the suggestions
    const wishlisted = new Set(games.map((g) => g.id));
    matches = catalog.filter(
      (game) =>
        !wishlisted.has(game.id) && game.title.toLowerCase().includes(query),
    );
    suggestions.replaceChildren();
    if (matches.length === 0) {
      const empty = document.createElement("li");
      empty.className = "empty";
      empty.textContent = "No matching games";
      suggestions.append(empty);
    }
    // Add a game option for each suggestion
    matches.forEach((game, index) => {
      const option = document.createElement("li");
      option.setAttribute("role", "option");
      option.textContent = game.title;
      // Keep focus in the input so blur doesn't close the list before the click
      option.addEventListener("mousedown", (event) => event.preventDefault());
      option.addEventListener("click", () => addGame(game));
      // Remove the active class tag from all options and then only give the active class to the mouseover option
      option.addEventListener("mouseover", () => {
        suggestions
          .querySelectorAll("li.active")
          .forEach((active) => active.classList.remove("active"));
        option.classList.add("active");
        activeIndex = index;
      });
      suggestions.append(option);
    });
    suggestions.hidden = false;
  }

  let seconds = 0;
  let intervalId = null;

  input.addEventListener("input", () => {
    if (intervalId) return;
    intervalId = setInterval(() => seconds++, 1000);
    renderSuggestions();
  }); // If we edit in the input field
  input.addEventListener("focus", renderSuggestions); // If we focus on the input field we show the suggestion dropdown
  input.addEventListener("blur", closeSuggestions);
  input.addEventListener("keydown", (event) => {
    if (suggestions.hidden) {
      return;
    }
  });
  // Close the modal if we press the button or if we press outside the modal
  dialog
    .querySelector(".close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });
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
