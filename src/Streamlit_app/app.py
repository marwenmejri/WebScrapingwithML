from utils import cleaning_utils, data_utils

import spacy_streamlit
import streamlit as st


# URL = 'https://www.wanimo.com/fr/chats/alimentation-pour-chat-sc6/lily-s-kitchen-tasty-cuts-sf22308/'
# WEBSITE = 'Wanimo'


def get_html_text(url, data: dict):
    cleaned_html = cleaning_utils.collect_relevant_html(url=url, tag=data['tag'], attribute=data['attribute'],
                                                        attribute_value=data['attribute_value'])
    if cleaned_html:
        return str(cleaned_html)
    else:
        return None


st.set_page_config(page_title="WebScrapingML", page_icon="natural-language-processing.png", layout="wide",
                   initial_sidebar_state="collapsed")
st.title("Make Predictions with Trained NER-large-Model")

spacy_models = ["../../Models/larger_model0/model-best", "../../Models/larger_model1/model-best"]
selected_model = st.sidebar.selectbox('Which Model do you like to use?', spacy_models)

entered_website = st.text_input(label="Please enter a Valid Website name")
meta_data = data_utils.load_data(file='meta-data.json')
# print(meta_data[entered_website])

if entered_website:
    if entered_website in list(meta_data.keys()):
        data = meta_data[entered_website]
        st.success("The Website entered is valid")
    else:
        st.error("Please enter a correct website url")

entered_url = st.text_input(label="Url to extract Data from")
if entered_url:
    html_text = get_html_text(url=entered_url, data=meta_data[entered_website])
    # print(html_text)
    if html_text:
        st.success("Succeeded to extract Html data from the given URL")
        button_analyse = st.button("make detections")
        if button_analyse:
            doc = spacy_streamlit.process_text(selected_model, html_text)

            predictions = [{ent.label_: ent.text} for ent in doc.ents]
            new_dict = {}
            for pred in predictions:
                if list(pred.keys())[0] not in list(new_dict.keys()):
                    new_dict[list(pred.keys())[0]] = [list(pred.values())[0]]
                else:
                    new_dict[list(pred.keys())[0]].append(list(pred.values())[0])
            for key, value in new_dict.items():
                new_dict[key] = set(value)
            st.json(body=new_dict)

            spacy_streamlit.visualize_ner(
                doc,
                labels=["NAME", "CHAINBRAND", "PRICE", "GTIN"],
                show_table=False,
                title="Rendered Html text with results",
                colors={'NAME': "#85C1E9", "CHAINBRAND": "#B3C100", "GTIN": "#5D535E", "PRICE": "#F52549"}
            )
            st.success(f"Analyzed using spaCy model {selected_model}")
    else:
        st.error("Please enter a valid url")

