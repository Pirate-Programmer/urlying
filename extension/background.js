let lastSelectedText = "";

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeText",
    title: "Check if your URL is Lying",
    contexts: ["all"]
  });
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "updateSelection") {
    lastSelectedText = msg.text;
  }
});

chrome.contextMenus.onClicked.addListener(() => {
  if (lastSelectedText) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        func: (text) => {
          console.log("Context Menu Selected text:", text);
        },
        args: [lastSelectedText]
      });
    });
  }
});
