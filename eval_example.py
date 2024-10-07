
import os
from datetime import datetime
import logging
import json

from guard import Guard, Policy, PolicyRuleType, PolicyRuleExpected, PolicyTarget, PolicyRule
from policies import policy_list
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
policies_ids = "hallucination-fact-checking,detect-direct-prompt-injection"

parser.add_argument('--policy-ids', type=str, help='Specify the policy_ids to run.', default=policies_ids)

# Parse the command-line arguments
args = parser.parse_args()

# Init guard client
client = Guard(api_key=os.getenv("METATEXT_API_KEY"))

application_id = "YOUR_APPLICATION_NAME"
now = datetime.now()
time_of_day = now.strftime("%I:%M %p")
system_prompt = f"""
You're a helfull assistant. 

Current time is {time_of_day}. 

You work for ACME company. 

Act as a customer support agent to help user to negotiate their debt.

Current customer is John, their debit is due and you need to convince him to pay it following the payment conditions:

Conditions: 1x of R$300 or 3x of R$300.

Do not accept or suggest anything other them the conditions. Discounts are not allowed.
"""
model = "gpt-4o-mini"

client.set_application(id=application_id, name=application_id)

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
    policy_list = [p for p in policy_list if p.id in policy_ids]
    logger.info(f"Policies: {', '.join([p.id for p in policy_list])}")
    status_code, result = client.evaluate(messages, application_id=application_id, policy_list=[p.model_dump() for p in policy_list], policy_ids=[p.id for p in policy_list])

    logger.info(f"Evaluation result: {result.get('status')}")
    if result.get("status") == "fail":
        [logger.info(f"Policy violations: {json.dumps(r, indent=4)}") for r in result.get("policy_violations").items()]
    
        if result.get("correction"):
            correction_choices = result.get("correction").get("choices", [])
            messages[-1] = {"role": "assistant", "content": correction_choices[0].get("content")}
        
        logger.info(f"Correction: {json.dumps(messages[-1], indent=4)}")
