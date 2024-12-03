import sys
import pandas as pd
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class DataProcessor:
    # File paths for standard weights, custom weights, and questionnaire interpreter
    STD_WEIGHT_FILE = 'storage/std_weights.csv'
    CUSTOM_WEIGHT_FILE = 'storage/new_weights.csv'
    QUESTIONNAIRE_FILE = 'storage/questionnaire_interpreter.json'

    def __init__(self):
        # Load CSV file, weights, and questionnaire interpreter on initialization
        self.df = self.load_csv_file()
        self.weights = self.load_weights(self.STD_WEIGHT_FILE)
        self.custom_weights = self.load_weights(self.CUSTOM_WEIGHT_FILE)
        self.current_weights = self.weights.copy()
        self.questionnaire_interpreter = self.load_questionnaire_interpreter()

    def load_csv_file(self):
        # Open file dialog to select a CSV file
        Tk().withdraw()
        filename = askopenfilename(title="Select Questionnaire CSV file", filetypes=[("CSV files", "*.csv")])
        if not filename:
            print("No file selected. Exiting...")
            sys.exit()
        try:
            return pd.read_csv(filename)
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            sys.exit()

    def save_weights(self):
        # Save weights to a CSV file
        try:
            weights_csv = pd.DataFrame(list(self.custom_weights.items()), columns=['attribute', 'weight'])
            weights_csv.to_csv(self.CUSTOM_WEIGHT_FILE, index=False)
        except Exception as e:
            print(f"Error saving weights: {e}")

    def load_weights(self, filename):
        # Load weights from a CSV file
        try:
            weights_csv = pd.read_csv(filename)
            weights = dict(zip(weights_csv['attribute'], weights_csv['weight']))
            return weights
        except Exception as e:
            print(f"Error loading weights: {e}")
            return {}

    def normalize_weights(self, weights):
        # Normalize weights so that their sum equals 1 and they fall within the range 0 to 1
        total_weight = sum(weights.values())
        if total_weight == 0:
            print("Total weight is zero, cannot normalize weights.")
            return weights
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        # Ensure weights fall within the range 0 to 1
        min_weight = min(normalized_weights.values())
        max_weight = max(normalized_weights.values())
        if min_weight < 0 or max_weight > 1:
            print("Weights out of range, adjusting to fit within 0 to 1.")
            range_weight = max_weight - min_weight
            normalized_weights = {k: (v - min_weight) / range_weight for k, v in normalized_weights.items()}
        return normalized_weights

    def load_questionnaire_interpreter(self):
        # Load questionnaire interpreter from a JSON file
        try:
            with open(self.QUESTIONNAIRE_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")
            return {}
        except Exception as e:
            print(f"Error loading questionnaire interpreter: {e}")
            return {}

    def get_data(self):
        # Return the loaded data
        return self.df

    def get_weights(self):
        # Return the loaded weights
        return self.weights
    
    def get_custom_weights(self):
        # Return the loaded custom weights
        return self.custom_weights
    
    def get_current_weights(self):
        # Return the current weights
        return self.current_weights
    
    def get_normalized_weights(self):
        # Return the normalized weights
        return self.normalize_weights(self.weights)
    
    def get_normalized_custom_weights(self):
        # Return the normalized custom weights
        return self.normalize_weights(self.custom_weights)
    
    def get_normalized_current_weights(self):
        # Return the normalized current weights
        return self.normalize_weights(self.current_weights)

    def get_questionnaire_interpreter(self):
        # Return the loaded questionnaire interpreter
        return self.questionnaire_interpreter