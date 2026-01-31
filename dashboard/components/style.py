# Standard:
import base64
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


def set_logo_title(title: str, logo: str="logo_abstract.png", height: int=42, gap: int=14) -> None:
    """
    Renders a page ``title`` with a leading ``logo`` in a single row.

    Parameters
    ----------
    title : str
        Page title text.

    logo : str, default="logo_abstract.png
        Filename inside ``assets/png``.

    height : int, default=42
        Logo height in pixels.

    gap : int, default=14
        Spacing between logo and title in pixels.
    """
    # Initialize:
    app_dir = Path(__file__).resolve().parents[1]
    path = app_dir / "assets" / "png" / logo

    # Read image:
    img = base64.b64encode(path.read_bytes()).decode()

    # Set title:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:{gap}px; margin: 0 0 0.5rem 0;">
            <img src="data:image/png;base64,{img}" style="height:{height}px; width:auto;" />
            <div style="font-size: 2.65rem; font-weight: 700; line-height: 1; margin:0;">
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )