chrome.storage.local.get(["lastBlockedDomain", "lastBlockedUrl"], ({ lastBlockedDomain, lastBlockedUrl }) => {
  const domain = lastBlockedDomain || null;
  const blockedUrl = lastBlockedUrl || null;
  const messageEl = document.getElementById("blocked-domain");

  // show only the domain on the blocked page
  if (domain) {
    messageEl.textContent = `The domain "${domain}" is in your blacklist.`;
  } else {
    messageEl.textContent = "This site is in your blacklist."; // default message if unable to fetch domain
  }

  // logic to handle "Remove from blacklist and continue"
  document.getElementById("unblock-btn").addEventListener("click", () => {
    if (!domain) return;

    chrome.runtime.sendMessage({ action: "moveToWhitelist", domain }, (res) => {
      if (res?.ok) {
        chrome.runtime.sendMessage({ action: "redirectAfterUnblock", domain, blockedUrl });
      } else {
        alert("Failed to unblock the domain."); // both cannot be retrieved
      }
    });
  });
});

// logic to handle "Go Back"
document.getElementById("go-back-btn").addEventListener("click", () => {
  if (window.history.length > 1) {
    window.history.back(); // take user to previous site
  } else {
    window.close();
  }
});
