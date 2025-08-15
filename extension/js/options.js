function renderList(listName, ulId) {
  chrome.storage.local.get([listName], (result) => {
    const ul = document.getElementById(ulId);
    ul.innerHTML = "";
    (result[listName] || []).forEach(domain => {
      const li = document.createElement("li");
      li.textContent = domain;

      const delBtn = document.createElement("button");
      delBtn.textContent = "Remove";
      delBtn.onclick = () => {
        chrome.storage.local.get([listName], (res) => {
          const updatedList = (res[listName] || []).filter(d => d !== domain);
          chrome.storage.local.set({ [listName]: updatedList }, () => {
            renderList(listName, ulId);
          });
        });
      };

      li.appendChild(delBtn);
      ul.appendChild(li);
    });
  });
}

document.getElementById("add-whitelist").onclick = () => {
  const input = document.getElementById("whitelist-input");
  const domain = input.value.trim();
  if (domain) {
    chrome.storage.local.get(["whitelist"], (result) => {
      const list = result.whitelist || [];
      if (!list.includes(domain)) {
        list.push(domain);
        chrome.storage.local.set({ whitelist: list }, () => {
          input.value = "";
          renderList("whitelist", "whitelist-list");
        });
      }
    });
  }
};

document.getElementById("add-blacklist").onclick = () => {
  const input = document.getElementById("blacklist-input");
  const domain = input.value.trim();
  if (domain) {
    chrome.storage.local.get(["blacklist"], (result) => {
      const list = result.blacklist || [];
      if (!list.includes(domain)) {
        list.push(domain);
        chrome.storage.local.set({ blacklist: list }, () => {
          input.value = "";
          renderList("blacklist", "blacklist-list");
        });
      }
    });
  }
};

// Initial render
renderList("whitelist", "whitelist-list");
renderList("blacklist", "blacklist-list");
