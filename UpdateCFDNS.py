import requests
import json
import yaml
import logging
import time
from typing import Dict

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudflare_dns.log'),
        logging.StreamHandler()
    ]
)

def load_config() -> Dict:
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config['cloudflare']
    except Exception as e:
        logging.error(f"加载配置文件失败：{e}")
        raise

def get_dns_record_id(config: Dict) -> str:
    """获取DNS记录ID"""
    url = f"https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records"
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }
    params = {
        "type": config['dns_type'],
        "name": config['record_name']
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json()["result"]
        if records:
            record_id = records[0]["id"]
            logging.info(f"成功获取DNS记录ID：{record_id}")
            return record_id
        raise Exception("未找到对应的DNS记录")
    except Exception as e:
        logging.error(f"获取DNS记录失败：{e}")
        raise

def update_dns_record(config: Dict, record_id: str, new_ip: str) -> None:
    """更新DNS记录"""
    url = f"https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "type": config['dns_type'],
        "name": config['record_name'],
        "content": new_ip,
        "ttl": config['ttl'],
        "proxied": config['proxied']
    }

    for attempt in range(config['max_retries']):
        try:
            response = requests.put(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            logging.info(f"DNS记录已成功更新为：{new_ip}")
            return
        except Exception as e:
            logging.error(f"第 {attempt + 1} 次更新失败：{e}")
            if attempt == config['max_retries'] - 1:
                raise
            time.sleep(config['retry_delay'])

def update_cloudflare_dns(ip_address: str) -> bool:
    """
    供外部调用的DNS更新函数
    
    Args:
        ip_address: 需要更新的IP地址
        
    Returns:
        bool: 更新是否成功
    """
    try:
        config = load_config()
        record_id = get_dns_record_id(config)
        update_dns_record(config, record_id, ip_address)
        return True
    except Exception as e:
        logging.error(f"更新DNS记录失败：{e}")
        return False