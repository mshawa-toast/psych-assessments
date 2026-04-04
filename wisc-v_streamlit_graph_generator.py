# wisc-v_graph_generator_app.py
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

# Page config
st.set_page_config(page_title="WISC-V Graph Generator", layout="wide")
st.title("📊 WISC-V Graph Generator: Subtest and Composite Score Profiles")

st.markdown("""
Generate either the **Subtest Scaled Score Profile** or the **Composite Score Profile** graph.
Adjust the values in the sidebar and click **Generate Graph** to view and download the graph.
""")

# --- Sidebar: Select Graph Type ---
graph_type = st.sidebar.radio(
    "Select Graph Type",
    ["Subtest Scaled Score Profile", "Composite Score Profile"]
)

# --- Subtest Scaled Score Profile ---
if graph_type == "Subtest Scaled Score Profile":
    st.subheader("Subtest Scaled Score Profile")

    categories = {
        "Verbal Comprehension": ["SI", "VC", "IN", "CO"],
        "Visual Spatial": ["BD", "VP"],
        "Fluid Reasoning": ["MR", "FW", "PC", "AR"],
        "Working Memory": ["DS", "PS", "LN"],
        "Processing Speed": ["CD", "SS", "CA"]
    }

    # Custom default scaled scores
    default_scores = {
        "SI": 10, "VC": 10, "IN": 10, "CO": 10,
        "BD": 10, "VP": 10,
        "MR": 10, "FW": None, "PC": None, "AR": None,
        "DS": 10, "PS": None, "LN": None,
        "CD": 10, "SS": 10, "CA": None
    }

    # Custom default SEMs
    default_sems = {
        "SI": 0.99, "VC": 0.99, "IN": 0.99, "CO": 0.99,
        "BD": 0.99, "VP": 0.99,
        "MR": 0.99, "FW": None, "PC": None, "AR": None,
        "DS": 0.99, "PS": None, "LN": None,
        "CD": 0.99, "SS": 0.99, "CA": None
    }

    st.sidebar.header("Adjust Scaled Scores and SEMs")
    scores = {}
    sems = {}

    for category, subtests in categories.items():
        st.sidebar.subheader(category)
        for subtest in subtests:
            if default_scores[subtest] is not None:
                scores[subtest] = st.sidebar.number_input(
                    f"{subtest} Scaled Score", min_value=1, max_value=19, value=default_scores[subtest]
                )
            else:
                scores[subtest] = None
                st.sidebar.markdown(f"{subtest} Scaled Score: *Not administered*")

            if default_sems[subtest] is not None:
                sems[subtest] = st.sidebar.number_input(
                    f"{subtest} SEM", min_value=0.0, max_value=3.0, value=default_sems[subtest]
                )
            else:
                sems[subtest] = None
                st.sidebar.markdown(f"{subtest} SEM: *N/A*")

    if st.button("Generate Graph"):
        subtests = sum(categories.values(), [])
        x = np.arange(len(subtests))
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each category separately to break lines
        start = 0
        for subs in categories.values():
            valid_subs = [s for s in subs if scores[s] is not None]
            x_cat = [x[subtests.index(s)] for s in valid_subs]
            y_cat = [scores[s] for s in valid_subs]
            yerr_cat = [sems[s] for s in valid_subs]

            if valid_subs:
                ax.errorbar(
                    x_cat, y_cat, yerr=yerr_cat,
                    fmt='o-', color='blue', ecolor='blue',
                    elinewidth=2, capsize=5
                )

            start += len(subs)

        # Highlight average band
        ax.axhspan(9.5, 10.5, color='lightblue', alpha=0.3)

        # Horizontal grid lines
        for i in range(1, 20):
            ax.axhline(i, color='lightgray', linewidth=0.7, zorder=0)

        # Vertical category dividers
        category_boundaries = np.cumsum([len(v) for v in categories.values()])[:-1]
        for b in category_boundaries:
            ax.axvline(b - 0.5, color='gray', linewidth=1)

        ax.set_xticks([])

        # Subtest labels
        for i, label in enumerate(subtests):
            ax.text(i, 20.2, label, ha='center', va='bottom', fontsize=9)

        # Category labels
        positions = [(sum(len(v) for v in list(categories.values())[:i]) +
                      sum(len(v) for v in list(categories.values())[:i + 1])) / 2 - 0.5
                     for i in range(len(categories))]
        for pos, cat in zip(positions, categories.keys()):
            ax.text(pos, 21.3, cat, ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_yticks(range(1, 20))
        ax.set_ylim(1, 21.4)
        ax.set_xlim(-0.5, len(subtests) - 0.25)
        plt.subplots_adjust(top=0.84, bottom=0.08, left=0.07, right=0.98)
        st.pyplot(fig)

        img_bytes = get_graph_as_image(fig)
        st.download_button(
            label="Download Subtest Profile Graph as PNG",
            data=img_bytes,
            file_name="wisc-v_subtest_scaled_score_profile.png",
            mime="image/png"
        )

# --- Composite Score Profile ---
elif graph_type == "Composite Score Profile":
    st.subheader("Composite Score Profile")

    indices = ['VCI', 'VSI', 'FRI', 'WMI', 'PSI']
    default_scores = [100] * 5
    default_sems = [1.99] * 5
    fsiq_label = ['FSIQ']
    default_fsiq_score = [100]
    default_fsiq_sem = [1.99]

    st.sidebar.header("Adjust Scores and SEMs")
    index_scores = []
    index_sems = []
    for i, index in enumerate(indices):
        score = st.sidebar.number_input(f"{index} Score", min_value=35, max_value=165, value=default_scores[i])
        sem = st.sidebar.number_input(f"{index} SEM", min_value=0.0, max_value=10.0, value=default_sems[i])
        index_scores.append(score)
        index_sems.append(sem)

    fsiq_score = [st.sidebar.number_input("FSIQ Score", min_value=35, max_value=165, value=100)]
    fsiq_sem = [st.sidebar.number_input("FSIQ SEM", min_value=0.0, max_value=10.0, value=1.99)]

    if st.button("Generate Graph"):
        fig, ax = plt.subplots(figsize=(6, 6))

        # Plot index scores
        ax.plot(indices, index_scores, marker='o', color='blue', linewidth=1.5, label='Index Scores')
        ax.errorbar(indices, index_scores, yerr=index_sems, fmt='o', color='blue', capsize=5)

        # Plot FSIQ separately
        ax.errorbar(fsiq_label, fsiq_score, yerr=fsiq_sem, fmt='o', color='blue', capsize=5)

        # Vertical line divider between PSI and FSIQ
        ax.axvline(x=4.5, color='lightgray', linestyle='-', linewidth=1)

        # Horizontal mean line
        ax.axhline(y=100, color='darkblue', linewidth=1.5)

        ax.set_ylim(35, 165)
        ax.set_yticks(range(35, 170, 5))
        ax.axhspan(97.5, 102.5, color='lightblue', alpha=0.3)

        ax.grid(True, which='major', axis='y', linestyle='-', linewidth=0.5, alpha=0.3)
        ax.set_facecolor('white')
        plt.tight_layout()
        st.pyplot(fig)

        img_bytes = get_graph_as_image(fig)
        st.download_button(
            label="Download Composite Score Profile Graph as PNG",
            data=img_bytes,
            file_name="wisc-v_composite_score_profile.png",
            mime="image/png"
        )

else:
    st.info("Select a graph type and adjust values in the sidebar.")
