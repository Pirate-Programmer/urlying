(function () {
  if (window.__urlCheckInjected) return; // prevent double injection
  window.__urlCheckInjected = true;

  const domain = window.location.hostname;

  // Helper to check domain list
  function isDomainInList(listName) {
    return new Promise((resolve) => {
      chrome.storage.local.get([listName], (result) => {
        const list = result[listName] || [];
        resolve(list.includes(domain));
      });
    });
  }

  // Blocked page HTML with "Unblock" button
  function showBlockedPage() {
    document.body.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;background-color:#1c1c1c;color:white;font-family:sans-serif;text-align:center;padding:20px;">
        <h1 style="font-size:32px;color:#ff4c4c;">🚫 This site is blocked</h1>
        <p style="font-size:20px;margin-top:10px;">The domain <strong>${domain}</strong> is in your blacklist.</p>
        <button id="unblock-btn" style="margin-top:20px;padding:12px 24px;font-size:18px;border:none;border-radius:8px;background-color:#4caf50;color:#fff;cursor:pointer;">
          Remove from blacklist & Refresh
        </button>
      </div>
    `;

    document.getElementById("unblock-btn").addEventListener("click", () => {
      chrome.storage.local.get(["blacklist"], (result) => {
        const updatedList = (result.blacklist || []).filter(d => d !== domain);
        chrome.storage.local.set({ blacklist: updatedList }, () => {
          location.reload();
        });
      });
    });
  }

  // Warning overlay
  function showWarningOverlay() {
    const overlay = document.createElement("div");
    overlay.id = "website-warning-modal";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.95)";
    overlay.style.zIndex = "999999";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.justifyContent = "center";
    overlay.style.alignItems = "center";
    overlay.style.color = "#fff";
    overlay.style.fontFamily = "Arial, sans-serif";
    overlay.style.padding = "20px";
    overlay.style.textAlign = "center";

    const heading = document.createElement("h1");
    heading.textContent = `You’re visiting: ${domain}`;
    heading.style.fontSize = "28px";
    heading.style.marginBottom = "30px";

    const continueBtn = document.createElement("button");
    continueBtn.textContent = "Continue";
    continueBtn.style.padding = "12px 24px";
    continueBtn.style.margin = "10px";
    continueBtn.style.fontSize = "18px";
    continueBtn.style.border = "none";
    continueBtn.style.borderRadius = "8px";
    continueBtn.style.backgroundColor = "#4caf50";
    continueBtn.style.color = "#fff";
    continueBtn.style.cursor = "pointer";
    continueBtn.onclick = () => {
      overlay.remove();
      chrome.storage.local.get(["whitelist"], (result) => {
        const list = result.whitelist || [];
        if (!list.includes(domain)) {
          list.push(domain);
          chrome.storage.local.set({ whitelist: list });
        }
      });
    };

    const backBtn = document.createElement("button");
    backBtn.textContent = "Go Back";
    backBtn.style.padding = "12px 24px";
    backBtn.style.margin = "10px";
    backBtn.style.fontSize = "18px";
    backBtn.style.border = "none";
    backBtn.style.borderRadius = "8px";
    backBtn.style.backgroundColor = "#f44336";
    backBtn.style.color = "#fff";
    backBtn.style.cursor = "pointer";
    backBtn.onclick = () => {
      chrome.storage.local.get(["blacklist"], (result) => {
        const list = result.blacklist || [];
        if (!list.includes(domain)) {
          list.push(domain);
          chrome.storage.local.set({ blacklist: list });
        }
      });
      window.history.back();
    };

    overlay.appendChild(heading);
    overlay.appendChild(continueBtn);
    overlay.appendChild(backBtn);
    document.body.appendChild(overlay);
  }

  // Main logic
  (async () => {
    const inWhitelist = await isDomainInList("whitelist");
    if (inWhitelist) return;

    const inBlacklist = await isDomainInList("blacklist");
    if (inBlacklist) {
      showBlockedPage();
      return;
    }

    showWarningOverlay();
  })();
})();
