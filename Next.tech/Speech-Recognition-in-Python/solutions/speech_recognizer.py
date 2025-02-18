import os
import argparse 

import numpy as np
from scipy.io import wavfile 
from hmmlearn import hmm
from python_speech_features import mfcc

# Ignore DeprecationWarning for function log_multivariate_normal_density
import warnings
warnings.filterwarnings("ignore")




# Function to parse input arguments
def build_arg_parser():
    parser = argparse.ArgumentParser(description='Trains the HMM classifier')
    parser.add_argument("--input-folder", dest="input_folder", required=True,
            help="Input folder containing the audio files in subfolders")
    return parser

#Let's initialize the class. We will use Gaussian HMMs to model our data. The n_components parameter defines the number of hidden states. The cov_type defines the type of covariance in our transition matrix, and n_iter indicates the number of iterations it will go through before it stops training:

#The choice of the preceding parameters depends on the problem at hand. You need to have an understanding of your data in order to select these parameters in a smart way. Initialize the variables:

#We built a class to handle HMM training and prediction, but we need some data to see it in action. We will use it in the next step to build a speech recognizer.

# Class to handle all HMM related processing
class HMMTrainer(object):
    def __init__(self, model_name='GaussianHMM', n_components=4, cov_type='diag', n_iter=1000):
        self.model_name = model_name
        self.n_components = n_components
        self.cov_type = cov_type
        self.n_iter = n_iter
        self.models = []

        if self.model_name == 'GaussianHMM':
            self.model = hmm.GaussianHMM(n_components=self.n_components, 
                    covariance_type=self.cov_type, n_iter=self.n_iter)
        else:
            raise TypeError('Invalid model type')

    # X is a 2D numpy array where each row is 13D
    def train(self, X):
        np.seterr(all='ignore')
        self.models.append(self.model.fit(X))

    # Run the model on input data
    def get_score(self, input_data):
        return self.model.score(input_data)

if __name__=='__main__':
    args = build_arg_parser().parse_args()
    input_folder = args.input_folder

    hmm_models = []

    # Parse the input directory
    for dirname in os.listdir(input_folder):
        # Get the name of the subfolder 
        subfolder = os.path.join(input_folder, dirname)

        if not os.path.isdir(subfolder): 
            continue

        # Extract the label. The name of the subfolder is the label of this class. Extract it using the following:
        label = subfolder[subfolder.rfind('/') + 1:]

        # Initialize variables
        X = np.array([])
        y_words = []

        # Iterate through the audio files (leaving 1 file for testing in each class)
        for filename in [x for x in os.listdir(subfolder) if x.endswith('.wav')][:-1]:
            # Read the input file
            filepath = os.path.join(subfolder, filename)
            sampling_freq, audio = wavfile.read(filepath)
            
            # Extract MFCC features
            mfcc_features = mfcc(audio, sampling_freq)

            # Append to the variable X
            if len(X) == 0:
                X = mfcc_features
            else:
                X = np.append(X, mfcc_features, axis=0)
            
            # Append the label
            y_words.append(label)

        print('X.shape =', X.shape)
        
        #Once you have extracted features from all the files in the current class, train and save the HMM model. As HMM is a generative model for unsupervised learning, we don't need labels to build HMM models for each class. We explicitly assume that separate HMM models will be built for each class:
        # Train and save HMM model
        hmm_trainer = HMMTrainer()
        hmm_trainer.train(X)
        hmm_models.append((hmm_trainer, label))
        hmm_trainer = None

    # Test files
    input_files = [
            'data/pineapple/pineapple15.wav',
            'data/orange/orange15.wav',
            'data/apple/apple15.wav',
            'data/kiwi/kiwi15.wav'
            ]

    # Classify input data
    for input_file in input_files:
        # Read input file
        sampling_freq, audio = wavfile.read(input_file)

        # Extract MFCC features
        mfcc_features = mfcc(audio, sampling_freq)

        # Define variables
        max_score = float("-inf")
        output_label = 'None'

        # Iterate through all HMM models and pick 
        # the one with the highest score
        for item in hmm_models:
            hmm_model, label = item
            # print(hmm_model)
            # print(label)
            score = hmm_model.get_score(mfcc_features)
            # print(score)
            if score > max_score:
                max_score = score
                output_label = label

        # Print the output
        print("\nTrue:", input_file[input_file.find('/')+1:input_file.rfind('/')])
        print("Predicted:", output_label) 

