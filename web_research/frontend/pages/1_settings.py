import streamlit as st
import requests

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings")

# API Configuration
st.header("🔌 API Configuration")

col1, col2 = st.columns(2)

with col1:
    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000/api/v1",
        help="URL of your Web Researcher API"
    )

with col2:
    if st.button("Test Connection", type="primary"):
        try:
            health_url = api_url.replace('/api/v1', '/health')
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    st.success("✅ API is healthy and connected!")
                else:
                    st.warning("⚠️ API responded but reported unhealthy status")
            else:
                st.error(f"❌ Connection failed (Status: {response.status_code})")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

st.divider()

# # Default Model Settings
# st.header("🤖 Default Model Settings")

# col1, col2 = st.columns(2)

# with col1:
#     default_provider = st.selectbox(
#         "Default Provider",
#         options=["openai", "anthropic", "google"],
#         help="Default AI model provider"
#     )

# with col2:
#     provider_models = {
#         "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
#         "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
#         "google": ["gemini-1.5-pro", "gemini-1.5-flash"]
#     }
    
#     default_model = st.selectbox(
#         "Default Model",
#         options=provider_models[default_provider]
#     )

# st.divider()

# # Research Defaults
# st.header("🔍 Research Defaults")

# col1, col2 = st.columns(2)

# with col1:
#     default_depth = st.select_slider(
#         "Default Research Depth",
#         options=["shallow", "moderate", "deep"],
#         value="moderate"
#     )

# with col2:
#     default_iterations = st.slider(
#         "Default Max Iterations",
#         min_value=1,
#         max_value=5,
#         value=2
#     )

# st.divider()

# # Export/Import History
# st.header("💾 Data Management")

# col1, col2 = st.columns(2)

# with col1:
#     if st.button("📥 Export History"):
#         if 'chat_history' in st.session_state and st.session_state.chat_history:
#             import json
#             history_json = json.dumps(st.session_state.chat_history, indent=2)
#             st.download_button(
#                 "Download JSON",
#                 data=history_json,
#                 file_name="research_history.json",
#                 mime="application/json"
#             )
#         else:
#             st.info("No history to export")

# with col2:
#     uploaded_file = st.file_uploader("📤 Import History", type=['json'])
#     if uploaded_file:
#         import json
#         try:
#             imported_data = json.load(uploaded_file)
#             if st.button("Confirm Import"):
#                 st.session_state.chat_history = imported_data
#                 st.success("✅ History imported successfully!")
#                 st.rerun()
#         except Exception as e:
#             st.error(f"❌ Import failed: {str(e)}")

# st.divider()

# # Danger Zone
# st.header("⚠️ Danger Zone")

# if st.button("🗑️ Clear All History", type="secondary"):
#     st.session_state.chat_history = []
#     st.session_state.current_thread_id = None
#     st.success("✅ History cleared!")
#     st.rerun()