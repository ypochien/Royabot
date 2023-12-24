## 安裝套件

要安裝所需的套件，請按照以下步驟進行操作：

1. 開啟終端機並導航到專案目錄。
2. 執行以下命令以安裝所需的套件：

    ```bash
    pip install flit
    ```
    ```bash
    flit install -s
    ```

3. 等待安裝過程完成。
4. 編輯 .env
    
    ```
    API_KEY=<Shioaji API Key>
    SECRET_KEY=<Shioaji Secret Key>
    TELEGRAM_TOKEN=<Telegram Bot Token>
    ```
4. 執行程式
    
    ```bash
    python -m royabot.bot
    ```

現在，您已經成功安裝了所需的套件，可以開始進行開發工作了。
