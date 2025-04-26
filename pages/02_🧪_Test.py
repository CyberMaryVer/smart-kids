import streamlit as st
import os
import re
import pandas as pd
import plotly.express as px

from content.categories import categories_info
from content.questions import questions_data

# --- CSS for Customization ---
css_path = ".streamlit/gpt.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    print(f"CSS file not found: {css_path}")


# --- Constants ---
CATEGORY_KEYS = ['a', 'b', 'c', 'd', 'e']  # Define the order


# --- Session State Initialization ---
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}  # Store {question_id: selected_option_index}
if 'test_complete' not in st.session_state:
    st.session_state.test_complete = False

# --- Map question ID to options for easier lookup during scoring ---
# Create this map once
if 'question_options_map' not in st.session_state:
    st.session_state.question_options_map = {q["id"]: q["options"] for q in questions_data}


# --- Functions for Navigation and Restart ---
def next_question():
    """Saves the current answer index and moves to the next question or completes the test."""
    q_index = st.session_state.current_question_index
    if q_index < len(questions_data):
        current_q = questions_data[q_index]
        current_q_id = current_q["id"]
        widget_key = f"q_{current_q_id}"

        if widget_key in st.session_state:
            selected_option_text = st.session_state[widget_key]
            try:
                # Find the index of the selected option text
                selected_index = current_q["options"].index(selected_option_text)
                # Store the INDEX in the answers dictionary
                st.session_state.answers[current_q_id] = selected_index
            except ValueError:
                # Should not happen with st.radio, but good practice
                st.warning(
                    f"Could not find selected option '{selected_option_text}' for question {current_q_id}. Skipping answer.")
                if current_q_id in st.session_state.answers:
                    del st.session_state.answers[current_q_id]  # Remove potentially bad data

    # Move to next question or finish
    if st.session_state.current_question_index < len(questions_data) - 1:
        st.session_state.current_question_index += 1
    else:
        st.session_state.test_complete = True
    # st.rerun()  # Rerun to update the display immediately


def restart_test():
    """Resets the session state to start the test over."""
    st.session_state.current_question_index = 0
    st.session_state.answers = {}
    st.session_state.test_complete = False

    # Clear widget states by removing their keys (Streamlit will re-initialize)
    # This is more robust than deleting specific widget keys if questions change.
    keys_to_delete = [key for key in st.session_state if key.startswith("q_")]
    for key in keys_to_delete:
        del st.session_state[key]

    st.rerun()


