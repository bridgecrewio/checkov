from typing import Dict, Optional, Any
from checkov.common.explainer.loader import explanation_loader

class RuleExplanationResolver:
    """规则解释解析器，处理回退策略和多语言支持"""
    
    def __init__(self, lang: str = "en"):
        self.lang = lang.lower()
        if self.lang not in ["en", "zh"]:
            self.lang = "en"
    
    def resolve_explanation(self, check_id: str, check: Any, runner_type: str) -> Dict[str, Any]:
        """解析指定规则的解释信息，包含回退策略"""
        # 获取规则解释
        explanation = explanation_loader.get_explanation(check_id)
        
        # 解析风险成因
        root_cause = self._resolve_field(explanation, "root_cause", check)
        
        # 解析影响面
        impact_surface = self._resolve_field(explanation, "impact_surface", check)
        if not impact_surface:
            # 生成通用影响面模板
            resource_type = self._get_resource_type(check)
            impact_surface = f"该配置可能影响资源类型 {resource_type} 与其关联权限/网络访问面，建议根据规则文档评估具体影响。"
        
        # 解析修复示例
        fix_examples = self._resolve_fix_examples(explanation, runner_type)
        
        return {
            "root_cause": root_cause,
            "impact_surface": impact_surface,
            "fix_examples": fix_examples
        }
    
    def _resolve_field(self, explanation: Optional[Dict], field_name: str, check: Any) -> str:
        """解析单个字段，支持多语言和回退策略"""
        if not explanation:
            # 回退到规则元数据
            return self._get_fallback_value(check, field_name)
        
        # 优先使用指定语言的字段
        lang_field_name = f"{field_name}_{self.lang}"
        if lang_field_name in explanation and explanation[lang_field_name]:
            return explanation[lang_field_name]
        
        # 回退到英文字段
        if field_name in explanation and explanation[field_name]:
            return explanation[field_name]
        
        # 回退到规则元数据
        return self._get_fallback_value(check, field_name)
    
    def _resolve_fix_examples(self, explanation: Optional[Dict], runner_type: str) -> Dict[str, Any]:
        """解析修复示例，支持按runner类型选择"""
        if not explanation or "fix_examples" not in explanation:
            return {}
        
        fix_examples = explanation["fix_examples"]
        
        # 按runner类型选择修复示例
        if runner_type in fix_examples:
            return {runner_type: fix_examples[runner_type]}
        
        # 回退到terraform示例
        if "terraform" in fix_examples:
            return {"terraform": fix_examples["terraform"]}
        
        # 回退到第一个可用的示例
        if fix_examples:
            first_type = next(iter(fix_examples))
            return {first_type: fix_examples[first_type]}
        
        return {}
    
    def _get_fallback_value(self, check: Any, field_name: str) -> str:
        """获取回退值，从规则元数据中提取"""
        # 尝试从规则元数据中提取不同字段
        fallback_fields = [
            "short_description",
            "description",
            "name",
            "id"
        ]
        
        for fallback_field in fallback_fields:
            if hasattr(check, fallback_field):
                value = getattr(check, fallback_field)
                if value and isinstance(value, str):
                    return value
        
        return ""
    
    def _get_resource_type(self, check: Any) -> str:
        """获取资源类型"""
        if hasattr(check, "resource_type"):
            return check.resource_type
        if hasattr(check, "entity_type"):
            return check.entity_type
        return "未知资源类型"

# 全局实例
explanation_resolver = RuleExplanationResolver()
