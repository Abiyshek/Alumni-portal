#!/usr/bin/env python
"""Test script to verify alumni data extraction"""

import pandas as pd

df = pd.read_csv('dataset/alumni_people_from_departmant.csv')
print(f"Total rows in CSV: {len(df)}")
print(f"Columns: {list(df.columns)}\n")

alumni_list = []

for idx, row in df.iterrows():
    alumni_id = f"ALUM{str(idx + 1).zfill(3)}"
    
    # Extract from correct columns
    name = str(row['0']).strip() if pd.notna(row.get('0')) else "Unknown"
    title = str(row.get('title', '')).strip() if pd.notna(row.get('title')) else ''
    company = str(row.get('company', '')).strip() if pd.notna(row.get('company')) else ''
    linkedin = str(row.get('LINK', '')).strip() if pd.notna(row.get('LINK')) else ''
    
    # Skip rows with empty names
    if not name or name == 'nan' or name == 'Unknown':
        continue
    
    # Generate engagement score based on index
    engagement_score = round(0.65 + (idx % 35) / 100.0, 2)
    
    # Estimate graduation year (vary from 2005-2023)
    grad_year = 2005 + (idx % 20)
    
    alumni_list.append({
        'id': alumni_id,
        'name': name,
        'company': company,
        'role': title,
        'gradYear': grad_year,
        'engagementScore': engagement_score,
        'linkedin_url': linkedin
    })

print(f"✓ Extracted {len(alumni_list)} valid alumni\n")
print("First 10 alumni:")
for alum in alumni_list[:10]:
    print(f"  {alum['id']}: {alum['name']} - {alum['company']} ({alum['role']}) - Score: {alum['engagementScore']}")
