if (document.body.classList.contains("links-highlighted")) {
  document.querySelectorAll('a').forEach(link => {
    link.style.backgroundColor = "";
    link.style.color = "";
    link.style.textDecoration = "";
    link.style.fontWeight = "";
    link.style.padding = "";
    link.style.borderRadius = "";
  });
  document.body.classList.remove("links-highlighted");
} else {
  document.querySelectorAll('a').forEach(link => {
    link.style.backgroundColor = 'yellow';
    link.style.color = 'red';
    link.style.textDecoration = 'underline';
    link.style.fontWeight = 'bold';
    link.style.padding = '2px 4px';
    link.style.borderRadius = '4px';
  });
  document.body.classList.add("links-highlighted");
}

if (!document.getElementById("website-visited-popup")) {
  const domain = window.location.hostname;

  const popup = document.createElement("div");
  popup.id = "website-visited-popup";
  popup.textContent = `Website visited: ${domain}`;
  popup.style.position = "fixed";
  popup.style.top = "20px";
  popup.style.right = "20px";
  popup.style.backgroundColor = "#333";
  popup.style.color = "#fff";
  popup.style.padding = "12px 20px";
  popup.style.borderRadius = "8px";
  popup.style.boxShadow = "0 0 10px rgba(0,0,0,0.5)";
  popup.style.fontSize = "14px";
  popup.style.zIndex = "99999";

  document.body.appendChild(popup);

  setTimeout(() => {
    popup.remove();
  }, 3000);
}
