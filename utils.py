import openai
def call_llm(messages):
  response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    max_tokens=1000
  )
  return response.choices[0].message.content