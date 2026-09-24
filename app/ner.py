import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
COURSES = {
    "DBMS": [
        "DBMS", "Database Management Systems",
        "डेटाबेस मैनेजमेंट सिस्टम",
        "ଡାଟାବେସ୍ ମ୍ୟାନେଜମେଣ୍ଟ ସିଷ୍ଟମ",
    ],
    "OS": [
        "OS", "Operating Systems",
        "ऑपरेटिंग सिस्टम",
        "ଅପରେଟିଂ ସିଷ୍ଟମ",
    ],
    "DSA": [
        "DSA", "Data Structures", "Data Structures and Algorithms",
        "डेटा स्ट्रक्चर",
        "ଡାଟା ଷ୍ଟ୍ରକ୍ଚର",
    ],
    "CN": [
        "CN", "Computer Networks",
        "कंप्यूटर नेटवर्क",
        "କମ୍ପ୍ୟୁଟର ନେଟୱାର୍କ",
    ],
    "OOP": [
        "OOP", "Object Oriented Programming", "Object-Oriented Programming",
        "ऑब्जेक्ट ओरिएंटेड प्रोग्रामिंग",
        "ଅବଜେକ୍ଟ ଓରିଏଣ୍ଟେଡ୍ ପ୍ରୋଗ୍ରାମିଂ",
    ],
    "COA": [
        "COA", "Computer Organisation and Architecture", "Computer Organization and Architecture",
        "कंप्यूटर संगठन और आर्किटेक्चर",
        "କମ୍ପ୍ୟୁଟର ଅର୍ଗାନାଇଜେସନ ଏବଂ ଆର୍କିଟେକଚର",
    ],
    "FCS": [
        "FCS", "Foundations of Computer Security",
        "कंप्यूटर सुरक्षा के मूल सिद्धांत",
        "କମ୍ପ୍ୟୁଟର ସୁରକ୍ଷାର ମୂଳ ସିଦ୍ଧାନ୍ତ",
    ],
}

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
for course_code, variants in COURSES.items():
    patterns = [nlp.make_doc(text) for text in variants]
    matcher.add(course_code, patterns)


def extract_entities(text: str) -> dict:
    doc = nlp(text)
    course_matches = matcher(doc)
    courses_found = set(nlp.vocab.strings[match_id] for match_id, start, end in course_matches)
    for course_code, variants in COURSES.items():
        for variant in variants:
            if not variant.isascii() and variant in text:
                courses_found.add(course_code)

    courses_found = sorted(courses_found)

    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    numbers = [ent.text for ent in doc.ents if ent.label_ == "CARDINAL"]

    return {
        "courses": courses_found,
        "dates": dates,
        "numbers": numbers,
    }


if __name__ == "__main__":
    test_queries = [
        "What's my attendance in DBMS?",
        "Check my marks in Operating Systems for semester 4",
        "When is the exam on 22.02.2027?",
        "डेटाबेस मैनेजमेंट सिस्टम में मेरी उपस्थिति क्या है?",
        "ଅପରେଟିଂ ସିଷ୍ଟମରେ ମୋର ନମ୍ବର ଯାଞ୍ଚ କର",
        "What's the weather today?",
        "What's my attendance in COA?",
        "कंप्यूटर संगठन और आर्किटेक्चर में मेरे अंक क्या हैं?",
        "Check my marks in Foundations of Computer Security",
        "FCS ର ମାର୍କ ମୋତେ ଦେଖାଅ",
    ]
    for q in test_queries:
        print(f"{q!r}")
        print(f"  -> {extract_entities(q)}")