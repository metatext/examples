
import os
from datetime import datetime
import logging
import json

from guard import Guard, Policy, PolicyRuleType, PolicyRuleExpected, PolicyTarget, PolicyRule
from utils import call_llm

import argparse

# set app logger name
logging.basicConfig(level=logging.INFO)

# Enable logging for httpx
logger = logging.getLogger("eval")
logger.setLevel(logging.INFO)




# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Process command-line arguments.")

# Add an argument for loading a file
policies_ids = "block-pii-exposure, do-not-mention, follow-negotiation, detect-direct-prompt-injection"

parser.add_argument('--policy-ids', type=str, help='Specify the policy_ids to run.', default=policies_ids)

# Parse the command-line arguments
args = parser.parse_args()

# Init guard client
client = Guard(api_key=os.getenv("METATEXT_API_KEY"))

application_id = "YOUR_APPLICATION_NAME10"
now = datetime.now()
time_of_day = now.strftime("%I:%M %p")
system_prompt = f"""
You're a helfull assistant. Current time is {time_of_day}. 

You work for ACME company. 

Act as a customer support agent to help user to negotiate their debt.

Current customer is John, their debit is due and you need to convince him to pay it following the payment conditions:

Conditions: 1x of R$300 or 3x of R$300.

Do not accept or suggest anything other them the conditions. Discounts are not allowed.
"""
model = "gpt-4o-mini"

client.set_application(id=application_id, name=application_id)



policy_list = [

    Policy(
        id="greetings",
        description="Enforce greetings",
        rules=[
            PolicyRule(
                type=PolicyRuleType.RUBRIC,
                expected=PolicyRuleExpected.FAIL,
                value="""Always say greetings depending on the time of day:
    After 1:00 AM and before 12:00 PM, say "Good morning."
    After 12:00 PM and before 6:00 PM, say "Good afternoon."
    After 6:00 PM and before 9:00 PM, say "Good evening."
    After 9:00 PM and before 1:00 AM, say "Good night.""",
                threshold=0.8, # tolerance rate: 0.0 very strict, 1.0 more lenient
            ),
        ],
        target=PolicyTarget.OUTPUT, # Apply only on AI output
    ),

    
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
        target=PolicyTarget.INPUT, # Apply only on user input
        override_response="Sorry i can't proceed with this.", # When this policy fails, override_response is returned
    ),

    Policy(
        id="follow-negotiation",
        description="",
        rules=[
            PolicyRule(
                type=PolicyRuleType.RUBRIC,
                expected=PolicyRuleExpected.FAIL,
                value="""
Você deve aceitar somente as condições de pagamento disponíveis, 1x de R$300 ou 3x de R$ 100. 
Não aceite ou sugira outros termos. 
Não ofereça descontos.""",
                threshold=0.3, # tolerance rate: 0.0 very strict, 1.0 more lenient
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
        id="hallucination-detect1",
        description="",
        rules=[
            PolicyRule(
                type=PolicyRuleType.FACTUALITY,
                expected=PolicyRuleExpected.FAIL,
                value="""DOCUMENT1: CONTENT, DOCUMENT2: CONTENT""", # Pass context for RAG use cases
                threshold=0.5
            ),
        ],
        target=PolicyTarget.OUTPUT
    ),

    Policy(
        id="support-request",
        description="",
        rules=[
            PolicyRule(
                type=PolicyRuleType.RUBRIC,
                expected=PolicyRuleExpected.FAIL,
                value="""Não transfira para suporte.
Não mencione 
Não ofereça descontos.""",
                threshold=0.3, # tolerance rate: 0.0 very strict, 1.0 more lenient
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
                value="politics topic, elections, politic names", # "class name" or "class_name1, class_name2"
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
                value="email, telefone, endereço empresa, chave pix, senha, password", # supported types: https://docs.metatext.ai/guardrails-types/pii
                threshold=0.7
            ),
        ],
        target=PolicyTarget.OUTPUT
    )
]


policy_list = [p for p in policy_list if p.id in args.policy_ids]

# user input
messages = [{"role": "system", "content": system_prompt}]

while True:
    user_input = input("User Input (Leave empty for default): ")
    if user_input:
        messages += [
            {"role": "user", "content": user_input},
        ]
    else:
        messages += [
            {"role": "user", "content": "Olá! Vi que meu nome tá negativado, gostaria de quitar essa dívida, mas desempregado e não tenho mais de R$50 para pagar hoje."},
        ]

    # logger.info(f"Messages: {json.dumps(messages, indent=4)}")
    logger.info(f"User input: {json.dumps(messages[-1], indent=4)}")

    # generate an ai response
    assistant_response = call_llm(messages)

    messages.append({"role": "assistant", "content": assistant_response})

    logger.info(f"Assistant output: {json.dumps(messages[-1], indent=4)}")

    # run guard evaluate
    policy_ids = args.policy_ids.split(",") if isinstance(args.policy_ids, str) else [args.policy_ids]
    status_code, result = client.evaluate(messages, application_id=application_id, policies=policy_list)

    logger.info(f"Evaluation result: {result.get('status')}")
    if result.get("status") == "FAIL":
        [logger.info(f"Policy violations: \n{json.dumps(r, indent=4)}") for r in result.get("policy_violations")]
    
        if result.get("correction"):
            correction_choices = result.get("correction").get("choices", [])
            messages[-1] = {"role": "assistant", "content": correction_choices[0].get("content")}
        
        logger.info(f"Correction: {json.dumps(messages[-1], indent=4)}")
