# BYTEROVER MCP HANDBOOK

> **DeepCode Multi-Agent AI Research Engine**  
> *Open-Source Code Generation & Research Automation Platform*

---

## 📋 Layer 1: System Overview

### Purpose
DeepCode is an **AI-powered development platform** that automates code generation and implementation tasks through **multi-agent systems**. The platform transforms research papers, natural language descriptions, and technical documentation into **production-ready code**, enabling researchers and developers to focus on innovation rather than implementation details.

### Tech Stack
- **Python 3.13** - Core runtime environment
- **Streamlit** - Web interface framework
- **AsyncIO** - Asynchronous task management
- **Model Context Protocol (MCP)** - Agent communication standard
- **Ollama** - Local AI model hosting (`gpt-oss:20b`)
- **PyYAML** - Configuration management
- **Markdown/PDF Processing** - Document analysis pipeline
- **Git Integration** - Repository management and cloning

### Architecture Pattern
**Multi-Agent Orchestration Architecture** with:
- **Central Orchestrating Agent** - Strategic decision making and workflow coordination
- **Intent Understanding Agent** - Semantic analysis and requirement extraction
- **Document Parsing Agent** - Research paper and technical document processing
- **Code Planning Agent** - Architecture design and technology stack optimization
- **Code Reference Mining Agent** - Repository discovery and framework analysis
- **Code Indexing Agent** - Knowledge graph building and semantic relationships
- **Code Generation Agent** - Implementation synthesis and testing

### Key Technical Decisions
- **Privacy-First Local Processing** - All AI operations via local Ollama server
- **Document Segmentation** - Intelligent handling of large research papers (50k+ chars)
- **Windows Compatibility** - Enhanced cross-platform MCP server support
- **Tool Calling Integration** - Native support for complex agent interactions

---

## 🗺️ Layer 2: Module Map

### Core Modules

#### 🎯 **Orchestration Layer** (`cli/`, `workflows/`)
- **CLI Interface** (`cli/cli_app.py`, `cli/cli_interface.py`) - Interactive terminal experience
- **Workflow Adapter** (`cli/workflows.py`) - Agent coordination and execution
- **Web Interface** (`ui/streamlit_app.py`, `ui/layout.py`) - Modern web dashboard

#### 🧠 **Agent Core** (`tools/`, `prompts/`)
- **MCP Servers** (`tools/`) - Specialized agent implementations
  - `code_implementation_server.py` - Code generation hub
  - `code_reference_indexer.py` - Intelligent code search
  - `document_segmentation_server.py` - Smart document analysis
  - `pdf_downloader.py` - Document processing
  - `git_command.py` - Repository management
- **Prompt System** (`prompts/code_prompts.py`) - Agent instruction templates

#### 📄 **Processing Engine** (`utils/`)
- **File Processor** (`utils/`) - Document encoding and conversion
- **Dialogue Logger** (`utils/`) - Conversation and process tracking
- **Memory Management** - Context engineering and storage

#### ⚙️ **Configuration Layer**
- **MCP Configuration** (`mcp_agent.config.yaml`) - Agent and server settings
- **Secrets Management** (`mcp_agent.secrets.yaml`) - API keys and credentials
- **Schema Validation** (`schema/`) - Configuration validation

### Data Layer
- **Local Knowledge Graph** - Code relationships and patterns
- **Document Segments** - Intelligent paper decomposition
- **Repository Index** - Codebase analysis and search
- **Process History** - Execution tracking and logging

### Utilities
- **Encoding Detection** - Automatic file format handling
- **PDF Conversion** - Research paper processing
- **Git Operations** - Repository cloning and analysis
- **Progress Tracking** - Real-time status updates

---

## 🔗 Layer 3: Integration Guide

### APIs & Interfaces

#### 🌐 **Web Interface** (Port 8501)
```bash
streamlit run ui/streamlit_app.py
# Access: http://localhost:8501
```
- **File Upload** - PDF, DOCX, TXT, HTML document processing
- **URL Input** - Research paper and documentation URLs
- **Real-time Progress** - Live agent execution tracking
- **Interactive Results** - Code preview and download

