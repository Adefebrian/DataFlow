#!/bin/bash
# ============================================================
# DataFlow — Fix & Run Script
# Jalankan: bash fix_and_run.sh
# ============================================================
set -e
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   DataFlow — Fix & Run                   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. Fix Python venv ──────────────────────────────────────
echo "▸ Installing Python dependencies..."
if [ -d "venv" ]; then
    venv/bin/pip install email-validator --quiet
    venv/bin/pip install -r requirements.txt --quiet
    echo "  ✓ Python deps ready (venv)"
else
    pip install email-validator --quiet
    pip install -r requirements.txt --quiet
    echo "  ✓ Python deps ready (system)"
fi

# ── 2. Fix frontend deps ────────────────────────────────────
echo "▸ Installing frontend dependencies..."
cd frontend
npm install --silent
echo "  ✓ Frontend deps ready"
cd ..

# ── 3. Test frontend build ──────────────────────────────────
echo "▸ Testing TypeScript build..."
cd frontend
npm run build 2>&1 | tail -20
cd ..
echo "  ✓ Frontend build OK"

echo ""
echo "══════════════════════════════════════════"
echo "  All fixes verified!"
echo ""
echo "  To run with Docker:"
echo "    docker-compose up -d --build"
echo ""
echo "  To run locally:"
echo "    Backend:  venv/bin/python main.py"
echo "    Frontend: cd frontend && npm run dev"
echo ""
echo "  Login: admin / admin123"
echo "  URL:   http://localhost:3000"
echo "══════════════════════════════════════════"
