import json

# Necesita el output de context.py
with open("output.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)


from groq import Groq

client = Groq(
        api_key="YOUR_GROQ_KEY"
    )

with open("reviews.txt", "a") as file:
    for i in range(len(data)):
        prompt = f"""
        Put yourself in the role of the reviewer, create ONE review based on the context provided. Return the review as a string. Only return your review, nothing else.

        Context:
        {data[i]}
        """

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {'role': 'user',
                 'content': prompt}
            ],
            temperature=0,
            max_tokens=50,
            top_p=0,
            stream=True,
            stop=None,
        )

        review = "" 
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            review += content 

        file.write(review + "\n") 