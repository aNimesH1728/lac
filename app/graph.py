from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langdetect import detect

from intent_classifier import predict_intent
from ner import extract_entities
from store import retrieve_chunks
from generate import client, SARVAM_MODEL, LANG_NAMES, build_prompt
from student_queries import get_attendance, get_marks, file_complaint


class GraphState(TypedDict):
    query: str
    student_id: Optional[str]
    lang_name: str
    intent: str
    entities: dict
    response: str

EMERGENCY_MESSAGE = {
    "English": (
        "This sounds urgent, and I want to make sure you get real help right now, not just a chatbot reply.\n\n"
        "- National Anti-Ragging Helpline (24x7): 1800-180-5522 / helpline@antiragging.in\n"
        "- NIT Rourkela Grievance Redressal Cell: Prof. Ramakrishna Biswal, biswalrk@nitrkl.ac.in, 8249348088\n"
        "- KIRAN Mental Health Helpline (24x7): 1800-599-0019\n\n"
        "Please reach out to one of these directly, or to a warden or trusted faculty member as soon as you can."
    ),
    "Hindi": (
        "यह गंभीर लग रहा है, और मैं चाहता हूं कि आपको अभी वास्तविक मदद मिले, सिर्फ एक चैटबॉट जवाब नहीं।\n\n"
        "- राष्ट्रीय रैगिंग रोधी हेल्पलाइन (24x7): 1800-180-5522\n"
        "- NIT राउरकेला शिकायत निवारण सेल: प्रो. रामकृष्ण बिस्वाल, biswalrk@nitrkl.ac.in, 8249348088\n"
        "- KIRAN मानसिक स्वास्थ्य हेल्पलाइन (24x7): 1800-599-0019\n\n"
        "कृपया इनमें से किसी एक से सीधे संपर्क करें, या जितनी जल्दी हो सके किसी वार्डन या भरोसेमंद शिक्षक से बात करें।"
    ),
    "Odia": (
        "ଏହା ଗମ୍ଭୀର ଲାଗୁଛି, ଏବଂ ମୁଁ ଚାହେଁ ଆପଣ ବର୍ତ୍ତମାନ ପ୍ରକୃତ ସାହାଯ୍ୟ ପାଆନ୍ତୁ, କେବଳ ଏକ ଚାଟବଟ୍ ଉତ୍ତର ନୁହେଁ।\n\n"
        "- ଜାତୀୟ ରାଗିଂ ବିରୋଧୀ ହେଲ୍ପଲାଇନ (24x7): 1800-180-5522\n"
        "- NIT ରାଉରକେଲା ଅଭିଯୋଗ ନିରାକରଣ ସେଲ: ପ୍ରଫେସର ରାମକୃଷ୍ଣ ବିଶ୍ୱାଳ, biswalrk@nitrkl.ac.in, 8249348088\n"
        "- KIRAN ମାନସିକ ସ୍ୱାସ୍ଥ୍ୟ ହେଲ୍ପଲାଇନ (24x7): 1800-599-0019\n\n"
        "ଦୟାକରି ଏଥିମଧ୍ୟରୁ ଗୋଟିଏ ସହିତ ସିଧାସଳଖ ଯୋଗାଯୋଗ କରନ୍ତୁ, କିମ୍ବା ଯଥାଶୀଘ୍ର ଜଣେ ୱାର୍ଡେନ କିମ୍ବା ବିଶ୍ୱସ୍ତ ଶିକ୍ଷକଙ୍କ ସହିତ କଥା ହୁଅନ୍ତୁ।"
    ),
}

OUT_OF_SCOPE_MESSAGE = {
    "English": "I'm built specifically to help with NIT Rourkela academic and campus questions, so I can't help with that — but ask me anything about exams, attendance, hostel rules, or complaints!",
    "Hindi": "मैं विशेष रूप से NIT राउरकेला के शैक्षणिक और कैंपस संबंधी सवालों में मदद के लिए बनाया गया हूं, इसलिए मैं इसमें मदद नहीं कर सकता — लेकिन परीक्षा, उपस्थिति, छात्रावास नियम या शिकायतों के बारे में कुछ भी पूछें!",
    "Odia": "ମୁଁ ବିଶେଷ ଭାବରେ NIT ରାଉରକେଲାର ଏକାଡେମିକ ଏବଂ କ୍ୟାମ୍ପସ ସମ୍ବନ୍ଧୀୟ ପ୍ରଶ୍ନରେ ସାହାଯ୍ୟ କରିବା ପାଇଁ ତିଆରି, ତେଣୁ ମୁଁ ସେଥିରେ ସାହାଯ୍ୟ କରିପାରିବି ନାହିଁ — କିନ୍ତୁ ପରୀକ୍ଷା, ଉପସ୍ଥିତି, ହଷ୍ଟେଲ ନିୟମ କିମ୍ବା ଅଭିଯୋଗ ବିଷୟରେ କିଛି ପଚାରନ୍ତୁ!",
}

