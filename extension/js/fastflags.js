export async function runFastFlags(url) {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname;

    // 1️⃣ IP address checks
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
      if (/^(127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(host))
        return { status: "allow", reason: "private or localhost IP" };
      else
        return { status: "block", reason: "public IP address" };
    }

    // 2️⃣ Punycode
    if (host.includes("xn--"))
      return { status: "block", reason: "punycode domain" };

    // 3️⃣ URL shorteners
    const shorteners = new Set(["bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "adf.ly"]);
    const cleanHost = host.replace(/^www\./, "");
    if (shorteners.has(cleanHost))
      return { status: "block", reason: "URL shortening service" };

    // 4️⃣ "@" redirect trick
    if (parsed.href.includes("@")) {
      const beforeAt = parsed.href.split("@")[0];
      const afterAt = parsed.href.split("@")[1];
      try {
        const redirectHost = new URL("https://" + afterAt).hostname.toLowerCase();
        const beforeHost = new URL(
          beforeAt.includes("://") ? beforeAt : "https://" + beforeAt
        ).hostname.toLowerCase();

        if (redirectHost !== beforeHost) {
          // Different — clearly an obfuscation trick → block
          return { status: "block", reason: "@ redirect mismatch" };
        } else {
          // Same host on both sides of '@' — do NOT decide here.
          // Return neutral so the URL proceeds to the full backend scan.
          return { status: "neutral", reason: "@ hosts match (defer to backend)" };
        }
      } catch (err) {
        // Malformed after-@ part or parse error — safer to block
        return { status: "block", reason: "malformed @ redirect" };
      }
}

    // 5️⃣ Harmful file extensions
    const ext = parsed.pathname.split(".").pop().toLowerCase();
    if (harmfulExtensions.has(ext))
      return { status: "block", reason: `harmful extension: .${ext}` };

    return { status: "neutral", reason: "no fast flags triggered" };

  } catch (err) {
    console.error("FastFlag error:", err);
    return { status: "neutral", reason: "URL parse error" };
  }
}

const harmfulExtensions = new Set([
  "exe","bat","cmd","js","vbs","vbe","wsf","wsh","scr","dll","msi","msp","mst",
  "jar","ps1","ps2","reg","pif","chm","hta","cpl","com","msc","ocx","inf"
]);
