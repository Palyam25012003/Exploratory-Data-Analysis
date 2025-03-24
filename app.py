import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import pygwalker as pyg
import chardet
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Data Visualization Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to detect encoding of CSV files
def detect_encoding(uploaded_file):
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    uploaded_file.seek(0)  # Reset file pointer
    return result['encoding']

def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            encoding = detect_encoding(uploaded_file)
            df = pd.read_csv(uploaded_file, encoding=encoding)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# Main content area
st.title("Interactive Data Visualization Dashboard")

# File uploader in the main bar
uploaded_file = st.file_uploader(
    "Upload your data file (CSV or Excel)",
    type=['csv', 'xls', 'xlsx']
)

# Initialize DataFrame
df = None

# Load data if a file is uploaded
if uploaded_file is not None:
    df = load_data(uploaded_file)

# Display PyGWalker explorer if data is loaded
if df is not None:
    st.header("Interactive Data Explorer")
    
    # Initialize PyGWalker renderer with caching
    @st.cache_resource
    def get_pyg_renderer(data_frame):
        return StreamlitRenderer(data_frame, spec="./gw_config.json", spec_io_mode="rw")
    
    renderer = get_pyg_renderer(df)
    
    # Render the PyGWalker explorer
    renderer.explorer()

    # Export to HTML section
    st.header("Export Visualization")
    
    # Generate HTML for the visualization
    html = pyg.to_html(df)
    
    # Download button for exporting the HTML
    st.download_button(
        label="Download HTML",
        data=html,
        file_name="pygwalker_export.html",
        mime="text/html"
    )
    
    # Show HTML preview
    if st.checkbox("Show HTML Preview"):
        st.components.v1.html(html, height=600, scrolling=True)

else:
    # If no file is uploaded, display a message in the main body
    st.warning("No file uploaded. Please upload a valid data file to proceed.")