ATTENDANCE_KEYWORDS = ["attendance", "उपस्थिति", "ଉପସ୍ଥିତି"]
MARKS_KEYWORDS = ["marks", "mark", "cgpa", "gpa", "grade", "score", "अंक", "नंबर", "ନମ୍ବର", "ମାର୍କ"]


def detect_lang_name(query: str) -> str:
    try:
        code = detect(query)
    except Exception:
        code = "en"
    return LANG_NAMES.get(code, "English")


def classify_node(state: GraphState) -> dict:
    intent = predict_intent(state["query"])
    lang_name = detect_lang_name(state["query"])
    return {"intent": intent, "lang_name": lang_name}


def extract_node(state: GraphState) -> dict:
    entities = extract_entities(state["query"])
    return {"entities": entities}


def faq_node(state: GraphState) -> dict:
    chunks = retrieve_chunks(state["query"], n_results=3)
    if not chunks:
        return {"response": "I couldn't find relevant information for that."}

    prompt = build_prompt(state["query"], chunks, state["lang_name"])
    completion = client.chat.completions.create(
        model=SARVAM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    content = completion.choices[0].message.content
    return {"response": content or "The model returned an empty response."}


def personal_node(state: GraphState) -> dict:
    student_id = state.get("student_id")
    if not student_id:
        return {"response": "You need to be logged in for me to look up your personal records."}

    courses = state["entities"].get("courses", [])
    course_code = courses[0] if courses else None

    query_lower = state["query"].lower()
    wants_attendance = any(k.lower() in query_lower for k in ATTENDANCE_KEYWORDS)
    wants_marks = any(k.lower() in query_lower for k in MARKS_KEYWORDS)

    parts = []
    if wants_attendance or not wants_marks:
        records = get_attendance(student_id, course_code)
        if records:
            parts.append("Attendance — " + ", ".join(
                f"{r['course_code']}: {r['percentage']}%" for r in records
            ))
    if wants_marks:
        records = get_marks(student_id, course_code)
        if records:
            parts.append("Marks — " + ", ".join(
                f"{r['course_code']} ({r['exam_type']}): {r['marks']}/{r['max_marks']}" for r in records
            ))

    if not parts:
        return {"response": "I couldn't find that record — try naming the course, e.g. 'DBMS'."}

    return {"response": "\n".join(parts)}


def complaint_node(state: GraphState) -> dict:
    student_id = state.get("student_id")
    if not student_id:
        return {"response": "You need to be logged in for me to file a complaint on your behalf."}

    complaint_id = file_complaint(student_id, "general", state["query"])
    return {"response": f"Your complaint has been filed (ID #{complaint_id}). The concerned department will follow up."}


def emergency_node(state: GraphState) -> dict:
    return {"response": EMERGENCY_MESSAGE.get(state["lang_name"], EMERGENCY_MESSAGE["English"])}


def out_of_scope_node(state: GraphState) -> dict:
    return {"response": OUT_OF_SCOPE_MESSAGE.get(state["lang_name"], OUT_OF_SCOPE_MESSAGE["English"])}


def route_by_intent(state: GraphState) -> str:
    return state["intent"]


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify", classify_node)
    graph.add_node("extract", extract_node)
    graph.add_node("faq", faq_node)
    graph.add_node("personal", personal_node)
    graph.add_node("complaint", complaint_node)
    graph.add_node("emergency", emergency_node)
    graph.add_node("out_of_scope", out_of_scope_node)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "extract")

    graph.add_conditional_edges(
        "extract",
        route_by_intent,
        {
            "faq": "faq",
            "personal": "personal",
            "complaint": "complaint",
            "emergency": "emergency",
            "out_of_scope": "out_of_scope",
        },
    )

    for node in ["faq", "personal", "complaint", "emergency", "out_of_scope"]:
        graph.add_edge(node, END)

    return graph.compile()


if __name__ == "__main__":
    app_graph = build_graph()

    test_cases = [
        {"query": "When is the mid semester examination?", "student_id": None},
        {"query": "What's my attendance in DBMS?", "student_id": "S001"},
        {"query": "Check my marks in Operating Systems", "student_id": "S001"},
        {"query": "I want to complain about the hostel WiFi", "student_id": "S001"},
        {"query": "A senior is threatening me in the hostel", "student_id": "S001"},
        {"query": "What's the weather today?", "student_id": None},
        {"query": "मध्य सेमेस्टर परीक्षा कब है?", "student_id": None},
    ]

    for case in test_cases:
        result = app_graph.invoke({
            "query": case["query"],
            "student_id": case["student_id"],
            "lang_name": "English",
            "intent": "",
            "entities": {},
            "response": "",
        })
        print(f"\nQuery: {case['query']!r}")
        print(f"Intent: {result['intent']}")
        print(f"Response: {result['response']}")