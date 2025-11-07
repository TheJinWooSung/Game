

<!-- BADGES -->
<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python Badge">
  </a>
  <a href="https://www.mongodb.com/">
    <img src="https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb&logoColor=white" alt="MongoDB Badge">
  </a>
  <a href="https://docs.aiogram.dev/">
    <img src="https://img.shields.io/badge/aiogram-Framework-0096D6?logo=telegram&logoColor=white" alt="Aiogram Badge">
  </a>
  <a href="https://hub.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker Badge">
  </a>
</p>

---

### ⚙️ **About This Project**

A **modular Telegram Game Bot** that lets users play fun games like **Trivia**, **TicTacToe**, and **Economy** directly inside Telegram — built with **Python**, **aiogram**, and **MongoDB**.

📦 `/bot/handlers` → All game modules  
🎮 `trivia.py` → Quiz-style questions  
⭕ `tictactoe.py` → PvP TicTacToe board  
💰 `economy.py` → Coins, shop & leaderboard  

**Fast, scalable, and async-ready — perfect for hobby or production use.**

---

### 🧠 **Tech Highlights**

| Category | Technology |
|-----------|-------------|
| Language | Python 3.11 |
| Framework | aiogram (async Telegram API) |
| Database | MongoDB (Motor) |
| Infrastructure | Docker & Docker Compose |
| Config | Pydantic + .env |

---

### 🗳️ **Project Structure**

```bash
game/
├─ bot/
│  ├─ bot.py
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ utils.py
│  ├─ keyboards.py
│  └─ handlers/
│     ├─ core.py
│     ├─ trivia.py
│     ├─ tictactoe.py
│     └─ economy.py
├─ .github/
│  └─ dependabot.yml
├─ Dockerfile
├─ requirements.txt
├─ LICENSE
└─ CODEOWNERS
