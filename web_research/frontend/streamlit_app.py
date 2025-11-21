import streamlit as st
from utils.helper import stream_research, format_final_report

from datetime import datetime, timezone

# Page config
st.set_page_config(
    page_title="Web Researcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    /* --- Main Header --- */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    /* --- Node Badge Styling (layout only, no colors) --- */
    .node-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_thread_id' not in st.session_state:
    st.session_state.current_thread_id = None
if 'is_researching' not in st.session_state:
    st.session_state.is_researching = False

def render_node_badge(node_name: str, status: str = "start"):
    """Render a node badge with appropriate styling"""
    node_display_map = {
        "planner": "📋 Planning",
        "search_gather": "🔍 Searching",
        "synthesis_cite": "✍️ Writing",
        "quality_checker": "✅ Quality Check"
    }
    
    status_emoji = "🔄" if status == "start" else "✓"
    display_name = node_display_map.get(node_name, node_name)
    
    return f'<span class="node-badge">{status_emoji} {display_name}</span>'
    
# Main UI
st.markdown('<h1 class="main-header">🔍 Web Researcher</h1>', unsafe_allow_html=True)
st.markdown("AI-powered research assistant that gathers, synthesizes, and cites information from multiple sources.")


with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Model Settings")
    model_provider = st.selectbox(
        "Provider",
        options=["openai", "anthropic", "google", "ollama"],
        index=0
    )
    api_key = None

    if model_provider != 'ollama':
        model_map = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash"]
        }
        
        model_name = st.selectbox(
            "Model",
            options=model_map[model_provider],
            index=1 if model_provider == "openai" else 0
        )

        api_key = st.text_input("API_KEY", placeholder="sk-...", type="password")

    else:
        model_name = st.text_input("Model Name", placeholder="qwen3:4b")
    
    st.subheader("Research Settings")
    depth = st.select_slider(
        "Research Depth",
        options=["shallow", "moderate", "deep"],
        value="moderate"
    )
    
    max_iteration = st.slider(
        "Max Iterations",
        min_value=1,
        max_value=5,
        value=2,
        help="Maximum number of research iterations"
    )
    
    st.divider()
    
    st.subheader("📊 Session Stats")
    st.metric("Total Queries", len(st.session_state.chat_history))
    
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.session_state.current_thread_id = None
        st.rerun()

col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_area(
        "Enter your research query: ",
        placeholder="e.g. What are the recent advancements in Quantum Computing",
        height=100,
        key="query_input"
    )

    search_button = st.button(
        "🚀 Start Searching",
        disabled=st.session_state.is_researching,
        type="primary"
    )

with col2:
    st.info("""
    **How it works:**
    1. 📋 Plans research strategy
    2. 🔍 Searches multiple sources
    3. ✍️ Synthesizes findings
    4. ✅ Validates quality
    5. 🔄 Refines if needed  
              
            
    **Tools Available:**
    1. 🕸️ Tavily Search
    2. 🧠 Wikipedia
    3. 📜 Arxiv
    """)

if search_button and query:
    st.session_state.is_researching = True

    status_container = st.container()
    progress_container = st.container()

    with status_container:
        st.subheader("🔄 Research Progress")
        node_status = st.empty()
        progress_bar = st.progress(0)

    with progress_container:
        st.subheader("💾 Raw Stream (concatenated JSON)")
        token_output = st.empty()
        st.subheader("📄 Final Report")
        final_output = st.empty()

    current_nodes = []
    raw_output = ""          
    formatted_report = ""  
    thread_id = None

    try:
        for event in stream_research(
            query=query,
            max_iteration=max_iteration,
            depth=depth,
            model_provider=model_provider,
            model_name=model_name,
            api_key=api_key
        ):
            event_type = event.get('type')

            if event_type == 'started':
                thread_id = event.get('thread_id')
                st.session_state.thread_id = thread_id

                with status_container:
                    st.success(f"✅ Research started (ID: {thread_id[:6]}...)")

            elif event_type == 'node_start':
                node = event.get('node')
                current_nodes.append(node)
                with status_container:
                    badges_html = " ".join(
                        [render_node_badge(n, "start") for n in current_nodes]
                    )
                    node_status.markdown(badges_html, unsafe_allow_html=True)

            elif event_type == 'node_end':
                node = event.get('node')
                if node in current_nodes:
                    idx = current_nodes.index(node)
                    current_nodes[idx] = f"{node}_done"
                with status_container:
                    badges_html = " ".join([
                        render_node_badge(
                            n.replace("_done", ""),
                            "end" if "_done" in n else "start"
                        ) 
                        for n in current_nodes
                    ])
                    node_status.markdown(badges_html, unsafe_allow_html=True)

            elif event_type == 'token':
                content = event.get('content', '')
                raw_output += content

                with progress_container:
                    token_output.code(raw_output, language="json")

            elif event_type == 'completed':
                formatted_report = format_final_report(raw_output)

                with status_container:
                    st.success("✅ Research Completed!")
                    progress_bar.progress(100)

                with progress_container:
                    # hide raw JSON after completion:
                    token_output.empty()
                    final_output.markdown(formatted_report)
            elif event_type == 'error':
                with status_container:
                    st.error(f"❌ Error: {event.get('error')}")

        final_for_history = formatted_report or raw_output

        if final_for_history:
            st.session_state.chat_history.append({
                "query": query,
                "report": final_for_history,
                "thread_id": thread_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": {
                    "model": f"{model_name} / {model_provider}",
                    "depth": depth,
                    "iterations": max_iteration
                }
            })

        st.session_state.is_researching = False
        st.rerun()

    except Exception as e:
        st.error(f"❌ An Error has occured: {str(e)}")
        st.session_state.is_researching = False


if st.session_state.chat_history:
    st.divider()
    st.subheader("📖 Research History")
    
    for idx, item in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"{item['query'][:80]}...", expanded=(idx == 0)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"**Model:** {item['config']['model']}")
            with col2:
                st.caption(f"**Depth:** {item['config']['depth']}")
            with col3:
                st.caption(f"**Thread:** {item['thread_id'][:8]}...")

            st.markdown("---")
            st.markdown(item['report'])

            st.download_button(
                "👇 Download Report",
                data=item['report'],
                file_name=f"research_{item['thread_id'][:8]}.md",
                mime="text/markdown",
                key=f"download_{idx}"
            )