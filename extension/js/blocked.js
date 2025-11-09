let blockedDomain = null;
let blockedUrl = null;
let blockedReason = null;
let blockedScore = null;

chrome.storage.local.get(
  ["lastBlockedDomain", "lastBlockedUrl", "lastBlockedReason", "lastBlockedScore"],
  ({ lastBlockedDomain, lastBlockedUrl, lastBlockedReason, lastBlockedScore }) => {
    blockedDomain = lastBlockedDomain || null;
    blockedUrl = lastBlockedUrl || null;
    blockedReason = lastBlockedReason || null;
    blockedScore = lastBlockedScore ?? null;

    const messageEl = document.getElementById("blocked-domain");

    // ===== MESSAGE LOGIC =====
    if (blockedDomain) {
      switch (blockedReason) {
        case "auto_blacklist":
          messageEl.textContent = `This domain "${blockedDomain}" has been flagged as malicious or harmful.`;
          break;
        case "dnr_rule":
          messageEl.textContent = `This domain "${blockedDomain}" is blocked by your blacklist rules.`;
          break;
        case "public IP address":
          messageEl.textContent = `"${blockedDomain}" is a public IP address.`;
          break;
        case "punycode domain":
          messageEl.textContent = `The domain is punycoded. It resolves to "${blockedDomain}".`;
          break;
        case "URL shortener":
          messageEl.textContent = `The domain is using a URL shortening service hiding the true destination.`;
          break;
        case "harmful extension":
          messageEl.textContent = `The URL is downloading a file with harmful file extension.`;
          break;
        case "@ redirect mismatch":
        case "malformed @ redirect":
          messageEl.textContent = `You are being redirected to "${blockedDomain}".`;
          break;
        default:
          messageEl.textContent = `The domain "${blockedDomain}" is in your blacklist.`;
      }
    } else {
      messageEl.textContent = "This site is in your blacklist.";
    }
  }
);

// ✅ Unblock button uses already loaded variables, not storage
document.getElementById("unblock-btn").addEventListener("click", () => {
  chrome.storage.local.get(["lastBlockedDomain", "lastBlockedUrl"], ({ lastBlockedDomain, lastBlockedUrl }) => {
    if (!lastBlockedDomain) {
      alert("No domain available to unblock.");
      return;
    }

    // Move to whitelist and rebuild rules first
    chrome.runtime.sendMessage({ action: "moveToWhitelist", domain: lastBlockedDomain }, async () => {
      // Wait a small delay to ensure rules rebuild
      await new Promise(resolve => setTimeout(resolve, 50));

      // Redirect after whitelist + rules update
      chrome.runtime.sendMessage({
        action: "redirectAfterUnblock",
        domain: lastBlockedDomain,
        blockedUrl: lastBlockedUrl || `https://${lastBlockedDomain}`
      });
    });
  });
});



// ✅ Go back button
document.getElementById("go-back-btn").addEventListener("click", () => {
  if (window.history.length > 1) window.history.back();
  else window.close();
});

