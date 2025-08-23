let lastSelectedText = "";
let lastLinkUrl = "";

// --- Safe defaults ---
const DEFAULT_STATE = {
  blacklist: [],
  whitelist: [],
  enableBlocking: true
};

// ✅ On install, only set defaults if missing (don’t clear lists)
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(Object.keys(DEFAULT_STATE), (data) => {
    const toSet = {};
    for (const [k, v] of Object.entries(DEFAULT_STATE)) {
      if (data[k] === undefined) {
        toSet[k] = v;
      }
    }
    if (Object.keys(toSet).length > 0) {
      chrome.storage.local.set(toSet);
    }
  });
});

// ✅ On startup, rebuild rules from current lists
chrome.runtime.onStartup.addListener(async () => {
  await rebuildRules();
});

// Rebuild whenever storage changes
chrome.storage.onChanged.addListener(async (changes, area) => {
  if (area !== "local") return;
  if (changes.blacklist || changes.whitelist || changes.enableBlocking) {
    await rebuildRules();
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "moveToWhitelist") {
    const domain = msg.domain;

    chrome.storage.local.get(["blacklist", "whitelist"], (data) => {
      let blacklist = data.blacklist || [];
      let whitelist = data.whitelist || [];

      // Remove from blacklist
      blacklist = blacklist.filter(d => d !== domain);

      // Add to whitelist if not already
      if (!whitelist.includes(domain)) {
        whitelist.push(domain);
      }

      // Save back
      chrome.storage.local.set({ blacklist, whitelist }, async () => {
        // 🔑 Rebuild rules immediately
        await rebuildRules();
        sendResponse({ ok: true });
      });
    });

    return true; // async
  }
});



// Track last blocked domain (for blocked.html display)
chrome.declarativeNetRequest.onRuleMatchedDebug.addListener(async (info) => {
  if (info.request && info.request.url) {
    const url = new URL(info.request.url);
    await chrome.storage.local.set({ lastBlockedDomain: url.hostname });
  }
});

// Build DNR rules from blacklist - whitelist
async function rebuildRules() {
  const { blacklist = [], whitelist = [], enableBlocking = true } =
    await chrome.storage.local.get(["blacklist", "whitelist", "enableBlocking"]);

  // Clear current rules
  const existing = await chrome.declarativeNetRequest.getDynamicRules();
  const existingIds = existing.map(r => r.id);
  if (existingIds.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: existingIds });
  }

  if (!enableBlocking) return;

  // Effective blocked domains = blacklist - whitelist
  const wl = new Set(whitelist.map(normalizeDomain));
  const effective = [...new Set(blacklist.map(normalizeDomain))].filter(d => !wl.has(d));

  // Build redirect rules
  const rules = effective.map((domain, idx) => ({
    id: 1000 + idx,
    priority: 1,
    action: {
      type: "redirect",
      redirect: { extensionPath: "/html/blocked.html" }
    },
    condition: {
      urlFilter: `||${domain}`,
      resourceTypes: ["main_frame"]
    }
  }));

  if (rules.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ addRules: rules });
  }
}

function normalizeDomain(d) {
  return (d || "").trim().toLowerCase();
}

// Handle unblock messages from blocked.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.action === "unblock" && msg.domain) {
    (async () => {
      const { blacklist = [] } = await chrome.storage.local.get("blacklist");
      const updated = blacklist.filter(d => normalizeDomain(d) !== normalizeDomain(msg.domain));
      await chrome.storage.local.set({ blacklist: updated });
      await rebuildRules();
      sendResponse({ ok: true });
    })();
    return true; // async
  }
});

// Context menu for “Check if your URL is Lying”
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeText",
    title: "Check if your URL is Lying",
    contexts: ["all"]
  });
});

// Track selection/link messages
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "updateSelection") {
    lastSelectedText = msg.text;
  }
  if (msg.type === "updateLink") {
    lastLinkUrl = msg.url;
  }
});

// Context menu click handler
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
