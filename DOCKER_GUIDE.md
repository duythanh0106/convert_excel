# 🐳 Hướng dẫn chạy Excel to DOCX Converter với Docker

## 📋 Yêu cầu hệ thống

- **Docker Desktop** đã cài đặt
  - Windows: https://www.docker.com/products/docker-desktop/
  - Mac: https://www.docker.com/products/docker-desktop/
  - Linux: `sudo apt-get install docker.io docker-compose`

## 🚀 Cách 1: Chạy nhanh với Docker Compose (Khuyến nghị)

### Bước 1: Chuẩn bị cấu trúc thư mục

```
your-project/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── templates/
│   └── index.html
├── uploads/       (tự tạo hoặc Docker sẽ tạo)
└── outputs/       (tự tạo hoặc Docker sẽ tạo)
```

### Bước 2: Build và chạy

Mở Terminal/CMD tại thư mục project, chạy:

```bash
# Build và start container
docker-compose up -d

# Xem logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Bước 3: Truy cập ứng dụng

- **Từ máy của bạn:** http://localhost:5000
- **Từ máy khác cùng mạng:** http://[IP-máy-bạn]:5000

Để biết IP máy bạn:
- **Windows:** `ipconfig` (tìm IPv4 Address)
- **Mac/Linux:** `ifconfig` hoặc `ip addr`

---

## 🔧 Cách 2: Chạy thủ công với Docker commands

```bash
# 1. Build image
docker build -t excel-converter:latest .

# 2. Run container
docker run -d \
  --name excel-converter-app \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --restart unless-stopped \
  excel-converter:latest

# 3. Xem logs
docker logs -f excel-converter-app

# 4. Stop container
docker stop excel-converter-app

# 5. Remove container
docker rm excel-converter-app
```

---

## 📱 Các lệnh quản lý hữu ích

```bash
# Xem containers đang chạy
docker ps

# Xem tất cả containers
docker ps -a

# Restart container
docker-compose restart
# hoặc
docker restart excel-converter-app

# Vào bên trong container (debug)
docker exec -it excel-converter-app /bin/bash

# Xem resource usage
docker stats excel-converter-app

# Xóa tất cả (cẩn thận!)
docker-compose down -v
```

---

## 🔄 Update ứng dụng

Khi bạn thay đổi code:

```bash
# 1. Stop container cũ
docker-compose down

# 2. Rebuild image
docker-compose build

# 3. Start lại
docker-compose up -d
```

Hoặc làm 1 lần:
```bash
docker-compose up -d --build
```

---

## 🌐 Chia sẻ cho đồng nghiệp

### Option A: Họ cũng dùng Docker (Khuyến nghị)

1. Chia sẻ toàn bộ code + Dockerfile
2. Họ chạy: `docker-compose up -d`
3. Xong!

### Option B: Họ không dùng Docker

1. **Bạn chạy trên máy mình**
2. **Chia sẻ IP của bạn:** 
   ```
   Gửi cho họ: http://192.168.1.XXX:5000
   (thay XXX bằng IP thật của bạn)
   ```
3. **Lưu ý:** Máy bạn phải bật và chạy Docker

---

## 🔒 Bảo mật

### Thêm tường lửa (nếu cần)

**Windows:**
```powershell
# Cho phép port 5000
New-NetFirewallRule -DisplayName "Excel Converter" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**Linux:**
```bash
sudo ufw allow 5000/tcp
```

---

## 🐛 Xử lý lỗi thường gặp

### Lỗi: Port 5000 đã được sử dụng

```bash
# Tìm process đang dùng port 5000
# Windows:
netstat -ano | findstr :5000

# Mac/Linux:
lsof -i :5000

# Hoặc đổi port trong docker-compose.yml:
ports:
  - "8080:5000"  # Dùng port 8080 thay vì 5000
```

### Lỗi: Container không start

```bash
# Xem logs chi tiết
docker-compose logs

# Hoặc
docker logs excel-converter-app
```

### Lỗi: Không truy cập được từ máy khác

1. **Tắt firewall tạm thời để test**
2. **Kiểm tra IP:** `ipconfig` hoặc `ifconfig`
3. **Ping thử từ máy khác:** `ping [IP-máy-bạn]`
4. **Đảm bảo cùng mạng WiFi/LAN**

---

## 📊 Monitoring

### Xem logs realtime

```bash
docker-compose logs -f --tail=100
```

### Kiểm tra dung lượng

```bash
# Xem dung lượng uploads/outputs
du -sh uploads outputs

# Xem dung lượng Docker
docker system df
```

### Auto cleanup file cũ

Thêm vào `app.py` hoặc tạo cron job:

```bash
# Xóa file > 7 ngày (chạy hàng ngày)
find uploads/ -type f -mtime +7 -delete
find outputs/ -type f -mtime +7 -delete
```

---

## 🚀 Nâng cao: Deploy lên Server công ty

### Bước 1: Chuẩn bị Server

```bash
# SSH vào server
ssh user@server-ip

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Cài Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Bước 2: Copy code lên server

```bash
# Từ máy local
scp -r your-project/ user@server-ip:/home/user/

# Hoặc dùng Git
git clone your-repo
```

### Bước 3: Chạy trên server

```bash
cd your-project/
docker-compose up -d
```

### Bước 4: Setup auto-start

```bash
# Tạo systemd service
sudo nano /etc/systemd/system/excel-converter.service
```

Nội dung:
```ini
[Unit]
Description=Excel to DOCX Converter
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/your-project
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable excel-converter
sudo systemctl start excel-converter
```

---

## 💡 Tips & Tricks

### 1. Chạy nhiều instance

```yaml
# docker-compose.yml
services:
  excel-converter-1:
    build: .
    ports:
      - "5001:5000"
  
  excel-converter-2:
    build: .
    ports:
      - "5002:5000"
```

### 2. Giới hạn resource

```yaml
services:
  excel-converter:
    # ... config cũ
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

### 3. Backup data

```bash
# Backup uploads & outputs
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ outputs/
```

---

## 📞 Support

Có vấn đề? Check:
1. `docker-compose logs` - Xem logs
2. `docker ps` - Container có chạy không?
3. `curl localhost:5000` - API có respond không?

---

**✅ Hoàn tất! Giờ bạn có thể chia sẻ app cho cả công ty dùng!**