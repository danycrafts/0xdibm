import os
import sys
import shutil
import psutil
import platform
import pdfplumber
import pandas as pd
import json
import requests
from utils.logger import get_logger
logger = get_logger()

def get_resource_path(relative_path: str) -> str:
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    except Exception as e:
        logger.error(f"Error getting resource path for {relative_path}: {e}")
        return ""

def create_directory(path: str) -> bool:
    abs_path = get_resource_path(path)
    try:
        os.makedirs(abs_path, exist_ok=True)
        logger.info(f"Directory created: {abs_path}")
        return True
    except OSError as e:
        logger.error(f"Error creating directory {abs_path}: {e}")
        return False

def delete_directory(path: str) -> bool:
    abs_path = get_resource_path(path)
    try:
        shutil.rmtree(abs_path)
        logger.info(f"Directory deleted: {abs_path}")
        return True
    except OSError as e:
        logger.error(f"Error deleting directory {abs_path}: {e}")
        return False

def pretty_print_json(json_data) -> None:
    try:
        pretty_json = json.dumps(json_data, indent=4, sort_keys=True)
        logger.debug(pretty_json)
    except ValueError as e:
        logger.error(f"Error parsing JSON: {e}")

def create_file(path: str, content: str = "") -> bool:
    abs_path = get_resource_path(path)
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as file:
            file.write(content)
        logger.info(f"File created: {abs_path}")
        return True
    except OSError as e:
        logger.error(f"Error creating file {abs_path}: {e}")
        return False

def delete_file(path: str) -> bool:
    abs_path = get_resource_path(path)
    try:
        os.remove(abs_path)
        logger.info(f"File deleted: {abs_path}")
        return True
    except FileNotFoundError:
        logger.warning(f"File {abs_path} not found.")
        return False
    except OSError as e:
        logger.error(f"Error deleting file {abs_path}: {e}")
        return False

def is_empty(d: dict) -> bool:
        if not isinstance(d, dict) or not d:  # Check if it's a dict and not empty
            return not d
        return all(is_empty(v) for v in d.values() if isinstance(v, dict))

def get_system_info():
    system_info = {
        'cpu_architecture': platform.machine(),
        'cpu_usage_percent': round(psutil.cpu_percent(interval=1), 2),
        'num_cores': psutil.cpu_count(logical=True),
        'available_ram_gb': round(psutil.virtual_memory().available / (1024 ** 3), 2),  # Convert bytes to GB
        'total_ram_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2),  # Convert bytes to GB
    }
    if platform.system().lower() == 'windows':
        system_info['os'] = 'Windows'
        system_info['os_version'] = platform.version()
    elif platform.system().lower() == 'darwin':
        system_info['os'] = 'macOS'
        system_info['os_version'] = platform.mac_ver()[0]
    elif platform.system().lower() == 'linux':
        system_info['os'] = 'Linux'
        system_info['os_version'] = platform.release()
    else:
        system_info['os'] = 'Unknown'
        system_info['os_version'] = 'Unknown'

    return system_info

def extract_tables(pdf_path) -> list:
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)
    return tables

def fetch_models(api_url, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    try:
        response = requests.get(api_url+"/models", headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return [item["id"] for item in json_response.get("data", []) if "id" in item]
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"An error occurred: {req_err}")
    return []