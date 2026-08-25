<div align="center">

# 🧪 CyberLabs

### Interactive Cybersecurity Labs Platform

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Labs](https://img.shields.io/badge/labs-30+-red)
![Categories](https://img.shields.io/badge/categories-6-purple)

**Learn cybersecurity through hands-on labs** with XP, badges, and progress tracking.

[CyberLabs](https://github.com/0xvanguard/cyberlabs) • [Quick Start](#quick-start) • [Labs](#lab-categories)

</div>

---

## 🧪 What is CyberLabs?

CyberLabs is an **interactive cybersecurity labs platform** with 30+ labs across 6 categories. Learn by doing with XP rewards, badges, and progress tracking.

### Why CyberLabs?

| Traditional Learning | With CyberLabs |
|---------------------|----------------|
| Passive reading | **Hands-on labs** |
| No feedback | **Instant validation** |
| No progress tracking | **XP and badges** |
| Boring | **Gamified learning** |

## 🎯 Lab Categories

| Category | Labs | Difficulty |
|----------|------|------------|
| **Web Security** | 5 | Beginner → Advanced |
| **Cryptography** | 5 | Beginner → Advanced |
| **Forensics** | 5 | Beginner → Advanced |
| **Network Security** | 5 | Beginner → Advanced |
| **Malware Analysis** | 5 | Beginner → Advanced |
| **Reverse Engineering** | 5 | Beginner → Expert |

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/0xvanguard/cyberlabs.git
cd cyberlabs

# List labs
python cli.py list

# Start a lab
python cli.py start web-001 --player yourname

# Submit flag
python cli.py submit web-001 --flag FLAG{xss_reflected_1nject3d} --player yourname

# Get hint
python cli.py hint web-001 --player yourname

# View stats
python cli.py stats --player yourname

# Leaderboard
python cli.py leaderboard
```

## 💻 Python API

```python
from cyberlabs import CyberLabs

platform = CyberLabs()

# List labs
web_labs = platform.list_labs(category="web")
print(f"Found {len(web_labs)} web labs")

# Start a lab
start = platform.start_lab("web-001", "player1")
print(f"Objective: {start['objective']}")

# Submit flag
result = platform.submit_flag("web-001", "player1", "FLAG{...}")
print(f"Solved: {result.solved}, XP: {result.xp_earned}")

# Player stats
stats = platform.get_player_stats("player1")
print(f"Level: {stats['player']['level']}, XP: {stats['player']['xp']}")
```

## 🏅 Badge System

| Badge | Requirement |
|-------|-------------|
| 🩸 First Blood | Complete first lab |
| 🌐 Web Warrior | Complete 10 web labs |
| 🔐 Crypto Cracker | Complete 10 crypto labs |
| 🔍 Digital Detective | Complete 10 forensics labs |
| 🕸️ Network Ninja | Complete 10 network labs |
| 🦠 Malware Hunter | Complete 10 malware labs |
| ⚙️ Binary Breaker | Complete 10 reverse labs |
| ⚡ Speed Demon | Complete lab in <60s |
| 🐺 Lone Wolf | 5 labs without hints |
| 💎 Perfectionist | First attempt solve |
| ⭐ Rising Star | Reach level 5 |
| 🌟 Cyber Expert | Reach level 10 |
| 🎯 Jack of All Trades | All categories |
| 🏆 Century Club | 100 labs completed |

## 📁 Project Structure

```
cyberlabs/
├── src/
│   ├── __init__.py
│   └── platform.py          # Core platform (600+ lines)
├── labs/                    # Lab content files
├── tests/
│   ├── __init__.py
│   └── test_cyberlabs.py    # 13 tests
├── cli.py                   # CLI tool
├── requirements.txt
└── README.md
```

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

## 📄 License

MIT License — Learn cybersecurity.

---

<div align="center">

**Built by [@0xvanguard](https://github.com/0xvanguard)** • [⭐ Star this repo](https://github.com/0xvanguard/cyberlabs) • [🐛 Report Bug](https://github.com/0xvanguard/cyberlabs/issues)

</div>
