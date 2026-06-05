# Profolio AI — Intelligent Portfolio Management System

A production-grade, AI-powered portfolio management system built with **Next.js 14**, **FastAPI**, **MongoDB**, and **PyTorch**.

## ✨ Key Features
- **PDF Parser Engine**: Extracts holdings from NSDL/CDSL CAS, Zerodha, Groww statements.
- **Asset Resolver**: Maps raw holding names to normalized NSE/BSE tickers.
- **AI Intelligence**: 
  - **LSTM Models** for price prediction.
  - **FinBERT** for sentiment analysis of market news.
- **Modern Dashboard**: Real-time asset allocation, XIRR calculation, and portfolio health checks.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** v18+
- **Python** 3.11+
- **MongoDB** (Running locally on port 27017)

### 1. Backend Setup (FastAPI)
Navigate to the API directory and set up the Python environment:

```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# (Edit .env with your secret keys if needed)

# Run the server
uvicorn main:app --reload --port 8000
```
*Backend runs at `http://localhost:8000`*

### 2. Frontend Setup (Next.js)
Open a new terminal and set up the web interface:

```bash
cd apps/web

# Install dependencies
npm install

# Create .env.local file
copy .env.example .env.local
# (Edit .env.local with your NextAuth secret)

# Run the development server
npm run dev
```
*Frontend runs at `http://localhost:3000`*

---

## 🐳 Docker Setup (Alternative)
If you have Docker installed, you can run the entire stack with one command:

```bash
docker-compose up --build
```

---

## 📦 How to Share checks
To share this project with someone else:

1. **Delete** the following folders to reduce size:
   - `apps/web/node_modules`
   - `apps/web/.next`
   - `apps/api/venv`
   - `apps/api/__pycache__`

2. **Zip** the entire `portfolio-system` folder.

3. The recipient just needs to unzip it and follow the **Quick Start Guide** above!

---

## 🛠 Tech Stack
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Motor (Async MongoDB), Pydantic
- **AI/ML**: PyTorch, Transformers (Hugging Face), Scikit-learn
- **Database**: MongoDB v6.0
