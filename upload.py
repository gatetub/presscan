



import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import os

import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import re
import pickle
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

stop_words = stopwords.words('english')
stemmer = SnowballStemmer('english')

text_cleaning_re = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"
path="Disease_symptom_and_patient_profile_dataset.csv"
df=pd.read_csv(path)
labels_array = df['Disease'].to_numpy()
from sklearn.preprocessing import LabelEncoder

# Assuming 'original_labels' is a list or NumPy array containing your original labels
label_encoder = LabelEncoder()
label_encoder.fit(labels_array)

# Now, you can use the fitted label encoder to transform and inverse transform labels
encoded_labels = label_encoder.transform(labels_array)

# To convert back to original labels from encoded labels
decoded_labels = label_encoder.inverse_transform(encoded_labels)

from flask import Flask, request, render_template,redirect
from PIL import Image
import pytesseract
import re
import pickle  # Import necessary libraries
import spacy
from spacy.matcher import Matcher
from nltk.tokenize import word_tokenize, sent_tokenize
import joblib

model1=joblib.load(open('disease1.joblib','rb'))
nlp = spacy.load("en_core_web_sm")
# Define stop_words, text_cleaning_re, stemmer, and other necessary variables here

app = Flask(__name__)
def intoken(text1):
  text1=text1.lower()
  words = text1.split()
  return(words)

def clean( text):
  text = re.sub(text_cleaning_re, ' ', str(text).lower()).strip()
  stem = False
  tokens = []
  for token in text.split():
     if token not in stop_words:
           if stem:
               tokens.append(stemmer.stem(token))
           else:
               tokens.append(token)
               processed_text = " ".join(tokens)
  return processed_text

def fever(tokentext):
  f="fever"
  if f in tokentext:
    return "Yes"
  else:

   return "No"


def cough(tokentext):
  c="cough"
  if c in tokentext:
    return "Yes"
  else:
    print(f"'{c}' not found in the string.")
  return "No"

def fatigue(tokentext):
  f="cough"
  if f in tokentext:
    return "Yes"
  else:
    return "No"

def extract_breathing_issues(tokentext):
    doc = nlp(tokentext)

    breathing_sentences = []


    for sentence in doc.sents:
        if 'breath' in sentence.text.lower() or 'breathe' in sentence.text.lower() or 'respiratory' in sentence.text.lower():
            breathing_sentences.append(sentence.text)

    return breathing_sentences

def breathing(text):
  breathing_issues = extract_breathing_issues(text)
  flag=0
  if breathing_issues:
    return "Yes"
  else:
    return "No"


def age(text):
  # Load the English NLP model
 nlp = spacy.load("en_core_web_sm")

# Create a Matcher object
 matcher = Matcher(nlp.vocab)

# Define a pattern for identifying age
 age_pattern = [{"IS_DIGIT": True}, {"LOWER": {"in": ["years", "yrs", "years old","age","y","AGE","Age"]}}]

# Add the pattern to the matcher
 matcher.add("AGE", [age_pattern])

# Process a text

 doc = nlp(text)

# Use the matcher to find matches
 matches = matcher(doc)

# Extract information about age
 for match_id, start, end in matches:
    if match_id == nlp.vocab.strings["AGE"]:
        age_text = doc[start:end].text
        g=age_text
        return(f"Age: {age_text}")

def categorize_blood_pressure(systolic, diastolic):
    if systolic < 90 or diastolic < 60:
        return "Low"
    elif systolic > 120 or diastolic > 80:
        return "High"
    else:
        return "Normal"

def blood_p(text):
 pattern = re.compile(r'(\d+/\d+\s?mmHg)')

 matches = pattern.findall(text)
 if matches!=" ":
     pattern2 = re.compile(r'(\d+/\d+\s?)')
     matches2 = pattern2.findall(text)
 else:
     return "UPLoad valid prescription"
# Output the result
 if matches2:
    for value in matches2:
        print("Blood Pressure:", value)
 else:
    print("No blood pressure values found in the text.")

 systolic, diastolic = map(int, value.split('/'))
 category = categorize_blood_pressure(systolic, diastolic)
 return category

def extract_cholesterol(text):
    # Use regular expression to find patterns related to cholesterol
    # Examples: Cholesterol: 150 mg/dL, Cholesterol: 200mg/dl, etc.
    pattern = re.compile(r'(\d+\s?mg/dL)')
    matches = pattern.findall(text)
    return matches

def deterchol(numeric_value):
  if (numeric_value<200 or numeric_value>40):
    return("Normal")
  elif (numeric_value<40):
    return("Low")
  else:
    return("High")

def cholestrol(text):
  value=""
  cholesterol_values = extract_cholesterol(text)

  if cholesterol_values:
    for value in cholesterol_values:
        print( value)
  else:
    print("No cholesterol values found in the text.")

  numeric_value = re.search(r'\d+(\.\d+)?', value).group()
  chol=deterchol(int(numeric_value))
  return chol
# Function to replace values based on the dictionary
def gender(text):
  gender_pattern = re.compile(r'\b(?:male|female|M|F)\b', re.IGNORECASE)
  genders_found = gender_pattern.findall(text)
  return genders_found[0]

def replace(value, dictionary):
    return dictionary.get(value, value)

def pred(input_data):
 model1=joblib.load(open('disease1.joblib','rb'))
 input_data_as_numpy=np.asarray(input_data)
 #input_data_as_numpy.shape
 input_data_reshaped=input_data_as_numpy.reshape(1,-1)
 #input_data_reshaped.shape
 prediction=model1.predict(input_data_reshaped)
 output = round(prediction[0], 2)

 return decoded_labels[output]


# HTML form to upload an image
@app.route('/')
def index():
    return '''
    <h>Upload Prescription Here</h><p>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form><p>
    '''

# Route to handle image upload and perform OCR
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:

        # Save the uploaded image temporarily
        img = Image.open(file)
        text = pytesseract.image_to_string(img)

    pt=clean(text)
    tokentext=intoken(pt)



    FVR=fever(tokentext)
    CGH=cough(tokentext)
    FTG=fatigue(tokentext)
    DB=breathing(text)
    AGE=age(text)
    GND=gender(text)
    BP=blood_p(text)
    CHL=cholestrol(text)
    outcome="Positive"

    add=""
    for x in AGE:
     if (x.isdigit()):
      add=add+x

    Age=add



    #dicc = { 'Yes': 1, 'No': 0, 'Low': 1, 'Normal': 2, 'High': 3,'Positive': 1, 'Negative': 0, 'Male': 0, 'Female': 1}
    dicc = {
    'Yes': '1', 'No': '0', 'Low': '1', 'Normal': '2', 'High': '3',
    'Positive': '1', 'Negative': '0', 'Male': '0', 'Female': '1'}

     # Input data
    input_data=[FVR,CGH,FTG,DB,Age,GND,BP,CHL,outcome]
    #input_data = ["Yes", "Yes", "No", "Yes", "25", "Male", "Normal", "Normal", "Positive"]
    input_data = [replace(y, dicc) for y in input_data]

    # Process input_data using the replace function
    #input=["1","0","0","0","30","1","2","2","0"]
    lol1 =pred(input_data)
    #return lol1
    return render_template('port.html',fo="{}".format(FVR),cg="{}".format(CGH),ft="{}".format(FTG),dibe="{}".format(DB),ag="{} years".format(Age),gen="{}".format(GND),blp="{}".format(BP),chl="{}".format(CHL),dis="{}".format(lol1))




if __name__ == '__main__':
  
    app.run()  # Run the Flask app
