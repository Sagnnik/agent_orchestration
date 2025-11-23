import streamlit as st
from utils.helper import markdown_to_pdf_bytes  

st.set_page_config(
    page_title="Research History",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .node-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.85rem;
            font-weight: 500;
            margin: 0.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="main-header">📖 Research History</h1>', unsafe_allow_html=True)
st.markdown("All research sessions for the **current Streamlit session**.")

history = st.session_state.chat_history

if not history:
    st.info("No research history found yet. Go to the main page and run a query.")
else:
    st.metric("Total Queries", len(history))
    st.divider()

    for idx, item in enumerate(reversed(history)):
        query_text = item.get("query", "")
        title = query_text[:80] + ("..." if len(query_text) > 80 else "")

        with st.expander(title, expanded=(idx == 0)):
            config = item.get("config", {})
            model = config.get("model", "N/A")
            depth = config.get("depth", "N/A")
            iterations = config.get("iterations", "N/A")
            thread_id = item.get("thread_id", "")
            timestamp = item.get("timestamp", "N/A")

            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                st.caption(f"**Model:** {model}")
            with col2:
                st.caption(f"**Depth:** {depth}")
            with col3:
                st.caption(f"**Iterations:** {iterations}")
            with col4:
                st.caption(f"**Timestamp (UTC):** {timestamp}")

            st.markdown("---")
            st.markdown(item.get("report", ""))

            base_name = f"research_{thread_id[:8]}" if thread_id else "research_report"

            st.download_button(
                "📄 Download Report (.md)",
                data=item.get("report", ""),
                file_name=f"{base_name}.md",
                mime="text/markdown",
                key=f"history_download_md_{idx}",
            )

            pdf_bytes = markdown_to_pdf_bytes(
                item.get("report", ""),
                title=query_text[:80],
            )
            st.download_button(
                "📄 Download Report (.pdf)",
                data=pdf_bytes,
                file_name=f"{base_name}.pdf",
                mime="application/pdf",
                key=f"history_download_pdf_{idx}",
            )
