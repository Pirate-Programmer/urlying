if (!window.__analyzeInjected) {
  window.__analyzeInjected = true;

  let analyzeBtn = document.createElement("button");
  analyzeBtn.id = "analyze-btn";
  analyzeBtn.innerText = "Analyze";
  analyzeBtn.style.display = "none";
  document.body.appendChild(analyzeBtn);

  let currentSelection = "";

  document.addEventListener("mouseup", () => {
    let text = window.getSelection().toString().trim();
    if (text.length > 0 && /^https?:\/\//i.test(text)) {
    currentSelection = text;
    chrome.runtime.sendMessage({ type: "updateSelection", text: text });

    let range = window.getSelection().getRangeAt(0);
    let rect = range.getBoundingClientRect();

    analyzeBtn.style.top = (window.scrollY + rect.bottom + 5) + "px";
    analyzeBtn.style.left = (window.scrollX + rect.left) + "px";
    analyzeBtn.style.position = "absolute";
    analyzeBtn.style.display = "block";
    } 
    else {
      text = null;
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

  //  Speedometer function
  window.showSpeedometer = function(displayText) {
    if (!/^https?:\/\//i.test(displayText)) {
        // Create a small popup message
        let oldMsg = document.getElementById("speedometerMessage");
        if (oldMsg) oldMsg.remove();

        let msg = document.createElement("div");
        msg.id = "speedometerMessage";
        msg.textContent = "Please select a URL starting with http:// or https://";
        msg.style.position = "fixed";
        msg.style.top = "50%";
        msg.style.left = "50%";
        msg.style.transform = "translate(-50%, -50%)";
        msg.style.background = "rgba(0,0,0,0.8)";
        msg.style.color = "white";
        msg.style.padding = "15px 25px";
        msg.style.borderRadius = "10px";
        msg.style.fontFamily = "Arial, sans-serif";
        msg.style.fontSize = "16px";
        msg.style.zIndex = "1000000";
        msg.style.textAlign = "center";
        msg.style.opacity = "1";
        msg.style.transition = "opacity 0.4s ease";

        document.body.appendChild(msg);

        // Remove the message after 2 seconds
        setTimeout(() => {
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 400);
        }, 2000);

        return; // stop execution
    }
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

    function polarToCartesian(cx, cy, r, angleDegrees) {
      let angleRadians = (angleDegrees - 90) * Math.PI / 180.0;
      return {
        x: cx + r * Math.cos(angleRadians),
        y: cy + r * Math.sin(angleRadians)
      };
    }

    function describeArc(cx, cy, r, startAngle, endAngle) {
      let start = polarToCartesian(cx, cy, r, endAngle);
      let end = polarToCartesian(cx, cy, r, startAngle);
      let largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
      let d = [
        "M", start.x, start.y,
        "A", r, r, 0, largeArcFlag, 0, end.x, end.y
      ].join(" ");
      return d;
    }

    let arcPath = describeArc(110, 110, 80, -135, 135);

    container.innerHTML = `
      <div style="margin-bottom:10px;font-size:14px;word-break:break-all;">
        ${displayText}
      </div>
      <svg width="220" height="220" viewBox="0 0 220 220">
        <defs>
          <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="green" />
            <stop offset="50%" stop-color="yellow" />
            <stop offset="100%" stop-color="red" />
          </linearGradient>
        </defs>
        <path d="${arcPath}" fill="none" stroke="url(#arcGradient)" stroke-width="15" stroke-linecap="round"/>
        <line id="needle" x1="110" y1="110" x2="110" y2="30" stroke="white"
          stroke-width="4" stroke-linecap="round"
          transform="rotate(-45, 110, 110)"
          style="transition: transform 1s ease-out;"/>
      </svg>
      <div id="speedValue" style="margin-top:15px;font-size:20px;font-weight:bold;"></div>
    `;

    document.body.appendChild(container);

    let fontLink = document.createElement("link");
    fontLink.href = "https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap";
    fontLink.rel = "stylesheet";
    document.head.appendChild(fontLink);

    let value = Math.floor(Math.random() * 270); // 0–270 along arc
    let rotation = value - 135; // rotation matches SVG rotation

    let needle = container.querySelector("#needle");
    setTimeout(() => {
      needle.setAttribute("transform", `rotate(${rotation}, 110, 110)`);
    }, 50);

    let speedValueElem = container.querySelector("#speedValue");
    let current = 0;
    let target = value; // show rotation instead of raw value
    let step = target > current ? 1 : -1;

    speedValueElem.style.fontFamily = "'Orbitron', sans-serif";
    speedValueElem.style.color = "#00ffcc";
    speedValueElem.style.letterSpacing = "2px";
    speedValueElem.style.position = "absolute";
    speedValueElem.style.top = "190px";               
    speedValueElem.style.left = "50%";
    speedValueElem.style.fontSize = "30px";
    speedValueElem.style.fontWeight = "bold";
    speedValueElem.style.transform = "translateX(-50%)";
    let interval = setInterval(() => {
      current += step;
      speedValueElem.textContent = current;
      if (current === target) clearInterval(interval);
    }, 20);

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