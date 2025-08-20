document.getElementById("blacklistBtn").addEventListener("click", () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    let url = new URL(tabs[0].url);
    let domain = url.hostname;

    chrome.storage.local.get({blacklist: [], whitelist: []}, (data) => {
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
