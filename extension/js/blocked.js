// Get last blocked info from storage
chrome.storage.local.get(["lastBlockedDomain", "lastBlockedUrl"], ({ lastBlockedDomain, lastBlockedUrl }) => {
  const domain = lastBlockedDomain || null;
  const blockedUrl = lastBlockedUrl || null;
  const messageEl = document.getElementById("blocked-domain");

  // Show only the domain
  if (domain) {
    messageEl.textContent = `The domain "${domain}" is in your blacklist.`;
  } else {
    messageEl.textContent = "This site is in your blacklist.";
  }

  // Handle Unblock button
  document.getElementById("unblock-btn").addEventListener("click", () => {
    if (!domain) return;

    chrome.runtime.sendMessage({ action: "moveToWhitelist", domain }, (res) => {
      if (res?.ok) {
        if (blockedUrl) {
          window.location.href = blockedUrl;
        } else {
          window.location.href = "https://" + domain; // fallback
        }
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
