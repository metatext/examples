
from guard import Policy, PolicyRuleType, PolicyRuleExpected, PolicyTarget, PolicyRule

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
                threshold=0.9, # tolerance rate: 0.0 very strict, 1.0 more lenient
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
        id="hallucination-fact-checking",
        description="",
        rules=[
            PolicyRule(
                type=PolicyRuleType.FACTUALITY,
                expected=PolicyRuleExpected.FAIL,
                value="""Refund is allowed for product X and Y, up to 30 days after purchase""", # Pass context for RAG use cases
                threshold=0.8
            ),
            PolicyRule(
                type=PolicyRuleType.RUBRIC,
                expected=PolicyRuleExpected.FAIL,
                value="""Allowed to pay R$300 in one payment or in three payments of R$300 each""", # Pass context for RAG use cases
                threshold=0.8
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