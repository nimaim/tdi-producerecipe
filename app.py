import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import random
import time
from st_aggrid import AgGrid, \
    GridOptionsBuilder, GridUpdateMode, JsCode

import model_helper as mh
import scraper

# Main title headers
# st.set_page_config(layout="wide")
st.title("ProduceRecipe")
st.markdown("Welcome to this simple web application that classifies produce and pulls a vegetarian recipe "
            "which incorporates it. The app utilizes a deep learning model that builds on top of ResNetV2, "
            "as well as Selenium for scraping, Streamlit for the UI, and a lot more under the hood.")

# Sidebar title headers
st.sidebar.title("User Interaction Panel")
class_names = mh.get_classes('resnetv2_250_cls_92_acc.json')
with st.sidebar.expander("List of classes:"):
    st.dataframe(pd.DataFrame.from_dict(class_names, orient='index', columns=['Class']),
                 use_container_width=True)

# Footer
hide_st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
# MainMenu {visibility: hidden;}
# header {visibility: hidden;}
st.markdown(hide_st_style, unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)
def load_resnet_model():
    loaded_model = mh.load_saved_model('resnetv2_250_cls_92_acc.hdf5')
    return loaded_model


def create_image_grid(len_images, n_cols):
    n_rows = 1 + len_images // int(n_cols)
    rows = [st.container() for _ in range(n_rows)]
    cols_per_row = [r.columns(n_cols) for r in rows]

    return [column for row in cols_per_row for column in row]


@st.experimental_memo(suppress_st_warning=True)
def process_predictions_to_df(pred_dict):

    def calc_confidence(row):
        if row['probability'] < 0.33:
            return 'Low'
        elif 0.33 <= row['probability'] <= 0.66:
            return 'Medium'
        else:
            return 'High'

    df = pd.DataFrame(pred_dict)
    df['probability'] = df['probability'].astype(float)
    df['confidence'] = df.apply(calc_confidence, axis=1)

    return df


@st.cache(allow_output_mutation=True)
def scrape_recipes(pred_dict, cuisine_opt, engine_opt, limit_opt, ignore_opt):

    def filter_preds():
        for idx, prob in enumerate(pred_dict['probability']):
            if float(prob) < 0.33:
                del pred_dict['filename'][idx]
                del pred_dict['prediction'][idx]
                del pred_dict['probability'][idx]

    if ignore_opt:
        filter_preds()

    if engine_opt == 'Google':
        recipe_dict = scraper.scrape_recipes_google(pred_dict['prediction'], cuisine_opt)
    else:
        recipe_dict = scraper.scrape_recipes_bing(pred_dict['prediction'], cuisine_opt, limit_opt)
    return recipe_dict


@st.experimental_memo(suppress_st_warning=True)
def process_recipes_to_df(recipe_dict, filter_opt):

    df = pd.DataFrame(recipe_dict)

    # Drop columns we won't be using
    df = df.drop(['servings', 'ingredients'], axis=1, errors='ignore')

    # Fill all NAs with 'None'
    # df = df.fillna(np.nan).replace([np.nan], [None])

    # Convert total_time hr min text to minutes
    h = df['total_time'].str.extract('(\d+)\s+hr').astype(float).mul(60)
    m = df['total_time'].str.extract('(\d+)\s+min').astype(float)
    df['total_time'] = h.add(m, fill_value=0)

    # Extract only the digits from calories
    if 'calories' in df.columns:
        df['calories'] = df['calories'].str.extract('(^\d*)')

    # Remove the 'reviews' text, and expand the thousands of reviews designated by k or K
    df['reviews'] = df[df['reviews'].notnull()]['reviews'] \
        .apply(lambda x: x.split()[0]) \
        .replace({'K': '*1e3', 'k': '*1e3'}, regex=True) \
        .map(pd.eval).astype(int)

    # Convert all ratings to float type
    df['ratings'] = df['ratings'].astype(float) / 1.0

    if filter_opt == 'Popularity':
        df = df.dropna(subset=['reviews'])\
            .sort_values(by='reviews', ascending=False)\
            .astype({'reviews': 'int32'})\
            .reset_index(drop=True)
    elif filter_opt == 'Calories':
        if 'calories' in df.columns:
            df = df.dropna(subset=['calories'])\
                .astype({'calories': 'int32'})\
                .sort_values(by='calories')\
                .reset_index(drop=True)
    elif filter_opt == 'Time':
        df = df.dropna(subset=['total_time'])\
            .astype({'total_time': 'int32'})\
            .sort_values(by='total_time').reset_index(drop=True)

    return df


