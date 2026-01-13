# Open MCP Servers Market 🚀

发现、筛选并连接最好的 Model Context Protocol (MCP) 服务。

[查看在线演示](https://three-water666.github.io/open-mcp-servers-market/) 🚀

## 🌟 项目简介

**Open MCP Servers Market** 是一个自动化的 MCP 服务导航站。它汇集了来自官方和社区的最全 MCP 服务列表，提供便捷的搜索、分类筛选以及开源/非开源标记，帮助开发者快速找到所需的上下文协议工具。

## ✨ 功能特点

- 🔍 **全量搜索**：支持对服务名称和描述的实时全文搜索。
- 🛡️ **双源合一**：整合了 `official` (官方参考实现) 和 `awesome` (社区精选) 两大主流来源。
- 🏷️ **多维筛选**：支持按编程语言、应用场景 (Scopes)、运行平台 (Platforms) 以及是否官方认证进行筛选。
- 🔓 **开源识别**：自动识别项目是否开源，并提供直接跳转到源码或官网的链接。
- 🔄 **全自动更新**：利用 GitHub Actions 每天自动同步上游仓库，确保数据永远最新。
- 📱 **响应式设计**：现代化的 UI 界面，完美适配桌面端和移动端。

## 🛠️ 技术实现

- **前端**：Vue 3 (Composition API) + Tailwind CSS + Font Awesome。
- **后端脚本**：Python 3 + `requests` + `re` (正则表达式解析 Markdown)。
- **自动化**：GitHub Actions 定时任务，每日 UTC 0:00 自动触发数据转换与部署。

## 🚀 快速开始

### 本地开发

1. **克隆仓库**：
   ```bash
   git clone https://github.com/three-water666/open-mcp-servers-market.git
   cd open-mcp-servers-market
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **运行数据转换脚本**：
   ```bash
   python convert_mcp_lists.py
   ```

4. **启动本地服务器**：
   ```bash
   # 使用 Python 快速启动
   python3 -m http.server 8000
   ```
   访问 `http://localhost:8000` 即可预览。

## 📦 自动化部署说明

本项目已经配置好了 GitHub Actions，无需手动干预数据更新：

1. **数据源**：脚本会自动从 `modelcontextprotocol/servers` 和 `punkpeye/awesome-mcp-servers` 获取最新 README。
2. **定时任务**：每天北京时间早上 8:00 自动运行。
3. **部署分支**：自动生成的静态文件会推送到 `gh-pages` 分支。

## 🤝 贡献

如果您发现数据有误或有更好的建议，欢迎提交 Issue 或 Pull Request。

---

**Open MCP Servers Market** - 让 MCP 服务触手可及。
