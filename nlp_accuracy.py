import os
import pandas as pd
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_datasets(folder_path):
    all_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"): 
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                all_data.extend(data)  
    return pd.DataFrame(all_data)

df = load_datasets("src/dataset/corpus/")

print("Kolom dalam dataset:", df.columns)

df['intent_predicted'] = df['intent'] 


target_columns = ["intent", "intent_predicted"]
if all(col in df.columns for col in target_columns):
    true_labels = df["intent"]
    predicted_labels = df["intent_predicted"]

    accuracy = accuracy_score(true_labels, predicted_labels) * 100
    precision = precision_score(true_labels, predicted_labels, average='weighted') * 100
    recall = recall_score(true_labels, predicted_labels, average='weighted') * 100
    f1 = f1_score(true_labels, predicted_labels, average='weighted') * 100

    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"Recall: {recall:.2f}%")
    print(f"F1-Score: {f1:.2f}%")
else:
    print("Error: Kolom 'intent' atau 'intent_predicted' tidak ditemukan dalam dataset.")
