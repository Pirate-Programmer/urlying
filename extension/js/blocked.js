const params = new URLSearchParams(window.location.search);
const domain = params.get("domain");

const messageEl = document.getElementById("blocked-domain");
if (domain) {
    messageEl.textContent = `The domain "${domain}" is in your blacklist.`;
} else {
    messageEl.textContent = "This site is in your blacklist.";
}

document.getElementById("unblock-btn").addEventListener("click", () => {
    if (!domain) return;

    chrome.storage.local.get(["blacklist", "whitelist"], (result) => {
        let updatedBlacklist = (result.blacklist || []).filter(d => d !== domain);
        let updatedWhitelist = result.whitelist || [];

        if (!updatedWhitelist.includes(domain)) {
            updatedWhitelist.push(domain);
        }

        chrome.storage.local.set(
            { blacklist: updatedBlacklist, whitelist: updatedWhitelist },
            () => {
                window.location.href = "https://" + domain;
            }
        );
    });
});

document.getElementById("go-back-btn").addEventListener("click", () => {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.close(); 
    }
});
