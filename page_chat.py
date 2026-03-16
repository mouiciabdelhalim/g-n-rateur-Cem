import streamlit as st
# Removed unused import time
from backend.services.chat_service import get_chat_service
from backend.database.db_manager import (
    create_chat_session, get_chat_sessions, delete_chat_session,
    add_chat_message, get_chat_messages
)
from frontend.translations import t

def render():
    chat_service = get_chat_service()
    
    # Helper functions for state
    def new_chat():
        st.session_state.current_chat_id = None
        st.session_state.messages = []
        welcome_msg = t("chat_welcome")
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        st.session_state.chat_session = chat_service.get_chat_session()
        
    def load_chat(session_id: int):
        st.session_state.current_chat_id = session_id
        # Load messages from DB
        db_msgs = get_chat_messages(session_id)
        if not db_msgs:
            # Fallback if empty
            db_msgs = [{"role": "assistant", "content": t("chat_welcome")}]
            
        st.session_state.messages = db_msgs
        # Restart Gemini session with history
        st.session_state.chat_session = chat_service.get_chat_session(history=db_msgs)

    def delete_chat(session_id: int):
        delete_chat_session(session_id)
        if st.session_state.get("current_chat_id") == session_id:
            new_chat()
        st.toast(t("chat_session_deleted"))

    # Initialization
    if "current_chat_id" not in st.session_state:
        new_chat()
        
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = chat_service.get_chat_session()

    # --- SIDEBAR: Chat History ---
    with st.sidebar:
        st.markdown(f"### {t('chat_history_title')}")
        
        if st.button(f"➕ {t('chat_new_session')}", use_container_width=True, type="primary"):
            new_chat()
            st.rerun()
            
        st.markdown("---")
        
        sessions = get_chat_sessions()
        if not sessions:
            st.caption(t("chat_empty_history"))
        else:
            for s in sessions:
                sid = s["id"]
                title = s["title"]
                
                # Active state styling
                is_active = (st.session_state.get("current_chat_id") == sid)
                btn_type = "primary" if is_active else "secondary"
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"💬 {title}", key=f"load_{sid}", use_container_width=True, type=btn_type):
                        load_chat(sid)
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{sid}", help=t("chat_delete_btn")):
                        delete_chat(sid)
                        st.rerun()

    # --- MAIN CHAT AREA ---
    st.title(t("chat_title"))

    # Custom CSS for Premium Dynamic Styling
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        }
        .assistant-marker, .user-marker { display: none; }

        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.05);
            line-height: 1.6;
            font-size: 1.05rem;
        }
        [data-testid="stChatMessage"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }

        [data-testid="stChatMessage"]:has(.assistant-marker) {
            background: linear-gradient(145deg, #1e1e2e 0%, #2a2a3e 100%) !important;
            border: none !important;
            border-left: 5px solid #00bfa5 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2) !important;
        }
        [data-testid="stChatMessage"]:has(.assistant-marker) * {
            color: #f8f9fa !important;
        }

        [data-testid="stChatMessage"]:has(.user-marker) {
            background-color: #ffffff !important;
            border: none !important;
            border-right: 5px solid #4a90e2 !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        }
        [data-testid="stChatMessage"]:has(.user-marker) * {
            color: #1e1e2e !important;
        }

        [data-testid="stChatMessageAvatar"] {
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            background-color: #ffffff;
        }
        [data-testid="stChatMessage"]:has(.assistant-marker) [data-testid="stChatMessageAvatar"] {
            border: 2px solid #00bfa5;
            background-color: #1e1e2e;
        }
        [data-testid="stChatMessage"]:has(.user-marker) [data-testid="stChatMessageAvatar"] {
            border: 2px solid #4a90e2;
        }

        [data-testid="stChatInput"] { margin-top: 1rem; }
        [data-testid="stChatInputContainer"] {
            border-radius: 20px !important;
            border: 1px solid #d1d5db !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stChatInputContainer"]:focus-within {
            border-color: #00bfa5 !important;
            box-shadow: 0 6px 20px rgba(0, 191, 165, 0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render Chat History
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = "👩‍🏫" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            marker = "<span class='assistant-marker'></span>" if role == "assistant" else "<span class='user-marker'></span>"
            st.markdown(f"{marker}\n\n{msg['content']}", unsafe_allow_html=True)

    # Chat Input
    if user_input := st.chat_input(t("chat_input_ph")):
        
        # 1. Create session if it's the first user message
        if st.session_state.current_chat_id is None:
            # Generate a short title from the first message
            title = user_input[:30] + "..." if len(user_input) > 30 else user_input
            sid = create_chat_session(title)
            st.session_state.current_chat_id = sid
            # Also save the initial welcome message to DB so it's kept
            add_chat_message(sid, "assistant", st.session_state.messages[0]["content"])
            
        # 2. Add User Message
        sid = st.session_state.current_chat_id
        st.session_state.messages.append({"role": "user", "content": user_input})
        add_chat_message(sid, "user", user_input)
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"<span class='user-marker'></span>\n\n{user_input}", unsafe_allow_html=True)
            
        # 3. Get AI Response with Streaming
        with st.chat_message("assistant", avatar="👩‍🏫"):
            try:
                # the marker is needed for CSS to work properly in stream
                # st.write_stream renders chunks one by one
                def stream_generator():
                    yield "<span class='assistant-marker'></span>\n\n"
                    stream_response = st.session_state.chat_session.send_message_stream(user_input)
                    for chunk in stream_response:
                        if chunk.text:
                            yield chunk.text

                response_text = st.write_stream(stream_generator)
                
                # We need to remove the marker from the final saved text so it doesn't double up
                clean_response = response_text.replace("<span class='assistant-marker'></span>\n\n", "")
                
            except Exception as e:
                clean_response = t("chat_error", error=str(e))
                st.markdown(f"<span class='assistant-marker'></span>\n\n{clean_response}", unsafe_allow_html=True)
                
            # 4. Store AI response
            st.session_state.messages.append({"role": "assistant", "content": clean_response})
            add_chat_message(sid, "assistant", clean_response)
