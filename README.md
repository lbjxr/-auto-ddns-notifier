
# IP Monitor & Notify System
 <div> <p align="center">中文 | <a href="./README.EN.md">English</a> <br></p></div>
一个用于监控本机所在网络的公网IP变化并自动通知的系统。当检测到IP地址变化时，系统会通过微信推送通知，并自动更新Cloudflare DNS记录。

## 功能特点
- 自动监控公网IP变化
- 通过WxPusher推送微信通知
- 自动更新Cloudflare DNS记录
- 完善的日志记录系统
- 可配置的重试机制
- 支持多服务地址通知

## 目录结构 
```bash
/opt/ip_monitor/
├── GetPubIPAndSend.py # 主程序
├── SendMessageByWxPusher.py # 消息发送模块
├── UpdateCFDNS.py # DNS更新模块
├── config.yaml # 配置文件
├── last_ip.txt # IP记录文件
└── logs/ # 日志目录
    ├── ip_monitor.log # IP监控日志
    ├── notification.log # 通知日志
    ├── cloudflare_dns.log # DNS更新日志
    └── cron.log # 定时任务日志
```

## 安装步骤

### 1. 环境要求
- Python 3.6+
- Linux/Windows 系统

### 2. 安装依赖 
```bash
pip install requests pyyaml
```

### 3. 配置文件
复制 `config.yaml` 并根据实际情况修改：

```yaml
# IP检查相关配置，相关参数请到IP查询网站查看https://www.ip.cn/
ip_check:
  api_url: "http://cip.cc"
  last_ip_file: "./last_ip.txt"
  ip_pattern: "IP\\s*:\\s*([\\d\\.]+)"
  max_retries: 3
  retry_delay: 2

# 通知相关配置，相关参数请到WxPubsher官网查看https://wxpusher.zjiecode.com/docs/#/
notification:
  script_path: "SendMessageByWxPusher.py"
  enabled: true
  wxpusher:
    app_token: "你的WxPusher_APP_Token"
    uids: ["你的UID"]
  services:
    s1_port: 系统1访问端口
    s2_port: 系统2访问端口

# Cloudflare配置，相关参数请到Cloudflare官网查看https://developers.cloudflare.com/api/
cloudflare:
  api_token: "你的Cloudflare_API_Token"
  zone_id: "你的Zone_ID"
  record_name: "你的域名"
  dns_type: "A"
  ttl: 120
  proxied: false
  max_retries: 3
  retry_delay: 2
```

### 4. Linux环境下部署
```bash
# 创建工作目录
sudo mkdir /opt/ip_monitor
sudo chown $USER:$USER /opt/ip_monitor  # 修改目录所有者
cd /opt/ip_monitor

# 复制所有文件到工作目录
cp /path/to/files/* .

# 设置执行权限
chmod +x *.py

# 设置配置文件权限
chmod 600 config.yaml

# 创建日志目录
mkdir logs
chmod 755 logs
```

### 5. 设置定时任务
```bash
# 编辑crontab
crontab -e

# 添加定时任务（每5分钟执行一次）
*/5 * * * * cd /opt/ip_monitor && /usr/bin/python3 GetPubIPAndSend.py >> /opt/ip_monitor/logs/cron.log 2>&1
```

### 6. 日志轮转（可选）
```bash
sudo nano /etc/logrotate.d/ip_monitor

# 添加以下内容
/opt/ip_monitor/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### 7. 修改日志配置
需要修改各个Python文件中的日志配置，将日志文件路径指向 logs 目录：

```python
# 在所有Python文件中修改日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/ip_monitor/logs/程序名.log'),  # 修改为对应的日志文件名
        logging.StreamHandler()
    ]
)
```

## 使用说明

### 手动运行测试
```bash
python3 GetPubIPAndSend.py
```

### 查看日志
```bash
# 查看IP监控日志
tail -f /opt/ip_monitor/logs/ip_monitor.log

# 查看通知日志
tail -f /opt/ip_monitor/logs/notification.log

# 查看DNS更新日志
tail -f /opt/ip_monitor/logs/cloudflare_dns.log

# 查看定时任务日志
tail -f /opt/ip_monitor/logs/cron.log
```

## 注意事项
1. 请妥善保管配置文件中的敏感信息
2. 建议定期检查日志文件大小
3. 确保Python和相关依赖包及时更新
4. 建议定期备份配置文件

## 问题排查
1. 确认Python版本：`python3 --version`
2. 检查依赖包：`pip3 list | grep -E "requests|pyyaml"`
3. 检查文件权限：`ls -l`
4. 检查cron日志：`grep CRON /var/log/syslog`

## License
MIT License

## 联系方式
如有问题，请提交 Issue
