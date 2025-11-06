# wais-iv_streamlit_graph_generator_app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io

# Function to save the graph as an image
def get_graph_as_image(fig):
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    return img_bytes

# Set page config
st.set_page_config(page_title="WAIS-IV Graph Generator", layout="wide")
st.title("📊 WAIS-IV Graph Generator: Subtest and Composite Score Profiles")

# Instructions for the user
st.markdown("""
Use this app to generate either the **Subtest Scaled Score Profile** graph or the **Composite Score Profile** graph for the WAIS-IV.
Adjust the values in the sidebar and click **Generate Graph** to view and download the graph.
""")

# --- Sidebar: Select Graph Type ---
graph_type = st.sidebar.radio(
    "Select Graph Type",
    ["Subtest Scaled Score Profile", "Composite Score Profile"]
)

# --- Subtest Scaled Score Profile Graph ---
if graph_type == "WAIS-IV Subtest Scaled Score Profile":
    st.subheader("WAIS-IV Subtest Scaled Score Profile Graph Generator")

    categories = {
        "Verbal Comprehension": ["SI", "VC", "IN", "(CO)"],
        "Perceptual Reasoning": ["BD", "MR", "VP", "(FW)", "(PCm)"],
        "Working Memory": ["DS", "AR", "(LN)"],
        "Processing Speed": ["SS", "CD", "(CA)"]
    }

    default_scores = {
        "SI": 10, "VC": 10, "IN": 10, "(CO)": None,
        "BD": 10, "MR": 10, "VP": 10, "(FW)": None, "(PCm)": None,
        "DS": 10, "AR": 10, "(LN)": None,
        "SS": 10, "CD": 10, "(CA)": None
    }

    default_sems = {
        "SI": 0.99, "VC": 0.99, "IN": 0.99, "(CO)": None,
        "BD": 0.99, "MR": 0.99, "VP": 0.99, "(FW)": None, "(PCm)": None,
        "DS": 0.99, "AR": 0.99, "(LN)": None,
        "SS": 0.99, "CD": 0.99, "(CA)": None
    }

    st.sidebar.header("Adjust Scaled Scores and SEMs")

    scores = {}
    sems = {}

    for category, subtests in categories.items():
        st.sidebar.subheader(category)
        for subtest in subtests:
            scores[subtest] = st.sidebar.number_input(
                f"{subtest} Scaled Score", min_value=1, max_value=19,
                value=default_scores[subtest] if default_scores[subtest] else 10
            ) if default_scores[subtest] is not None else None

            sems[subtest] = st.sidebar.number_input(
                f"{subtest} SEM", min_value=0.0, max_value=3.0,
                value=default_sems[subtest] if default_sems[subtest] else 1.0
            ) if default_sems[subtest] is not None else None

    if st.button("Generate Graph"):
        subtests = sum(categories.values(), [])
        x = np.arange(len(subtests))
        y = [scores[s] if scores[s] is not None else np.nan for s in subtests]
        yerr = [sems[s] if sems[s] is not None else np.nan for s in subtests]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.errorbar(x, y, yerr=yerr, fmt='o-', color='blue', ecolor='blue', elinewidth=2, capsize=5)

        # Highlight average band (9–11)
        ax.axhspan(9.5, 10.5, color='lightblue', alpha=0.3)

        # Add horizontal grid lines
        for i in range(1, 20):
            ax.axhline(i, color='lightgray', linewidth=0.7, zorder=0)

        # Add vertical category dividers
        category_boundaries = np.cumsum([len(v) for v in categories.values()])[:-1]
        for b in category_boundaries:
            ax.axvline(b - 0.5, color='gray', linewidth=1)

        # Remove bottom x labels
        ax.set_xticks([])

        # Add subtest labels
        for i, label in enumerate(subtests):
            ax.text(i, 20.2, label, ha='center', va='bottom', fontsize=9)

        # Add category labels
        positions = [(sum(len(v) for v in list(categories.values())[:i]) +
                      sum(len(v) for v in list(categories.values())[:i + 1])) / 2 - 0.5
                     for i in range(len(categories))]
        for pos, cat in zip(positions, categories.keys()):
            ax.text(pos, 21.4, cat, ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Y-axis setup
        ax.set_yticks(range(1, 20))
        ax.set_ylim(1, 21.4)
        ax.set_xlim(-0.5, len(subtests) - 0.25)

        plt.subplots_adjust(top=0.84, bottom=0.08, left=0.07, right=0.98)
        st.pyplot(fig)

        # Save graph and provide download button
        img_bytes = get_graph_as_image(fig)
        st.download_button(
            label="Download Subtest Profile Graph as PNG",
            data=img_bytes,
            file_name="wais-iv_subtest_scaled_score_profile.png",
            mime="image/png"
        )

# --- Composite Score Profile Graph ---
elif graph_type == "WAIS-IV Composite Score Profile":
    st.subheader("WAIS-IV Composite Score Profile Graph Generator")

    # Data for Composite Score Profile
    indices = ['VCI', 'PRI', 'WMI', 'PSI']

    # Define default values for the indices and SEMs
    default_index_scores = [100, 100, 100, 100]
    default_index_sem = [1.99, 1.99, 1.99, 1.99]

    default_fsiq_score = 100
    default_fsiq_sem = 1.99

    # Sidebar for user inputs
    st.sidebar.header("Adjust Scores and SEMs")

    index_scores = {}
    index_sem = {}

    for i, index in enumerate(indices):
        index_scores[index] = st.sidebar.number_input(
            f"{index} Score", min_value=35, max_value=165,
            value=default_index_scores[i]
        )
        index_sem[index] = st.sidebar.number_input(
            f"{index} SEM", min_value=0.0, max_value=10.0,
            value=default_index_sem[i]
        )

    # Get FSIQ score and SEM from the user input
    fsiq_score = st.sidebar.number_input("FSIQ Score", min_value=35, max_value=165, value=default_fsiq_score)
    fsiq_sem = st.sidebar.number_input("FSIQ SEM", min_value=0.0, max_value=10.0, value=default_fsiq_sem)

    if st.button("Generate Graph"):
        # Create the figure
        plt.figure(figsize=(5, 6))  # Match original figure size

        # Plot index scores with their respective SEM
        plt.plot(indices, index_scores.values(), marker='o', color='blue', linewidth=1.5, label='Index Scores')
        plt.errorbar(indices, index_scores.values(), yerr=index_sem.values(), fmt='o', color='blue', capsize=5)

        # Plot FSIQ separately with its SEM
        plt.errorbar(['FSIQ'], [fsiq_score], yerr=[fsiq_sem], fmt='o', color='blue', capsize=5)

        # Add a vertical line between PSI and FSIQ
        plt.axvline(x=3.5, color='lightgray', linestyle='-', linewidth=1)

        # Add a horizontal line at mean (100)
        plt.axhline(y=100, color='darkblue', linewidth=1.5)

        # Customize the y-axis
        plt.ylim(35, 165)
        plt.yticks(range(35, 170, 5))
        plt.axhspan(97.5, 102.5, color='lightblue', alpha=0.3)

        # Grid and style
        plt.grid(True, which='major', axis='y', linestyle='-', linewidth=0.5, alpha=0.3)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('')

        # Match the WAIS report look
        plt.gca().set_facecolor('white')
        plt.tight_layout()

        st.pyplot(plt)

        # Save graph and provide download button
        img_bytes = get_graph_as_image(plt)
        st.download_button(
            label="Download Composite Score Profile Graph as PNG",
            data=img_bytes,
            file_name="wais-iv_composite_score_profile.png",
            mime="image/png"
        )

else:
    st.info("Adjust values in the sidebar and select a graph type to generate.")
