urlying

<br>
<hr>
<h3> File Structure</h3>
<pre>
urlying/
│── datasets/ # Static lists and threat intel
│ ├── cipher_suites/
│ ├── harmful_file_extensions/
│ ├── raw_dataset/
│ ├── tlds/
│ ├── tor_nodes_ips/
│ ├── url_shorteners/
│ ├── vpn_ips/
│ └── README.md
│
│── extension/ # Chrome Extension (MV3)
│ ├── css/ # Stylesheets
│ ├── feature_extraction/ # JS scripts for URL feature extraction
│ ├── html/ # Popup & UI
│ ├── icons/ # Extension icons
│ ├── js/ # Logic & utilities
│ ├── background.js # Background script
│ └── manifest.json # Extension manifest
│
│── hashed_files/ # Cached / processed files
│
│── ipynbs/ # ML workflow in Jupyter notebooks
│ ├── eda/ # Exploratory Data Analysis
│ ├── pca/ # PCA decomposition
│ ├── training/ # Model training & evaluation
│ ├── features.ipynb # Feature engineering
│ └── train_val_test_split.ipynb
│
│── json/ # Exported scaler/PCA/mappings for JS
│── scripts/ # Utility scripts
│
│── app.py # Backend API (Flask/FastAPI)
└── requirements.txt # Python dependencies
</pre>

<h3>Requirements</h3>