import sqlite3
import openai
from dotenv import load_dotenv
import os

# 載入 .env 檔案中的環境變數
load_dotenv()

# 使用 API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

# 1. 定義模擬 SQL 資料
tableA = [
    {"id": 1, "name": "Alice", "dept_id": 101},
    {"id": 2, "name": "Bob", "dept_id": 102},
    {"id": 3, "name": "Charlie", "dept_id": 101},
]

tableB = [
    {"dept_id": 101, "dept_name": "Sales"},
    {"dept_id": 102, "dept_name": "Engineering"},
]

# 2. 讀取欄位資訊並生成資料庫綱要
tableA_columns = list(tableA[0].keys())
tableB_columns = list(tableB[0].keys())

tableA_schema = {
    "columns": tableA_columns,
    "primary_key": "id",
    "foreign_keys": {"dept_id": {"references": "tableB", "references_column": "dept_id"}},
}

tableB_schema = {
    "columns": tableB_columns,
    "primary_key": "dept_id",
    "foreign_keys": {},
}

# 3. 生成 prompt 給 GPT-3.5 Turbo
def generate_sql(question, tableA_schema, tableB_schema):
    prompt = f"""
    你是 SQL 生成器。
    請參照以下資料庫綱要生成正確的 SQL 語法。

    tableA 綱要: {tableA_schema}
    tableB 綱要: {tableB_schema}

    有主鍵外鍵跟參照表格的時候，請記得用 JOIN。

    用戶問題: {question}
    SQL:
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    
    return response.choices[0].message["content"].strip()


# 4. 利用生成的 SQL 對模擬資料執行查詢
def execute_sql(sql, tableA, tableB):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # 創建 tableA
    cursor.execute(
        f"""
        CREATE TABLE tableA (
            {', '.join([f'{col} TEXT' for col in tableA_schema['columns']])},
            PRIMARY KEY ({tableA_schema['primary_key']}),
            FOREIGN KEY (dept_id) REFERENCES tableB(dept_id)
        )
        """
    )
    for row in tableA:
        cursor.execute(
            f"""
            INSERT INTO tableA ({', '.join(row.keys())})
            VALUES ({', '.join(['?' for _ in row.values()])})
            """,
            list(row.values()),
        )

    # 創建 tableB
    cursor.execute(
        f"""
        CREATE TABLE tableB (
            {', '.join([f'{col} TEXT' for col in tableB_schema['columns']])},
            PRIMARY KEY ({tableB_schema['primary_key']})
        )
        """
    )
    for row in tableB:
        cursor.execute(
            f"""
            INSERT INTO tableB ({', '.join(row.keys())})
            VALUES ({', '.join(['?' for _ in row.values()])})
            """,
            list(row.values()),
        )
    
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return result

def extract_sql_from_response(gpt_response):
    try:
        start = gpt_response.index("{")
        end = gpt_response.rindex("}")
        return gpt_response[start:end+1].strip()
    except ValueError:
        # fallback: if no braces, return raw
        return gpt_response.strip()


# 5. 將查詢結果再丟一次 GPT，回答用戶問題
def answer_question(question, result):
    prompt = f"""
    用戶問題: {question}
    查詢結果: {result}

    請根據用戶問題和查詢結果回答用戶問題。
    答案:
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message["content"].strip()


# main 模擬用戶問題
question = "所有 Sales 部門的員工姓名?"

# 生成 SQL
raw_sql = generate_sql(question, tableA_schema, tableB_schema)
sql = extract_sql_from_response(raw_sql)
print(f"清洗後 SQL:\n{sql}")


# 執行 SQL 查詢
result = execute_sql(sql, tableA, tableB)
print(f"查詢結果: {result}")

# 回答用戶問題
answer = answer_question(question, result)
print(f"答案: {answer}")