def build_and_configure_aggrid(df):
    # st.dataframe(recipe_df, use_container_width=True)
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)

    cell_renderer = JsCode("""
    function(params) {return `<a href=${params.data.link} target="_blank">${params.value}</a>`}
    """)

    gd.configure_column('title', cellRenderer=cell_renderer)
    gd.configure_column('link', hide='True')
    gd.configure_selection(selection_mode='single', use_checkbox=True)
    grid_options = gd.build()

    return grid_options
    # st.write(recipes_df.to_html(escape=False, index=False), unsafe_allow_html=True)


# NOTE: There is no entry point for a streamlit app, the entire script will re-run on any UI interaction
def main():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(f'---{current_time}: SCRIPT START ---')

    # Define initial session states
    if 'classify_btn_clicked' not in st.session_state:
        st.session_state.classify_btn_clicked = False

    if 'scrape_btn_clicked' not in st.session_state:
        st.session_state.scrape_btn_clicked = False

    if 'results_btn_clicked' not in st.session_state:
        st.session_state.results_btn_clicked = False

    # Define session state callbacks
    def classify_click_cb():
        st.session_state.classify_btn_clicked = True

    def scrape_click_cb():
        st.session_state.scrape_btn_clicked = True

    def results_click_cb():
        st.session_state.results_btn_clicked = True

    with st.spinner('Loading model...'):
        loaded_model = load_resnet_model()

    pred_dict = {
        'filename': [],
        'prediction': [],
        'probability': []
    }
    image_list = []

    # Disable warning
    st.set_option('deprecation.showfileUploaderEncoding', False)

    with st.sidebar.form(key='uploader_form'):
        st.subheader("Step 1: Classify")

        uploaded_files = st.file_uploader("Upload image(s) of produce:",
                                          type=["jpg", 'jpeg', "png"],
                                          accept_multiple_files=True,
                                          key='file_uploader')
        st.caption('Note: Not all images can be processed due to encoding.')
        classify_btn = st.form_submit_button("Classify Images",
                                             on_click=classify_click_cb)

    if uploaded_files:
        grid = create_image_grid(len(uploaded_files), 3)

        for idx, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            image_list.append(image)

            grid[idx].image(image, caption=f'Image #{idx}:\n{uploaded_file.name}')
            pred_dict['filename'].append(uploaded_file.name)

    if classify_btn or st.session_state.classify_btn_clicked:
        if not image_list:  # This will only be populated if images were uploaded
            st.sidebar.warning('Please upload image(s) first!')
        else:
            for idx, single_image in enumerate(image_list):
                cur_pred, cur_prob = mh.predict(single_image, loaded_model, class_names)
                pred_dict['prediction'].append(cur_pred)
                pred_dict['probability'].append(f'{cur_prob:.4f}')

            pred_df = process_predictions_to_df(pred_dict)
            st.dataframe(pred_df, use_container_width=True)

            #time.sleep(1)
            st.success('Image classification successful!')

    with st.sidebar.form(key='scraper_form'):
        st.subheader("Step 2: Scrape")

        ignore_option = st.checkbox("Ignore 'Low' confidence classifications", value=True)

        engine_option = st.radio(
            'Select search engine:',
            options=('Google', 'Bing')
        )
        st.caption('Use Google for accuracy, Bing for more variety.')

        limit_option = st.select_slider(
            'Select max recipes to scrape:',
            options=[i for i in range(15, 505, 5)],
            value=15,
            key='limit_slider'
        )
        st.caption('Note: Option is ignored for Google as it only returns 15 recipes, Bing returns ~500.\n'
                   'Lower number will speed up Bing scraping.')

        col1, col2 = st.columns(2)
        with col1:
            cuisine_option = st.selectbox(
                'Select cuisine type:',
                options=('Any', 'Indian', 'Mexican', 'Chinese', 'Italian'),
            )

        with col2:
            filter_option = st.selectbox(
                'Sort by:',
                options=('None', 'Popularity', 'Calories', 'Time'),
            )

        scrape_btn = st.form_submit_button("Scrape Recipes",
                                           on_click=scrape_click_cb)
        # st.write('\n')

    if scrape_btn or st.session_state.scrape_btn_clicked:
        if not st.session_state.classify_btn_clicked:
            st.sidebar.warning('Please classify image(s) first!')
            st.session_state.scrape_btn_clicked = False
        else:
            recipe_dict = scrape_recipes(pred_dict, cuisine_option, engine_option, limit_option, ignore_option)
            recipe_df = process_recipes_to_df(recipe_dict, filter_option)
            row_idx = recipe_df.head(15).sample(frac=1.0, random_state=111).head(1).index.tolist()[0]

            # Display some images
            st.subheader("Sample of scraped recipes:")
            grid2 = create_image_grid(6, 3)

            for idx in range(6):
                grid2[idx].image(recipe_dict['image'][idx], caption=f"{recipe_dict['title'][idx]}")

            st.success('Recipe scraping successful!')
            st.info('Please proceed to Step 3 to display complete results.')

    with st.sidebar.form(key='results_form'):
        st.subheader("Step 3: Display")

        results_btn = st.form_submit_button("Show Recipes", on_click=results_click_cb)
        hungry_check = st.checkbox("I'm Feeling Hungry", value=True)
        st.caption('Click button to display results and a recipe title to go to a recipe in a new window. '
                   'Additionally, check option to instantly pick and display a random recipe on the current page.')

    if results_btn or st.session_state.results_btn_clicked:
        if not st.session_state.scrape_btn_clicked:
            st.sidebar.warning('Please scrape image(s) first!')
            st.session_state.results_btn_clicked = False
        else:

            gb = GridOptionsBuilder.from_dataframe(recipe_df)
            gb.configure_pagination(enabled=True)
            gb.configure_column('title', cellRenderer=JsCode("""
            function(params) {return `<a href=${params.data.link} target="_blank">${params.value}</a>`}
            """))
            gb.configure_column('link',  hide='True')
            gb.configure_column('image', hide='True')

            # TODO: Do NOT pick something with number in title that we won't be able to parse json for
            if hungry_check:
                gb.configure_selection(selection_mode='single',
                                       use_checkbox=True,
                                       pre_selected_rows=[row_idx])
            else:
                gb.configure_selection(selection_mode='single', use_checkbox=False)

            aggrid_options = gb.build()
            aggrid_table = AgGrid(recipe_df,
                                  fit_columns_on_grid_load=True,
                                  gridOptions=aggrid_options,
                                  update_mode=GridUpdateMode.SELECTION_CHANGED,
                                  allow_unsafe_jscode=True,
                                  theme='streamlit')

            if hungry_check:
                sel_row = aggrid_table.selected_rows

                if sel_row:
                    st.write(sel_row)
                    json_ld = scraper.get_recipe_json(sel_row[0]['link'])
                    if json_ld:
                        scraper.parse_recipe_json(json_ld)
                    else:
                        st.error('JSON-LD script not found on page, try another recipe.')

            st.success('Done! ProduceRecipe successful!')


if __name__ == "__main__":
    main()
