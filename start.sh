#!/bin/bash
# ═══════════════════════════════════════════════════════
#  DevOps Autopilot - Quick Start
#  Kullanım: chmod +x start.sh && ./start.sh
# ═══════════════════════════════════════════════════════
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   🚀 DevOps Autopilot - Quick Start      ║"
echo "║   n8n + Prometheus + Grafana + Loki      ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── .env kontrol ──────────────────────────────────────
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}⚠️  .env dosyası bulunamadı. .env.example kopyalanıyor...${NC}"
  cp .env.example .env
  echo -e "${RED}❗ .env dosyasını kendi bilgilerinizle düzenleyin ve tekrar çalıştırın!${NC}"
  exit 1
fi

# ── Eksik klasörleri otomatik oluştur ─────────────────
echo -e "${GREEN}📁 Klasör yapısı kontrol ediliyor...${NC}"
mkdir -p prometheus alertmanager promtail n8n-workflows

# prometheus config yoksa minimal bir tane oluştur
if [ ! -f "prometheus/prometheus.yml" ]; then
  cat > prometheus/prometheus.yml << 'PROM'
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'django-api'
    static_configs:
      - targets: ['django-api:8000']
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
PROM
  echo -e "${YELLOW}  ℹ️  prometheus/prometheus.yml oluşturuldu${NC}"
fi

if [ ! -f "prometheus/alerts.yml" ]; then
  cat > prometheus/alerts.yml << 'ALERTS'
groups:
  - name: django
    rules:
      - alert: ServiceDown
        expr: up{job="django-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Django API down"
ALERTS
  echo -e "${YELLOW}  ℹ️  prometheus/alerts.yml oluşturuldu${NC}"
fi

# alertmanager config yoksa oluştur
if [ ! -f "alertmanager/alertmanager.yml" ]; then
  cat > alertmanager/alertmanager.yml << 'AM'
route:
  receiver: 'n8n-webhook'
receivers:
  - name: 'n8n-webhook'
    webhook_configs:
      - url: 'http://n8n:5678/webhook/prometheus-alert'
        send_resolved: true
AM
  echo -e "${YELLOW}  ℹ️  alertmanager/alertmanager.yml oluşturuldu${NC}"
fi

# promtail config yoksa oluştur
if [ ! -f "promtail/promtail.yml" ]; then
  cat > promtail/promtail.yml << 'PT'
server:
  http_listen_port: 9080
  grpc_listen_port: 0
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: docker
    static_configs:
      - targets: [localhost]
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*-json.log
PT
  echo -e "${YELLOW}  ℹ️  promtail/promtail.yml oluşturuldu${NC}"
fi

# myproject yoksa dur
if [ ! -d "myproject" ]; then
  echo -e "${RED}❗ 'myproject' klasörü bulunamadı. Repo'nun doğru klasöründe misiniz?${NC}"
  exit 1
fi

# ── Docker Compose build + up ─────────────────────────
echo -e "${GREEN}🐳 Image build ediliyor ve servisler başlatılıyor...${NC}"
docker compose up -d --build

# ── Django migrate (container ayağa kalkana kadar bekle) ──
echo -e "${GREEN}⏳ Django API'nin hazır olması bekleniyor...${NC}"
RETRIES=15
until docker compose exec -T django-api curl -sf http://localhost:8000/health/ > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "   bekleniyor... ($RETRIES)"
  sleep 4
  RETRIES=$((RETRIES - 1))
done

if [ $RETRIES -gt 0 ]; then
  echo -e "${GREEN}🔄 Migration çalıştırılıyor...${NC}"
  docker compose exec -T django-api python manage.py migrate --noinput
  echo -e "${GREEN}👤 Superuser oluşturuluyor (zaten varsa atlanır)...${NC}"
  docker compose exec -T django-api python manage.py shell -c \
    "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='admin').exists() or U.objects.create_superuser('admin','admin@devops.local','admin123')" 2>/dev/null || true
else
  echo -e "${YELLOW}⚠️  Django API'ye ulaşılamadı. Migration'ı manuel çalıştırın:${NC}"
  echo "   docker compose exec django-api python manage.py migrate"
fi

# ── Özet ─────────────────────────────────────────────
echo ""
echo -e "${GREEN}✅ Servisler hazır!${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "  🌐 Django API    →  http://localhost:8000"
echo -e "  🔧 n8n           →  http://localhost:5678"
echo -e "  📊 Grafana       →  http://localhost:3000"
echo -e "  🔥 Prometheus    →  http://localhost:9090"
echo -e "  🚨 Alertmanager  →  http://localhost:9093"
echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo ""
