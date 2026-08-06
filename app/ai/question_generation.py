import instructor

from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, Literal


class LanguageLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class MultipleChoiceQuestion(BaseModel):
    "Return the multiple choice question according to the schema below"
    type: Literal["multiple_choice"] = "multiple_choice"
    level: LanguageLevel
    prompt: Annotated[str, "Question prompt."]
    correct: int = Field(description="Position of the correct answer among the choices below (starting from zero).", ge=0, le=3)
    choices: list[str] = Field(description="List of alternatives", min_length=4, max_length=4)
    explanations: list[str] = Field(
        description="If the alternative is wrong, explain why it is wrong. Otherwise return 'Good Job!'",
        min_length=4, max_length=4
    )
    suggested_score: float = Field(description="How many points (out of 10) should this question be worth", gt=0, lt=5)


class MultipleSelectionQuestion(BaseModel):
    "Return the multiple selection question according to the schema below"
    type: Literal["multiple_selection"] = "multiple_selection"
    level: LanguageLevel
    prompt: Annotated[str, "Question prompt."]
    correct: list[int] = Field(
        description="Positions of the correct answers among the choices below (starting from zero).",
        min_length=1, max_length=4
    )
    choices: list[str] = Field(description="List of alternatives", min_length=4, max_length=4)
    explanations: list[str] = Field(
        description="If the alternative is wrong, explain why it is wrong. Otherwise return 'Good Job!'",
        min_length=4, max_length=4
    )
    suggested_score: float = Field(description="How many points (out of 10) should this question be worth", gt=0, lt=5)


class TrueFalseQuestion(BaseModel):
    "Return the true or false question according to the schema below"
    type: Literal["true_false"] = "true_false"
    level: LanguageLevel
    prompt: Annotated[str, "Affirmation based on the text"]
    correct: Annotated[bool, "Boolean indicating if the affirmation is true or false."]
    suggested_score: float = Field(description="How many points (out of 10) should this question be worth", gt=0, lt=5)


class ShortTextQuestion(BaseModel):
    """Return the multiple choice question according to the schema below
    Ex.: I ____ to the the school yesterday. (went)
    """
    type: Literal["short_text"] = "short_text"
    level: LanguageLevel
    prompt: Annotated[str, "Question prompt."]
    correct: str = Field(description="Answer to the prompt. It should be no more than a single word", max_length=10, min_length=1)
    suggested_score: float = Field(description="How many points (out of 10) should this question be worth", gt=0, lt=5)


text = f"""

Much of today's business is conducted across international borders, and while the majority of the global business community might share the use of English as a common language, the nuances and expectations of business communication might differ greatly from culture to culture. A lack of understanding of the cultural norms and practices of our business acquaintances can result in unfair judgements, misunderstandings and breakdowns in communication. Here are three basic areas of differences in the business etiquette around the world that could help stand you in good stead when you next find yourself working with someone from a different culture.

# Addressing someone
When discussing this topic in a training course, a German trainee and a British trainee got into a hot debate about whether it was appropriate for someone with a doctorate to use the corresponding title on their business card. The British trainee maintained that anyone who wasn't a medical doctor expecting to be addressed as 'Dr' was disgustingly pompous and full of themselves. The German trainee, however, argued that the hard work and years of education put into earning that PhD should give them full rights to expect to be addressed as 'Dr'.
This stark difference in opinion over something that could be conceived as minor and thus easily overlooked goes to show that we often attach meaning to even the most mundane practices. When things that we are used to are done differently, it could spark the strongest reactions in us. While many Continental Europeans and Latin Americans prefer to be addressed with a title, for example Mr or Ms and their surname when meeting someone in a business context for the first time, Americans, and increasingly the British, now tend to prefer using their first names. The best thing to do is to listen and observe how your conversation partner addresses you and, if you are still unsure, do not be afraid to ask them how they would like to be addressed.

# Smiling
A so-called 'smile of respect' is seen as insincere and often regarded with suspicion in Russia. A famous Russian proverb even states that 'laughing without reason is a sign of idiocy'. Yet in countries like the United States, Australia and Britain, smiling is often interpreted as a sign of openness, friendship and respect, and is frequently used to break the ice.
In a piece of research done on smiles across cultures, the researchers found that smiling individuals were considered more intelligent than non-smiling people in countries such as Germany, Switzerland, China and Malaysia. However, in countries like Russia, Japan, South Korea and Iran, pictures of smiling faces were rated as less intelligent than the non-smiling ones. Meanwhile, in countries like India, Argentina and the Maldives, smiling was associated with dishonesty.

# Eye contact
An American or British person might be looking their client in the eye to show that they are paying full attention to what is being said, but if that client is from Japan or Korea, they might find the direct eye contact awkward or even disrespectful. In parts of South America and Africa, prolonged eye contact could also be seen as challenging authority. In the Middle East, eye contact across genders is considered inappropriate, although eye contact within a gender could signify honesty and truthfulness.
Having an increased awareness of the possible differences in expectations and behaviour can help us avoid cases of miscommunication, but it is vital that we also remember that cultural stereotypes can be detrimental to building good business relationships. Although national cultures could play a part in shaping the way we behave and think, we are also largely influenced by the region we come from, the communities we associate with, our age and gender, our corporate culture and our individual experiences of the world. The knowledge of the potential differences should therefore be something we keep at the back of our minds, rather than something that we use to pigeonhole the individuals of an entire nation.
"""

def generate_questions(level) -> list[
    MultipleChoiceQuestion
    | TrueFalseQuestion
    | MultipleSelectionQuestion
    | ShortTextQuestion
]:
    client = instructor.from_provider(
        "ollama/gemma4:cloud", mode=instructor.Mode.JSON
    )
    return client.create(
        response_model=list[
            MultipleChoiceQuestion
            | TrueFalseQuestion
            | MultipleSelectionQuestion
            | ShortTextQuestion
        ],
        messages=[{
            "role": "user",
            "content": f"""
                You're an english language learning assistant hired to create questions for a quiz based on the text bellow:
                {text}
                Questions level {level}. Generate a diverse ensemble of at least 10 questions.
            """
        }],
    )


if __name__ == "__main__":
    import json
    from pathlib import Path

    level = "C1"

    questions = generate_questions(level)
    out = Path(__file__).parent / "generated_questions.json"
    out.write_text(
        json.dumps([q.model_dump() for q in questions], indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(questions)} questions to {out}")
