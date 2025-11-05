// blocked.js
let blockedDomain = null;
let blockedUrl = null;

chrome.storage.local.get(
  ["lastBlockedDomain", "lastBlockedUrl", "lastBlockedReason", "lastBlockedScore"],
  ({ lastBlockedDomain, lastBlockedUrl, lastBlockedReason, lastBlockedScore }) => {

    blockedDomain = lastBlockedDomain || null;  // ✅ store globally for later use
    blockedUrl = lastBlockedUrl || null;

    const reason = lastBlockedReason || null;
    const score = lastBlockedScore ?? null;

    const messageEl = document.getElementById("blocked-domain");
    const detailsEl = document.getElementById("blocked-details");

    // ===== MESSAGE LOGIC =====
    if (reason === "auto_blacklist") {
      messageEl.textContent = blockedDomain
        ? `This domain (${blockedDomain}) has been flagged as malicious or harmful.`
        : "This site has been blacklisted.";
    } else if (reason === "dnr_rule") {
      messageEl.textContent = blockedDomain
        ? `This domain (${blockedDomain}) is blocked by your blacklist rules.`
        : "This site is blocked by your blacklist rules.";
    } else {
      messageEl.textContent = blockedDomain
        ? `The domain "${blockedDomain}" is in your blacklist.`
        : "This site is in your blacklist.";
    }

    // ===== DETAILS =====
    if (score !== null || blockedUrl) {
      let parts = [];
      if (score !== null) parts.push(`Risk score: ${score}`);
      if (blockedUrl) parts.push(`URL: ${blockedUrl}`);
      detailsEl.textContent = parts.join(" • ");
    } else {
      if (detailsEl) detailsEl.style.display = "none";
    }
});
  

// ✅ Unblock button now uses the stored domain value
document.getElementById("unblock-btn").addEventListener("click", () => {
  if (!blockedDomain) {
    alert("No domain available to unblock.");
    return;
  }

  chrome.runtime.sendMessage({ action: "moveToWhitelist", domain: blockedDomain }, (res) => {
    if (res?.ok) {
      chrome.runtime.sendMessage({
        action: "redirectAfterUnblock",
        domain: blockedDomain,
        blockedUrl
      });
    } else {
      alert("Failed to unblock the domain.");
    }
  });
});


// ✅ Go back button
document.getElementById("go-back-btn").addEventListener("click", () => {
  if (window.history.length > 1) window.history.back();
  else window.close();
});
