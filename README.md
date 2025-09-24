# RoyaBot 📈

> 專為台灣股市數據分析設計的 Telegram 機器人

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

RoyaBot 是一個智能股票分析 Telegram 機器人，它能夠處理用戶上傳的 Excel 股票代碼文件，自動獲取歷史市場數據，計算技術指標（NATR），並返回完整的分析報告。

## ✨ 核心功能

- 🤖 **Telegram 機器人介面**：透過 Telegram 輕鬆互動
- 📊 **Excel 文件處理**：支援股票代碼清單上傳
- 📈 **市場數據獲取**：使用 Shioaji API 獲取台股歷史數據
- 📉 **技術指標計算**：自動計算 NATR（標準化平均真實範圍）
- ⚡ **高效數據處理**：基於 Polars 的快速數據處理
- 🐳 **Docker 容器化**：完整的容器化部署方案
- 🕐 **時區支援**：正確顯示台北時間

## 🚀 快速開始

### 環境需求

- Python 3.10+
- Docker 和 Docker Compose（推薦）
- 或者直接使用 uv 進行本地開發

### 1. 克隆專案

```bash
git clone <repository-url>
cd royabot
```

### 2. 環境變數設定

創建 `.env` 文件並配置以下變數：

```env
# Shioaji API 憑證
API_KEY=your_shioaji_api_key
SECRET_KEY=your_shioaji_secret_key

# Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token
```

### 3. 部署方式

#### 🐳 Docker 部署（推薦）

```bash
# 使用 Docker Compose 啟動
docker compose up -d

# 查看日誌
docker compose logs -f royabot

# 停止服務
docker compose down
```

#### 🔧 本地開發

```bash
# 安裝依賴
uv sync

# 運行機器人
uv run royabot
```

## 📁 專案結構

```
royabot/
├── src/royabot/
│   ├── __init__.py          # 套件入口點
│   ├── bot.py              # Telegram 機器人處理器
│   ├── config.py           # 環境配置管理
│   ├── data_processing.py  # 主要數據處理流水線
│   ├── fetcher.py          # 市場數據獲取器
│   ├── indicators.py       # 技術指標計算
│   └── util.py             # 工具函數
├── downloads/              # 文件下載目錄
├── data/                   # 數據存儲目錄
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile             # Docker 鏡像配置
└── pyproject.toml         # 專案配置
```

## 🔄 工作流程

1. **文件上傳**：用戶透過 Telegram 上傳包含股票代碼的 Excel 文件
2. **數據獲取**：系統自動從 Shioaji API 獲取歷史市場數據
3. **數據處理**：使用 Polars 進行高效數據處理和合併
4. **指標計算**：透過 TA-Lib 計算 NATR 技術指標
5. **結果返回**：處理後的 Excel 文件返回給用戶

## 🛠️ 技術棧

### 核心框架
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)**：Telegram Bot API 框架
- **[Shioaji](https://sinotrade.github.io/)**：台灣證券 API
- **[Polars](https://pola.rs/)**：高效數據處理框架

### 數據處理
- **[TA-Lib](https://github.com/mrjbq7/ta-lib)**：技術分析指標庫
- **[PyArrow](https://arrow.apache.org/docs/python/)**：高效數據序列化
- **[FastExcel](https://github.com/Rotbart/fastexcel)**：快速 Excel 處理

### 開發工具
- **[uv](https://github.com/astral-sh/uv)**：快速 Python 套件管理器
- **[Loguru](https://github.com/Delgan/loguru)**：結構化日誌記錄
- **[Pydantic](https://pydantic.dev/)**：數據驗證和設定管理

## 🔧 開發指令

### 套件管理
```bash
# 安裝依賴
uv sync

# 新增依賴
uv add <package-name>

# 運行機器人
uv run royabot
```

### Docker 指令
```bash
# 建構鏡像
docker build -t royabot .

# 運行容器
docker run --env-file .env -v $(pwd)/downloads:/app/downloads royabot

# 使用 Docker Compose
docker compose up -d           # 啟動服務
docker compose down           # 停止服務
docker compose logs -f royabot # 查看日誌
docker compose up --build -d  # 重建並啟動
```

## 📊 數據格式

### 輸入格式
- Excel 文件包含股票代碼列
- 支援台股代碼格式（例如：2330、0050）

### 輸出格式
- 包含原始數據的 Excel 文件
- 新增技術指標欄位（NATR）
- 按日期排序的歷史數據

## 🔐 安全注意事項

- API 金鑰和令牌儲存在 `.env` 文件中，請勿提交到版本控制
- 建議在生產環境中使用 Docker Secrets 管理敏感資訊
- 定期更新依賴套件以修復安全漏洞

## 📈 效能優化

- 使用 Polars 替代 Pandas 提高數據處理速度
- Parquet 格式儲存歷史數據，提升 I/O 效能
- Shioaji speed 擴展包（based58、ciso8601）提升 API 效能
- Docker 多階段構建優化鏡像大小

## 🤝 貢獻指南

1. Fork 此專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

此專案使用 MIT 授權條款。詳情請見 [LICENSE](LICENSE) 文件。

## 🙏 致謝

- [Shioaji](https://sinotrade.github.io/) - 提供台灣證券市場 API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - 優秀的 Telegram Bot 框架
- [Polars](https://pola.rs/) - 高效的數據處理引擎

---

**免責聲明**：本工具僅供學習和研究目的，不構成投資建議。使用者應自行承擔投資風險。