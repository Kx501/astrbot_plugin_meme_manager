import json
import re
import aiohttp
import random
import string
from typing import Dict, Any
from pathlib import Path
from astrbot.api import logger

def should_download_memes(memes_dir):
    """检查表情包目录，如果为空则返回 True（表示需要从 GitHub 下载）"""
    # 确保目录存在
    memes_path = Path(memes_dir) if not isinstance(memes_dir, Path) else memes_dir
    memes_path.mkdir(parents=True, exist_ok=True)
    
    # 检查是否存在任何子文件夹（表情包类别文件夹）
    # 如果存在任何文件夹，说明用户已有表情包，不需要下载
    try:
        for item in memes_path.iterdir():
            if item.is_dir():
                logger.info(f"检测到表情包类别文件夹 {item.name}，跳过默认表情包下载")
                return False
    except (OSError, PermissionError) as e:
        logger.warning(f"无法读取表情包目录 {memes_path}: {e}")
        return False
    
    # 目录为空，需要从 GitHub 下载
    logger.info("表情包目录为空，将在后台从 GitHub 自动下载")
    return True

def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """保存 JSON 数据到文件"""
    try:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
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

async def download_memes_from_github(plugin_data_dir):
    """从 GitHub Releases 下载默认表情包（zip 文件）
    
    压缩包标准：包含 memes 文件夹，直接解压到 plugin_data_dir 即可
    """
    import zipfile
    import io
    
    # GitHub Releases 下载链接
    ZIP_URL = "https://github.com/Kx501/picx-images-hosting/releases/download/astrbot-memes/memes.zip"
    
    plugin_data_path = Path(plugin_data_dir) if not isinstance(plugin_data_dir, Path) else plugin_data_dir
    
    try:
        logger.info("开始从 GitHub 下载默认表情包...")
        logger.info(f"下载地址: {ZIP_URL}")
        
        # 下载 zip 文件
        async with aiohttp.ClientSession() as session:
            async with session.get(ZIP_URL, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status != 200:
                    logger.error(f"下载失败，HTTP状态码: {resp.status}")
                    logger.error(f"URL: {ZIP_URL}")
                    return False
                
                # 检查文件大小
                content_length = resp.headers.get('Content-Length')
                if content_length:
                    size_mb = int(content_length) / 1024 / 1024
                    logger.info(f"文件大小: {size_mb:.2f} MB")
                
                logger.info("正在下载文件...")
                zip_content = await resp.read()
                logger.info("下载完成，开始解压...")
        
        # 直接解压到 plugin_data_dir（压缩包内包含 memes 文件夹，解压后会自动创建）
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            # 检查 zip 文件是否有效
            zip_file.testzip()
            
            # 解压到 plugin_data_dir
            zip_file.extractall(plugin_data_path)
            
            # 统计解压的文件数量（排除目录）
            namelist = zip_file.namelist()
            file_count = len([name for name in namelist if not (name.endswith("/") or name.endswith("\\"))])
            logger.info(f"解压完成，共 {file_count} 个文件")
        
        logger.info(f"默认表情包下载并解压完成: {plugin_data_path}")
        return True
        
    except zipfile.BadZipFile:
        logger.error("下载的文件不是有效的 zip 文件")
        return False
    except aiohttp.ClientError as e:
        logger.error(f"网络请求失败: {e}")
        return False
    except Exception as e:
        logger.error(f"从 GitHub 下载表情包失败: {e}", exc_info=True)
        return False

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
