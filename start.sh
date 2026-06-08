#!/bin/bash
# ─────────────────────────────────────────────────────────
#  ESG Platform — Démarrage local (Mac / Linux)
#  Lancer une seule fois : bash start.sh
# ─────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ███████╗███████╗ ██████╗     Platform"
echo "  ██╔════╝██╔════╝██╔════╝"
echo "  █████╗  ███████╗██║  ███╗   Générateur ESG / RSE"
echo "  ██╔══╝  ╚════██║██║   ██║   100% Local — Aucune API"
echo "  ███████╗███████║╚██████╔╝"
echo "  ╚══════╝╚══════╝ ╚═════╝"
echo -e "${NC}"

# ── 1. Python ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo -e "${YELLOW}⚠  Python 3 non trouvé. Installer depuis https://python.org${NC}"
  exit 1
fi
PYTHON=$(command -v python3)
echo -e "${GREEN}✓ Python :${NC} $($PYTHON --version)"

# ── 2. Node.js ───────────────────────────────────────────
if ! command -v node &>/dev/null; then
  echo -e "${YELLOW}⚠  Node.js non trouvé. Installer depuis https://nodejs.org${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Node   :${NC} $(node --version)"

# ── 3. Dépendances Python ────────────────────────────────
echo ""
echo "📦 Installation des dépendances Python..."
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
  $PYTHON -m venv "$SCRIPT_DIR/backend/venv"
fi
source "$SCRIPT_DIR/backend/venv/bin/activate"
pip install -q -r "$SCRIPT_DIR/backend/requirements.txt"
echo -e "${GREEN}✓ Dépendances Python installées${NC}"

# ── 4. Dépendances Node ──────────────────────────────────
echo "📦 Installation des dépendances Node..."
cd "$SCRIPT_DIR/frontend"
npm install --silent
echo -e "${GREEN}✓ Dépendances Node installées${NC}"

# ── 5. Build frontend ────────────────────────────────────
echo "🔨 Build du frontend..."
npm run build --silent
echo -e "${GREEN}✓ Frontend compilé${NC}"

# ── 6. Démarrage ─────────────────────────────────────────
echo ""
echo -e "${CYAN}🚀 Démarrage de l'application...${NC}"
echo -e "${GREEN}   → http://localhost:8000${NC}"
echo ""
echo "  Ctrl+C pour arrêter."
echo ""

cd "$SCRIPT_DIR/backend"
exec uvicorn main:app --host 127.0.0.1 --port 8000
