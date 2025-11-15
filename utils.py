import os
import json
import logging
import re
import aiohttp
import random
import string
from typing import Dict, Any
import shutil
from .config import MEMES_DIR, CURRENT_DIR

logger = logging.getLogger(__name__)

def ensure_dir_exists(path) -> None:
    """确保目录存在，不存在则创建"""
    from pathlib import Path
    if isinstance(path, Path):
        path.mkdir(parents=True, exist_ok=True)
    else:
        if not os.path.exists(path):
            os.makedirs(path)

def copy_memes_if_not_exists():
    """如果 MEMES_DIR 下没有表情包文件，则复制 CURRENT_DIR 下的 memes 文件夹内容"""
    from pathlib import Path
    
    # 确保目录存在
    ensure_dir_exists(MEMES_DIR)
    
    # 将 MEMES_DIR 转换为 Path 对象以便统一处理
    memes_path = Path(MEMES_DIR) if not isinstance(MEMES_DIR, Path) else MEMES_DIR
    
    # 检查是否存在任何子文件夹（表情包类别文件夹）
    # 如果存在任何文件夹，说明用户已有表情包，跳过复制以避免覆盖
    try:
        for item in memes_path.iterdir():
            if item.is_dir():
                logger.info(f"检测到表情包类别文件夹 {item.name}，跳过默认表情包复制")
                return
    except (OSError, PermissionError) as e:
        logger.warning(f"无法读取表情包目录 {memes_path}: {e}")
        return
    
    # 只有当目录完全为空（没有任何文件夹）时，才复制默认表情包
    source_dir = Path(CURRENT_DIR) / "memes"
    if not source_dir.exists():
        logger.warning(f"默认表情包目录不存在: {source_dir}")
        return
    
    # 复制所有文件
    for item in source_dir.iterdir():
        src_path = source_dir / item.name
        dst_path = memes_path / item.name
        if src_path.is_dir():
            if not dst_path.exists():
                shutil.copytree(str(src_path), str(dst_path))
        else:
            shutil.copy2(str(src_path), str(dst_path))
    
    logger.info(f"已将默认表情包复制到 {memes_path}")

def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """保存 JSON 数据到文件"""
    try:
        ensure_dir_exists(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存 JSON 文件失败 {filepath}: {e}")
        return False

def load_json(filepath: str, default: Dict = None) -> Dict:
    """从文件加载 JSON 数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载 JSON 文件失败 {filepath}: {e}")
        return default if default is not None else {}

def dict_to_string(dictionary):
    lines = [f"{key} - {value}" for key, value in dictionary.items()]
    return "\n".join(lines)

def generate_secret_key(length=8):
    """生成随机秘钥"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def get_public_ip():
    """异步获取公网IPv4地址"""
    ipv4_apis = [
        'http://ipv4.ifconfig.me/ip',        # IPv4专用接口
        'http://api-ipv4.ip.sb/ip',          # 樱花云IPv4接口
        'http://v4.ident.me',                # IPv4专用
        'http://ip.qaros.com',               # 备用国内服务
        'http://ipv4.icanhazip.com',         # IPv4专用
        'http://4.icanhazip.com'             # 另一个变种地址
    ]
    
    async with aiohttp.ClientSession() as session:
        for api in ipv4_apis:
            try:
                async with session.get(api, timeout=5) as response:
                    if response.status == 200:
                        ip = (await response.text()).strip()
                        # 添加二次验证确保是IPv4格式
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            return ip
            except:
                continue
    
    return "[服务器公网ip]"
