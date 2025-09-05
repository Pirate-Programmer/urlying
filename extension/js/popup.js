// Blacklist button logic
const blacklistBtn = document.getElementById("blacklistBtn");
blacklistBtn.addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    let url = new URL(tabs[0].url);
    let domain = url.hostname;

    chrome.storage.local.get({ blacklist: [], whitelist: [] }, (data) => {
      let { blacklist, whitelist } = data;

      whitelist = whitelist.filter(d => d !== domain);

      if (!blacklist.includes(domain)) {
        blacklist.push(domain);
      }

      chrome.storage.local.set({ blacklist, whitelist }, () => {
        alert(`${domain} has been blacklisted`);
      });
    });
  });
});

// ==========================
// Toggle ON/OFF logic
// ==========================
const toggle = document.getElementById("holo-toggle");
const statusText = document.getElementById("protectionStatus");
const onOrOff = document.getElementById("data-text");

function updateToggleUI(isEnabled) {
  if (isEnabled) {
    onOrOff.textContent = "ON";
    onOrOff.style.color = "limegreen"; // use string, not variable
    blacklistBtn.disabled = false;
    blacklistBtn.style.opacity = "1";
    blacklistBtn.style.pointerEvents = "auto";
  } else {
    onOrOff.textContent = "OFF";
    onOrOff.style.color = "red"; // use string
    blacklistBtn.disabled = true;
    blacklistBtn.style.opacity = "0.5";  // dim when off
    blacklistBtn.style.pointerEvents = "none";
  }
}

toggle.addEventListener("change", () => {
  updateToggleUI(toggle.checked);
});

// initialize on load
updateToggleUI(toggle.checked);

