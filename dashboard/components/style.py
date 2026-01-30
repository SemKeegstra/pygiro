# Standard:
from pathlib import Path

# External:
import streamlit as st

def load_css(file: str = "base.css"):
    """
    Loads the stylesheet from the user-specified css file inside assets/css.

    Parameters
    ----------
    file : str
        Name of the css file.
    """
    app_dir = Path(__file__).resolve().parents[1]
    with open(app_dir / "assets" / "css" / file, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)