# 🎯 SideHustleTracker

> 📊 一个现代化的收入追踪系统，帮助你更好地管理和分析副业收入

## ✨ 功能特性

- 📝 轻松记录每笔收入，包含日期、类型、金额和描述
- 📊 可视化数据展示，包括收入趋势图和分布图
- 📅 按周、月查看收入统计
- 💰 自动计算总收入和预测年收入
- 🏷️ 支持多种收入类型分类
- 🌙 优雅的深色主题界面

## 🛠️ 技术栈

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- Pinia - 状态管理
- Element Plus - UI 组件库
- Axios - HTTP 客户端
- ECharts - 数据可视化

### 后端
- FastAPI - 现代化的 Python Web 框架
- Uvicorn - ASGI 服务器
- Python 3.8+

## 🚀 快速开始

### 前端设置
```bash
cd frontend
npm install
npm run dev
```

### 后端设置
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

## 📦 项目结构
```
SideHustleTracker/
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/           # API 配置
│   │   ├── components/    # Vue 组件
│   │   ├── store/         # Pinia 状态管理
│   │   ├── views/         # 页面视图
│   │   └── App.vue        # 根组件
│   └── package.json
│
└── backend/               # 后端项目
    ├── routes/           # API 路由
    ├── models/          # 数据模型
    ├── data/           # JSON 数据存储
    └── main.py        # 主应用入口
```

## 🌐 API 端点

- GET `/api/incomes` - 获取所有收入记录
- POST `/api/incomes` - 创建新收入记录
- PUT `/api/incomes/{id}` - 更新收入记录
- DELETE `/api/incomes/{id}` - 删除收入记录

## 🤝 贡献指南

欢迎提交 Issues 和 Pull Requests 来帮助改进这个项目！

## 📄 许可证

[MIT License](LICENSE)

## 👨‍💻 作者

MilesSG

---
⭐️ 如果这个项目对你有帮助，欢迎给它一个星标！ 