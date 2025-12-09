# PO Manager - Program Outcome Management System

🎓 Akademik birimlerin derslerden elde edilen öğrenci notlarını ve öğrenme çıktıları (Learning Outcomes) aracılığıyla Program Outcome (PO) skorlarını hesaplayıp yönetebileceği web uygulaması.

## 🚀 Hızlı Başlangıç

### Tek Komutla Başlatma

```bash
# Projeyi başlat (hem backend hem frontend)
./start.sh

# Durumu kontrol et
./status.sh

# Durdur
./stop.sh
```

## 📋 Gereksinimler

- Python 3.8+
- Node.js 16+
- npm

## 🛠️ Manuel Kurulum

### Backend (Django)

```bash
cd po_manager
source ../venv/bin/activate
python manage.py migrate
python manage.py runserver
```

### Frontend (Vue.js)

```bash
cd frontend
npm install
npm run dev
```

## 🌐 URL'ler

- **Frontend**: http://localhost:5173 (veya 5174)
- **Backend API**: http://127.0.0.1:8000/api/
- **Django Admin**: http://127.0.0.1:8000/admin/

## 👤 Demo Kullanıcılar

- **Admin**: `admin` / (şifre belirlenmeli)
- **Instructor**: `instructor1` / `password123`
- **Student**: `student1` / `password123`

## 📦 Özellikler

✅ Ders yönetimi (Course Management)
✅ Program Outcomes (PO) tanımlama
✅ Learning Outcomes (LO) oluşturma
✅ LO ↔ PO ilişki haritalama (görsel editör)
✅ Öğrenci değerlendirme ve not girişi
✅ Otomatik PO skor hesaplama
✅ Modern dashboard ve raporlama

## 🏗️ Teknolojiler

- **Backend**: Django 5.2 + Django REST Framework
- **Frontend**: Vue 3 + Rete.js v2
- **Database**: SQLite (geliştirme)
- **API**: RESTful API

## 📁 Proje Yapısı

```
obs/
├── po_manager/          # Django backend
│   ├── core/           # Ana app (models, views, serializers)
│   ├── po_manager/     # Proje ayarları
│   └── db.sqlite3      # Veritabanı
├── frontend/           # Vue.js frontend
│   ├── src/
│   │   ├── components/ # Dashboard, ReteEditor
│   │   ├── services/   # API servisi
│   │   └── App.vue
│   └── package.json
├── venv/              # Python virtual environment
├── start.sh           # Başlatma scripti
├── stop.sh            # Durdurma scripti
└── status.sh          # Durum kontrolü
```

## 🔧 API Endpoints

- `GET /api/courses/` - Ders listesi
- `GET /api/program-outcomes/` - PO listesi
- `GET /api/learning-outcomes/` - LO listesi
- `GET /api/mappings/` - LO-PO mapping listesi
- `GET /api/students/{id}/po_scores/` - Öğrenci PO skorları
- `POST /api/learning-outcomes/{id}/mappings/` - LO-PO mapping oluştur

## 📊 Demo Veriler

Proje demo verilerle birlikte gelir:
- 5 Program Outcome (PO1-PO5)
- 2 Ders (CSE311, CSE321)
- 3 Learning Outcome
- 6 LO-PO Mapping
- 1 Öğrenci ve örnek notlar

## 🎯 Kullanım

1. **Dashboard** sekmesinde:
   - Dersler ekleyin/görüntüleyin
   - Program Outcomes tanımlayın
   - Öğrenci PO skorlarını kontrol edin

2. **LO-PO Editor** sekmesinde:
   - Learning Outcomes ve Program Outcomes'u görsel olarak bağlayın
   - Sürükle-bırak ile ilişkiler oluşturun
   - Değişiklikler otomatik kaydedilir
