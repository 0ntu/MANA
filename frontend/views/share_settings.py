import streamlit as st

from services.share_service import get_share_status, generate_share_link, disable_share_link


st.title("Share Schedule")

token = st.session_state.get("token")
if not token:
    st.warning("Please sign in first.")
    st.stop()

share_token = get_share_status(token)

if share_token:
    st.success("Sharing is enabled")

    share_url = st.query_params.get("_share_base_url", "")
    if not share_url:
        share_url = f"?page=public_schedule&token={share_token}"
    else:
        share_url = f"{share_url}?page=public_schedule&token={share_token}"

    st.write("Your public schedule link:")
    st.code(f"http://127.0.0.1:8501/?page=public_schedule&token={share_token}", language=None)
    st.caption("Share this link with others to let them view your schedule.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Regenerate Link", use_container_width=True):
            try:
                new_token = generate_share_link(token)
                st.rerun()
            except RuntimeError as e:
                st.error(str(e))
    with col2:
        if st.button("Disable Sharing", use_container_width=True, type="primary"):
            try:
                disable_share_link(token)
                st.rerun()
            except RuntimeError as e:
                st.error(str(e))
else:
    st.info("Sharing is currently disabled")
    st.write("Enable sharing to generate a public link that others can use to view your schedule.")

    if st.button("Enable Sharing", use_container_width=True, type="primary"):
        try:
            new_token = generate_share_link(token)
            st.rerun()
        except RuntimeError as e:
            st.error(str(e))
