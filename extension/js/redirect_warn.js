document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get(["lastAtSpoof"], ({ lastAtSpoof }) => {
    if (!lastAtSpoof) return;

    const { spoofedPart, actualHost } = lastAtSpoof;

    const redirectDomain = actualHost || null;
    const pretendedDomain = spoofedPart || null;
    const messageRedirectDomain = document.getElementById("redirect-domain");
    const messageRedirectDomain2 = document.getElementById("redirect-domain-2");
    const messagePretendedDomain = document.getElementById("spoof-domain");
    const fullParagraph = document.getElementById("suspicious-domain");

    if (redirectDomain && pretendedDomain) {
      messageRedirectDomain.textContent = `"${redirectDomain}"`;
      messageRedirectDomain2.textContent = `"${redirectDomain}"`;
      messagePretendedDomain.textContent = pretendedDomain;
    } else {
      fullParagraph.textContent =
        "The link is redirecting you to another site while pretending to be legitimate.";
    }

    // continue button → move to whitelist
    document.getElementById("continue-btn").addEventListener("click", () => {
      if (!redirectDomain) return;
      chrome.runtime.sendMessage(
        { action: "moveToWhitelist", domain: redirectDomain },
        (res) => {
          if (res?.ok) {
            // actually go to the site now
            window.location.href = "https://" + redirectDomain;
          }
        }
      );
    });

    // go to spoofed (pretended) domain
    document.getElementById("spoof-btn").addEventListener("click", () => {
      if (!pretendedDomain) return;
      window.location.href = "https://" + pretendedDomain;
    });

    // go back
    document.getElementById("go-back-btn").addEventListener("click", () => {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.close();
      }
    });
  });
});
