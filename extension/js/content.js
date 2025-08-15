if (!window.__analyzeButtonInjected) {
  window.__analyzeButtonInjected = true; // prevent double injection

  let analyzeBtn = document.createElement("button");
  analyzeBtn.id = "analyze-btn";
  analyzeBtn.innerText = "Analyze";
  analyzeBtn.style.display = "none";
  document.body.appendChild(analyzeBtn);

  let currentSelection = "";

  document.addEventListener("mouseup", () => {
    let text = window.getSelection().toString().trim();

    if (text.length > 0) {
      currentSelection = text;

      // Send selection to background for context menu use
      chrome.runtime.sendMessage({ type: "updateSelection", text: text });

      // Position button
      let range = window.getSelection().getRangeAt(0);
      let rect = range.getBoundingClientRect();

      analyzeBtn.style.top = (window.scrollY + rect.bottom + 5) + "px";
      analyzeBtn.style.left = (window.scrollX + rect.left) + "px";
      analyzeBtn.style.display = "block";
    } else {
      analyzeBtn.style.display = "none";
    }
  });

  analyzeBtn.addEventListener("click", () => {
    console.log("Floating Button Selected text:", currentSelection);
    analyzeBtn.style.display = "none";
  });
}
