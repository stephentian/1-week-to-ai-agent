# SSL证书目录

## 📋 证书文件说明

本目录用于存放SSL/TLS证书文件。

### 必需文件

1. **fullchain.pem** - 完整证书链（域名证书 + 中间CA证书）
2. **privkey.pem** - 私钥文件

### 获取方式

#### 方式一：Let's Encrypt（推荐，免费）

```bash
# 使用Certbot获取免费证书
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d your-domain.com \
  -d www.your-domain.com

# 复制证书到本项目
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/
```

#### 方式二：自签名证书（仅用于开发测试）

```bash
# 生成自签名证书（有效期365天）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=AI-Agent/CN=localhost"

# ⚠️ 浏览器会提示不安全警告，生产环境请使用正式证书
```

#### 方式三：购买商业证书

从以下机构购买：
- DigiCert
- Comodo/Sectigo
- GlobalSign
- 阿里云/腾讯云SSL证书服务

### 自动续期（Let's Cert）

添加Cron任务：

```bash
# 编辑crontab
sudo crontab -e

# 添加定时任务（每天凌晨3点检查并续期）
0 3 * * * certbot renew --quiet && docker exec ai-agent-nginx nginx -s reload
```

### 安全注意事项

⚠️ **重要**:
- 私钥文件权限应设置为 `600` (仅所有者可读写)
- 不要将私钥提交到版本控制系统
- 生产环境建议使用 `.gitignore` 排除此目录

### .gitignore 配置

```
# SSL证书（不要提交到Git）
ssl/*.pem
!ssl/.keep
```
