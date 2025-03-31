USPL: Unified Schema Prompt Layer
==============================

🔐 原創證明
------------

本專案內含設計概念與原創技術證明文件，詳見：

📄 docs/USPL_Design_Technical_Proof_v1.1_TW.txt

該文件詳述 USPL 的技術背景、創作脈絡與應用價值，作為專利申請、學術發表與公開展示之原始創作依據。

📘 專案介紹
------------

USPL 是一個使用自然語言查詢結構化資料的 Python 原型系統，核心功能包括：

- 根據資料庫欄位綱要與用戶問題，自動產生 SQL 查詢語法（GPT-3.5-turbo）
- 執行 SQL 並獲得查詢結果
- 將查詢結果交由 GPT 生成自然語言回應
- 全流程模擬實務資料表、欄位結構與關聯查詢邏輯

🚀 使用方法
-----------

1. 建立 `.env` 檔案，填入你的 OpenAI API 金鑰：

   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

2. 執行主程式：

   python USPL.py

3. 查看輸出：
   - GPT 生成的 SQL
   - 查詢結果
   - 自然語言回覆

📦 需求套件
------------

- openai
- python-dotenv
- sqlite3（Python 標準庫）

安裝方式：

   pip install openai python-dotenv

📂 專案結構
------------

USPL/
├── USPL.py                                  # 主程式
├── .env                                     # API 金鑰設定（已加入 .gitignore）
├── .gitignore                               # 忽略機敏設定檔
├── README.md                                # 本說明文件
└── docs/
    └── USPL_Design_Technical_Proof_v1.1.txt # 技術原創證明檔

🧠 作者
--------

TSAI PEI LIN  
2025.04.01  
b131ab131a@gmail.com

---

## 📄 授權 License

本專案採用 [MIT License](LICENSE) 授權，歡迎自由使用、修改與發表。  
請保留原作者署名：TSAI PEI LIN。