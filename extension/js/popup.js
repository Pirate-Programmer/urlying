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
    window.location.href = `../html/blocked.html?domain=${domain}`;

    document.getElementById("unblock-btn").addEventListener("click", () => {
      chrome.storage.local.get(["blacklist"], (result) => {
        const updatedList = (result.blacklist || []).filter(d => d !== domain);
        chrome.storage.local.set({ blacklist: updatedList }, () => {
          location.reload();
        });
      });
    });
  }

  (async () => {
    const inWhitelist = await isDomainInList("whitelist");
    if (inWhitelist) return;

    const inBlacklist = await isDomainInList("blacklist");
    if (inBlacklist) {
      showBlockedPage();
      return;
    }

  })();
})();