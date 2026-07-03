import os
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

db = SQLDatabase.from_uri("sqlite:///insights.db")

print("DATABASE INFO")

print("Database Daialect:", db.dialect)
print("Available Tables:", db.get_usable_table_names())

schema = db.get_table_info(
     table_names=["transport_logistics"]
)
print(schema)

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)


user_question = input("Which vehicle type from our logistics network consumes the most fuel on average?> ")
def generated_sql(user_question, schema):
    sql_prompt = f"""

You are an expert SQL analyst.

Read the question carefully.

Think about:

- Is the user asking for an average?
- Is grouping required?
- Is sorting required?
- Is LIMIT needed?

Then generate ONE SQLite query.

Database schema:

{schema}

User Question:
{user_question}

Rules:
1. Return ONLY SQL.
2. Do NOT explain anything.
3. Use aggregate functions (AVG, SUM, COUNT, etc.) whenever the question asks for averages, totals, highest, lowest, etc.
4. Use GROUP BY whenever aggregation by category is required.
5. Use ORDER BY DESC and LIMIT 1 when the question asks for the highest value.
6. Only use tables and columns from the schema.

SQL:
"""
    return llm.invoke(sql_prompt).content

def clean_markdown(sql):
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def validate_sql(sql, schema):
    
    forbidden = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE"
    ]

    upper_sql = sql.upper()

    for keyword in forbidden:
        if keyword in upper_sql:
            raise ValueError(f"Unsafe SQL detected: {keyword}")

    return sql
   

raw_output = generated_sql(user_question, schema)

clean_sql = clean_markdown(raw_output)

validated_sql = validate_sql(clean_sql, schema)


try:
    result = db.run(validated_sql)

    print("RAW DATABASE RESULTS:")
    print(result)

except Exception as e:
    print("\nSQL Execution Error:")
    print(e)
    exit()

answer_prompt = f"""
You are a data analyst.

User Question:
{user_question}

SQL Query:
{validated_sql}

SQL Result:
{result}
Explain the answer in simple English.
"""
final_answer = llm.invoke(answer_prompt).content

print("FINAL ANSWER")

print(final_answer)
