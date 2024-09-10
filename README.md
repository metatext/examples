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
policy_list = [

        
        Policy(
            id="detect-direct-prompt-injection",
            description="",
            rules=[
                PolicyRule(
                    type=PolicyRuleType.JAILBREAK,
                    expected=PolicyRuleExpected.FAIL,
                    value="",
                    threshold=0.8,
                ),
            ],
            target=PolicyTarget.INPUT
        ),

        

        Policy(
            id="follow-negotiation",
            description="",
            rules=[
                PolicyRule(
                    type=PolicyRuleType.RUBRIC,
                    expected=PolicyRuleExpected.FAIL,
                    value="Você deve trabalhar somente as condições de pagamento disponíveis, 1x de R$300 ou 3x de R$ 100. Não aceite ou sugira outros termos. Sem descontos.",
                    threshold=0.3, # 0.0 very strict, 1.0 would be more lenient
                ),
            ],
            target=PolicyTarget.OUTPUT
        ),

        

        Policy(
            id="do-not-mention",
            description="",
            rules=[
                PolicyRule(
                    type=PolicyRuleType.CLASSIFIER,
                    expected=PolicyRuleExpected.FAIL,
                    value="Itaú, Bradesco, Santander", # class name or "class_name1, class_name2"
                    threshold=0.7
                ),
                PolicyRule(
                    type=PolicyRuleType.SIMILARITY,
                    expected=PolicyRuleExpected.FAIL,
                    value="concorrentes",
                    threshold=0.8
                ),
                PolicyRule(
                    type=PolicyRuleType.FACTUALITY,
                    expected=PolicyRuleExpected.FAIL,
                    value="Concorrentes do Nubank ou outras empresas de serviços financeiros",
                    threshold=0.8
                ),
            ],
            target=PolicyTarget.OUTPUT
        ),

        Policy(
            id="do-not-talk-about-politics",
            description="",
            rules=[
                PolicyRule(
                    type=PolicyRuleType.CLASSIFIER,
                    expected=PolicyRuleExpected.FAIL,
                    value="politics", # class name or "class_name1, class_name2"
                    threshold=0.5
                ),
            ],
            target=PolicyTarget.BOTH
        ),

        Policy(
            id="block-pii-exposure",
            description="",
            rules=[
                PolicyRule(
                    type=PolicyRuleType.PII,
                    expected=PolicyRuleExpected.FAIL,
                    value="email, telefone, endereço empresa, chave pix, senha, password", # add one or many labels
                    threshold=0.7
                ),
            ],
            target=PolicyTarget.OUTPUT
        )
    ]

for p in policy_list:
    client.add_policy(
            **p
    )
```


