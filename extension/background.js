let lastSelectedText = "";
let lastLinkUrl = "";

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeText",
    title: "Check if your URL is Lying",
    contexts: ["all"]
  });
});

// Listen for selection or link clicks
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "updateSelection") {
    lastSelectedText = msg.text;
  }
  if (msg.type === "updateLink") {
    lastLinkUrl = msg.url;
  }
});

// On context menu click, inject into page
chrome.contextMenus.onClicked.addListener(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: (text, link) => {
        if (link) {
          showSpeedometer(link);
        } else if (text) {
          showSpeedometer(text);
        } else {
          alert("No text or link selected.");
        }
      },
      args: [lastSelectedText, lastLinkUrl]
    });
  });
});
