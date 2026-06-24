import os
import html
from typing import Dict, List, Any
from datetime import datetime

class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self, output_path: str = "checkov_explain.html"):
        self.output_path = output_path
    
    def generate_report(self, results: List[Dict[str, Any]], explain_lang: str = "en") -> str:
        """生成HTML报告"""
        # 准备报告数据
        report_data = self._prepare_report_data(results, explain_lang)
        
        # 生成HTML内容
        html_content = self._generate_html(report_data, explain_lang)
        
        return html_content
    
    def _prepare_report_data(self, results: List[Dict[str, Any]], explain_lang: str) -> Dict[str, Any]:
        """准备报告数据"""
        # 合并所有报告中的失败检查
        failed_checks = []
        for report in results:
            failed_checks.extend(report.get("results", {}).get("failed_checks", []))
        
        # 统计信息
        total_failed = len(failed_checks)
        severity_counts = self._count_by_severity(failed_checks)
        iac_type_counts = self._count_by_iac_type(failed_checks)
        
        # 准备明细数据
        details = []
        for check in failed_checks:
            # 获取解释信息
            explanation = check.get("explanation", {})
            root_cause = explanation.get("root_cause", "")
            impact_surface = explanation.get("impact_surface", "")
            fix_examples = explanation.get("fix_examples", {})
            
            # 准备修复示例
            examples_html = self._prepare_fix_examples(fix_examples)
            
            details.append({
                "check_id": check.get("check_id", ""),
                "title": check.get("check_name", ""),
                "description": check.get("check_result", {}).get("description", ""),
                "severity": check.get("severity", "MEDIUM"),
                "resource": check.get("resource", ""),
                "file_path": check.get("file_path", ""),
                "root_cause": root_cause,
                "impact_surface": impact_surface,
                "fix_examples": examples_html
            })
        
        return {
            "total_failed": total_failed,
            "severity_counts": severity_counts,
            "iac_type_counts": iac_type_counts,
            "details": details,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _count_by_severity(self, checks: List[Dict]) -> Dict[str, int]:
        """按严重级别统计"""
        counts = {}
        for check in checks:
            severity = check.get("severity", "MEDIUM").upper()
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_iac_type(self, checks: List[Dict]) -> Dict[str, int]:
        """按IaC类型统计"""
        counts = {}
        for check in checks:
            file_path = check.get("file_path", "")
            # 简单根据文件扩展名判断IaC类型
            if file_path.endswith(".tf"):
                iac_type = "Terraform"
            elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
                iac_type = "YAML"
            elif file_path.endswith(".json"):
                iac_type = "JSON"
            elif file_path.endswith(".template") or file_path.endswith(".cfn"):
                iac_type = "CloudFormation"
            else:
                iac_type = "Unknown"
            counts[iac_type] = counts.get(iac_type, 0) + 1
        return counts
    
    def _prepare_fix_examples(self, fix_examples: Dict) -> str:
        """准备修复示例的HTML内容"""
        if not fix_examples:
            return "<p>暂无修复示例</p>"
        
        examples_html = []
        for iac_type, examples in fix_examples.items():
            examples_html.append(f"<h4>{iac_type.upper()} 修复示例</h4>")
            
            # 显示错误示例
            if "bad" in examples and examples["bad"]:
                bad_example = self._truncate_code(examples["bad"])
                examples_html.append(f"<div class='example bad-example'><h5>错误示例</h5><pre><code>{html.escape(bad_example)}</code></pre></div>")
            
            # 显示正确示例
            if "good" in examples and examples["good"]:
                good_example = self._truncate_code(examples["good"])
                examples_html.append(f"<div class='example good-example'><h5>正确示例</h5><pre><code>{html.escape(good_example)}</code></pre></div>")
        
        return "".join(examples_html)
    
    def _truncate_code(self, code: str, max_lines: int = 50) -> str:
        """截断代码示例，最多显示指定行数"""
        lines = code.splitlines()
        if len(lines) <= max_lines:
            return code
        
        truncated = lines[:max_lines]
        truncated.append("...")
        return "\n".join(truncated)
    
    def _generate_html(self, report_data: Dict[str, Any], explain_lang: str) -> str:
        """生成HTML内容"""
        # 翻译文本
        if explain_lang == "zh":
            title = "Checkov 规则解释报告"
            summary = "扫描结果汇总"
            total_failed = "失败规则总数"
            severity = "严重级别"
            iac_type = "IaC 类型"
            details = "详细信息"
            check_id = "规则ID"
            title_col = "标题"
            description_col = "描述"
            severity_col = "严重级别"
            resource_col = "资源"
            file_path_col = "文件路径"
            root_cause = "风险成因"
            impact_surface = "影响面"
            fix_examples = "修复示例"
            generated_at = "生成时间"
        else:
            title = "Checkov Rule Explanation Report"
            summary = "Scan Summary"
            total_failed = "Total Failed Checks"
            severity = "Severity"
            iac_type = "IaC Type"
            details = "Details"
            check_id = "Check ID"
            title_col = "Title"
            description_col = "Description"
            severity_col = "Severity"
            resource_col = "Resource"
            file_path_col = "File Path"
            root_cause = "Risk Cause"
            impact_surface = "Impact Surface"
            fix_examples = "Fix Examples"
            generated_at = "Generated At"
        
        # 生成统计信息HTML
        severity_html = "".join([f"<li>{severity}: {count}</li>" for severity, count in report_data["severity_counts"].items()])
        iac_type_html = "".join([f"<li>{iac_type}: {count}</li>" for iac_type, count in report_data["iac_type_counts"].items()])
        
        # 生成明细HTML
        details_html = []
        for detail in report_data["details"]:
            details_html.append(f"""
                <div class='check-item'>
                    <div class='check-header'>
                        <h3>{detail['check_id']}: {html.escape(detail['title'])}</h3>
                        <span class='severity severity-{detail['severity'].lower()}'>{detail['severity']}</span>
                    </div>
                    <div class='check-meta'>
                        <p><strong>{resource_col}:</strong> {html.escape(detail['resource'])}</p>
                        <p><strong>{file_path_col}:</strong> {html.escape(detail['file_path'])}</p>
                    </div>
                    <div class='check-description'>
                        <h4>{description_col}</h4>
                        <p>{html.escape(detail['description'])}</p>
                    </div>
                    <div class='check-explanation'>
                        <div class='explanation-section'>
                            <h4>{root_cause}</h4>
                            <p>{html.escape(detail['root_cause'])}</p>
                        </div>
                        <div class='explanation-section'>
                            <h4>{impact_surface}</h4>
                            <p>{html.escape(detail['impact_surface'])}</p>
                        </div>
                        <div class='explanation-section'>
                            <h4>{fix_examples}</h4>
                            {detail['fix_examples']}
                        </div>
                    </div>
                </div>
            """)
        
        # 完整HTML模板
        html_template = f"""
        <!DOCTYPE html>
        <html lang='{explain_lang}'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>{title}</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
                .header { background-color: #007bff; color: #fff; padding: 20px; text-align: center; }
                .header h1 { font-size: 24px; margin-bottom: 10px; }
                .header p { font-size: 14px; opacity: 0.9; }
                .summary { padding: 20px; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }
                .summary h2 { font-size: 18px; margin-bottom: 15px; color: #333; }
                .summary-stats { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px; }
                .stat-item { flex: 1; min-width: 200px; background-color: #fff; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                .stat-item h3 { font-size: 14px; margin-bottom: 10px; color: #666; }
                .stat-item ul { list-style: none; }
                .stat-item li { font-size: 14px; margin-bottom: 5px; color: #333; }
                .details { padding: 20px; }
                .details h2 { font-size: 18px; margin-bottom: 15px; color: #333; }
                .check-item { margin-bottom: 25px; padding: 20px; background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #007bff; }
                .check-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
                .check-header h3 { font-size: 16px; color: #333; flex: 1; }
                .severity { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
                .severity-critical { background-color: #dc3545; color: #fff; }
                .severity-high { background-color: #fd7e14; color: #fff; }
                .severity-medium { background-color: #ffc107; color: #212529; }
                .severity-low { background-color: #28a745; color: #fff; }
                .check-meta { display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; font-size: 14px; color: #666; }
                .check-description { margin-bottom: 20px; }
                .check-description h4 { font-size: 14px; margin-bottom: 8px; color: #333; font-weight: bold; }
                .check-description p { font-size: 14px; color: #666; line-height: 1.5; }
                .check-explanation { display: flex; flex-direction: column; gap: 15px; }
                .explanation-section h4 { font-size: 14px; margin-bottom: 8px; color: #333; font-weight: bold; }
                .explanation-section p { font-size: 14px; color: #666; line-height: 1.5; margin-bottom: 10px; }
                .example { margin-bottom: 15px; }
                .example h5 { font-size: 13px; margin-bottom: 8px; color: #333; font-weight: bold; }
                .example pre { background-color: #282c34; color: #abb2bf; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 12px; line-height: 1.4; }
                .example code { font-family: 'Courier New', monospace; }
                .bad-example h5 { color: #dc3545; }
                .good-example h5 { color: #28a745; }
                @media (max-width: 768px) {
                    .summary-stats { flex-direction: column; }
                    .stat-item { min-width: 100%; }
                    .check-meta { flex-direction: column; gap: 5px; }
                }
            </style>
        </head>
        <body>
            <div class='container'>
                <div class='header'>
                    <h1>{title}</h1>
                    <p>{generated_at}: {report_data['generated_at']}</p>
                </div>
                <div class='summary'>
                    <h2>{summary}</h2>
                    <div class='summary-stats'>
                        <div class='stat-item'>
                            <h3>{total_failed}</h3>
                            <ul><li>{report_data['total_failed']}</li></ul>
                        </div>
                        <div class='stat-item'>
                            <h3>{severity}</h3>
                            <ul>{severity_html}</ul>
                        </div>
                        <div class='stat-item'>
                            <h3>{iac_type}</h3>
                            <ul>{iac_type_html}</ul>
                        </div>
                    </div>
                </div>
                <div class='details'>
                    <h2>{details}</h2>
                    {''.join(details_html)}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
