document.addEventListener("DOMContentLoaded", () => {
  function renderList(listName, ulId, filter = "") {
    chrome.storage.local.get([listName, "whitelist", "blacklist"], (result) => {
      const ul = document.getElementById(ulId);
      ul.innerHTML = "";

      let list = result[listName] || [];

      // ✅ If whitelist, clean up expired entries silently
      if (listName === "whitelist") {
        const now = Date.now();
        list = list.filter(entry => entry.expiry > now); // keep only valid
        if (list.length !== (result[listName] || []).length) {
          chrome.storage.local.set({ whitelist: list });
        }
      }

      // Normalize to strings for rendering
      const displayList = listName === "whitelist"
        ? list.map(entry => entry.domain)
        : list;

      displayList
  .filter(domain => domain.toLowerCase().includes(filter.toLowerCase()))
  .forEach(domain => {
    const li = document.createElement("li");

    // Make li a flex container
    li.style.display = "flex";
    li.style.alignItems = "center";
    li.style.justifyContent = "space-between";
    li.style.padding = "4px 8px";
    li.style.boxSizing = "border-box";
    li.style.width = "17cm";  // make li full width of ul

    // Domain text container
    const textSpan = document.createElement("span");
    textSpan.textContent = domain;

    // Make text scrollable horizontally
    textSpan.style.flex = "1";
    textSpan.style.overflowX = "auto";
    textSpan.style.whiteSpace = "nowrap";
    textSpan.style.marginRight = "5px"; // small gap before buttons
    textSpan.style.textOverflow = "clip";
    textSpan.style.scrollbarColor = "wheat #1e1e1e";

    // Button container
    const btnGroup = document.createElement("div");
    btnGroup.style.display = "inline-flex";

    // Arrow button
    const arrowBtn = document.createElement("button");
    arrowBtn.textContent = listName === "whitelist" ? "\u2192" : "\u2190";
    arrowBtn.title = listName === "whitelist" ? "Move to blacklist" : "Move to whitelist";
    arrowBtn.style.marginLeft = "15px";
    arrowBtn.onclick = () => {
      chrome.storage.local.get(["whitelist", "blacklist"], (res) => {
        let whitelist = res.whitelist || [];
        let blacklist = res.blacklist || [];

        if(listName === "whitelist"){
          whitelist = whitelist.filter(e => e.domain !== domain);
          if(!blacklist.includes(domain)) blacklist.push(domain);
        } else {
          blacklist = blacklist.filter(d => d !== domain);
          const expiry = Date.now() + 30*24*60*60*1000;
          if(!whitelist.some(e => e.domain === domain)) whitelist.push({domain, expiry});
        }

        chrome.storage.local.set({whitelist, blacklist}, () => {
          renderList("whitelist", "whitelist-list");
          renderList("blacklist", "blacklist-list");
        });
      });
    };

    // Remove button
    const delBtn = document.createElement("button");
    delBtn.textContent = "Remove";
    delBtn.style.marginLeft = "10px"; // keep arrow 10px left
    delBtn.onclick = () => {
      chrome.storage.local.get([listName], (res) => {
        let updated = res[listName] || [];
        if(listName === "whitelist") updated = updated.filter(e => e.domain !== domain);
        else updated = updated.filter(d => d !== domain);
        chrome.storage.local.set({[listName]: updated}, () => {
          renderList(listName, li.parentElement.id);
        });
      });
    };

    // Append buttons and text
    btnGroup.appendChild(arrowBtn);
    btnGroup.appendChild(delBtn);

    li.appendChild(textSpan);
    li.appendChild(btnGroup);

    ul.appendChild(li);
  });

    });
  }

  // --- Add to whitelist with expiry ---
  document.getElementById("add-whitelist").onclick = () => {
    const input = document.getElementById("whitelist-input");
    const domain = input.value.trim().toLowerCase();
    if (!domain) return;

    const expiryPeriod = 30 * 24 * 60 * 60 * 1000; // 30 days
    const expiry = Date.now() + expiryPeriod;

    chrome.storage.local.get(["whitelist", "blacklist"], (result) => {
      let whitelist = result.whitelist || [];
      let blacklist = result.blacklist || [];

      // Remove from blacklist if present
      blacklist = blacklist.filter(d => d !== domain);

      // Only add if not already whitelisted
      if (!whitelist.some(e => e.domain === domain)) {
        whitelist.push({ domain, expiry });
      }

      chrome.storage.local.set({ whitelist, blacklist }, () => {
        input.value = "";
        renderList("whitelist", "whitelist-list");
        renderList("blacklist", "blacklist-list");
      });
    });
  };

  // --- Add to blacklist ---
  document.getElementById("add-blacklist").onclick = () => {
    const input = document.getElementById("blacklist-input");
    const domain = input.value.trim().toLowerCase();
    if (!domain) return;

    chrome.storage.local.get(["whitelist", "blacklist"], (result) => {
      let whitelist = result.whitelist || [];
      let blacklist = result.blacklist || [];

      // Remove from whitelist if present
      whitelist = whitelist.filter(e => e.domain !== domain);

      if (!blacklist.includes(domain)) {
        blacklist.push(domain);
      }

      chrome.storage.local.set({ whitelist, blacklist }, () => {
        input.value = "";
        renderList("blacklist", "blacklist-list");
        renderList("whitelist", "whitelist-list");
      });
    });
  };

  // --- Search filters ---
  ["whitelist", "blacklist"].forEach(listName => {
    document.getElementById(`search-${listName}`).addEventListener("input", (e) => {
      renderList(listName, `${listName}-list`, e.target.value);
    });
  });

  document.getElementById("search-whitelist").value = "";
  document.getElementById("search-blacklist").value = "";

  renderList("whitelist", "whitelist-list");
  renderList("blacklist", "blacklist-list");
});

// --- Allow Enter key to trigger Add buttons ---
document.getElementById("whitelist-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    document.getElementById("add-whitelist").click();
  }
});

document.getElementById("blacklist-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    document.getElementById("add-blacklist").click();
  }
});
