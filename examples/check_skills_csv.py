# check_skills_csv.py
import pandas as pd
from pathlib import Path

csv_path = Path("models/skills_dataset.csv")
df = pd.read_csv(csv_path)

print("🔍 Checking skills dataset for duplicates...")
for role, skills in df.groupby('role'):
    skill_list = skills['skills'].values[0].split(';')
    print(f"\n{role}:")
    print(f"Skills: {skill_list}")
    print(f"Count: {len(skill_list)}")
    print(f"Duplicates: {[skill for skill in skill_list if skill_list.count(skill) > 1]}")