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
        ? `This domain "${blockedDomain}" has been flagged as malicious or harmful.`
        : "This site has been blacklisted.";
    } else if (reason === "dnr_rule") {
      messageEl.textContent = blockedDomain
        ? `This domain "${blockedDomain}" is blocked by your blacklist rules.`
        : "This site is blocked by your blacklist rules.";
    } else if(reason === "public IP address") {
      messageEl.textContent = blockedDomain
        ? `"${blockedDomain}" is Public IP address.`
        : "This site may be malicious or harmful.";
    }else if(reason === "punycode domain"){
      messageEl.textContent = blockedDomain
        ? `The domain is punycoded. It resolves to "${blockedDomain}".`
        : "This site may be malicious or harmful.";
    }else if(reason === "URL shortener"){
      messageEl.textContent = blockedDomain
        ? `The domain is using shortening service hiding true destination.`
        : "This site may be malicious or harmful.";
    }else if(reason === "harmful extension") {
      messageEl.textContent = blockedDomain
        ? `The URL is downloading a file with harmful file extension`
        : "Please review before downloading.";
    }else if(reason === "@ redirect mismatch" || reason === "malformed @ redirect"){
      messageEl.textContent = blockedDomain
        ? `You are being redirected to "${blockedDomain}"`
        : "We have blacklisted this domain as it may be malicious or harmful.";
    }else {
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
      console.log(`✅ ${blockedDomain} moved to whitelist. Redirecting...`);
      chrome.runtime.sendMessage({
        action: "redirectAfterUnblock",
        domain: blockedDomain,
        blockedUrl: blockedUrl || `https://${blockedDomain}`
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
