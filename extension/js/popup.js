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

document.getElementById("listBtn").addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});


const toggle = document.getElementById("cb3-8");

function updateToggleUI(isEnabled) {
  if (isEnabled) {
    blacklistBtn.disabled = false;
    blacklistBtn.style.opacity = "1";
    blacklistBtn.style.pointerEvents = "auto";
  } else {
    blacklistBtn.disabled = true;
    blacklistBtn.style.opacity = "0.5";  // dim when off
    blacklistBtn.style.pointerEvents = "none";
  }
}

toggle.addEventListener("change", () => {
  const isEnabled = toggle.checked;
  chrome.storage.local.set({ enableBlocking: isEnabled }, () => {
    updateToggleUI(isEnabled);
  });
});

chrome.storage.local.get({ enableBlocking: false }, (data) => {
  toggle.checked = data.enableBlocking;
  updateToggleUI(data.enableBlocking);
});


// --- Security level (1-6) ---
const fanRadios = document.querySelectorAll('input[name="fan"]');

// Load saved security level
chrome.storage.local.get({ securityLevel: 3 }, (data) => {
  const level = data.securityLevel;
  const radio = document.getElementById(`fan_${level}`);
  if (radio) radio.checked = true;
});

// Save when user changes level
fanRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.checked) {
      const level = parseInt(radio.id.split('_')[1], 10);
      chrome.storage.local.set({ securityLevel: level });
    }
  });
});

