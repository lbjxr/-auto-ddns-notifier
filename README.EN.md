# IP Monitor & Notify System
 <div> <p align="center">English | <a href="./README.md">中文</a> <br></p></div>
A system designed to monitor public IP address changes and automatically send notifications via WeChat while updating Cloudflare DNS records.

## Features
Automatically monitor public IP changes.

Send notifications via WxPusher (WeChat Push Service).

Automatically update Cloudflare DNS records.

Comprehensive logging system.

Configurable retry mechanism.

Support for notifications to multiple service addresses.

## Directory Structure
```bash
/opt/ip_monitor/
├── GetPubIPAndSend.py # Main program
├── SendMessageByWxPusher.py # Notification module
├── UpdateCFDNS.py # DNS update module
├── config.yaml # Configuration file
├── last_ip.txt # IP record file
└── logs/ # Log directory
    ├── ip_monitor.log # IP monitoring log
    ├── notification.log # Notification log
    ├── cloudflare_dns.log # DNS update log
    └── cron.log # Cron job log
```
## Installation
### 1. Environment Requirements
Python 3.6+
Linux/Windows system
### 2. Install Dependencies
```bash
pip install requests pyyaml
```
### 3. Configuration File
Copy config.yaml and modify it according to your needs:
```yaml
# IP check configuration, refer to IP query websites such as https://www.ip.cn/
ip_check:
  api_url: "http://cip.cc"
  last_ip_file: "./last_ip.txt"
  ip_pattern: "IP\\s*:\\s*([\\d\\.]+)"
  max_retries: 3
  retry_delay: 2

# Notification configuration, refer to WxPusher official documentation https://wxpusher.zjiecode.com/docs/#/
notification:
  script_path: "SendMessageByWxPusher.py"
  enabled: true
  wxpusher:
    app_token: "Your WxPusher_APP_Token"
    uids: ["Your UID"]
  services:
    s1_port: Port for System 1
    s2_port: Port for System 2

# Cloudflare configuration, refer to Cloudflare official documentation https://developers.cloudflare.com/api/
cloudflare:
  api_token: "Your Cloudflare_API_Token"
  zone_id: "Your Zone_ID"
  record_name: "Your Domain"
  dns_type: "A"
  ttl: 120
  proxied: false
  max_retries: 3
  retry_delay: 2
```
### 4. Deployment in Linux Environment
```bash
# Create working directory
sudo mkdir /opt/ip_monitor
sudo chown $USER:$USER /opt/ip_monitor  # Change directory ownership
cd /opt/ip_monitor

# Copy all files to the working directory
cp /path/to/files/* .

# Set execution permissions
chmod +x *.py

# Set configuration file permissions
chmod 600 config.yaml

# Create log directory
mkdir logs
chmod 755 logs
```
### 5. Set Up Cron Job
```bash
# Edit crontab
crontab -e

# Add cron job (run every 5 minutes)
*/5 * * * * cd /opt/ip_monitor && /usr/bin/python3 GetPubIPAndSend.py >> /opt/ip_monitor/logs/cron.log 2>&1
```
### 6. Log Rotation (Optional)
```bash
sudo nano /etc/logrotate.d/ip_monitor

# Add the following content
/opt/ip_monitor/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```
### 7. Modify Log Configuration
Modify the log configuration in all Python files to point the log file paths to the logs directory:
```Python
# Modify log configuration in all Python files
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/ip_monitor/logs/program_name.log'),  # Modify to the corresponding log file name
        logging.StreamHandler()
    ]
)
```
## Usage
### Manual Test Run
```bash
python3 GetPubIPAndSend.py
```
### View Logs
```bash
# View IP monitoring log
tail -f /opt/ip_monitor/logs/ip_monitor.log

# View notification log
tail -f /opt/ip_monitor/logs/notification.log

# View DNS update log
tail -f /opt/ip_monitor/logs/cloudflare_dns.log

# View cron job log
tail -f /opt/ip_monitor/logs/cron.log
```
## Notes
Keep sensitive information in the configuration file secure.
Regularly check the size of log files.
Ensure Python and related packages are up-to-date.
Regularly back up the configuration file.
Troubleshooting
Confirm Python version: python3 --version
Check installed packages: pip3 list | grep -E "requests|pyyaml"
Check file permissions: ls -l
Check cron logs: grep CRON /var/log/syslog
## License
MIT License
## Contact
If you have any questions, please submit an Issue.
This English version of the README.md file maintains the original structure and content while ensuring clarity and accuracy in English.
