# Guard client example

`$ python eval_example.py`

```
INFO:root:Starting the application
INFO:root:User input: {
    "role": "user",
    "content": "Hi! I would like to create an investment account."
}
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:root:Assistant output: {
    "role": "assistant",
    "content": "Creating an investment account is a great step towards building your financial future! Here\u2019s a general guide on how to get started:\n\n### 1. Determine Your Investment Goals\n- **Purpose**: Are you saving for retirement, a house, or other goals?\n- **Time Horizon**: How long do you plan to invest? Short-term (1-3 years), medium-term (3-10 years), or long-term (10+ years)?\n- **Risk Tolerance**: Assess your comfort"
}
INFO:root:Evaluation result: FAIL
INFO:root:Policy violations:
{
    "policy_id": "greetings",
    "score": 0.931
}
INFO:root:Correction: {
    "role": "assistant",
    "content": "Hi, good evening! I'm happy to help you create an investment account with ACME company. Creating an investment account is a great step towards building your financial future! Here's a general guide on how to get started: ### 1. Determine Your Investment Goals - **Purpose**: Are you saving for retirement, a house, or other goals? - **Time Horizon**: How long do you plan to invest? Short-term (1-3 years), medium-term (3-10 years), or long-term (10+ years)? - **Risk Tolerance**: Assess your comfort"
}
```
