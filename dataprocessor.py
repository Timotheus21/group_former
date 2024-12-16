import sys
import pandas as pd
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class DataProcessor:
    # File paths for standard weights, custom weights, and questionnaire interpreter
    STD_WEIGHT_FILE = 'storage/std_weights.csv'
    CUSTOM_WEIGHT_FILE = 'storage/custom_weights.csv'
    QUESTIONNAIRE_FILE = 'storage/questionnaire_interpreter.json'

    def __init__(self):
        # Load CSV file, weights, and questionnaire interpreter on initialization
        results_survey = self.load_csv_file()
        questionnaire_responses = pd.read_csv('storage/questionnaire_responses.csv')
        self.weights = self.load_weights(self.STD_WEIGHT_FILE)
        self.custom_weights = self.load_weights(self.CUSTOM_WEIGHT_FILE)
        self.current_weights = self.weights.copy()
        self.questionnaire_interpreter = self.load_questionnaire_interpreter()

        column_mapping = {
        "CodingExperience": "CodingExperience",
        "PeersGroup": "PeersGroup",
        "PrimaryLanguage": "PrimaryLanguage",
        "PythonProficiency": "PythonProficiency",
        "ExperienceYears": "ExperienceYears",
        "ProgrammingContext": "ProgrammingContext",
        "GitFamiliarity": "GitFamiliarity",
        "AdditionalMotivation": "AdditionalMotivation",
        "OtherInterests": "OtherInterests",
        "EducationLevel": "EducationLevel",
        "IsStudent": "IsStudent",
        "StudyField": "StudyField",
        "Semester": "Semester",
        "Gender": "Gender",
        "NativeLanguage": "NativeLanguage",
        "Age": "Age",
        "CulturalBackground": "CulturalBackground",
        "PreferredChallenge": "PreferredChallenge",
        "GroupImportance": "GroupImportance",
        "KnownParticipants": "KnownParticipants",
        "FamiliarityOthers": "FamiliarityOthers",
        "Name": "Name"
        }

    # Merge columns with similar names
        def merge_columns(df, base_name):
            columns_to_merge = [col for col in df.columns if col.startswith(base_name)]
            df[base_name] = df[columns_to_merge].apply(lambda x: ', '.join(x.dropna().astype(str)), axis=1)
            df.drop(columns=columns_to_merge, inplace=True)

            # Merge specific columns
        merge_columns(results_survey, "ProgrammingCourses")
        merge_columns(results_survey, "PracticedConcepts")
        merge_columns(results_survey, "Motivations")
        merge_columns(results_survey, "PreferredLearning")
        merge_columns(results_survey, "PreferredGamesEasy")
        merge_columns(results_survey, "PreferredGamesMedium")
        merge_columns(results_survey, "PreferredGamesHard")

        # Rename columns in the results_survey DataFrame
        results_survey_renamed = results_survey.rename(columns=column_mapping)

        # Ensure all required columns are present
        missing_columns = [col for col in questionnaire_responses.columns if col not in results_survey_renamed.columns]
        for col in missing_columns:
            results_survey_renamed[col] = None

        # Select only the columns that are present in the questionnaire_responses DataFrame
        results_survey_transformed = results_survey_renamed[questionnaire_responses.columns]

        # Save the transformed DataFrame to a new CSV file
        results_survey_transformed.to_csv('storage/transformed_results_survey.csv', index=False)

        self.df = pd.read_csv('storage/transformed_results_survey.csv')
        self.apply_interpreter()

        self.skill_attributes = [
            'CodingExperience', 'ProgrammingCourses', 
            'PythonProficiency', 'ExperienceYears',
            'ProgrammingContext', 'PracticedConcepts', 'GitFamiliarity'
        ]
        self.motivation_attributes = [
            'Motivations', 'PreferredLearning'
        ]
        self.project_attributes = [
            'PreferredChallenge', 'PreferredGames'
        ]
        self.familiarity_attributes = [
            'GroupImportance', 'KnownParticipants'
        ]
        self.background_attributes = [
            'EducationLevel', 'StudyField', 'Gender', 'NativeLanguage', 'CulturalBackground'
        ]
        self.homogenous_attributes = self.flatten_lists([self.skill_attributes, self.motivation_attributes, self.project_attributes, 'GroupImportance'])
        self.heterogenous_attributes = self.flatten_lists([self.background_attributes, 'KnownParticipants'])

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
        
    def apply_interpreter(self):
        # Apply the entry mappings to specific columns
        for column, mappings in self.questionnaire_interpreter.get('entry_mapping', {}).items():
            if column in self.df.columns:
                # Ensure the column values are strings
                self.df[column] = self.df[column].astype(str)
                # Split the values in the column
                self.df[column] = self.df[column].apply(
                    lambda x: ', '.join([
                        mappings.get(value.strip(), value.strip()) for value, (key, mappings) in zip(x.split(', '), self.questionnaire_interpreter['entry_mapping'][column].items())
                    ])
                )

        # Apply scale mappings for skill levels
        for column, scale_info in self.questionnaire_interpreter.get('SkillLevelAssessment', {}).items():
            scale = scale_info.get('scale', {})
            if column in self.df.columns and isinstance(scale, dict):
                # Ensure the column values are strings and map the scale
                self.df[column] = self.df[column].astype(str)
                self.df[column] = self.df[column].apply(
                    lambda x: ', '.join([scale.get(value.strip(), value.strip()) for value in x.split(', ')])
                )

        
    def flatten_lists(self, lists):
        # Flatten a list of lists
        return [item for sublist in lists for item in (sublist if isinstance(sublist, list) else [sublist])]
        
    def add_homogenous_attribute(self, attribute):
        # Add a homogenous attribute to the list and remove it from the heterogenous list
        if attribute not in self.homogenous_attributes:
            print(f"Adding {attribute} as homogenous attribute.")
            self.homogenous_attributes.append(attribute)
            print(f"Homogenous: {self.homogenous_attributes}")
        if attribute in self.heterogenous_attributes:
            self.heterogenous_attributes.remove(attribute)

    def add_heterogenous_attribute(self, attribute):
        # Add a heterogenous attribute to the list and remove it from the homogenous list
        if attribute not in self.heterogenous_attributes:
            print(f"Adding {attribute} as heterogenous attribute.")
            self.heterogenous_attributes.append(attribute)
            print(f"Heterogenous: {self.heterogenous_attributes}")
        if attribute in self.homogenous_attributes:
            self.homogenous_attributes.remove(attribute)

    def remove_attribute(self, attribute):
        # Remove an attribute from both lists
        if attribute in self.homogenous_attributes:
            print(f"Removing homogenous attribute: {attribute}")
            self.homogenous_attributes.remove(attribute)
            print(f"Homogenous: {self.homogenous_attributes}")
        elif attribute in self.heterogenous_attributes:
            print(f"Removing heterogenous attribute: {attribute}")
            self.heterogenous_attributes.remove(attribute)
            print(f"Heterogenous: {self.heterogenous_attributes}")

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

    def get_normalized_current_weights(self):
        # Return the normalized current weights
        return self.normalize_weights(self.current_weights)

    def get_questionnaire_interpreter(self):
        # Return the loaded questionnaire interpreter
        return self.questionnaire_interpreter
    
    def get_skill_attributes(self):
        # Return the skill attributes
        return self.skill_attributes
    
    def get_motivation_attributes(self):
        # Return the motivation attributes
        return self.motivation_attributes
    
    def get_project_attributes(self):
        # Return the project attributes
        return self.project_attributes
    
    def get_familiarity_attributes(self):
        # Return the familiarity attributes
        return self.familiarity_attributes
    
    def get_background_attributes(self):
        # Return the background attributes
        return self.background_attributes
    
    def get_other_attributes(self):
        # Return all the attributes except the skill attributes
        return self.motivation_attributes + self.project_attributes + self.familiarity_attributes + self.background_attributes
    
    def get_homogenous_attributes(self):
        # Return the flattened homogenous attributes
        return self.homogenous_attributes
    
    def get_heterogenous_attributes(self):
        # Return the flattened heterogenous attributes
        return self.heterogenous_attributes
    
    def get_removed_attributes(self):
        # Return the removed attributes
        all_attributes = set(self.flatten_lists([self.skill_attributes, self.motivation_attributes, self.project_attributes, self.familiarity_attributes, self.background_attributes]))
        current_attributes = set(self.get_homogenous_attributes() + self.get_heterogenous_attributes())
        return list(all_attributes - current_attributes)