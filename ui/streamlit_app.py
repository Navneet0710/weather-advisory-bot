import sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from dotenv import load_dotenv
from app.graph import build_graph
load_dotenv()
st.set_page_config(page_title="Weather Advisory Bot",page_icon="🌦️")
st.title("🌦️ Weather-Advisory Support Bot")
st.caption("Live Open-Meteo data + editable SOPs. No generic safety advice.")
if st.button("New Chat"):
    st.session_state.history = []
    st.session_state.messages = []
    st.rerun()
if "messages" not in st.session_state:st.session_state.messages=[]
if "history" not in st.session_state:st.session_state.history=[]
for m in st.session_state.messages:
    with st.chat_message(m["role"]):st.markdown(m["content"])
if prompt:=st.chat_input("e.g. Is it safe to cycle in Bhopal today?"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking live weather and SOPs..."):
            result=build_graph().invoke({"user_message":prompt,"history":st.session_state.history})
        response=result.get("response","No response produced.");st.markdown(response)
    st.session_state.messages.append({"role":"assistant","content":response})
    st.session_state.history += [{"role":"user","content":prompt},{"role":"assistant","content":response}]
