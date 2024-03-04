import sqlite3
import google.generativeai as genai
import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("gemini_api_key"))

def  get_gemini_response(question,prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0],question])
    return response.text

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if len(rows) > 1 or len(rows[0]) > 1:
        columns = [description[0] for description in cur.description]
        data = pd.DataFrame(rows, columns=columns)
        st.dataframe(data)
    else:
        st.write(rows[0][0])
    conn.commit()
    conn.close()
    return rows


prompt=["""
You are an expert in converting English questions to SQL query!
Pay attention to use CURDATE() function to get the current date, if the question involves "today".
The SQL database has the name rewardola and has the following tables - coupons , freq , reward_history ,
reward , store_address , store_category , store , user_store_visit , users .
Also the sql code should not have ``` in beginning or end and sql word in output.
\n\nFor example,\nExample 1 - How many users are in data ?,the SQL commond will be something like this 
SELECT COUNT(*) AS num_users FROM users;
\nExample 2 - Which users didn't redeem any offers?,the SQL commond will be something like this 
SELECT id as user_id,first_name as user_name
FROM users
WHERE NOT EXISTS (select user_id from reward_history WHERE users.id = reward_history.user_id);
\nExample 3 - Which offers are getting redeemed and how many times (highest to the lowest includingzero redeemed),the SQL commond will be something like this 
SELECT rh.reward_id,re.title,COUNT(rh.reward_id) AS count
FROM reward_history AS rh
JOIN reward AS re ON rh.reward_id = re.id
GROUP BY rh.reward_id
ORDER BY count DESC;
\nExample 4 - Which customers downloaded the app (store unlocked) but had no activity after that?,the SQL commond will be something like this 
SELECT user_id,store_id FROM store_reward_program WHERE user_id NOT IN (SELECT user_id FROM reward_history);
\nExample 5 - Which customers had activity after the app download?,the SQL commond will be something like this 
SELECT user_id,store_id FROM store_reward_program WHERE user_id IN (SELECT user_id FROM reward_history);
\nExample 6 - How many times a user had an activity for a store?,the SQL commond will be something like this 
SELECT user_id, store_id, COUNT(*) AS activity_count FROM user_store_visit GROUP BY user_id, store_id;
\nExample 7 - Which users had an activity in 15 days?,the SQL commond will be something like this 
SELECT user_id FROM reward_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 15 DAY);
\nExample 8 - Which users had an activity in 30 days?,the SQL commond will be something like this 
SELECT user_id FROM reward_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY);
\nExample 9 - Which users didn't have activity in 15 days?,the SQL commond will be something like this 
SELECT DISTINCT user_id FROM users WHERE user_id NOT IN (SELECT DISTINCT user_id FROM reward_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 15 DAY));
\nExample 10 - Which users didn't have activity in 30 days?,the SQL commond will be something like this 
SELECT DISTINCT user_id FROM users WHERE user_id NOT IN (SELECT DISTINCT user_id FROM reward_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY));
\nExample 11 - Which users redeemed which offer and when?,the SQL commond will be something like this 
SELECT user_id ,reward_id , type as reward_type , created_at as time FROM reward_history ;
"""]




st.set_page_config(page_title="AI Analytics")
st.header("Gemini App to retrive SQL Data")

question=st.text_input("Input:",key="input")
submit=st.button('Send ⬆️')

if submit:
    response = get_gemini_response(question, prompt)
    st.subheader("The Response is")
    data = read_sql_query(response, "rewardola.db")
