# Curlew Explorer

Curlew Explorer is a Python-based GUI application for analysing Eurasian Curlew nest temperature datasets.

The application allows comparison between:

- Nest temperature data
- Ambient temperature data

It provides:

- Full dataset visualisation
- Daily breakdowns
- Statistical summaries
- Rate-of-change analysis
- Temperature smoothing
- Interactive graph navigation

---

# Features

- Interactive Tkinter GUI
- Matplotlib graphing
- Savitzky-Golay smoothing
- CSV import support
- Legacy dataset compatibility
- Daily and combined visualisations
- Temperature uncertainty visualisation
- Statistical reporting
- Click-to-navigate timeline analysis

---

# Screenshots

(Add screenshots here later)

---

# Installation

## Clone repository

```
git clone https://github.com/YOUR_USERNAME/curlew-explorer.git
cd curlew-explorer
```

---

## Create virtual environment

### Windows

```
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```
python3 -m venv venv
source venv/bin/activate
```

---

## Install dependencies

```
pip install -r requirements.txt
```

---

# Running the Application

```
python gui.py
```

---

# Building Executable

```
pyinstaller --noconsole --onedir --noupx --add-data "assets/frame0;assets/frame0" gui.py
```

The executable will appear in:

```
dist/gui/
```

---

# CSV Format

The application expects CSV temperature logs containing:

- Date
- Time
- Unit
- Temperature

Legacy 3-column formats are also supported.

---

# Project Structure

```
curlew-explorer/
│
├── gui.py
├── curlewExplorer.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── frame0/
│
├── build/
├── dist/
└── venv/
```

---

# Current Status

Version: 0.4 BETA

This project is under active development.

---

# License

MIT License