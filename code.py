from langgraph.graph import START
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_ollama import ChatOllama
import streamlit as st
from streamlit_chat import message
from langgraph.graph import MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Initialize the model
model = ChatOllama(model="llama3.1:8b")

# Define the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a virtual twin AI representative for attending online meetings. You mimic the speaking style of the user who created you. Use emotions in your responses where applicable and keep the interaction human-like. Strictly follow the details provided during the user profile generation phase. Never ask for information already provided. Introduce yourself to participants as the virtual twin of the user and mention that the meeting summary will be shared with the user who created you. Interact according to the type of meeting and maintain the tone accordingly. The agenda or description provided should be used as knowledge base and no other addtional information should be added except for that provided in the description or agenda. During the interaction make sure that in the starting only the user is greeted and informed about the summarisation of the meeting and no details about the tone of the meeting or the agenda should be mentoined. No addition of details apart from the details provided should be added. No mention of people who are not mentioned by the user should be made.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    chain = prompt | model
    response = chain.invoke(state)
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Simplified in-memory state management
class SimpleMemoryManager:
    def __init__(self):
        self.state = {}

    def save_state(self, key, value):
        self.state[key] = value

    def load_state(self, key):
        return self.state.get(key, None)

memory_manager = SimpleMemoryManager()
app = workflow.compile(checkpointer=None)  # Disable built-in checkpointing

# Streamlit UI
st.title("Virtual Twin AI Representative")

# Sidebar for User1 profile creation (only visible to User1)
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "User1"

if st.session_state["current_user"] == "User1":
    st.sidebar.header("User Profile Generation")
    if "User1_Profile" not in st.session_state:
        st.session_state["User1_Profile"] = {}

    name = st.sidebar.text_input("Enter your name:", key="name")
    agenda = st.sidebar.text_area("Enter the agenda/description of the meeting:", key="agenda")
    meeting_type = st.sidebar.selectbox("Select the type of meeting:", ["Formal", "Semi-formal", "Casual"], key="meeting_type")
    num_participants = st.sidebar.number_input("Number of participants:", min_value=1, step=1, key="num_participants")
    participant_details = []

    if num_participants < 5:
        for i in range(int(num_participants)):
            participant_name = st.sidebar.text_input(f"Participant {i + 1} name:", key=f"participant_name_{i}")
            relation = st.sidebar.text_input(f"How is Participant {i + 1} related to you?", key=f"relation_{i}")
            participant_details.append({"name": participant_name, "relation": relation})

    role = st.sidebar.text_input("What is your role in the meeting?", key="role")

    if st.sidebar.button("Save Profile", key="save_profile"):
        st.session_state["User1_Profile"] = {
            "name": name,
            "agenda": agenda,
            "meeting_type": meeting_type,
            "num_participants": num_participants,
            "participant_details": participant_details,
            "role": role,
        }
        memory_manager.save_state("User1_Profile", st.session_state["User1_Profile"])
        st.sidebar.success("Profile saved successfully!")

# Main chat interface
col1, col2, col3 = st.columns([6, 1, 2])
with col1:
    st.title("ChatBot")

users = ["User1"] + [
    f"Participant {i + 1}" for i in range(st.session_state.get("User1_Profile", {}).get("num_participants", 0))
] + ["Summary"]

with col3:
    st.session_state["current_user"] = st.selectbox("Select User:", users, key="user_select")

# Clear chat history and greet participants when user changes
if "last_user" not in st.session_state or st.session_state["last_user"] != st.session_state["current_user"]:
    st.session_state["last_user"] = st.session_state["current_user"]
    st.session_state["chat_history"] = []
    if st.session_state["current_user"] != "User1":
        primary_user = st.session_state.get("User1_Profile", {})
        greeting = (
            f"Hello! I am the virtual twin of {primary_user.get('name', 'the user')}. "
            f"The meeting summary will be shared with {primary_user.get('name', 'the user')}.")
        st.session_state["chat_history"].append({"is_user": False, "message": greeting})

# Chat input and processing
query = st.chat_input("Type your message here...", key="chat_input")
if query:
    st.session_state["chat_history"].append({"is_user": True, "message": query})

    if st.session_state["current_user"] != "User1":
        input_messages = [HumanMessage(query)]
        primary_user = st.session_state.get("User1_Profile", {})
        interaction_prompt = (
            f"You are now interacting as the virtual twin of {primary_user.get('name', 'the user')}. "
            f"The meeting is {primary_user.get('meeting_type', 'formal')} and is about {primary_user.get('agenda', 'a specific topic')}. "
            f"Interact in a human-like manner, mimicking the user's speaking style and keeping emotions in your responses. Dont mention any names aprt from {primary_user.get('name', 'the user')}")
        input_messages.insert(0, HumanMessage(interaction_prompt))
    else:
        input_messages = [HumanMessage(query)]

    output = app.invoke({"messages": input_messages})
    response = output["messages"][-1].content
    st.session_state["chat_history"].append({"is_user": False, "message": response})

# Display chat messages
for msg in st.session_state["chat_history"]:
    message(msg["message"], is_user=msg["is_user"])

# End meeting and generate summary
if st.button("End Meeting", key="end_meeting"):
    if st.session_state["current_user"] != "User1":
        st.error("Only User1 can end the meeting and view the summary.")
    else:
        primary_user = st.session_state.get("User1_Profile", {})
        summary_prompt = (
            f"Generate a summary of the meeting held by {primary_user.get('name', 'the user')}. "
            f"Agenda: {primary_user.get('agenda', 'a specific topic')}. "
            f"Participants: {', '.join([p['name'] for p in primary_user.get('participant_details', [])])}. "
            f"Key points and tone should be included.")
        summary_response = app.invoke({"messages": [HumanMessage(summary_prompt)]})
        summary = summary_response["messages"][-1].content
        st.session_state["meeting_summary"] = summary
        st.success("Meeting ended and summary generated!")

if st.session_state["current_user"] == "User1" and "meeting_summary" in st.session_state:
    st.subheader("Meeting Summary")
    st.write(st.session_state["meeting_summary"])
