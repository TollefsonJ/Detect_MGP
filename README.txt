Hi, thanks for checking out my project!

This repo includes notebooks to train and test CNN and MLP machine learning models to predict the presence of manufactured gas plants (MGP) in historic Sanborn fire insurance maps. It also includes notebooks to download new Sanborn maps using the Library of Congress' (LOC) api, and produce MGP predictions using an ensemble of multiple CNN and MLP models.

I'm now working on running this method to extract coal gas site data for the US. If you think this is interesting and would like to collaborate, feel free to get in touch!

This folder:
1: trains MLP and CNN models using full training dataset (under ML_training/training_data), and saves models to ML_models. Trained models are already included with this repo; only run this script if you want to reproduce the full model training process.
2: downloads new maps for analysis using LOC api
3: uses trained models to generate predictions on new LOC maps

ML_training folder:
1: trains MLP and CNN models using a 5-fold cross-validation process, saves training models and test data under "saved_models"
2: evaluates training/testing results using training models and test data produced above
