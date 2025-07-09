if (!document.getElementById("website-warning-modal")) {
  const domain = window.location.hostname;

  const overlay = document.createElement("div");
  overlay.id = "website-warning-modal";
  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.backgroundColor = "rgba(0, 0, 0, 0.95)";
  overlay.style.zIndex = "999999";
  overlay.style.display = "flex";
  overlay.style.flexDirection = "column";
  overlay.style.justifyContent = "center";
  overlay.style.alignItems = "center";
  overlay.style.color = "#fff";
  overlay.style.fontFamily = "Arial, sans-serif";
  overlay.style.padding = "20px";
  overlay.style.textAlign = "center";

  const heading = document.createElement("h1");
  heading.textContent = `You’re visiting: ${domain}`;
  heading.style.fontSize = "28px";
  heading.style.marginBottom = "30px";

  const continueBtn = document.createElement("button");
  continueBtn.textContent = "Continue";
  continueBtn.style.padding = "12px 24px";
  continueBtn.style.margin = "10px";
  continueBtn.style.fontSize = "18px";
  continueBtn.style.border = "none";
  continueBtn.style.borderRadius = "8px";
  continueBtn.style.backgroundColor = "#4caf50";
  continueBtn.style.color = "#fff";
  continueBtn.style.cursor = "pointer";
  continueBtn.onclick = () => {
    overlay.remove();
  };

  const backBtn = document.createElement("button");
  backBtn.textContent = "Go Back";
  backBtn.style.padding = "12px 24px";
  backBtn.style.margin = "10px";
  backBtn.style.fontSize = "18px";
  backBtn.style.border = "none";
  backBtn.style.borderRadius = "8px";
  backBtn.style.backgroundColor = "#f44336";
  backBtn.style.color = "#fff";
  backBtn.style.cursor = "pointer";
  backBtn.onclick = () => {
    window.history.back();
  };

  overlay.appendChild(heading);
  overlay.appendChild(continueBtn);
  overlay.appendChild(backBtn);
  document.body.appendChild(overlay);
}