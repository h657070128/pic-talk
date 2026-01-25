class EvaluationService:

    def evaluate(self, text: str):
        # mock 的文本分析
        return {
            "content_match_score": 80,
            "feedback": [
                {
                    "issue": "Sentence is too simple",
                    "suggestion": "Try to add more details",
                    "example": "The man is cooking food happily in a bright kitchen."
                }
            ],
            "encouragement": "Good job! Keep practicing."
        }
