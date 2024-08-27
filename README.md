# Guard client example

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

### Example run

```python
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
