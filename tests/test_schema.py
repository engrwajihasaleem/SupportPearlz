from src.chains.schemas import SupportAnswer
def test_refusal_schema():
    x=SupportAnswer(answer='Not documented',sources=[],confidence='none',answered=False); assert x.answered is False