#### 🖥️ **CLI Interface**
```bash
python cli/main_cli.py
# Interactive terminal menu system
```
- **Multi-input Support** - URLs, files, chat requirements
- **Configuration Management** - Document segmentation settings
- **History Tracking** - Previous execution records
- **Progress Visualization** - Terminal-based status display

#### 🔧 **MCP Server Endpoints**
- **Ollama API** - `http://localhost:11434/v1` (Local AI processing)
- **Code Implementation** - File operations and execution
- **Document Segmentation** - Intelligent content analysis
- **Reference Indexing** - Code pattern search and discovery

### Configuration Files

#### 📋 **mcp_agent.config.yaml**
```yaml
# Core agent configuration
anthropic: null
openai:
  default_model: "gpt-oss:20b"  # Local model
document_segmentation:
  enabled: true
  size_threshold_chars: 50000
execution_engine: asyncio
```

#### 🔐 **mcp_agent.secrets.yaml**
```yaml
# Local development setup
openai:
  api_key: "ollama"
  base_url: "http://localhost:11434/v1"
```

### External Dependencies
- **Ollama Server** - Local AI model hosting
- **Git** - Repository cloning and management
- **Python Environment** - Core runtime and dependencies
- **Optional: LibreOffice** - Advanced document conversion

---

## 🛠️ Layer 4: Extension Points

### Design Patterns

#### 🎭 **Multi-Agent Pattern**
```python
# Central orchestration with specialized agents
class CLIWorkflowAdapter:
    def __init__(self, cli_interface):
        self.agents = {
            'orchestrator': CentralAgent(),
            'parser': DocumentAgent(),
            'planner': PlanningAgent(),
            'generator': CodeAgent()
        }
```

#### 🔧 **MCP Server Pattern**
```python
# Standardized tool integration
mcp:
  servers:
    code-implementation:
      command: python
      args: [tools/code_implementation_server.py]
      env: {PYTHONPATH: .}
```

#### 📄 **Document Segmentation Pattern**
```python
# Intelligent content processing
def update_segmentation_config(self):
    config["document_segmentation"] = {
        "enabled": True,
        "size_threshold_chars": 50000
    }
```

### Customization Areas

#### 🎯 **Agent Specialization**
- **Custom Prompts** - Modify `prompts/code_prompts.py` for domain-specific instructions
- **New Agent Types** - Add specialized agents for specific programming languages
- **Workflow Customization** - Extend `workflows/` for custom processing pipelines

#### 📊 **Processing Configuration**
- **Document Thresholds** - Adjust segmentation limits for different document types
- **Model Selection** - Switch between local AI models via configuration
- **Output Formats** - Customize code generation templates and structures

#### 🔍 **Tool Integration**
- **Custom MCP Servers** - Add new tools for specialized tasks
- **API Extensions** - Integrate additional web services and databases
- **Local Services** - Connect to custom development environments

### Extension Examples

#### 🌐 **Web Framework Integration**
```python
# Add React/Vue.js frontend generation
class WebFrameworkAgent:
    def generate_frontend(self, requirements):
        # Custom web development logic
        pass
```

#### 🗄️ **Database Integration**
```python
# Add database schema generation
class DatabaseAgent:
    def generate_schema(self, requirements):
        # Custom database design logic
        pass
```

#### 🧪 **Testing Framework**
```python
# Enhanced test generation
class TestingAgent:
    def generate_comprehensive_tests(self, codebase):
        # Advanced testing strategies
        pass
```

---

## 📚 Implementation Notes

### Recent Enhancements
- **Document Segmentation v1.2.0** - Intelligent large document processing
- **Windows Compatibility** - Enhanced MCP server reliability
- **Local Privacy** - Complete offline operation capability
- **Tool Calling Support** - Advanced agent interaction patterns

### Development Workflow
1. **Configuration** - Set up local Ollama and MCP servers
2. **Input Processing** - Document analysis and requirement extraction
3. **Agent Orchestration** - Multi-agent workflow execution
4. **Code Generation** - Implementation with testing and documentation
5. **Quality Assurance** - Validation and error handling

### Best Practices
- **Local-First Development** - Prioritize privacy and offline capability
- **Modular Architecture** - Maintain clean separation between agents
- **Error Handling** - Robust fallback mechanisms for agent failures
- **Performance Monitoring** - Track processing times and resource usage

---

*Generated by Byterover MCP Tools - AI Agent Navigation System*