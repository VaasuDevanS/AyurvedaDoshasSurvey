"""
Author: Vaasudevan Srinivsan <vaasuceg.96@gmail.com>
Created: Oct 10, 2024
Modified: Oct 24, 2024
References:
    - https://docs.streamlit.io/develop/tutorials/databases/private-gsheet
"""

from collections import Counter
from copy import deepcopy
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
        total_ques = len(questions['questions'])

    ques_desc = [q.popitem()[0] for q in deepcopy(questions['questions'])]
    # for q in ques_desc:
    #     print(q)

    responses = {
        'name': st.text_input('Name:red[*]', placeholder='Enter your name'),
        'answers': {},
    }
    answer_keys = {}
    for ix, ques in enumerate(deepcopy(questions['questions']), start=1):
        ques_label, options = ques.popitem()
        answer_keys[ix] = options = {v: k for k, v in options.items() if v is not None}
        responses['answers'][ix] = st.radio(
            f'{ix}.) {ques_label}', options.keys(), index=None
        )

    # https://discuss.streamlit.io/t/delete-widgets/7596/5
    placeholder = st.empty()
    submitted = placeholder.form_submit_button('Submit your response')

    if submitted and not responses['name']:
        st.error('Please enter your name')

    if submitted and responses['name']:
        placeholder.empty()
        st.form_submit_button('Submitted', disabled=True)

        # Stats
        categories = []
        answers_with_cat = []
        for ix, answer in responses['answers'].items():
            if answer is not None:
                categories.append(answer_keys[ix][answer])
                answers_with_cat.append(f'{answer} ({categories[-1]})')
            else:
                answers_with_cat.append(None)
        cat_counts = Counter(categories)

        # Save to Google Sheet
        conn = st.connection('gsheets', type=GSheetsConnection)
        df = conn.read(worksheet='Responses')
        df.loc[len(df.index)] = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            responses['name'],
            len(categories),
            cat_counts['Pitta'],
            cat_counts['Vata'],
            cat_counts['Kapha'],
            cat_counts['No Dosha'],
            *answers_with_cat,
        ]
        conn.update(worksheet='Responses', data=df)
        st.cache_data.clear()

        st.success(f'Thanks "{responses["name"]}" for completing the survey!')
        st.write(f'You answered {len(categories)} out of {total_ques} questions')
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
