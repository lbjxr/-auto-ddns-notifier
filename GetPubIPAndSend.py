import requests
import os
import subprocess
import re
import yaml
import logging
from time import sleep
from UpdateCFDNS import update_cloudflare_dns

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ip_monitor.log'),
        logging.StreamHandler()
    ]
)

def load_config():
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败：{e}")
        raise

def is_valid_ip(ip_address):
    """
    验证IP地址格式是否有效
    
    规则：
    1. 必须是4段数字，以点分隔
    2. 每段数字范围为0-255
    3. 不能是回环地址(127.x.x.x)或保留地址
    """
    try:
        # 分割IP地址
        parts = ip_address.split('.')
        
        # 检查是否为4段
        if len(parts) != 4:
            return False
            
        # 检查每段是否为有效数字
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
                
        # 检查是否为回环地址
        if parts[0] == '127':
            return False
            
        # 检查是否为保留地址
        if parts[0] == '0' or parts[0] == '169' and parts[1] == '254':
            return False
            
        return True
    except:
        return False

def get_public_ip(config):
    api_url = config['ip_check']['api_url']
    ip_pattern = config['ip_check']['ip_pattern']
    max_retries = config['ip_check']['max_retries']
    retry_delay = config['ip_check']['retry_delay']
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            match = re.search(ip_pattern, response.text)
            if match:
                ip_address = match.group(1)
                # 添加IP地址验证
                if is_valid_ip(ip_address):
                    logging.info(f"成功获取有效IP地址：{ip_address}")
                    return ip_address
                else:
                    logging.error(f"获取到无效IP地址：{ip_address}")
            else:
                logging.error("未找到IP地址")
        except requests.RequestException as e:
            logging.error(f"第 {attempt + 1} 次获取IP失败：{e}")
            if attempt < max_retries - 1:
                sleep(retry_delay)
    return None

def main():
    try:
        # 加载配置
        config = load_config()
        last_ip_file = config['ip_check']['last_ip_file']

        # 获取当前IP
        current_ip = get_public_ip(config)
        if not current_ip:
            logging.error("无法获取公网IP地址")
            return

        # 检查IP是否变化
        ip_changed = False
        if os.path.isfile(last_ip_file):
            try:
                with open(last_ip_file, 'r') as file:
                    last_ip = file.read().strip()
                if current_ip == last_ip:
                    logging.info("IP地址未发生变化")
                    return
                ip_changed = True
            except IOError as e:
                logging.error(f"读取上次IP文件失败：{e}")

        # 保存新IP
        try:
            with open(last_ip_file, 'w') as file:
                file.write(current_ip)
            logging.info(f"已保存新IP地址：{current_ip}")
        except IOError as e:
            logging.error(f"保存IP地址失败：{e}")
            return

        if ip_changed:
            # 发送通知
            if config['notification']['enabled']:
                script_path = config['notification']['script_path']
                try:
                    result = subprocess.run(
                        ["python", script_path, current_ip],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logging.info("通知发送成功")
                except subprocess.CalledProcessError as e:
                    logging.error(f"通知脚本执行失败：{e.stderr}")
                except FileNotFoundError:
                    logging.error(f"通知脚本 '{script_path}' 未找到")
                except Exception as e:
                    logging.error(f"发送通知时发生意外错误：{e}")

            # 更新DNS记录
            if update_cloudflare_dns(current_ip):
                logging.info("DNS记录更新成功")
            else:
                logging.error("DNS记录更新失败")

    except Exception as e:
        logging.error(f"程序执行过程中发生错误：{e}")

if __name__ == "__main__":
    main()
    