import requests
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# set app logger name
logging.getLogger("Test").setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
logging.info("Starting the application")

URL = 'https://ai-guard.metatext.ai'
EVALUATE = '/v1/evaluate'
API_KEY = os.getenv("METATEXT_API_KEY")

# client
class Guard:
    def __init__(self, api_key):
      
        self.url = URL+EVALUATE
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        self.application_id = application_id
        self.override_policy = []  # Initialize an empty list for policies

    def add_application(self, application_id, system_prompt = None):
        """
        Adds an application to the Metatext API.
        
        :param application_id: Unique ID for the application.
        :param application_name: Name of the application.
        """
        application = {
            "id": application_id,
            "system_prompt": system_prompt
        }
        self.application = application

    def add_policy(self, policy_id, rule, examples, override_response=None):
        """
        Adds a policy to the override_policy list.
        
        :param description: Description of the policy.
        :param example: A list of example dictionaries showing how the policy should behave.
        :param policy_id: Unique ID for the policy.
        :param severity: Severity level of the policy (e.g., CRITICAL).
        :param override_response: Optional response to override when the policy triggers.
        """
        policy = {
            "rule": rule,
            "examples": examples,
            "id": policy_id
        }
        if override_response:
            policy["override_response"] = override_response # override response if this policy is violated
        
        self.override_policy.append(policy)
    
    def evaluate(self, messages, threshold=0.3, correction_enabled=True, override_response=None, fail_fast=False, policy_ids=None):
        if policy_ids is None:
            policy_ids = []

        assert self.application, "Please add an application before evaluating messages"
        assert len(messages) > 0, "Please provide at least one message to evaluate"
        assert messages[-1].get("role") == "assistant", "The last message should be from the assistant"
        assert messages[-2].get("role") == "user", "The last last message should be from user"

        if messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.application.get("system_prompt")})
        
        data = {
            "messages": messages,
            "application": self.application_id,
            "threshold": threshold,
            "correction_enabled": correction_enabled,
            "fail_fast": fail_fast,
            "policy_ids": policy_ids,
            "override_policy": self.override_policy,
            "override_response": override_response # override if any policy is violated
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        result = response.json()
        assert response.status_code == 200 or result is not None, f"Failed to evaluate messages: {result}"
        return response.status_code, result

# example usage
client = Guard(api_key=API_KEY)
