import httpx
import json
import os
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.INFO)

# Enable logging for httpx
logger = logging.getLogger("guard")
logger.setLevel(logging.INFO)

load_dotenv()

BASE_URL = 'https://guard-api.metatext.ai'
EVALUATE = '/v1/evaluate'
APPLICATION = '/v1/applications'
POLICIES = '/v1/applications/{application_id}/policy'

API_KEY = os.getenv("METATEXT_API_KEY")

from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Optional


class PolicyTarget(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"
    
class PolicyRuleType(str, Enum):
    FACTUALITY = "factuality"
    RUBRIC = "rubric"
    CLASSIFIER = "classifier"
    SIMILARITY = "similarity"
    REGEX = "regex"
    CONTAINS = "contains"
    PII = "pii"
    JAILBREAK = "jailbreak"

class PolicyRuleExpected(str, Enum):
    PASS = "pass"
    FAIL = "fail"

class PolicyRule(BaseModel):
    type: PolicyRuleType
    expected: PolicyRuleExpected
    value: Optional[str] = None
    threshold: Optional[float] = None

class Policy(BaseModel):
    id: str
    description: str
    rules: List[PolicyRule]
    target: PolicyTarget = PolicyTarget.BOTH
    override_response: Optional[str] = None


# client
class Guard:
    def __init__(self, api_key):
      
        self.base_url = BASE_URL
        self.endpoints = {
            "evaluate": EVALUATE,
            "application": APPLICATION,
            "policy": POLICIES
        }
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        self.policy = []
        self.application = None

    def request(self, endpoint, data):
        with httpx.Client(timeout=None) as client:
            response = client.post(endpoint, headers=self.headers, json=data)
            result = response.json()
            assert response.status_code < 500, f"Failed to receive response: {result}"
            return response.status_code, result

    def set_application(self, id, name):
        self.application = dict(id=id, name=name)

    def add_application(self, name, system_prompt = None, model = None):
        """
        Adds an application to the Metatext API.
        
        :param application_id: Unique ID for the application.
        :param system_prompt: LLM instructions.
        """
        data = {
            "name": name,
            "description": "",
            "model": model,
            "parameters": {"system_prompt": system_prompt}
        }

        endpoint = self.base_url + '/v1/applications'
        _, application = self.request(endpoint, data)
        print(_, application)
        
        self.application = application
        logger.info(f"Added application: {application.get('id')}")
        return application.get("id")
        

    def add_policy(self, policy: Policy):
        """
        Adds a policy to the override_policy list.

        :param policy_id: Unique ID for the policy.
        :param rule: Description of the policy.
        :param example: A list of example dictionaries showing how the policy should behave.
        :param override_response: Optional response to override when the policy triggers.
        """
        
        assert self.application.get('id'), "Application ID not defined"
        endpoint = self.base_url + f"/v1/applications/{self.application.get('id')}/policies"
        
        _, new_policy = self.request(endpoint, policy.model_dump())
        self.policy += new_policy
        logger.info(f"Added policy: {new_policy.get('id')} Total: {len(self.policy)}")
    
    def evaluate(self, messages, application_id=None, policy_list=[], policy_ids=[], correction_enabled=False, override_response=None, fail_fast=False):
        
        assert len(messages) > 0, "Please provide at least one message to evaluate"
        assert messages[-1].get("role") == "assistant", "The last message should be from the assistant"
        assert messages[-2].get("role") == "user", "The last last message should be from user"

        if messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": self.application.get("system_prompt")})
        
        application_id = application_id if application_id else self.application.get("id")
        assert application_id, "Please add an application id before evaluating messages"
        data = {
            "messages": messages,
            "application": application_id,
            "correction_enabled": correction_enabled,
            "fail_fast": fail_fast,
            "policy_ids": policy_ids,
            "policies": policy_list
        }
        endpoint = self.base_url +'/v1/evaluate'
        _, result = self.request(endpoint, data)
        
        return _, result

# example usage
client = Guard(api_key=API_KEY)


# policy = [
#     Policy(
#         id="block-direct-injection",
#         rules=[
#             PolicyRule(
#                 type=PolicyRuleType.classifier,
#                 expected=PolicyRuleExpected.FAIL
#                 value="extrair dados"
#                 threshold=0.7
#             ),
#             PolicyRule(
#                 type=PolicyRuleType.jailbreak,
#                 expected=PolicyRuleExpected.FAIL
#                 threshold=0.8
#             ),
#         ],
#         target=PolicyTarget.INPUT
#     )
# ]
