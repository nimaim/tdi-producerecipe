## ProduceRecipe

https://nimaim-tdi-producerecipe-app-hh7ojz.streamlit.app/

### 1. Business Objective

We are eating too much fast food which is resulting in serious health problems such as heart disease, and second, we are contributing to waste on a global scale: a whopping 40% of all food produced is wasted.

By leveraging technologies such as computer vision, ProduceRecipe can accurately transform produce ingredients into something you can make at home and not have to feel guilty about eating! 


### 2. Data Ingestion

Ten fruit/vegetable datasets were acquired on Kaggle totaling ~25GB and merged/cleaned. Links to these can be found in the notebook.

Furthermore, web scraping through Selenium and BS4 was done to parse and extract all the recipes from Google / Bing search headers.

Finally, to go to a specific website and scrape that recipe, a JSON parser to parse JSON-LD was used.

### 3. Visualizations

Several visualizations are available in the notebook. 

This includes a Matplotlib figure of one sample image per class, class distribution to see the class imbalances, Keras accuracy/loss plot, metrics such as classfiication report / confusion matrix, and more.


### 4a. Machine Learning


This project involves a softmax classification using a CNN model built on top of ResNetV2 and utilizing transfer learning.

Tensorflow (Keras API) was used to build and train the model.

### 4b. Distributed Computing

N/A


### 4c. Interactive Website

Streamlit was used to build and serve the application, whose link you can find on top of this page.


### 5. Deliverable

Deliverable is in the form of this repository which contains this README, link to the interactive website, and commented Jupyter notebook.

The trained model and list of classes is also available in this repository so anyone can use it out of the box.
