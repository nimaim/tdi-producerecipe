import streamlit as st
import pandas as pd
from PIL import Image
import time, random
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

import model_helper as mh
import recipe_scraper as scraper
import recipe_parser as parser

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
        df = df.dropna(subset=['reviews']) \
            .astype({'reviews': 'int32'}) \
            .sort_values(by='reviews', ascending=False)\
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
            .sort_values(by='total_time')\
            .reset_index(drop=True)

    return df


def build_and_configure_aggrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_selection(selection_mode='disabled', use_checkbox=False)
    gb.configure_column('title', cellRenderer=JsCode("""
    function(params) {return `<a href=${params.data.link} target="_blank">${params.value}</a>`}
    """))
    gb.configure_column('link', hide='True')
    gb.configure_column('image', hide='True')

    grid_options = gb.build()

    return grid_options


def print_recipe(recipe_item):
    if recipe_item.name:
        st.subheader(recipe_item.name)
    if recipe_item.image:
        st.image(recipe_item.image)
    if recipe_item.description:
        st.write(recipe_item.description)
    if recipe_item.author:
        st.write(recipe_item.author)
    if recipe_item.servings:
        st.write(recipe_item.servings)
    if recipe_item.ingredients:
        st.markdown(recipe_item.ingredients)
    if recipe_item.instructions:
        st.write(recipe_item.instructions)
    if recipe_item.nutrition:
        st.write(recipe_item.nutrition)


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

    if 'random_number' not in st.session_state:
        st.session_state.random_number = -1

    # Define session state callbacks
    def classify_click_cb():
        st.session_state.classify_btn_clicked = True

    def scrape_click_cb():
        st.session_state.scrape_btn_clicked = True

    def results_click_cb():
        st.session_state.random_number = random.randint(0, 14)
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
            # st.session_state.recipe_df = process_recipes_to_df(recipe_dict, filter_option)

            # Display some images
            st.subheader("Sample of scraped recipes:")
            grid2 = create_image_grid(6, 3)

            for idx in range(6):
                grid2[idx].image(recipe_dict['image'][idx], caption=f"{recipe_dict['title'][idx]}")

            st.success('Recipe scraping successful!')
            st.info('Please proceed to Step 3 to display complete results.')

    with st.sidebar.form(key='results_form'):
        st.subheader("Step 3: Display")

        results_btn = st.form_submit_button("Show Recipe(s)", on_click=results_click_cb)
        hungry_check = st.checkbox("I'm Feeling Hungry", value=False)
        st.caption('Click button to display results table and a recipe title to go to recipe in a new window. '
                   'Check option to bypass results and display a randomly selected recipe on the current page.')

    if results_btn or st.session_state.results_btn_clicked:
        if not st.session_state.scrape_btn_clicked:
            st.sidebar.warning('Please scrape image(s) first!')
            st.session_state.results_btn_clicked = False
        else:
            # TODO: Do NOT pick something with number in title that we won't be able to parse json for
            if hungry_check:
                # Display a random recipe on the page
                recipe_filled = False

                while not recipe_filled:
                    row_idx = recipe_df.head(100).sample().index.tolist()[0]
                    print(row_idx, recipe_df.loc[row_idx, 'title'])
                    json_ld = scraper.get_recipe_json(recipe_df.loc[row_idx, 'link'])
                    if not json_ld:
                        continue
                    recipe_item = parser.RecipeItem(json_ld)
                    # TODO: This assumes at least one recipe will parse, fix to add max retries
                    recipe_filled = recipe_item.fill_values()

                if recipe_item.name:
                    with st.container():
                        print_recipe(recipe_item)
                    st.success('Done! Recipe produced successfully!')
                    # st.snow()
                else:
                    st.error('Error parsing JSON-LD script, try another recipe.')

            else:
                # Display the entire table of recipes
                aggrid_options = build_and_configure_aggrid(recipe_df)
                aggrid_table = AgGrid(recipe_df,
                                      fit_columns_on_grid_load=True,
                                      gridOptions=aggrid_options,
                                      update_mode=GridUpdateMode.SELECTION_CHANGED,
                                      allow_unsafe_jscode=True,
                                      theme='streamlit')

                st.success('Done! Recipes produced successfully!')
                # st.snow()


if __name__ == "__main__":
    main()
