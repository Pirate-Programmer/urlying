if (!window.__analyzeInjected) {
  window.__analyzeInjected = true;

  let analyzeBtn = document.createElement("button");
  analyzeBtn.id = "analyze-btn";
  analyzeBtn.innerText = "Analyze";
  analyzeBtn.style.display = "none";
  document.body.appendChild(analyzeBtn);

  let currentSelection = "";

  // Track text selection
  document.addEventListener("mouseup", () => {
    let text = window.getSelection().toString().trim();
    if (text.length > 0) {
      currentSelection = text;
      chrome.runtime.sendMessage({ type: "updateSelection", text: text });

      let range = window.getSelection().getRangeAt(0);
      let rect = range.getBoundingClientRect();

      analyzeBtn.style.top = (window.scrollY + rect.bottom + 5) + "px";
      analyzeBtn.style.left = (window.scrollX + rect.left) + "px";
      analyzeBtn.style.position = "absolute";
      analyzeBtn.style.display = "block";
    } else {
      analyzeBtn.style.display = "none";
    }
  });

  // Track right-clicked links
  document.addEventListener("contextmenu", (e) => {
    let link = e.target.closest("a");
    if (link && link.href) {
      chrome.runtime.sendMessage({ type: "updateLink", url: link.href });
    } else {
      chrome.runtime.sendMessage({ type: "updateLink", url: "" });
    }
  });

  // Button click triggers speedometer
  analyzeBtn.addEventListener("click", () => {
    analyzeBtn.style.display = "none";
    showSpeedometer(currentSelection);
  });

  // Speedometer function
  window.showSpeedometer = function (displayText) {
    let oldGauge = document.getElementById("speedometer");
    if (oldGauge) oldGauge.remove();

    let container = document.createElement("div");
    container.id = "speedometer";
    container.style.position = "fixed";
    container.style.top = "50%";
    container.style.left = "50%";
    container.style.transform = "translate(-50%, -50%)";
    container.style.background = "rgba(0,0,0,0.7)";
    container.style.padding = "20px";
    container.style.borderRadius = "10px";
    container.style.zIndex = "1000000";
    container.style.transition = "opacity 0.4s ease";
    container.style.opacity = "1";
    container.style.textAlign = "center";
    container.style.color = "white";
    container.style.fontFamily = "Arial, sans-serif";

    container.innerHTML = `
      <div style="margin-bottom:10px;font-size:14px;word-break:break-all;">${displayText}</div>
      <svg width="220" height="140" viewBox="0 0 220 140">
        <defs>
          <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="red" />
            <stop offset="50%" stop-color="yellow" />
            <stop offset="100%" stop-color="green" />
          </linearGradient>
        </defs>
        <path d="M30 110 A80 80 0 0 1 190 110"
          fill="none" stroke="url(#arcGradient)"
          stroke-width="15" stroke-linecap="round"/>
        <path id="needle" d="M110 110 L110 40" stroke="white"
          stroke-width="4" stroke-linecap="round"
          transform="rotate(-90, 110, 110)"
          style="transition: transform 1s ease-out;"/>
      </svg>
    `;

    document.body.appendChild(container);

    let value = Math.floor(Math.random() * 180) - 90;
    let needle = container.querySelector("#needle");
    setTimeout(() => {
      needle.setAttribute("transform", `rotate(${value}, 110, 110)`);
    }, 50);

    // Click outside to remove
    setTimeout(() => {
      document.addEventListener("click", function handler(e) {
        if (!container.contains(e.target)) {
          container.style.opacity = "0";
          setTimeout(() => container.remove(), 400);
          document.removeEventListener("click", handler);
        }
      });
    }, 100);
  };
}
