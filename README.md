# Guard client example

### Example run
```bash
pip install -r requirements.txt
python eval_example.py
```
#### Output
```python
INFO:eval:Starting the application
INFO:guard:Added policy: greetings Total: 1
User Input (Leave empty for default): 
INFO:eval:User input: {
    "role": "user",
    "content": "Hi! I would like to create an investment account."
}
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:eval:Assistant output: {
    "role": "assistant",
    "content": "Creating an investment account is a great step toward building wealth. Here\u2019s a basic guide on how to get started:\n\n### Steps to Create an Investment Account\n\n1. **Determine Your Investment Goals**:\n   - Are you saving for retirement, a home, education, or something else?\n   - This will guide your investment choices.\n\n2. **Choose the Type of Account**:\n   - **Brokerage Account**: For general investing; you can buy and sell stocks, bonds, and mutual funds"
}
INFO:httpx:HTTP Request: POST https://guard-api.metatext.ai/v1/evaluate "HTTP/1.1 200 OK"
INFO:eval:Evaluation result: FAIL
INFO:eval:Policy violations: 
{
    "policy_id": "greetings",
    "score": 0.96
}
INFO:eval:Correction: {
    "role": "assistant",
    "content": "Good morning! I'm happy to help you create an investment account with ACME company. Creating an investment account is a great step toward building wealth. Here's a basic guide on how to get started: ### Steps to Create an Investment Account 1. **Determine Your Investment Goals**: - Are you saving for retirement, a home, education, or something else? - This will guide your investment choices. 2. **Choose the Type of Account**: - **Brokerage Account**: For general investing; you can buy and sell stocks, bonds, and mutual funds"
}
```

## Init
```python
client = Guard(api_key=os.getenv("METATEXT_API_KEY"))
```

## Add application
```python
application_id = "YOUR_APPLICATION_ID"
system_prompt = f"You're a helfull assistant. Current time is {time_of_day}."
client.add_application(application_id=application_id, system_prompt=system_prompt)
```

## Add policy
```python
policy_1 = dict(
    policy_id="greetings",
    rule="""Always say greetings depending on the time of day:
    After 1:00 AM and before 12:00 PM, say "Good morning."
    After 12:00 PM and before 6:00 PM, say "Good afternoon."
    After 6:00 PM and before 9:00 PM, say "Good evening."
    After 9:00 PM and before 1:00 AM, say "Good night.""",
    examples=[dict(
        output_example="Saying 'Good morning!' when current time is after 6:00PM",
        type="FAIL"
        ),
        dict(
            output_example="Hi!",
            type="FAIL"
        ),
        dict(
            output_example="Hi, good evening!",
            type="PASS"
        )   
    ],
    override_response=None,# Could add a default response here
)

client.add_policy(
        **p
)
```


