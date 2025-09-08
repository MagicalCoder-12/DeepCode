#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra-simplified LLM Response Logger
Focused on logging core content of LLM responses, with simple and easy-to-use configuration
"""

import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class SimpleLLMLogger:
    """Ultra-simplified LLM response logger"""

    def __init__(self, config_path: str = "mcp_agent.config.yaml"):
        """
        初始化日志记录器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.llm_config = self.config.get("llm_logger", {})

        # Return directly if disabled
        if not self.llm_config.get("enabled", True):
            self.enabled = False
            return

        self.enabled = True
        self._setup_logger()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Configuration file load failed: {e}, using default configuration")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "llm_logger": {
                "enabled": True,
                "output_format": "json",
                "log_level": "basic",
                "log_directory": "logs/llm_responses",
                "filename_pattern": "llm_responses_{timestamp}.jsonl",
                "include_models": ["claude-sonnet-4", "gpt-4", "o3-mini"],
                "min_response_length": 50,
            }
        }

    def _setup_logger(self):
        """设置日志记录器"""
        log_dir = self.llm_config.get("log_directory", "logs/llm_responses")

        # Create log directory
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Generate log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_pattern = self.llm_config.get(
            "filename_pattern", "llm_responses_{timestamp}.jsonl"
        )
        self.log_file = os.path.join(
            log_dir, filename_pattern.format(timestamp=timestamp)
        )

        print(f"📝 LLM Response Log: {self.log_file}")

    def log_response(self, content: str, model: str = "", agent: str = "", **kwargs):
        """
        记录LLM响应 - 简化版本

        Args:
            content: LLM响应内容
            model: 模型名称
            agent: Agent名称
            **kwargs: 其他可选信息
        """
        if not self.enabled:
            return

        # Check if should log
        if not self._should_log(content, model):
            return

        # Build log record
        log_entry = self._build_entry(content, model, agent, kwargs)

        # Write log
        self._write_log(log_entry)

        # Console display
        self._console_log(content, model, agent)

    def _should_log(self, content: str, model: str) -> bool:
        """检查是否应该记录"""
        # Check length
        min_length = self.llm_config.get("min_response_length", 50)
        if len(content) < min_length:
            return False

        # Check model
        include_models = self.llm_config.get("include_models", [])
        if include_models and not any(m in model for m in include_models):
            return False

        return True

    def _build_entry(self, content: str, model: str, agent: str, extra: Dict) -> Dict:
        """构建日志条目"""
        log_level = self.llm_config.get("log_level", "basic")

        if log_level == "basic":
            # Basic level: only log core content
            return {
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "model": model,
            }
        else:
            # Detailed level: include more information
            entry = {
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "model": model,
                "agent": agent,
            }
            # Add extra information
            if "token_usage" in extra:
                entry["tokens"] = extra["token_usage"]
            if "session_id" in extra:
                entry["session"] = extra["session_id"]
            return entry

    def _write_log(self, entry: Dict):
        """写入日志文件"""
        output_format = self.llm_config.get("output_format", "json")

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if output_format == "json":
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                elif output_format == "text":
                    timestamp = entry.get("timestamp", "")
                    model = entry.get("model", "")
                    content = entry.get("content", "")
                    f.write(f"[{timestamp}] {model}: {content}\n\n")
                elif output_format == "markdown":
                    timestamp = entry.get("timestamp", "")
                    model = entry.get("model", "")
                    content = entry.get("content", "")
                    f.write(f"**{timestamp}** | {model}\n\n{content}\n\n---\n\n")
        except Exception as e:
            print(f"⚠️ Log write failed: {e}")

    def _console_log(self, content: str, model: str, agent: str):
        """控制台简要显示"""
        preview = content[:80] + "..." if len(content) > 80 else content
        print(f"🤖 {model} ({agent}): {preview}")


# Global instance
_global_logger = None


def get_llm_logger() -> SimpleLLMLogger:
    """Get global LLM logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = SimpleLLMLogger()
    return _global_logger


def log_llm_response(content: str, model: str = "", agent: str = "", **kwargs):
    """便捷函数：记录LLM响应"""
    logger = get_llm_logger()
    logger.log_response(content, model, agent, **kwargs)


# Example usage
if __name__ == "__main__":
    # Test log recording
    log_llm_response(
        content="This is a test LLM response content to verify that the simplified logger functionality works correctly.",
        model="claude-sonnet-4-20250514",
        agent="TestAgent",
    )

    print("✅ Simplified LLM log test complete")
