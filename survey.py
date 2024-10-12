"""
Author: Vaasudevan Srinivsan <vaasuceg.96@gmail.com>
Created: Oct 10, 2024
Modified: Oct 12, 2024
References:
    - https://docs.streamlit.io/develop/tutorials/databases/private-gsheet
"""

import re
from collections import Counter
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
import yaml
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title='Ayurveda Doshas Survey')

st.markdown(
    "<h1 style='text-align: center;'>Ayurveda Doshas Survey</h1>",
    unsafe_allow_html=True,
)
st.image('header.jpg')

with st.form('survey_form'):
    with open('questions.yml', 'r') as file:
        questions = yaml.safe_load(file)

    responses = {
        'name': st.text_input('Name:red[*]', placeholder='Enter your name'),
        'answers': {},
    }
    for ix, ques in enumerate(questions['questions'], start=1):
        ques_label, options = ques.popitem()
        options = [f'{v} ({k})' for k, v in options.items() if v is not None]
        responses['answers'][ix] = st.radio(f'{ix}.) {ques_label}', options, index=None)

    def disable_button():
        st.session_state.submitted = True

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    submitted = st.form_submit_button(
        'Submit your response',
        on_click=disable_button,
        disabled=st.session_state.submitted,
    )

    if submitted:
        if not responses['name']:
            st.error('Please enter your name')

        else:
            # Stats
            answers = [r for r in responses['answers'].values() if r is not None]
            categories = [re.findall(r'\((.*?)\)', answer)[0] for answer in answers]
            cat_counts = Counter(categories)

            # Save to Google Sheet
            conn = st.connection('gsheets', type=GSheetsConnection)
            df = conn.read(worksheet='Responses')
            df.loc[len(df.index)] = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                responses['name'],
                len(answers),
                cat_counts['Pitta'],
                cat_counts['Vata'],
                cat_counts['Kapha'],
                *responses['answers'].values(),
            ]
            conn.update(worksheet='Responses', data=df)
            st.cache_data.clear()

            st.success(f'Thanks {responses["name"]} for completing the survey!')
            st.write(f'You answered {len(answers)} out of 29 questions')
            st.write(cat_counts)

            cat_counts_df = pd.DataFrame(
                cat_counts.items(), columns=['Doshas', '#Questions']
            )
            pie_chart = (
                alt.Chart(cat_counts_df)
                .mark_arc()
                .encode(
                    theta=alt.Theta(field='#Questions', type='quantitative'),
                    color=alt.Color(field='Doshas', type='nominal'),
                    tooltip=['Doshas', '#Questions'],
                )
            )
            st.altair_chart(pie_chart, use_container_width=True)
