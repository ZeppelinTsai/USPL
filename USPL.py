import sqlite3
import openai
from dotenv import load_dotenv
import os
import re
import sys

# Load environment variables from .env file
load_dotenv()

# Use the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# 1. Define mock SQL data
tableA = [
    {"id": 1, "name": "Alice", "dept_id": 101},
    {"id": 2, "name": "Bob", "dept_id": 102},
    {"id": 3, "name": "Charlie", "dept_id": 101},
]

tableB = [
    {"dept_id": 101, "dept_name": "Sales"},
    {"dept_id": 102, "dept_name": "Engineering"},
]

# 2. Read column information and define database schemas
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

# 3. Generate prompt for GPT-3.5 Turbo
def generate_sql(question, tableA_schema, tableB_schema):
    prompt = f"""
    You are a SQL generator.
    Please generate a correct SQL query based on the following database schemas.
    If multiple queries are needed to answer the user's question, please generate them all.

    Schema of tableA: {tableA_schema}
    Schema of tableB: {tableB_schema}

    If there are primary keys, foreign keys, and reference tables, remember to use JOIN.

    User question: {question}
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

# 4. Execute the generated SQL query on mock data
def execute_sql(sql, tableA, tableB):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create tableA
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

    # Create tableB
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

# Extract SQL from GPT response (handling format issues)
def extract_sql_from_response(gpt_response):
    # Use regex to extract ALL SQL statements (ending with ;)
    matches = re.findall(r"(SELECT\s.+?;)", gpt_response, re.IGNORECASE | re.DOTALL)
    return [sql.strip() for sql in matches]


# 5. Send query result back to GPT to answer the user's question
def answer_question(question, result):
    prompt = f"""
    User question: {question}
    Query result: {result}

    Please answer the user's question based on the result above.
    Answer:
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message["content"].strip()


# 6. Generate Summary
def summarize_answers(question, answers):
    joined = "\n".join(answers)
    prompt = f"""
    User question: {question}
    The following are multiple answers based on different SQL results:

    {joined}

    Please summarize and combine these into a single cohesive answer.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message["content"].strip()
        



def main():
    # Simulate a user question
    question = sys.argv[1] if len(sys.argv) > 1 else input("Enter your question: ")
    # question = "List the names of employees in the Sales department; also show how many employees are in each department."

    # Generate SQL
    raw_sql = generate_sql(question, tableA_schema, tableB_schema)
    sql_list = extract_sql_from_response(raw_sql)

    answers = []

    if not sql_list:
        print("❌ No valid SQL statements found.")
    else:
        for idx, sql in enumerate(sql_list):
            print(f"\n[Query {idx + 1}] SQL:\n{sql}")
            result = execute_sql(sql, tableA, tableB)
            print(f"Query Result: {result}")
            answer = answer_question(question, result)
            print(f"Answer: {answer}")
            answers.append(answer)

        # Final Summary
        summary = summarize_answers(question, answers)
        print("\n🔎 Final Summary:\n", summary)

if __name__ == "__main__":
    main()