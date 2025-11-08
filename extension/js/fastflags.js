// Global sets (shared across invocations)
const harmfulExtensions = new Set([
  "exe", "bat", "cmd", "js", "vbs", "vbe", "wsf", "wsh", "scr", "dll",
  "msi", "msp", "mst", "jar", "ps1", "ps2", "reg", "pif", "chm", "hta",
  "cpl", "com", "msc", "ocx", "inf"
]);

const shorteners = new Set([
  "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "adf.ly", "rb.gy",
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
    const host = parsed.hostname;

    // ✅ Check whitelist first
    if (whitelist.has(host) || whitelist.has(url)) {
      return { status: "allow", reason: "whitelisted" };
    }

    // 1️⃣ IP address checks
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
      if (/^(127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(host)) {
        return { status: "allow", reason: "private/local IP" };
      } else {
        addToBlacklist(url);
        return { status: "block", reason: "public IP address" };
      }
    }

    // 2️⃣ Punycode
    if (host.includes("xn--")) {
      addToBlacklist(url);
      return { status: "block", reason: "punycode domain" };
    }

    // 3️⃣ URL shorteners
    const cleanHost = host.replace(/^www\./, "");
    if (shorteners.has(cleanHost)) {
      addToBlacklist(url);
      return { status: "block", reason: "URL shortener" };
    }

    // 4️⃣ "@" redirect trick
    if (parsed.href.includes("@")) {
      try {
        const [beforeAt, afterAt] = parsed.href.split("@");
        const redirectHost = new URL("https://" + afterAt).hostname.toLowerCase();
        const beforeHost = new URL(
          beforeAt.includes("://") ? beforeAt : "https://" + beforeAt
        ).hostname.toLowerCase();

        if (redirectHost !== beforeHost) {
          addToBlacklist(url);
          return { status: "block", reason: "@ redirect mismatch" };
        }
      } catch {
        addToBlacklist(url);
        return { status: "block", reason: "malformed @ redirect" };
      }
    }

    // 5️⃣ Harmful file extensions
    const ext = parsed.pathname.split(".").pop().toLowerCase();
    if (harmfulExtensions.has(ext)) {
      addToBlacklist(url);
      return { status: "block", reason: `harmful extension: .${ext}` };
    }

    return { status: "neutral", reason: "no fast flags triggered" };
  } catch (err) {
    console.error("FastFlags error:", err);
    return { status: "neutral", reason: "URL parse error" };
  }
}

// Helper to add to blacklist and persist
function addToBlacklist(url) {
  if (!blacklist.has(url)) {
    blacklist.add(url);
    chrome.storage.local.set({ blacklist: Array.from(blacklist) });
  }
}
