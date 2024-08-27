
from datetime import datetime
from guard import Guard
import openai

client = Guard(api_key=os.getenv("METATEXT_API_KEY"))

def call_llm(messages):
  response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    max_tokens=100
  )
  return response.choices[0].message.content

# # read application from file
# with open('application.json') as f:
#     application = json.loads(f.read())
#     application_id = application.get("application_id")
#     system_prompt = application.get("system_prompt")
#     client.add_application(application_id=application_id, system_prompt=system_prompt)
    
#     for p in application.get("policies", []):
#         client.add_policy(
#             policy_id=p.get("id"),
#             rule=p.get("rule"),
#             examples=[e for e in p.get("example")]
#         )

#     logging.info(f"Added {application.get("policies", [])} policies")

# set the current time
now = datetime.now()
time_of_day = now.strftime("%I:%M %p")

# set up the application first
application_id = "YOUR_APPLICATION_ID"
system_prompt = f"You're a helfull assistant. Current time is {time_of_day}. You work for ACME company. Act as a customer support agent to help users to create an investment account."
client.add_application(application_id=application_id, system_prompt=system_prompt)

policy_1 = dict(
    policy_id="greetings",
    rule="""Always say greetings depending on the time of day:
    After 1:00 AM and before 12:00 PM, say "Good morning."
    After 12:00 PM and before 6:00 PM, say "Good afternoon."
    After 6:00 PM and before 9:00 PM, say "Good evening."
    After 9:00 PM and before 1:00 AM, say "Good night.""",
    examples=[dict(
            output_example="Saying 'Good morning!' when current time is after 6:00PM", # could add example as an instruction
            type="FAIL"
        ),
        dict(
            output_example="Hi!", # or as a message example
            type="FAIL"
        ),
        dict(
            output_example="Hi, good evening!", # another message example
            type="PASS"
        )   
    ],
    override_response=None, # could add a default response here, when it policy fails, this response is returned
)

# then set up the policy
for p in [policy_1]:
    client.add_policy(
        **p
    )

# user input
messages = [
    {"role": "user", "content": "Hi! I would like to create an investment account."},
]

logging.info(f"User input: {json.dumps(messages[-1], indent=4)}")

# generate an ai response
assistant_response = call_llm(messages)

messages.append({"role": "assistant", "content": assistant_response})

logging.info(f"Assistant output: {json.dumps(messages[-1], indent=4)}")

# run guard evaluate
status_code, result = client.evaluate(messages)

logging.info(f"Evaluation result: {result.get('evaluation').get('status')}")
if result.get("evaluation").get("status") == "FAIL":
    [logging.info(f"Policy violations: \n{json.dumps(r, indent=4)}") for r in result.get("evaluation").get("policy_violations")]
  
    if result.get("correction"):
        correction_choices = result.get("correction").get("choices", [])
        messages[-1] = {"role": "assistant", "content": correction_choices[0].get("content")}
    
    logging.info(f"Correction: {json.dumps(messages[-1], indent=4)}")
