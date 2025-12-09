#!/bin/bash

# PO Manager - Başlatma Scripti
# Bu script hem Django backend'i hem Vue frontend'i aynı anda başlatır

echo "🚀 PO Manager Başlatılıyor..."
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend dizini
BACKEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/po_manager"
FRONTEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/frontend"
VENV_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/venv"

# Virtual environment kontrolü
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment bulunamadı!${NC}"
    echo "Lütfen önce: python -m venv venv"
    exit 1
fi

# Node modules kontrolü
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies bulunamadı!${NC}"
    echo "Yükleniyor..."
    cd "$FRONTEND_DIR"
    npm install
fi

echo -e "${BLUE}📦 Django Backend başlatılıyor...${NC}"
cd "$BACKEND_DIR"
source "$VENV_DIR/bin/activate"

# Migration kontrolü
python manage.py migrate --check 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Migration gerekli, çalıştırılıyor...${NC}"
    python manage.py migrate
fi

# Django'yu arka planda başlat
python manage.py runserver > /tmp/django.log 2>&1 &
DJANGO_PID=$!
echo -e "${GREEN}✓ Django Backend başlatıldı (PID: $DJANGO_PID)${NC}"
echo -e "  URL: ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  Admin: ${BLUE}http://127.0.0.1:8000/admin${NC}"
echo -e "  API: ${BLUE}http://127.0.0.1:8000/api/${NC}"
echo ""

# Biraz bekle ki Django tamamen başlasın
sleep 2

echo -e "${BLUE}🎨 Vue Frontend başlatılıyor...${NC}"
cd "$FRONTEND_DIR"

# Vue'yu arka planda başlat
npm run dev > /tmp/vue.log 2>&1 &
VUE_PID=$!
echo -e "${GREEN}✓ Vue Frontend başlatıldı (PID: $VUE_PID)${NC}"
echo ""

# Port bilgisi için bekle
sleep 3

# Vue'nun hangi portta çalıştığını bul
VUE_PORT=$(grep -oP "(?<=localhost:)\d+" /tmp/vue.log | head -1)
if [ ! -z "$VUE_PORT" ]; then
    echo -e "  URL: ${BLUE}http://localhost:$VUE_PORT${NC}"
else
    echo -e "  URL: ${BLUE}http://localhost:5173${NC} (veya 5174)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ PO Manager başarıyla başlatıldı!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Durdurmak için:${NC} ./stop.sh veya CTRL+C"
echo -e "${YELLOW}Logları görmek için:${NC}"
echo -e "  Django: tail -f /tmp/django.log"
echo -e "  Vue: tail -f /tmp/vue.log"
echo ""

# PID'leri kaydet
echo $DJANGO_PID > /tmp/po_manager_django.pid
echo $VUE_PID > /tmp/po_manager_vue.pid

# CTRL+C ile durdurma
trap "echo ''; echo 'Durduruluyor...'; ./stop.sh; exit" INT TERM

# Sonsuz döngü (script çalışır durumda kalsın)
echo -e "${BLUE}📊 Loglar canlı olarak gösteriliyor (CTRL+C ile çıkış):${NC}"
echo ""
tail -f /tmp/django.log /tmp/vue.log