def show_pie_chart(scores, background='transparent'):
    """Displays a pie chart of the scores."""
    # Set the background color (hex code)
    background = background if background != 'transparent' else 'rgba(0,0,0,0)'  # Default to transparent
    # Prepare data, ensuring only categories with scores > 0 are shown for clarity
    chart_data = {categories_info[k]['name'].split('(')[0].strip(): v for k, v in scores.items() if
                  v > 0}  # Use short names for labels
    if not chart_data:
        st.info("No scores recorded to display the chart.")
        return

    df = pd.DataFrame(list(chart_data.items()), columns=['Category', 'Score'])

    fig = px.pie(df, values='Score', names='Category', title='Score Distribution by Type', hole=0.4)
    fig.update_traces(textposition='outside', textinfo='percent+label',
                      pull=[0.05 if score == df['Score'].max() else 0 for score in
                            df['Score']])  # Highlight max score slightly
    fig.update_layout(
        title_x=0.5,  # Center title
        legend_title_text='Categories',
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        margin=dict(l=20, r=20, t=50, b=20)  # Adjust margins
    )
    fig.update_traces(marker=dict(colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA07A']))  # Custom colors
    fig.update_layout(
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(color='black'),  # Font color
    )

    st.plotly_chart(fig, use_container_width=True)


# --- Sidebar ---
with st.sidebar:
    logo_path = os.path.join("images", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_column_width=True)
    else:
        st.caption("(logo.png not found)")
    st.markdown("---")
    st.info("**Правила игры**")
    st.markdown("""**Йоу! 👋 Готов узнать свою суперсилу?**
Этот тест – не домашка по нудному предмету, а твой личный квест! Поможет понять, что тебя реально прёт, и какие скиллы стоит прокачивать для будущей профы мечты.

Читай вопросики и выбирай **ОДИН** вариант, который больше всего про тебя. Не тормози, первая мысль – самая верная!
""")
    # Add restart button to sidebar for easy access
    if st.button("🔄 Restart Test", key="restart_sidebar"):
        restart_test()

# --- Main App Logic ---
title_placeholder = st.empty()


if not st.session_state.test_complete:
    title_placeholder.title("Кто ты? Найди свою суперсилу! 🚀")
    # --- Display Current Question ---
    st.markdown(f"**Question {st.session_state.current_question_index + 1} of {len(questions_data)}**")

    q_index = st.session_state.current_question_index
    current_q = questions_data[q_index]
    q_id = current_q["id"]
    question_text = current_q["question"]
    options = current_q["options"]
    widget_key = f"q_{q_id}"  # Unique key for the radio widget

    st.subheader(question_text)

    # --- Radio Button Logic ---
    # Determine the default selected index for the radio button
    # If an answer was previously selected for this question, use its index
    # Otherwise, default to index 0
    selected_index_for_radio = st.session_state.answers.get(q_id, 0)  # Default to 0 if not answered yet
    # Ensure the index is valid
    if not isinstance(selected_index_for_radio, int) or selected_index_for_radio >= len(options):
        selected_index_for_radio = 0

    # The radio widget needs the TEXT of the previously selected option, not the index.
    # We find the text corresponding to the stored index.
    # If no answer stored yet (or index invalid), default to the text of the first option.
    try:
        default_option_text = options[selected_index_for_radio]
    except IndexError:
        default_option_text = options[0]

    # Initialize the widget's state in session_state if it doesn't exist
    if widget_key not in st.session_state:
        st.session_state[widget_key] = default_option_text

    # Display the radio button widget
    # Its value will be stored in st.session_state[widget_key]
    st.radio(
        label="Choose your answer:",
        options=options,
        index=options.index(st.session_state[widget_key]),  # Set index based on current widget state
        key=widget_key,  # Crucial for state persistence
        label_visibility="collapsed"
    )
    # Note: The answer index is saved to st.session_state.answers ONLY when 'next_question' is clicked.

    st.divider()

    # --- Navigation Button ---
    button_label = "Next →" if st.session_state.current_question_index < len(questions_data) - 1 else "Show Results!"
    button_type = "secondary" if st.session_state.current_question_index < len(questions_data) - 1 else "primary"
    st.button(button_label, on_click=next_question, type=button_type)

else:
    # --- Display Results ---
    st.balloons()

    # --- Calculate Scores ---
    scores = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0}
    for q_id, selected_index in st.session_state.answers.items():
        if isinstance(selected_index, int) and 0 <= selected_index < len(CATEGORY_KEYS):
            category_key = CATEGORY_KEYS[selected_index]
            scores[category_key] += 1
        else:
            st.warning(
                f"Invalid answer index ({selected_index}) stored for question ID {q_id}. Skipping.")  # Debugging info

    # --- Determine Top Categories ---
    max_score = 0
    if scores:
        valid_scores = [v for v in scores.values() if v > 0]
        if valid_scores:
            max_score = max(valid_scores)

    # --- Display Top Category Details ---
    if max_score > 0:
        top_categories_keys = sorted([k for k, v in scores.items() if v == max_score])

        # Define top category based on the first key in sorted order
        top_category_key = top_categories_keys[0] if top_categories_keys else None

        superpower = categories_info.get(top_category_key, {}).get("superpower", "Unknown Superpower")
        title_placeholder.title(f":orange[ТВОЯ СУПЕРСИЛА: {superpower}]")

        description = categories_info.get(top_category_key, {}).get("description", "No description available.")
        study_raw = categories_info.get(top_category_key, {}).get("study_raw", "No study recommendations available.")
        professions = categories_info.get(top_category_key, {}).get("professions", "No professions listed.")
        name = categories_info.get(top_category_key, {}).get("name", "Unknown")
        type = categories_info.get(top_category_key, {}).get("type", "Unknown")
        emoji = categories_info.get(top_category_key, {}).get("emoji", "❓")
        title = categories_info.get(top_category_key, {}).get("title", "Unknown Title")

        html_content = f"""
        <style>
          .card {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 24px;
            font-family: sans-serif;
            color: #333;
          }}
          .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .5px;
            background: #e0e0e0;
            margin-right: 8px;
          }}
          .emoji {{
            font-size: 48px;
            line-height: 1;
            margin-right: 12px;
            vertical-align: middle;
          }}
          .header-row {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
          }}
          .title {{
            font-size: 48px;
            font-weight: 700;
            margin: 0;
            color: #555;
            vertical-align: middle;
          }}
          .badges-row {{
            margin-bottom: 16px;
          }}
          .description {{
            font-size: 14px;
            line-height: 1.5;
            color: #444;
            margin-bottom: 16px;
            background: #fafafa;
            border-radius: 8px;
            padding: 16px;
          }}
          .superpower {{
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(90deg, #ff8a65, #ff5722);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 16px 0;
          }}
        </style>

        <div class="card">

          <div class="header-row">
            <span class="emoji">{emoji}</span>
            <h2 class="title">{title}</h2>
          </div>

          <div class="badges-row">
            <span class="badge">{name}</span>
            <span class="badge" style="background:#ffe082; color:#5d4037;">{type}</span>
          </div>

          <div class="description">
            {description}
          </div>

          <div style="
              background: #e3f2fd;
              border-radius: 8px;
              padding: 12px;
              margin-bottom:16px;
              font-size:14px;
              font-family:sans-serif;
              color:#1a237e;
          ">Что ботать: {study_raw}</div>

          <div style="
              background: #f1f8e9;
              border-radius: 8px;
              padding: 12px;
              font-size:14px;
              font-family:sans-serif;
              color:#33691e;
          ">Кем стать: {professions}</div>
        </div>
        """

        col1, col2 = st.columns((1, 2))

        # — Left column: image and description
        with col1:
            image_path = os.path.join("images", f"{top_category_key}.png")
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.caption(f"(Image {top_category_key}.png not found)")

        # — Right column: pie chart
        with col2:
            st.markdown(html_content, unsafe_allow_html=True)
        show_pie_chart(scores, background='transparent')

    else:
        st.warning("Hmm, no scores were recorded. Did you answer the questions? 🤔 Try restarting.")

    st.divider()
    DISCLAIMER = """
    **Помни!** Этот тест – твой гайд по миру возможностей 🧭, а не строгий сценарий. Твои интересы могут меняться, как уровни в игре. Главное – не бойся пробовать новое! Удачи!
    """
    st.markdown(f"""

    <div style="background-color: #f0f0f0; padding: 16px; border-radius: 8px;">
        <p style="font-size: 14px; color: #555;">{DISCLAIMER}</p>""", unsafe_allow_html=True)
    # Restart button at the end
    if st.button("🔄 Take Test Again", key="restart_main"):
        restart_test()
