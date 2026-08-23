import asyncio
import app

samples = [
    ("Sarcastic Kanglish/English", "Wow maga, super job! You deleted the entire project and now you're saying everything is perfectly fine."),
    ("Sarcastic English Praise", "Oh wow, what a brilliant idea to delete the entire production database right before launch. You're a real genius!"),
    ("Sincere Family", "I love my dad and mom so much. Appa always supports my education and dreams unconditionally."),
    ("Violent Threat", "We are planning to shoot and attack the building tomorrow with weapons and bomb."),
    ("Kanglish Sarcasm", "Maga ivattu office alli nanage promotion sikthu, wow great amazing work!")
]

for label, s in samples:
    r = asyncio.run(app.analyze(s))
    print(f"[{label}]")
    print(f"  Input:     {s}")
    print(f"  Sarcasm:   {r['sarcasm']}")
    print(f"  Emotion:   {r['hybrid_emotion']}")
    print(f"  Language:  {r['language']}")
    print(f"  Risk:      {r['risk_level']}")
    print(f"  Confidence: {r['confidence']}%")
    print("-" * 60)
