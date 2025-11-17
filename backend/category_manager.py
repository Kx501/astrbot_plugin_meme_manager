from pathlib import Path
from typing import Dict, Set, List, Tuple
from ..constants import DEFAULT_CATEGORY_DESCRIPTIONS
from ..utils import save_json, load_json
from astrbot.api import logger

class CategoryManager:
    def __init__(self, memes_dir, memes_data_path):
        """初始化类别管理器
        
        Args:
            memes_dir: 表情包目录路径
            memes_data_path: 类别描述数据文件路径
        """
        self.memes_dir = Path(memes_dir)
        self.memes_data_path = Path(memes_data_path)
        self.memes_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_data_file()
        self.descriptions = self._load_descriptions()
        
    def _ensure_data_file(self) -> None:
        """确保 memes_data.json 文件存在，不存在则创建并写入默认数据"""
        if not self.memes_data_path.exists():
            save_json(DEFAULT_CATEGORY_DESCRIPTIONS, str(self.memes_data_path))
            logger.info(f"创建默认类别描述文件: {self.memes_data_path}")
            
    def _load_descriptions(self) -> Dict[str, str]:
        """加载类别描述配置"""
        return load_json(str(self.memes_data_path), DEFAULT_CATEGORY_DESCRIPTIONS)
    
    def get_local_categories(self) -> Set[str]:
        """获取本地文件夹中的类别"""
        try:
            return {item.name for item in self.memes_dir.iterdir() if item.is_dir()}
        except Exception as e:
            logger.error(f"获取本地类别失败: {e}")
            return set()
    
    def get_sync_status(self) -> Tuple[List[str], List[str]]:
        """获取同步状态
        返回: (missing_in_config, deleted_categories)
        """
        local_categories = self.get_local_categories()
        config_categories = set(self.descriptions.keys())
        
        return (
            list(local_categories - config_categories),  # 本地有但配置没有
            list(config_categories - local_categories)   # 配置有但本地没有
        )
    
    def update_description(self, category: str, description: str) -> bool:
        """更新类别描述"""
        try:
            self.descriptions[category] = description              # 更新内存中的 descriptions
            # 同步保存到文件
            return save_json(self.descriptions, str(self.memes_data_path))
        except Exception as e:
            logger.error(f"更新类别描述失败: {e}")
            return False

    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """重命名类别"""
        try:
            if old_name not in self.descriptions:
                return False
            
            # 获取旧类别的描述
            description = self.descriptions[old_name]
            
            # 更新配置
            del self.descriptions[old_name]
            self.descriptions[new_name] = description
            
            # 更新文件夹名称
            old_path = self.memes_dir / old_name
            new_path = self.memes_dir / new_name
            if old_path.exists():
                old_path.rename(new_path)
            
            # 同步更新内存中的数据
            return save_json(self.descriptions, str(self.memes_data_path))
        except Exception as e:
            logger.error(f"重命名类别失败: {e}")
            return False


    
    def delete_category(self, category: str) -> bool:
        """删除类别"""
        try:
            # 从配置中删除
            if category in self.descriptions:
                del self.descriptions[category]
                save_json(self.descriptions, str(self.memes_data_path))
            
            # 删除文件夹
            category_path = self.memes_dir / category
            if category_path.exists():
                import shutil
                shutil.rmtree(category_path)
            
            return True
        except Exception as e:
            logger.error(f"删除类别失败: {e}")
            return False
    
    def get_descriptions(self) -> Dict[str, str]:
        """获取所有类别描述"""
        return self.descriptions.copy()  # 返回字典的副本 
    
    def sync_with_filesystem(self) -> bool:
        """同步文件系统和配置"""
        try:
            local_categories = self.get_local_categories()
            changed = False
            
            # 为新类别添加默认描述
            for category in local_categories:
                if category not in self.descriptions:
                    self.descriptions[category] = "请添加描述"
                    changed = True
            
            if changed:
                return save_json(self.descriptions, str(self.memes_data_path))
            return True
        except Exception as e:
            logger.error(f"同步文件系统失败: {e}")
            return False 