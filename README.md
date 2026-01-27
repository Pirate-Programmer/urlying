<picture align="center">
  <img alt="URLying Logo" src="extension/icons/banner.png">
</picture>

-----------------
## URLying: A powerful, lightweight and real-time malicious URL detector  
## What is it?

**URLying** is a Chromium-based browser extension for real-time malicious URL detection.  
It uses a **hybrid detection framework** to accurately identify and block malicious URLs as users browse the web.

The extension works across all **Chromium-based browsers** (Chrome, Edge, Brave, etc.) and is designed to provide lightweight, real-time protection without impacting browsing performance.

## Dependencies
All project dependencies are listed in [`requirements.txt`](requirements.txt).

To install them, run:
```bash
pip install -r requirements.txt
```

#### 🔐 OpenSSL Installation

#### Linux : 
```bash
sudo apt install openssl
```
#### Windows using Chocolatey : 
First install Chocolatey:
https://chocolatey.org/install<br>
To install openssl run: 
```bash
choco install openssl
```

## To run:
As this extension is not available on Chrome Web Store, you need to manually load it into the browser. To do that open your browser, go to
**Manage Extensions** > Turn on **Developer Mode**.

You will see a **Load Unpacked** option at the top left.<br>
Load the **<a href="https://github.com/Pirate-Programmer/urlying/tree/main/extension">extension</a>** folder using that.

Now run the **<a href="https://github.com/Pirate-Programmer/urlying/blob/main/scripts/backend.py">backend.py</a>**.
```bash
python backend.py 
```
or
```bash
python3 backend.py
```

> Note: Open the browser only after running the backend.py.<br>
> The websites are analyzed only after they are loaded completely.
## Contributors
<p>
  <a href="https://github.com/the404packet">
    <img src="https://github.com/the404packet.png"
     width=50"
     height=50"
     style="border-radius:50%;"
     alt="the404packet"/>
  </a>
  <a href="https://github.com/Pirate-Programmer">
    <img src="https://github.com/Pirate-Programmer.png"
     width=50"
     height=50"
     style="border-radius:50%;"
     alt="Pirate-Programmer"/>
  </a>
  <a href="https://github.com/Ecstaticvanilla">
    <img src="https://github.com/Ecstaticvanilla.png"
     width=50"
     height=50"
     style="border-radius:50%;"
     alt="Ecstaticvanilla"/>
  </a>
</p>
