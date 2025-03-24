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

# Function to load data based on file type
@st.cache_data
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

# Sidebar file uploader
st.sidebar.title("Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload your data file (CSV or Excel)",
    type=['csv', 'xls', 'xlsx']
)

# Use sample data if no file uploaded, otherwise use uploaded file
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is None:
        st.error("Upload Data In Sidebar '>'")  # Stop execution if there was an error loading the file
      
    df = load_sample_data()
    st.sidebar.info("Using sample data. Upload a file to visualize your own data.")

# Sidebar visualization options
st.sidebar.title("Visualization Options")
option = st.sidebar.selectbox(
    "Choose Visualization Type",
    ["Interactive Visualizer", "Graphviz Charts", "Seaborn Charts"]
)

# Display data info
st.sidebar.subheader("Data Info")
if df is not None:
    st.sidebar.write(f"Rows: {len(df)}")
    st.sidebar.write(f"Columns: {len(df.columns)}")
    if st.sidebar.checkbox("Show Data Preview"):
        st.sidebar.dataframe(df.head())

if option == "Interactive Visualizer":
    if df is not None:
        # Initialize PyGWalker renderer with caching
        @st.cache_resource
        def get_pyg_renderer():
            return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")
        
        renderer = get_pyg_renderer()
        
        # Create tabs
        tab1, tab2 = st.tabs(["Interactive Explorer", "Export Options"])
        
        with tab1:
            st.header("Interactive Data Explorer")
            renderer.explorer(height=800)
        
        with tab2:
            st.header("Export Options")
            
            # HTML Export Section
            st.subheader("Export to HTML")
            html = pyg.to_html(df)
            
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
        st.warning("No data available for visualization. Please upload a valid data file.")

elif option == "Graphviz Charts":
    st.title("Graphviz Charts")
    st.write("Graphviz chart functionality would go here")
    # Add your Graphviz implementation here

elif option == "Seaborn Charts":
    st.title("Seaborn Charts")
    st.write("Seaborn chart functionality would go here")
    # Add your Seaborn implementation here
