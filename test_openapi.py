# from openai import OpenAI

# client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key="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")

# response = client.chat.completions.create(
#     model="anthropic/claude-sonnet-4",
#     messages=[{"role": "user", "content": "Hello from Python!"}]
# )

# print(response.choices[0].message.content)

# import google.generativeai as genai
# import os

# # The client automatically picks up the GEMINI_API_KEY environment variable.
# # genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# genai.configure(api_key="AIzaSyAtRXYETGcVHyuKmcsocA1IcrTlqd26sng")
# model = genai.GenerativeModel('gemini-1.5-pro-latest') # You can also use other models like 'gemini-1.5-flash-latest'

# response = model.generate_content("Explain how a black hole is formed in a few sentences.")

# print(response.text)


# from openai import OpenAI

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key="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",
# )

# completion = client.chat.completions.create(
#   extra_headers={
#     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#   },
#   extra_body={},
#   model="anthropic/claude-sonnet-4",
#   messages=[
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "text",
#           "text": "What is in this moon?"
#         }
#       ]
#     }
#   ]
# )
# print(completion.choices[0].message.content)



# from openai import OpenAI

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1/chat/completions",
#   api_key="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",
# )

# completion = client.chat.completions.create(
#   extra_headers={
#     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#   },
#   extra_body={},
#   model="deepseek/deepseek-r1:free",
#   messages=[
#     {
#       "role": "user",
#       "content": "What is the meaning of life?"
#     }
#   ]
# )
# print(completion.choices[0].message.content)

import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek/deepseek-r1:free",
    "messages": [
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ]
}

llm_response = requests.post(API_URL, json=payload, headers=headers, timeout=10)

print(llm_response.json())