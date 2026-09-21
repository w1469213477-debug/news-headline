# 新闻资讯

一个前后端分离的新闻阅读项目。前端使用 Vue 3，后端使用 FastAPI，从 MySQL 读取新闻与分类数据。

> **在线状态**：目前 [Cloudflare 页面](https://news-headline.w1469213477.workers.dev/)只部署了前端，后端和数据库尚未部署到公网。页面可以打开，但在线新闻、登录、收藏和历史记录无法正常获取；完整功能需要在本地同时启动前后端，并连接已有数据的 MySQL。

## 功能

- 按分类浏览新闻、分页加载、下拉刷新，查看详情和相关推荐。
- 注册、登录、个人资料、收藏和浏览历史。
- 中英文界面和主题设置。
- AI 问答界面：需另行配置第三方接口；当前实现由浏览器直接发起请求，不适合在公开站点中放入 API 密钥。

## 技术栈与目录

| 部分 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Vant、Pinia、Vue Router、vue-i18n、Axios |
| 后端 | FastAPI、SQLAlchemy 异步会话、aiomysql、bcrypt |
| 数据 | MySQL；Redis 用于新闻缓存，连接失败时查询会回退到 MySQL |

```text
news-headline-frontend/   Vue 前端及 Cloudflare 静态资源配置
news-headline-backend/    FastAPI 接口、模型和数据访问代码
```

## 本地运行

以下命令以 PowerShell 为例。需要先安装 Python、Node.js、MySQL，并准备好 `news_app` 数据库及新闻数据。仓库**未提供数据库迁移或种子数据**，不会在启动时自动建表或导入新闻。后端目前也没有锁定版本的 Python 依赖文件。

### 1. 启动后端

```powershell
cd news-headline-backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy aiomysql redis bcrypt

$env:ASYNC_DATABASE_URL = 'mysql+aiomysql://USER:PASSWORD@127.0.0.1:3306/news_app?charset=utf8mb4'
$env:ALLOWED_ORIGINS = 'http://localhost:5173'
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

将 `USER`、`PASSWORD` 换成自己的数据库账号信息。密码含有 `@`、`:` 等 URL 特殊字符时，需先进行 URL 编码。GitHub 当前版本的后端从**进程环境变量**读取 `ASYNC_DATABASE_URL`，不会自动加载 `.env`；`.env.example` 仅是配置示例。启动后可访问 `http://127.0.0.1:8000/docs` 查看接口文档。

Redis 目前默认连接 `localhost:6379`。没有 Redis 时，新闻缓存读写会报错并回退到数据库查询，但日志中会出现缓存连接错误。

### 2. 启动前端

另开一个 PowerShell 窗口，在项目根目录执行：

```powershell
cd news-headline-frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

默认 API 地址为 `http://127.0.0.1:8000`，可在 `.env.local` 中通过 `VITE_API_BASE_URL` 修改。前端开发地址以终端输出为准，通常为 `http://localhost:5173`。

## 主要接口

| 接口 | 用途 |
| --- | --- |
| `GET /api/news/categories` | 新闻分类 |
| `GET /api/news/list?categoryId=1&page=1&pageSize=10` | 分类新闻列表 |
| `GET /api/news/detail?id=1` | 新闻详情及相关推荐 |
| `/api/users/*` | 注册、登录、用户资料 |
| `/api/favorite/*` | 收藏 |
| `/api/history/*` | 浏览历史 |

收藏、历史和用户资料接口需要登录令牌。完整参数及响应以本地启动后的 `/docs` 为准。

## 部署与安全说明

- `news-headline-frontend/wrangler.jsonc` 只配置 Vite 构建产物 `dist` 的静态托管和单页应用回退，**不包含 FastAPI 或 MySQL**。
- 正式部署需另行提供可从公网访问的 HTTPS 后端，并在前端构建时设置 `VITE_API_BASE_URL`；后端的 `ALLOWED_ORIGINS` 也需包含前端域名。
- `VITE_` 开头的变量会进入浏览器构建产物。**不要**在公开部署中设置 `VITE_AI_API_KEY` 或其他密钥；若要开放 AI 问答，应改由后端代理第三方接口。
- 数据库连接串及其他敏感配置只应保存在私有环境变量中，不要提交 `.env`、数据库导出文件或用户数据到仓库。
