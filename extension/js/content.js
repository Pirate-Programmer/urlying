if (!window.__analyzeInjected) {
  window.__analyzeInjected = true;

  let analyzeBtn = document.createElement("button");
  analyzeBtn.id = "analyze-btn";
  analyzeBtn.innerText = "Analyze";
  analyzeBtn.style.display = "none";
  document.body.appendChild(analyzeBtn);

  let currentSelection = "";

  document.addEventListener("mouseup", () => {
      let sel = window.getSelection();
      if (!sel.rangeCount) return;

      let text = sel.toString().trim();
      let range = sel.getRangeAt(0);
      let anchor = range.startContainer.parentElement.closest("a"); // get enclosing link

      if (anchor && anchor.href) {
          currentSelection = anchor.href; // prioritize actual link
      } else if (/^https?:\/\//i.test(text)) {
          currentSelection = text;
      } else {
          currentSelection = "";
      }

      // Update background
      chrome.runtime.sendMessage({ type: "updateSelection", text: currentSelection });

    // Position Analyze button only if extension is enabled
    if (currentSelection) {
        chrome.storage.local.get({ enableBlocking: true }, (data) => {
            if (!data.enableBlocking) {
                analyzeBtn.style.display = "none"; // Hide if extension off
                return;
            }

            let rect = range.getBoundingClientRect();
            analyzeBtn.style.top = (window.scrollY + rect.bottom + 5) + "px";
            analyzeBtn.style.left = (window.scrollX + rect.left) + "px";
            analyzeBtn.style.position = "absolute";
            analyzeBtn.style.display = "block";
        });
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

// Button click sends url to background.js to be sent to backend and also triggers speedometer
  analyzeBtn.addEventListener("click", () => {
      analyzeBtn.style.display = "none";

      if (!currentSelection) return;
      risk_score = chrome.storage.local.get({
        lastBlockedScore
      });
      chrome.runtime.sendMessage({ type: "analyzeURL", url: currentSelection }, (response) => {
          if (response && response.risk_score !== undefined) {
              showSpeedometer(currentSelection, response.risk_score);
          } else {
              showSpeedometer(currentSelection, 0); // fallback
          }
      });
  });


  //  Speedometer function
  window.showSpeedometer = function(displayText, riskScore=0) {
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

    // Use riskScore from backend instead of random
    let needle = container.querySelector("#needle");
    let speedValueElem = container.querySelector("#speedValue");

    let rotation = (riskScore / 100) * 270 - 135; // map 0–100 → -135 to 135 degrees
    setTimeout(() => {
      needle.setAttribute("transform", `rotate(${rotation}, 110, 110)`);
    }, 50);

    // Animate numeric value from 0 → riskScore
    let current = 0;
    let target = riskScore;
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

      // Stop when current passes target
      if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
        speedValueElem.textContent = target; // make sure final value matches exactly
        clearInterval(interval);
      }
    }, 20);


    setTimeout(() => {
      const containerEl = document.getElementById("speedometer");
      function handler(e) {
        if (!containerEl.contains(e.target)) {
          containerEl.style.opacity = "0";
          setTimeout(() => containerEl.remove(), 400);
          document.removeEventListener("click", handler);
        }
      }
      document.addEventListener("click", handler);
    }, 100);
  };
}


chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "updateRisk" && msg.risk_score !== undefined) {
    let riskScore = msg.risk_score;
    let displayUrl = msg.url || "Selected URL";

    updateSpeedometer(riskScore, displayUrl);
  }
});
