let lastSelectedText = "";
let lastLinkUrl = "";

// --- Storage keys & defaults ---
const DEFAULT_STATE = {
  blacklist: [],  // ["example.com", "bad.site"]
  whitelist: [],  // ["my-safe.site"]
  enableBlocking: true
};

// Ensure defaults exist
chrome.runtime.onInstalled.addListener(async () => {
  const current = await chrome.storage.local.get(Object.keys(DEFAULT_STATE));
  const toSet = {};
  for (const [k, v] of Object.entries(DEFAULT_STATE)) {
    if (!(k in current)) toSet[k] = v;
  }
  if (Object.keys(toSet).length) await chrome.storage.local.set(toSet);
  await rebuildRules();
});

chrome.runtime.onStartup.addListener(async () => {
  await rebuildRules();
});

// Rebuild rules whenever lists change
chrome.storage.onChanged.addListener(async (changes, area) => {
  if (area !== "local") return;
  if (changes.blacklist || changes.whitelist || changes.enableBlocking) {
    await rebuildRules();
  }
});

// Listen which rule matched to know what was blocked (for blocked.html to show domain)
chrome.declarativeNetRequest.onRuleMatchedDebug.addListener(async (info) => {
  // We encode domain in rule's id map/metadata
  if (info.rule && info.rule.id && info.request) {
    // Store the last blocked domain for the blocked page to display
    const url = new URL(info.request.url);
    await chrome.storage.local.set({ lastBlockedDomain: url.hostname });
  }
});

// Build DNR rules from blacklist (minus whitelist)
async function rebuildRules() {
  const { blacklist = [], whitelist = [], enableBlocking = true } =
    await chrome.storage.local.get(["blacklist", "whitelist", "enableBlocking"]);

  // First, clear existing dynamic rules
  const existing = await chrome.declarativeNetRequest.getDynamicRules();
  const existingIds = existing.map(r => r.id);
  if (existingIds.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: existingIds });
  }

  if (!enableBlocking) return;

  // Compute effective blocked domains
  const wl = new Set(whitelist.map(normalizeDomain));
  const effective = [...new Set(blacklist.map(normalizeDomain))].filter(d => !wl.has(d));

  // Create redirect rules (main_frame only) to local blocked.html
  // Use regexFilter to match domain + subdomains
  // NOTE: We can't pass query params to extensionPath, so we store domain via onRuleMatchedDebug
  const rules = effective.map((domain, idx) => {
    const escaped = domain.replace(/\./g, "\\.");
    return {
      id: 1000 + idx, // unique id
      priority: 1,
      action: {
        type: "redirect",
        redirect: { extensionPath: "/html/blocked.html" }
      },
      condition: {
        regexFilter: `^https?://([^.]+\\.)*${escaped}(/|$)`,
        resourceTypes: ["main_frame"]
      }
    };
  });

  if (rules.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ addRules: rules });
  }
}

function normalizeDomain(d) {
  return (d || "").trim().toLowerCase();
}

// Message handlers (used by blocked.js to remove a domain)
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
