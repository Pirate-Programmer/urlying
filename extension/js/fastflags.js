// Global sets (shared across invocations)
const harmfulExtensions = new Set([
  "bat", "cmd", "js", "vbs", "vbe", "wsf", "wsh", "scr", "dll",
  "msi", "msp", "mst", "jar", "ps1", "ps2", "reg", "pif", "chm", "hta",
  "cpl", "com", "msc", "ocx", "inf", "sh"
]);

const shorteners = new Set([
  "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "adf.ly", "rb.gy",
  "bit.do", "shorte.st", "trib.al", "lnkd.in", "rebrand.ly", "shorturl.at",
  "clck.ru", "cutt.ly", "tiny.cc", "ouo.io", "v.gd", "short.io", "urlzs.com",
  "rb6.me", "mcaf.ee", "gg.gg", "s.id", "q.gs", "adfoc.us", "t.ly", "bitly.com",
  "lc.chat", "soo.gd", "shrtco.de", "zi.pe", "vzturl.com", "db.tt", "wp.me",
  "yourls.org", "0rz.tw", "t2m.io", "linktr.ee", "tinu.be", "2u.xf.cz", "short.cm",
  "linkbun.ch", "lnk.to", "dlvr.it", "smarturl.it", "x.co", "rb6.co", "qbn.ru",
  "bc.vc", "hyperurl.co", "linkn.co", "thesa.us", "cutt.us", "po.st", "url.ie",
  "shrunkin.com", "tcrn.ch", "z9.fr", "qxp.sk", "ad7.biz", "ph.ly", "zi.pe",
  "wa.link", "jmp2.net", "tini.cc", "minurl.fr", "zz.gd", "2.gp", "lnk.in",
  "clk.sh", "isra.li", "y2u.be", "lurl.no", "shortna.me", "moourl.com", "tr.im",
  "snip.ly", "ulvis.net", "updat.es", "dfl8.me", "decenturl.com", "tiny.pl",
  "url4.eu", "sptfy.com", "picz.in", "kapwi.ng", "git.io", "linkvertise.com"
]);

// Persistent whitelist/blacklist (populated from storage)
let whitelist = new Set();
let blacklist = new Set();

chrome.storage.local.get(["whitelist", "blacklist"], (data) => {
  whitelist = new Set(data.whitelist || []);
  blacklist = new Set(data.blacklist || []);
});

export async function runFastFlags(url) {
  try {
    const parsed = new URL(url);
    let host = parsed.hostname.toLowerCase();
    if (host.startsWith("www.")) host = host.slice(4); // strip www

    const result = { status: "neutral", reason: "no fast flags triggered", domain: host };

    // Whitelist check
    if (whitelist.has(host) || whitelist.has(url)) {
      result.status = "allow";
      result.reason = "whitelisted";
      return result;
    }

    // Helper to persist blocked info
    async function setBlocked(reasonStr) {
      await chrome.storage.local.set({
        lastBlockedDomain: host,
        lastBlockedUrl: url,
        lastBlockedReason: reasonStr,
        lastBlockedScore: null,
        timestamp: Date.now()
      });
    }

    // Public IP
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
      if (/^(127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(host)) {
        result.status = "allow";
        result.reason = "private/local IP";
      } else {
        addToBlacklist(host);
        result.status = "block";
        result.reason = "public IP address";
        await setBlocked(result.reason);
      }
      return result;
    }

    // Punycode
    if (host.includes("xn--")) {
      addToBlacklist(host);
      result.status = "block";
      result.reason = "punycode domain";
      await setBlocked(result.reason);
      return result;
    }

    // URL shortener
    if (shorteners.has(host)) {
      addToBlacklist(host);
      result.status = "block";
      result.reason = "URL shortener";
      await setBlocked(result.reason);
      return result;
    }

    // @ redirect trick
    if (parsed.href.includes("@")) {
      try {
        const [beforeAt, afterAt] = parsed.href.split("@");
        const redirectHost = new URL("https://" + afterAt).hostname.toLowerCase();
        const beforeHost = new URL(
          beforeAt.includes("://") ? beforeAt : "https://" + beforeAt
        ).hostname.toLowerCase();

        if (redirectHost !== beforeHost) {
          addToBlacklist(host);
          result.status = "block";
          result.reason = "@ redirect mismatch";
          await setBlocked(result.reason);
          return result;
        }
      } catch {
        addToBlacklist(host);
        result.status = "block";
        result.reason = "malformed @ redirect";
        await setBlocked(result.reason);
        return result;
      }
    }

    // Harmful extensions
    const ext = parsed.pathname.split(".").pop().toLowerCase();
    if (harmfulExtensions.has(ext)) {
      addToBlacklist(host);
      result.status = "block";
      result.reason = "harmful extension";
      await setBlocked(result.reason);
      return result;
    }

    return result;

  } catch (err) {
    console.error("FastFlags error:", err);
    return { status: "neutral", reason: "URL parse error", domain: null };
  }
}


// ✅ Normalize and persist correctly
function addToBlacklist(domain) {
  if (!blacklist.has(domain)) {
    blacklist.add(domain);
    chrome.storage.local.set({ blacklist: Array.from(blacklist) }, () => {
      console.log("🚫 FastFlag added to blacklist:", domain);
    });
  }
}
