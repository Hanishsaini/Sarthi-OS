class Critic:
    @staticmethod
    def validate(output: str) -> str:
        # Basic hallucination / quality check (expand later with LLM critic)
        if len(output.strip()) < 10:
            return "I need more context to give you a good answer. Can you rephrase?"
        return output