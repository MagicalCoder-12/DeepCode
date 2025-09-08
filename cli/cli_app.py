#!/usr/bin/env python3
"""
DeepCode - CLI Application Main Program
深度代码 - CLI应用主程序

🧬 Open-Source Code Agent by Data Intelligence Lab @ HKU
⚡ Revolutionizing research reproducibility through collaborative AI
"""

import os
import sys
import asyncio
import time
import json

# 禁止生成.pyc文件
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 导入MCP应用和工作流

from cli.workflows import CLIWorkflowAdapter
from cli.cli_interface import CLIInterface, Colors


class CLIApp:
    """CLI应用主类 - 升级版智能体编排引擎"""

    def __init__(self):
        self.cli = CLIInterface()
        self.workflow_adapter = CLIWorkflowAdapter(cli_interface=self.cli)
        self.app = None  # Will be initialized by workflow adapter
        self.logger = None
        self.context = None
        # Document segmentation configuration
        self.segmentation_config = {"enabled": True, "size_threshold_chars": 50000}

    async def initialize_mcp_app(self):
        """初始化MCP应用 - 使用工作流适配器"""
        # Workflow adapter will handle MCP initialization
        return await self.workflow_adapter.initialize_mcp_app()

    async def cleanup_mcp_app(self):
        """清理MCP应用 - 使用工作流适配器"""
        await self.workflow_adapter.cleanup_mcp_app()

    def update_segmentation_config(self):
        """Update document segmentation configuration in mcp_agent.config.yaml"""
        import yaml
        import os

        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mcp_agent.config.yaml",
        )

        try:
            # Read current config
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Update document segmentation settings
            if "document_segmentation" not in config:
                config["document_segmentation"] = {}

            config["document_segmentation"]["enabled"] = self.segmentation_config[
                "enabled"
            ]
            config["document_segmentation"]["size_threshold_chars"] = (
                self.segmentation_config["size_threshold_chars"]
            )

            # Write updated config
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            self.cli.print_status(
                "📄 Document segmentation configuration updated", "success"
            )

        except Exception as e:
            self.cli.print_status(
                f"⚠️ Failed to update segmentation config: {str(e)}", "warning"
            )

    async def process_input(self, input_source: str, input_type: str):
        """处理输入源（URL或文件）- 使用升级版智能体编排引擎"""
        try:
            # Update segmentation configuration before processing
            self.update_segmentation_config()

            self.cli.print_separator()
            self.cli.print_status(
                "🚀 Starting intelligent agent orchestration...", "processing"
            )

            # 显示处理阶段（根据配置决定）
            self.cli.display_processing_stages(0, self.cli.enable_indexing)

            # 使用工作流适配器进行处理
            result = await self.workflow_adapter.process_input_with_orchestration(
                input_source=input_source,
                input_type=input_type,
                enable_indexing=self.cli.enable_indexing,
            )

            if result["status"] == "success":
                # 显示完成状态
                final_stage = 8 if self.cli.enable_indexing else 5
                self.cli.display_processing_stages(
                    final_stage, self.cli.enable_indexing
                )
                self.cli.print_status(
                    "🎉 Agent orchestration completed successfully!", "complete"
                )

                # 显示结果
                self.display_results(
                    result.get("analysis_result", ""),
                    result.get("download_result", ""),
                    result.get("repo_result", ""),
                    result.get("pipeline_mode", "comprehensive"),
                )
            else:
                self.cli.print_status(
                    f"❌ Processing failed: {result.get('error', 'Unknown error')}",
                    "error",
                )

            # 添加到历史记录
            self.cli.add_to_history(input_source, result)

            return result

        except Exception as e:
            error_msg = str(e)
            self.cli.print_error_box("Agent Orchestration Error", error_msg)
            self.cli.print_status(f"Error during orchestration: {error_msg}", "error")

            # 添加错误到历史记录
            error_result = {"status": "error", "error": error_msg}
            self.cli.add_to_history(input_source, error_result)

            return error_result

    def display_results(
        self,
        analysis_result: str,
        download_result: str,
        repo_result: str,
        pipeline_mode: str = "comprehensive",
    ):
        """显示处理结果"""
        self.cli.print_results_header()

        # 显示流水线模式
        if pipeline_mode == "chat":
            mode_display = "💬 Chat Planning Mode"
        elif pipeline_mode == "comprehensive":
            mode_display = "🧠 Comprehensive Mode"
        else:
            mode_display = "⚡ Optimized Mode"
        print(
            f"{Colors.BOLD}{Colors.PURPLE}🤖 PIPELINE MODE: {mode_display}{Colors.ENDC}"
        )
        self.cli.print_separator("─", 79, Colors.PURPLE)

        print(f"{Colors.BOLD}{Colors.OKCYAN}📊 ANALYSIS PHASE RESULTS:{Colors.ENDC}")
        self.cli.print_separator("─", 79, Colors.CYAN)

        # 尝试解析并格式化分析结果
        try:
            if analysis_result.strip().startswith("{"):
                parsed_analysis = json.loads(analysis_result)
                print(json.dumps(parsed_analysis, indent=2, ensure_ascii=False))
            else:
                print(
                    analysis_result[:1000] + "..."
                    if len(analysis_result) > 1000
                    else analysis_result
                )
        except Exception:
            print(
                analysis_result[:1000] + "..."
                if len(analysis_result) > 1000
                else analysis_result
            )

        print(f"\n{Colors.BOLD}{Colors.PURPLE}📥 DOWNLOAD PHASE RESULTS:{Colors.ENDC}")
        self.cli.print_separator("─", 79, Colors.PURPLE)
        print(
            download_result[:1000] + "..."
            if len(download_result) > 1000
            else download_result
        )

        print(
            f"\n{Colors.BOLD}{Colors.GREEN}⚙️  IMPLEMENTATION PHASE RESULTS:{Colors.ENDC}"
        )
        self.cli.print_separator("─", 79, Colors.GREEN)
        print(repo_result[:1000] + "..." if len(repo_result) > 1000 else repo_result)

        # 尝试提取生成的代码目录信息
        if "Code generated in:" in repo_result:
            code_dir = (
                repo_result.split("Code generated in:")[-1].strip().split("\n")[0]
            )
            print(
                f"\n{Colors.BOLD}{Colors.YELLOW}📁 Generated Code Directory: {Colors.ENDC}{code_dir}"
            )

        # 显示处理完成的工作流阶段
        print(
            f"\n{Colors.BOLD}{Colors.OKCYAN}🔄 COMPLETED WORKFLOW STAGES:{Colors.ENDC}"
        )

        if pipeline_mode == "chat":
            stages = [
                "🚀 Engine Initialization",
                "💬 Requirements Analysis",
                "🏗️ Workspace Setup",
                "📝 Implementation Plan Generation",
                "⚙️ Code Implementation",
            ]
        else:
            stages = [
                "📄 Document Processing",
                "🔍 Reference Analysis",
                "📋 Plan Generation",
                "📦 Repository Download",
                "🗂️ Codebase Indexing",
                "⚙️ Code Implementation",
            ]

        for stage in stages:
            print(f"  ✅ {stage}")

        self.cli.print_separator()

    async def run_interactive_session(self):
        """运行交互式会话"""
        # 清屏并显示启动界面
        self.cli.clear_screen()
        self.cli.print_logo()
        self.cli.print_welcome_banner()

        # 初始化MCP应用
        await self.initialize_mcp_app()

        try:
            # 主交互循环
            while self.cli.is_running:
                self.cli.create_menu()
                choice = self.cli.get_user_input()

                if choice in ["q", "quit", "exit"]:
                    self.cli.print_goodbye()
                    break

                elif choice in ["u", "url"]:
                    url = self.cli.get_url_input()
                    if url:
                        await self.process_input(url, "url")

                elif choice in ["f", "file"]:
                    file_path = self.cli.upload_file_gui()
                    if file_path:
                        await self.process_input(f"file://{file_path}", "file")

                elif choice in ["t", "chat", "text"]:
                    chat_input = self.cli.get_chat_input()
                    if chat_input:
                        await self.process_input(chat_input, "chat")

                elif choice in ["h", "history"]:
                    self.cli.show_history()

                elif choice in ["c", "config", "configure"]:
                    # Sync current segmentation config from CLI interface
                    self.segmentation_config["enabled"] = self.cli.segmentation_enabled
                    self.segmentation_config["size_threshold_chars"] = (
                        self.cli.segmentation_threshold
                    )

                    self.cli.show_configuration_menu()

                    # Sync back from CLI interface after configuration changes
                    self.segmentation_config["enabled"] = self.cli.segmentation_enabled
                    self.segmentation_config["size_threshold_chars"] = (
                        self.cli.segmentation_threshold
                    )

                else:
                    self.cli.print_status(
                        "Invalid choice. Please select U, F, T, C, H, or Q.", "warning"
                    )

                # Ask whether to continue
                if self.cli.is_running and choice in ["u", "f", "t", "chat", "text"]:
                    if not self.cli.ask_continue():
                        self.cli.is_running = False
                        self.cli.print_status("Session ended by user", "info")

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Process interrupted by user{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Unexpected error: {str(e)}{Colors.ENDC}")
        finally:
            # Clean up resources
            await self.cleanup_mcp_app()


async def main():
    """Main function"""
    start_time = time.time()

    try:
        # Create and run CLI application
        app = CLIApp()
        await app.run_interactive_session()

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Application interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Application error: {str(e)}{Colors.ENDC}")
    finally:
        end_time = time.time()
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}⏱️  Total runtime: {end_time - start_time:.2f} seconds{Colors.ENDC}"
        )

        # Clean up cache files
        print(f"{Colors.YELLOW}🧹 Cleaning up cache files...{Colors.ENDC}")
        if os.name == "nt":  # Windows
            os.system(
                "powershell -Command \"Get-ChildItem -Path . -Filter '__pycache__' -Recurse -Directory | Remove-Item -Recurse -Force\" 2>nul"
            )
        else:  # Unix/Linux/macOS
            os.system('find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null')

        print(
            f"{Colors.OKGREEN}✨ Goodbye! Thanks for using DeepCode CLI! ✨{Colors.ENDC}"
        )


if __name__ == "__main__":
    asyncio.run(main())
