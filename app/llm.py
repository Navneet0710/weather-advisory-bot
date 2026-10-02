import os
import re
from dotenv import load_dotenv

from typing import Optional
load_dotenv()
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
class Intent(BaseModel):
    is_outdoor_activity: bool
    activity_tag: str=Field(description="One supplied activity tag, or unknown")
    location: Optional[str]=None
    time_ref: str="today"
def model():
    return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"),temperature=0,google_api_key=os.getenv("GEMINI_API_KEY"))
def extract_intent(message,history,tags):
    m=model().with_structured_output(Intent)
    prompt=("Extract intent only. Never give safety advice or invent policy/weather. "
            f"Allowed tags: {tags}. Unknown activity must be 'unknown'. Previous turns: {history[-6:]}. "
            f"Current message: {message}")
    return m.invoke(prompt)
def compose_advice(sop,location,summary):
    p=("Write 1-2 concise sentences using ONLY the approved SOP guidance. "
       "Do not add advice, facts, forecasts, numbers, thresholds, or new policy. "
       f"Approved guidance: {sop['guidance']} Location: {location}. Weather summary is provided only for context: {summary}")
    text=model().invoke(p).content.strip()
    return sop["guidance"] if re.search(r"\d",text) else text
