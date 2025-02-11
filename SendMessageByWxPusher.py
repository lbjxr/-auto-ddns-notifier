import sys
import requests
import json
import yaml
import logging
from time import sleep

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败：{e}")
        return None

def send_notification(ip_address):
    config = load_config()
    if not config:
        return False

    wxpusher_config = config['notification']['wxpusher']
    services_config = config['notification']['services']
    max_retries = config['ip_check']['max_retries']
    retry_delay = config['ip_check']['retry_delay']

    api_url = "https://wxpusher.zjiecode.com/api/send/message"
    
    json_payload = {
        "appToken": wxpusher_config['app_token'],
        "content": f"<h1>公网IP变更：</h1><br/>"
                  f"<p>你的相关服务访问地址为：</p>"
                  f"<p>xx系统地址： "
                  f"<a href=\"http://{ip_address}:{services_config['s1_port']}\">"
                  f"http://{ip_address}:{services_config['s1_port']}</a></p>"
                  f"<p>xx2系统地址： "
                  f"<a href=\"http://{ip_address}:{services_config['s2_port']}\">"
                  f"http://{ip_address}:{services_config['s2_port']}</a></p>",
        "summary": "公网IP变更",
        "contentType": 2,
        "uids": wxpusher_config['uids'],
        "url": "",
        "verifyPay": False
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(json_payload),
                timeout=10
            )
            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get('code') == 1000:
                logging.info("通知发送成功")
                return True
            else:
                logging.error(f"发送失败：{response_data.get('msg')}")
                
        except requests.RequestException as e:
            logging.error(f"第 {attempt + 1} 次发送失败：{e}")
            if attempt < max_retries - 1:
                sleep(retry_delay)
                continue
    
    return False

def main():
    if len(sys.argv) < 2:
        logging.error("使用方法: python SendMessage.py <IP_ADDRESS>")
        sys.exit(1)

    ip_address = sys.argv[1]
    if not send_notification(ip_address):
        sys.exit(1)

if __name__ == "__main__":
    main()