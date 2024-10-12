"""
Author: Vaasudevan Srinivsan <vaasuceg.96@gmail.com>
Created: Oct 10, 2024
Modified: Oct 12, 2024
References:
    - https://docs.streamlit.io/develop/tutorials/databases/private-gsheet
"""

import re
from collections import Counter

import streamlit as st
import yaml
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title='Ayurveda Doshas Survey')
st.title('Ayurveda Doshas Survey')

with st.form('survey_form'):
    with open('questions.yml', 'r') as file:
        questions = yaml.safe_load(file)

    responses = {
        'name': st.text_input('Your Name:'),
        'answers': {},
    }
    for ix, ques in enumerate(questions['questions'], start=1):
        ques_label, options = ques.popitem()
        options = [f'{v} ({k})' for k, v in options.items() if v is not None]
        responses['answers'][ix] = st.radio(f'{ix}.) {ques_label}', options, index=None)
    submitted = st.form_submit_button('Submit your responses')

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
