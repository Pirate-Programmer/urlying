document.addEventListener("DOMContentLoaded", () => {
  function renderList(listName, ulId, filter = "") {
    chrome.storage.local.get([listName], (result) => {
      const ul = document.getElementById(ulId);
      ul.innerHTML = "";

      (result[listName] || [])
        .filter(domain => domain.toLowerCase().includes(filter.toLowerCase()))
        .forEach(domain => {
          const li = document.createElement("li");
          li.textContent = domain;

          const delBtn = document.createElement("button");
          delBtn.textContent = "Remove";
          delBtn.onclick = () => {
            chrome.storage.local.get([listName], (res) => {
              const updatedList = (res[listName] || []).filter(d => d !== domain);
              chrome.storage.local.set({ [listName]: updatedList }, () => {
                renderList(listName, ulId, filter);
              });
            });
          };

          li.appendChild(delBtn);
          ul.appendChild(li);
        });
    });
  }

  // --- Add to whitelist ---
  document.getElementById("add-whitelist").onclick = () => {
    const input = document.getElementById("whitelist-input");
    const domain = input.value.trim().toLowerCase();
    if (!domain) return;

    chrome.storage.local.get(["whitelist", "blacklist"], (result) => {
      let whitelist = result.whitelist || [];
      let blacklist = result.blacklist || [];

      // Remove from blacklist if present
      blacklist = blacklist.filter(d => d !== domain);

      if (!whitelist.includes(domain)) {
        whitelist.push(domain);
      }

      chrome.storage.local.set({ whitelist, blacklist }, () => {
        input.value = "";
        renderList("whitelist", "whitelist-list");
        renderList("blacklist", "blacklist-list"); // refresh both
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
      whitelist = whitelist.filter(d => d !== domain);

      if (!blacklist.includes(domain)) {
        blacklist.push(domain);
      }

      chrome.storage.local.set({ whitelist, blacklist }, () => {
        input.value = "";
        renderList("blacklist", "blacklist-list");
        renderList("whitelist", "whitelist-list"); // refresh both
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

