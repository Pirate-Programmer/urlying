let lastSelectedText = "";
let lastLinkUrl = "";
const risk_score_threshold = 70;

// default state if blacklist and whitelist are empty
const DEFAULT_STATE = {
  blacklist: [],
  whitelist: [], // now stores {domain, expiry}
  enableBlocking: true,
  securityLevel: 3
};

// On install, only set defaults if missing (don’t clear lists)
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

  // ✅ Context menu for “Check if your URL is Lying”
  chrome.contextMenus.create({
    id: "analyzeText",
    title: "Check if your URL is Lying",
    contexts: ["all"]
  });
});

// On startup, rebuild rules from current lists
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

// ---------------------------
// Fast flag + backend processing
// ---------------------------
async function processUrl(url, tabId = null) {
  try {
    const domain = new URL(url).hostname.toLowerCase();
    const { blacklist = [], whitelist = [] } = await chrome.storage.local.get(["blacklist", "whitelist"]);

    // Fast flag: blacklist → block immediately
    if (blacklist.map(normalizeDomain).includes(domain)) {
      if (tabId) chrome.tabs.update(tabId, { url: chrome.runtime.getURL("html/blocked.html") });
      return;
    }

    // Fast flag: whitelist (remove expired entries)
    const now = Date.now();
    const validWhitelist = (whitelist || []).filter(e => e.expiry > now);
    if (validWhitelist.some(e => normalizeDomain(e.domain) === domain)) {
      return;
    }

    // TODO: additional fast flags can be added here

    // Send to backend only if not blacklisted/whitelisted
  const lvl = await chrome.storage.local.get("securityLevel");
  const securityLevel = lvl.securityLevel || 3;

    
    const res = await fetch("http://127.0.0.1:5000/check_url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, config: { securityLevel } }),
    });

    const data = await res.json();
    console.log("Backend scan result:", data);

    // Notify content script (speedometer) if tabId exists
    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        type: "updateRisk",
        risk_score: data.risk_score,
        url: url
      });
    }

    // // Optional: notify user
    // chrome.notifications.create({
    //   type: "basic",
    //   iconUrl: "icons/icon128.png",
    //   title: "URL Scan Result",
    //   message: `${url}\nRisk Score: ${data.risk_score} (${data.verdict})`,
    // });

    // Block if high-risk
    if (tabId && data.risk_score > risk_score_threshold) {
      chrome.tabs.update(tabId, { url: chrome.runtime.getURL("html/blocked.html") });
    }

    return data;  //returning result from backend to extention

  } catch (err) {
    console.error("processUrl error:", err);
  }
}

// ---------------------------
// Handle messages from content.js or popup
// ---------------------------
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  // Track selection/link messages
  if (msg.type === "updateSelection") lastSelectedText = msg.text;
  if (msg.type === "updateLink") lastLinkUrl = msg.url;

  // Analyze button clicked → process URL through fast flags + backend
  if (msg.type === "analyzeURL" && msg.url) {
    processUrl(msg.url).then(async (backendResult) => {
      // backendResult = { risk_score, url, api_results }
      sendResponse({ risk_score: backendResult?.risk_score || 0, url: msg.url });
    });
    return true; // keep async
  }

  // Move domain to whitelist
  if (msg.action === "moveToWhitelist" && msg.domain) {
    const domain = msg.domain;
    const expiryPeriod = 5000; // 24 hours
    const expiry = Date.now() + expiryPeriod;

    chrome.storage.local.get(["blacklist", "whitelist"], (data) => {
      let blacklist = data.blacklist || [];
      let whitelist = data.whitelist || [];

      // Remove from blacklist
      blacklist = blacklist.filter(d => d !== domain);

      // Add to whitelist if not already
      if (!whitelist.some(e => e.domain === domain)) {
        whitelist.push({ domain, expiry });
      }

      // Save back and rebuild rules
      chrome.storage.local.set({ blacklist, whitelist }, async () => {
        await rebuildRules();
        sendResponse({ ok: true });
      });
    });

    return true; // async
  }

  // Handle unblock messages from blocked.js
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

// ---------------------------
// Track last blocked domain (for blocked.html display)
// ---------------------------
chrome.declarativeNetRequest.onRuleMatchedDebug.addListener(async (info) => {
  if (info.request && info.request.url) {
    const url = new URL(info.request.url);
    await chrome.storage.local.set({
      lastBlockedDomain: url.hostname,
      lastBlockedUrl: info.request.url
    });
  }
});

// ---------------------------
// Context menu click handler
// ---------------------------
chrome.contextMenus.onClicked.addListener(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: (text, link) => {
        if (link) showSpeedometer(link);
        else if (text) showSpeedometer(text);
        else alert("No text or link selected.");
      },
      args: [lastSelectedText, lastLinkUrl]
    });
  });
});

// ---------------------------
// WebNavigation listener for automatic scanning
// ---------------------------
chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0) {
    processUrl(details.url, details.tabId);
  }
});

// ---------------------------
// Build DNR rules from blacklist - whitelist
// ---------------------------
async function rebuildRules() {
  const { blacklist = [], whitelist = [], enableBlocking = true } =
    await chrome.storage.local.get(["blacklist", "whitelist", "enableBlocking"]);

  const existing = await chrome.declarativeNetRequest.getDynamicRules();
  const existingIds = existing.map(r => r.id);
  if (existingIds.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: existingIds });
  }

  if (!enableBlocking) return;

  const now = Date.now();
  const validWhitelist = (whitelist || []).filter(e => e.expiry > now);
  if (validWhitelist.length !== (whitelist || []).length) {
    await chrome.storage.local.set({ whitelist: validWhitelist });
  }

  const wl = new Set(validWhitelist.map(e => normalizeDomain(e.domain)));
  const effectiveBlacklist = [...new Set(blacklist.map(normalizeDomain))].filter(d => !wl.has(d));

  const rules = effectiveBlacklist.map((domain, idx) => ({
    id: 1000 + idx,
    priority: 1,
    action: { type: "redirect", redirect: { extensionPath: "/html/blocked.html" } },
    condition: { urlFilter: `||${domain}`, resourceTypes: ["main_frame"] },
  }));

  if (rules.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ addRules: rules });
  }
}

// ---------------------------
// Helper: normalize domains
// ---------------------------
function normalizeDomain(d) {
  return (d || "").trim().toLowerCase();
}
