// Get last blocked domain from storage
chrome.storage.local.get("lastBlockedDomain", ({ lastBlockedDomain }) => {
  const domain = lastBlockedDomain || null;
  const messageEl = document.getElementById("blocked-domain");

  if (domain) {
    messageEl.textContent = `The domain "${domain}" is in your blacklist.`;
  } else {
    messageEl.textContent = "This site is in your blacklist.";
  }

  // Handle Unblock button
  document.getElementById("unblock-btn").addEventListener("click", () => {
    if (!domain) return;

    // Ask background.js to move domain from blacklist → whitelist
    chrome.runtime.sendMessage({ action: "moveToWhitelist", domain }, (res) => {
      if (res?.ok) {
        // Redirect user back to site
        window.location.href = "https://" + domain;
      } else {
        alert("Failed to unblock the domain.");
      }
    });
  });
});

// Handle Go Back button
document.getElementById("go-back-btn").addEventListener("click", () => {
  if (window.history.length > 1) {
    window.history.back();
  } else {
    window.close();
  }
});
