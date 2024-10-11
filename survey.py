"""
Author: Vaasudevan Srinivsan <vaasuceg.96@gmail.com>
Created: Oct 10, 2024
Modified: Oct 11, 2024
Description: Script that contains the Survey Questionaire
References:
    - https://docs.streamlit.io/develop/tutorials/databases/private-gsheet
"""

import re
from collections import Counter

import pandas as pd
import streamlit as st
import yaml


def save_responses(responses):
    df = pd.DataFrame(responses)
    df.to_csv('survey_responses.csv', index=False)


st.title('Ayurveda Doshas Survey')

with st.form('survey_form'):

    with open('questions.yml', 'r') as file:
        questions = yaml.safe_load(file)

    responses = {'name': st.text_input('Your Name:'),
                 'answers': {},
                 }
    for ix, ques in enumerate(questions['questions'], start=1):
        ques_label, options = ques.popitem()
        options = [f'{v} ({k})' for k, v in options.items() if v is not None]
        responses['answers'][ix] = st.radio(f'{ix}.) {ques_label}', options, index=None)
    submitted = st.form_submit_button('Submit')

    if submitted:
        st.success(f'Thanks {responses['name']} for completing the survey!')
        answers = [r for r in responses['answers'].values() if r is not None]
        categories = [re.findall(r'\((.*?)\)', answer)[0] for answer in answers]
        st.write(f'You answered {len(answers)} out of 29 questions')
        st.write(Counter(categories))
