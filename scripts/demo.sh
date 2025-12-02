#!/bin/bash
# Stainless Demo Script - Run everything needed for the demo

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🧪 Stainless SDK Generation Demo${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

case "${1:-help}" in
  export)
    echo -e "${GREEN}📤 Exporting OpenAPI spec...${NC}"
    uv run python scripts/export_openapi.py
    echo ""
    echo -e "${GREEN}✓ Done! Now run: stl dev --target typescript${NC}"
    ;;
    
  dev)
    echo -e "${GREEN}📤 Exporting OpenAPI spec...${NC}"
    uv run python scripts/export_openapi.py
    echo ""
    echo -e "${GREEN}🚀 Starting Stainless in dev mode...${NC}"
    echo -e "${YELLOW}   Tip: Make changes to app/ files, then re-run 'demo.sh export'${NC}"
    echo ""
    stl dev --target typescript
    ;;
    
  watch)
    echo -e "${GREEN}👀 Starting watch mode...${NC}"
    echo -e "${YELLOW}   Watching app/ for changes, will auto-export OpenAPI spec${NC}"
    echo ""
    # Use fswatch if available, otherwise fall back to a loop
    if command -v fswatch &> /dev/null; then
      fswatch -o app/ | while read; do
        echo -e "${GREEN}📤 Change detected, exporting spec...${NC}"
        uv run python scripts/export_openapi.py
      done
    else
      echo -e "${YELLOW}   fswatch not found. Install with: brew install fswatch${NC}"
      echo -e "${YELLOW}   Falling back to manual polling (every 5 seconds)...${NC}"
      while true; do
        uv run python scripts/export_openapi.py
        sleep 5
      done
    fi
    ;;
    
  full)
    echo -e "${GREEN}🎬 Full demo mode (3 terminals recommended)${NC}"
    echo ""
    echo "Terminal 1 - FastAPI server:"
    echo -e "  ${BLUE}uv run uvicorn app.main:app --reload${NC}"
    echo ""
    echo "Terminal 2 - Spec watcher (exports on file changes):"
    echo -e "  ${BLUE}./scripts/demo.sh watch${NC}"
    echo ""
    echo "Terminal 3 - Stainless SDK generator:"
    echo -e "  ${BLUE}stl dev --watch --target typescript${NC}"
    echo ""
    echo "Then make API changes and watch the SDK update!"
    ;;
    
  *)
    echo "Usage: ./scripts/demo.sh <command>"
    echo ""
    echo "Commands:"
    echo "  export   - Export OpenAPI spec once"
    echo "  dev      - Export spec and run stl dev"
    echo "  watch    - Watch app/ and auto-export spec on changes"
    echo "  full     - Show full 3-terminal demo setup instructions"
    echo ""
    echo "Quick start:"
    echo "  ./scripts/demo.sh export    # Export your API spec"
    echo "  stl dev --target typescript # Generate SDK"
    ;;
esac
