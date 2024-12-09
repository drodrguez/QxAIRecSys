import pandas as pd
import ast


ruta = 'dataset/3_core/'

interactions = pd.read_csv(ruta + 'interaction.csv', sep='\t')
bigfive = pd.read_csv(ruta + 'bigfive.csv', sep='\t')
users = pd.read_csv(ruta + 'user.csv', sep='\t')
videos = pd.read_csv(ruta + 'video.csv', sep='\t')
tags_df = pd.read_csv(ruta + 'tag_map.csv', sep='\t')
test = pd.read_csv(ruta + 'test.csv', sep='\t')

def tag_map(tag_list, df):
    temp = []
    actual_list = ast.literal_eval(tag_list)
    for tag in actual_list:
        tag_row = df.loc[df['tag_id'] == tag, 'tag_content']
        tag_content = tag_row.iloc[0]
        temp.append(tag_content)

    return temp

def age_map(age_code):
    if age_code == 0:
        return "Young (<20 years)"
    elif 1 <= age_code <= 2:
        return "Young Adult (20-29 years)"
    elif 3 <= age_code <= 5:
        return "Adult (30-44 years)"
    elif 6 <= age_code <= 7:
        return "Older Adult (45-55 years)"
    elif age_code == 8:
        return "Senior (>55 years)"

    
def gender_map(gender_code):
    if gender_code == 0:
        return 'Female'
    
    return 'Male'

def education_map(education_code):
    if education_code <= 3:
        return "Senior high school"
    elif education_code == 4:
        return "Associate degree"
    elif education_code == 5:
        return "Bachelor's degree"
    elif education_code == 6:
        return "Master's degree"
    else:
        return "Other"

import json

data = list()

for row in test.iterrows():

    # Interaction data
    filter_row = row[1]
    user_id = filter_row['user_id']
    video_id = filter_row['video_id']
    rating = filter_row['rating']
    review = filter_row['review']
    video_tag = filter_row['video_tag']
    watch_again = filter_row['watch_again']

    # User data
    user = users[users['user_id'] == user_id]
    age = age_map(user['age'][user_id])
    gender = gender_map(user['gender'][user_id])
    education = education_map(user['education'][user_id])
    career = user['career'][user_id]
    income = user['income'][user_id]
    hobbies = user['hobby'][user_id]

    # Video data
    video = videos[videos['video_id'] == video_id]
    title = video['title'][video_id]
    tag_ids = video['tags'][video_id]
    category_tag = video['category']

    # Tags
    tags = tag_map(tag_ids, tags_df)

    info = {
        "user_id": user_id,
        "age_group": age,
        "gender": gender,
        "education": education,
        "hobbies": hobbies,
        "video_id": video_id,
        "video_title": title,
        "tags": tags,
        "rating": rating
    }

    data.append(info)

json_output = json.dumps(data, indent=4, ensure_ascii=False)
with open("output.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_output)
