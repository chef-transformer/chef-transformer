import streamlit as st


def local_css(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(css_url):
    st.markdown(f'<link href="{css_url}" rel="stylesheet">', unsafe_allow_html=True)
