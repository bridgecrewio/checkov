import os
import yaml
from typing import Dict, Optional

class RuleExplanationLoader:
    """规则解释加载器，单例模式"""
    
    _instance: Optional['RuleExplanationLoader'] = None
    _explanations: Optional[Dict[str, Dict]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_explanations(self) -> Dict[str, Dict]:
        """加载规则解释文件，缓存结果"""
        if self._explanations is not None:
            return self._explanations
        
        # 查找规则解释文件
        file_path = self._find_explanation_file()
        if not file_path:
            self._explanations = {}
            return self._explanations
        
        # 解析YAML文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._explanations = yaml.safe_load(f) or {}
        except Exception as e:
            # 如果加载失败，返回空字典
            self._explanations = {}
        
        return self._explanations
    
    def get_explanation(self, check_id: str) -> Optional[Dict]:
        """获取指定规则的解释信息"""
        explanations = self.load_explanations()
        return explanations.get(check_id)
    
    def _find_explanation_file(self) -> Optional[str]:
        """查找规则解释文件的位置"""
        # 可能的文件路径
        possible_paths = [
            # 相对于当前文件的路径
            os.path.join(os.path.dirname(__file__), '../../data/rule_explanations.yaml'),
            # 相对于项目根目录的路径
            os.path.join(os.getcwd(), 'checkov/data/rule_explanations.yaml'),
            # 系统路径
            '/etc/checkov/rule_explanations.yaml',
        ]
        
        # 检查文件是否存在
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                return path
        
        return None

# 全局实例
explanation_loader = RuleExplanationLoader()
