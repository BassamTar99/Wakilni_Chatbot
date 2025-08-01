
import re
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Load and parse chat log
pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4},\s*\d{1,2}:\d{2}:\d{2}\s*[AP]M)\]\s*([^:]+):\s*(.+)")
rows = []
with open(r"c:\Users\pc\Desktop\_chat.txt", 'r', encoding='utf-8') as f:
    for line in f:
        m = pattern.match(line)
        if m:
            ts, sender, msg = m.groups()
            rows.append({
                'timestamp_raw': ts,
                'sender': sender.strip(),
                'message': msg.strip()
            })

df = pd.DataFrame(rows)
df['timestamp'] = pd.to_datetime(df['timestamp_raw'], format='%d/%m/%Y, %I:%M:%S %p')
df = df.sort_values('timestamp').reset_index(drop=True)

# Use OpenAI to classify each message as question or answer
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_with_openai(msg):
    prompt = (
        f"Label the following chat message as either 'question' (problem/issue) or 'answer' (solution/help). "
        f"Return only the label.\nMessage: {msg}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a support assistant."}, {"role": "user", "content": prompt}],
            temperature=0
        )
        label = resp.choices[0].message.content.strip().lower()
        if 'question' in label:
            return 'question'
        elif 'answer' in label:
            return 'answer'
        else:
            return 'other'
    except Exception as e:
        print(f"OpenAI error: {e}")
        return 'other'

df['qa_label'] = df['message'].apply(classify_with_openai)

# Link each question to its next answer(s)
pairs = []
last_question = None
for idx, row in df.iterrows():
    if row['qa_label'] == 'question':
        last_question = row
    elif row['qa_label'] == 'answer' and last_question is not None:
        pairs.append({
            'question_timestamp': last_question['timestamp'],
            'question_sender': last_question['sender'],
            'question': last_question['message'],
            'answer_timestamp': row['timestamp'],
            'answer_sender': row['sender'],
            'answer': row['message']
        })
        last_question = None  # Only link first answer after question

# Save pairs to CSV for training
pairs_df = pd.DataFrame(pairs)
pairs_df.to_csv(r"c:\Users\pc\Desktop\chat_qa_pairs.csv", index=False)
print(pairs_df.head(10))
