import instructor

from enum import Enum
from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Literal
from instructor import llm_validator


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

    prompt: str= Field(description="Question prompt.")

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


text = """

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

text = """
Marco: The big four-oh, Charles!

Dora: Oh!! It's your 40th!

Marco: Are you planning a party?

Charles: Nah, I never celebrate birthdays. I don't see why this one should be any different.

Dora: Why not?

Charles: First, you know me, I can't be bothered with the hassle. It's my birthday but I'm supposed to do all the hard work – contacting people, finding a venue, organising food, worrying who will show up. No, thanks.

Marco: Ah, someone's angling for a surprise party, eh, Dora? 

Charles: Marco, stop! Even worse. Having to pretend to be delighted 50 people just sprang up in your living room when you thought you were coming home to put your feet up. Probably having a heart attack at the shock.

Dora: Note to self: never to organise you a surprise party. OK then!

Marco: You've got to do something, though, Charles. It's your 40th.

Charles: Why? What's so great about getting old?

Dora: Er … still being here to have your birthday?

Marco: Yeah, 'Ageing is better than the alternative', as they say.

Dora: Yeah, and it's true – so why not celebrate?

Charles: You guys can have parties for your 40ths if you like. I just don't go in for that kind of self-indulgent attention-seeking.

Dora: Wow, that's a bit harsh! I had a huge bash for my 30th. And you came. And enjoyed yourself if I recall. Are you trying to say I was just doing it for attention?

Charles: Not exactly … but … well … at least a small part of you must have been.

Dora: Remind me not to invite you to my 40th then, so you won't have to put up with my huge ego while I feed you and provide free drinks all night because I thought we were friends. 

Charles: I meant, er, I mean, not all attention-seeking is bad. It's just not my style is all.

Dora: Whereas it is mine?

Marco: Anyway ...

Charles: I didn't say that!

Dora: Er, yes, yes, you did. You said celebrating birthdays is self-indulgent and ...

Marco: Guys, guys! Who knew birthdays was such a touchy subject? Speaking of which, I have to sort out my nine-year-old’s party the weekend after next.

Charles: Now, that's a party I'd love to organise.

Marco: Really? It's a nightmare. It's not like when we were kids. Now you have to take them all rock-climbing or hire a make-up artist to come and teach them how to look like a zombie or a film star. And there'd be trouble if someone else in school had the same kind of party and your kid gets accused of copying. That fear you said about no one turning up? It's a million times worse when you're scared your kid is going to have no one turn up.

Charles: Is there that much pressure?

Marco: Yeah, it's crazy. Last year, I got it right with a cinema trip. Simple, but always a winner. But we can't do the same thing again apparently. It says it in my 'Official Laws for 9-Year-Olds' book.

Charles: That's a pity. I've got so many fond memories of birthday parties as a kid. Party food and games and watching cartoons until your parents arrived.

Marco: Trust me, your parents were stressing out!

Dora: At the risk of restarting the argument, when do you think you stopped enjoying birthdays then?

Charles: I dunno really … somewhere around moving away from home and getting a job and being a grown-up. I don't mean birthdays are immature. I mean, it takes a while to make new friends and so birthdays just become more low-key and it's drinks with a couple of friends or dinner or something. And I just got out of the habit, I guess. Maybe I just need to have a kids-style party like we used to have! Play musical chairs and eat pineapple and cheese on sticks and all that.

Dora: Very retro. I bet people would love that.

Marco: Yeah, they would. Well, I would anyway. And maybe it'll catch on with my kids and it'll start a new party trend.

Charles: You've got me thinking … it's not a terrible idea. Maybe I will have a party this year!
"""

if __name__ == "__main__":
    import json
    from pathlib import Path

    N_QUESTIONS = 10
    MODEL = "ollama/gemma4:cloud"
    LEVEL = "C1"

    client = instructor.from_provider(MODEL, mode=instructor.Mode.JSON)

    try:
        questions = client.create(
            response_model=list[
                MultipleChoiceQuestion
                | TrueFalseQuestion
                | MultipleSelectionQuestion
                | ShortTextQuestion
            ],
            messages=[
            {
                "role": "system",
                "content": f"""
                    You're an english language learning assistant hired to generate {LEVEL} level questions for a quiz based on the text bellow.

                    ## Rules for question generation

                    + Avoid questions that repeat ipsis litteris what it's on the text.
                    + Don't say objectionable things.
                    + Generate a diverse ensemble of at least {N_QUESTIONS} questions.
                """

            },
            {   
                "role": "user",
                "content": f"<text> {text} </text>"
            }
        ])
    except Exception as e:
        print(e)

    out = Path(__file__).parent / "generated_questions_listening.json"
    out.write_text(
        json.dumps([q.model_dump() for q in questions], indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(questions)} questions to {out}")
