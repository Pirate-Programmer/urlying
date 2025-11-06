let lastSelectedText = "";
let lastLinkUrl = "";
const risk_score_threshold = 10;

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
  await cleanExpiredWhitelist();
  await rebuildRules();

  const enabled = await isExtensionEnabled();
  if (enabled) attachListeners();
  else detachListeners();

  // 🔹 Trigger dataset update on backend
  try {
    await fetch("http://127.0.0.1:5000/update_dataset", {
      method: "POST",
    });
    console.log("Triggered dataset update on backend startup.");
  } catch (err) {
    console.error("Failed to trigger dataset update:", err);
  }
});


// Rebuild whenever storage changes
chrome.storage.onChanged.addListener(async (changes, area) => {
  if (area !== "local") return;

  if (changes.enableBlocking) {
    if (changes.enableBlocking.newValue) {
      attachListeners();
    } else {
      detachListeners();
    }
  }

  if (changes.blacklist || changes.whitelist) {
    await rebuildRules();
  }
});

// ---------------------------
// Fast flag + backend processing
// ---------------------------
async function processUrl(url, tabId = null) {
  try {
    if(url.startsWith("chrome", 0)) {
      return;
    }
    const normDomain = normalizeDomain(url); // canonical domain for all checks

    // read lists (chrome.storage.local.get returns a promise in MV3)
    const { blacklist = [], whitelist = [] } = await chrome.storage.local.get(["blacklist", "whitelist"]);

    // Fast flag: blacklist → block immediately (compare normalized)
    const normalizedBlacklist = (blacklist || []).map(d => normalizeDomain(d));
    if (normalizedBlacklist.includes(normDomain)) {
      if (tabId) chrome.tabs.update(tabId, { url: chrome.runtime.getURL("html/blocked.html") });
      chrome.storage.local.set({
        lastBlockedReason: "dnr_rule",
      });
      return;
    }

    // Fast flag: whitelist (remove expired entries and compare normalized)
    const now = Date.now();
    const validWhitelist = (whitelist || []).filter(e => e && e.expiry > now);
    // persist cleanup if some expired
    if (validWhitelist.length !== (whitelist || []).length) {
      chrome.storage.local.set({ whitelist: validWhitelist });
    }
    const whitelistSet = new Set(validWhitelist.map(e => normalizeDomain(e.domain)));
    if (whitelistSet.has(normDomain)) {
      // whitelisted — skip scanning and do not block
      console.log("✅ Domain is whitelisted, skipping scan:", normDomain);

      // clear lastBlocked info so blocked page won't erroneously show
      chrome.storage.local.set({
        lastBlockedDomain: null,
        lastBlockedUrl: null,
        lastBlockedReason: null,
        lastBlockedScore: null
      });
      return;
    }

    // Not blacklisted or whitelisted → call backend
    const lvlObj = await chrome.storage.local.get("securityLevel");
    const securityLevel = lvlObj.securityLevel || 3;

    const res = await fetch("http://127.0.0.1:5000/check_url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, config: { securityLevel } }),
    });

    if (!res.ok) {
      console.error("Backend HTTP error", res.status, await res.text());
      return;
    }

    const data = await res.json();
    if (!data) {
      console.error("No data from backend");
      return;
    }

    console.log("Backend scan result:", data);

    if (tabId) {
      chrome.tabs.sendMessage(tabId, {
        type: "updateRisk",
        risk_score: data.risk_score,
        url: url
      });
    }

    // Use backend-provided domain if present, otherwise our normalized domain
    const backendDomain = data?.domain;
    const domainToBlacklist = normalizeDomain(backendDomain ?? url);
    const score = Number(data.risk_score);

    // only auto-blacklist when threshold exceeded
    if (tabId && !Number.isNaN(score) && score > risk_score_threshold) {
      // add to persistent blacklist (avoid duplicates)
      chrome.storage.local.get(["blacklist"], (items) => {
        const bl = items.blacklist || [];
        const already = bl.some(d => normalizeDomain(d) === domainToBlacklist);
        if (!already) {
          bl.push(domainToBlacklist);
          chrome.storage.local.set({ blacklist: bl }, () => {
            console.log("Added to blacklist:", domainToBlacklist);
          });
        }
      });

      // save lastBlocked info for blocked page
      chrome.storage.local.set({
        lastBlockedDomain: domainToBlacklist,
        lastBlockedUrl: url,
        lastBlockedReason: "auto_blacklist",
        lastBlockedScore: score,
        timestamp: Date.now()
      }, () => {
        // rebuild rules then redirect
        (async () => {
          try {
            await rebuildRules();
          } catch (err) {
            console.warn("rebuildRules failed:", err);
          } finally {
            chrome.tabs.update(tabId, { url: chrome.runtime.getURL("html/blocked.html") });
          }
        })();
      });
    } 
    else if(tabId && !Number.isNaN(score) && score <= 60 && score >= 30) {
      const susDomain = domainToBlacklist;

      chrome.storage.local.set({
        lastBlockedDomain: domainToBlacklist,
        lastBlockedUrl: url,
        lastBlockedReason: "auto_blacklist",
        lastBlockedScore: score,
        timestamp: Date.now()
      }, () => {
        // rebuild rules then redirect
        (async () => {
          try {
            await rebuildRules();
          } catch (err) {
            console.warn("rebuildRules failed:", err);
          } finally {
            chrome.tabs.update(tabId, { url: chrome.runtime.getURL("html/suspicious.html") });
          }
        })();
      });

    } else {
      const wlDomain = domainToBlacklist; // already normalized above

      chrome.storage.local.get(["blacklist", "whitelist"], (items) => {
        let blacklist = items.blacklist || [];
        let whitelist = items.whitelist || [];

        // remove from blacklist if present
        blacklist = blacklist.filter(d => normalizeDomain(d) !== wlDomain);

        // add to whitelist if not already present (compare normalized)
        const alreadyWhitelisted = whitelist.some(e => normalizeDomain(e.domain) === wlDomain);
        if (!alreadyWhitelisted) {
          const expiry = Date.now() + 30 * 24 * 60 * 60 * 1000; // 30 days
          whitelist.push({ domain: wlDomain, expiry });
          console.log("Added to whitelist:", wlDomain);
        } else {
          console.log("Domain already whitelisted:", wlDomain);
        }

        // save updated lists and rebuild rules
        chrome.storage.local.set({ blacklist, whitelist }, () => {
          // rebuild rules so DNR reflects the updated lists
          (async () => {
            try {
              await rebuildRules();
            } catch (err) {
              console.warn("rebuildRules failed after whitelist update:", err);
            }
          })();
        });
      });
    }

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
    const domain = normalizeDomain(msg.domain);

    chrome.storage.local.get(["blacklist", "whitelist"], (data) => {
      let blacklist = data.blacklist || [];
      let whitelist = data.whitelist || [];

      // Remove from blacklist
      blacklist = blacklist.filter(d => normalizeDomain(d) !== normalizeDomain(domain));

      // Add to whitelist if not already
      if (!whitelist.some(e => e.domain === domain)) {
        // Use default 30 days (same as options.js)
        const expiry = Date.now() + 30 * 24 * 60 * 60 * 1000; //30 dayz expiry matches with options.js
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
  if (msg.action === "redirectAfterUnblock") {
    const target = msg.blockedUrl || `https://${msg.domain}`;
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) chrome.tabs.update(tabs[0].id, { url: target });
    });
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
// --- Navigation handler ---
async function navigationHandler(details) {
  if (details.frameId !== 0) return; // only main frame
  const enabled = await isExtensionEnabled();
  if (!enabled) {
    console.log(" Skipping navigation scan — extension disabled");
    return;
  }
  processUrl(details.url, details.tabId);
}

// --- Listener control ---
function attachListeners() {
  if (!chrome.webNavigation.onCompleted.hasListener(navigationHandler)) {
    chrome.webNavigation.onCompleted.addListener(navigationHandler);
    console.log(" Navigation listener attached");
  }
}

function detachListeners() {
  if (chrome.webNavigation.onCompleted.hasListener(navigationHandler)) {
    chrome.webNavigation.onCompleted.removeListener(navigationHandler);
    console.log(" Navigation listener detached");
  }
}


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
function normalizeDomain(input) {
  if (!input) return "";
  try {
    const url = new URL(input.startsWith("http") ? input : "https://" + input);
    let host = url.hostname.toLowerCase();
    if (host.startsWith("www.")) host = host.slice(4);  // <-- strip www
    return host;
  } catch {
    let host = input.trim().toLowerCase().replace(/\/+$/, "");
    if (host.startsWith("www.")) host = host.slice(4);
    return host;
  }
}


//helper function to check exention enable state
async function isExtensionEnabled() {
  const { enableBlocking = true } = await chrome.storage.local.get("enableBlocking");
  return enableBlocking;
}


//this runs for now when chrome starts/lauches
async function cleanExpiredWhitelist() {
  const { whitelist = [] } = await chrome.storage.local.get("whitelist");
  const now = Date.now();
  const valid = whitelist.filter(e => e.expiry > now);
  if (valid.length !== whitelist.length) {
    await chrome.storage.local.set({ whitelist: valid });
  }
}


// --- Periodic cleanup of expired whitelist entries ---
setInterval(async () => {
  const { whitelist = [] } = await chrome.storage.local.get("whitelist");
  const now = Date.now();
  console.log("Cleanup check:", { now, whitelist });
  const valid = whitelist.filter(e => e.expiry > now);
  if (valid.length !== whitelist.length) {
    console.log("⚠️ Removing expired entries...");
    await chrome.storage.local.set({ whitelist: valid });
    await rebuildRules();
    console.log("✅ Cleaned expired whitelist entries");
  }
}, 5 * 10 * 1000); //runs every 5 mins to check for expired whitelist
