import sys
import os
import pandas as pd
import json
import re

"""
    The DataProcessor class is responsible for handling and processing the data used in the Group Former application.
    It loads survey results, weights, and questionnaire interpreters, processes the data, and provides various methods
    to retrieve and manipulate the data.

    Key Responsibilities:
    - Load survey results from a CSV file.
    - Load and save weights from/to CSV files.
    - Load questionnaire interpreter from a JSON file.
    - Process survey results to transform and map the data according to the questionnaire interpreter.
    - Normalize weights to ensure they sum up to 1 and fall within the range 0 to 1.
    - Provide methods to retrieve various attributes and weights.
    - Manage homogenous, heterogenous, and emphasized attributes.
    - Apply the questionnaire interpreter to the survey results to map and scale the data.
    - Handle user interactions such as reloading survey results and adjusting weights.

    The class interacts with the GUI and Config classes to provide the necessary data for displaying and managing the
    graphical user interface. It ensures that the data is processed and formatted correctly for use in the application.
"""

class DataProcessor:
    # File paths for standard weights, custom weights, and questionnaire interpreter
    STD_WEIGHT_FILE = 'storage/std_weights.csv'
    CUSTOM_WEIGHT_FILE = 'storage/custom_weights.csv'
    INTERPRETER_FILE = 'storage/interpreter.json'

    def __init__(self, filepath):
        # Load CSV files, weights, and questionnaire interpreter on initialization
        self.results_survey = self.load_csv_file(filepath)
        self.weights = self.load_weights(self.STD_WEIGHT_FILE)
        self.custom_weights = self.load_weights(self.CUSTOM_WEIGHT_FILE)
        self.current_weights = self.weights.copy()
        self.questionnaire_interpreter = self.load_questionnaire_interpreter()

        # Define attribute lists for homogenous and heterogenous attributes
        self.attributes = []
        self.skill_attributes = []
        self.homogenous_attributes = []
        self.heterogenous_attributes = []
        self.emphasized_attributes_type = {}
        self.emphasized_attributes = []

        # Process survey results
        results_survey_transformed = self.process_survey_results()

        # Sort the transformed survey results alphabetically, only columns
        results_survey_transformed = results_survey_transformed.reindex(sorted(results_survey_transformed.columns), axis=1)

        results_survey_transformed.to_csv('storage/transformed_results_survey.csv', index=False)

        # Load the transformed survey results
        self.df = pd.read_csv('storage/transformed_results_survey.csv')
        self.apply_interpreter()

    # Load a CSV file from the given filepath
    def load_csv_file(self, filepath):
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            with open(filepath, 'r') as file:
                sample = file.read(1024)
                delimiter = ',' if ',' in sample else ';'
                file.seek(0)

            csv = pd.read_csv(filepath, delimiter = delimiter, dtype = str)

            if csv.columns[0].startswith('Column'):
                csv.columns = csv.iloc[0]
                csv = csv[1:]

            return csv

        except Exception as e:
            print(f"Error loading CSV file: {e}")
            sys.exit()

    # Save custom weights to a CSV file and create a new file if it does not exist
    def save_weights(self):
        try:
            if not os.path.exists(self.CUSTOM_WEIGHT_FILE):
                # Create a new file if it does not exist
                with open(self.CUSTOM_WEIGHT_FILE, 'w') as file:
                    file.write("attribute,weight\n")
            weights_csv = pd.DataFrame(list(self.custom_weights.items()), columns=['attribute', 'weight'])
            weights_csv.to_csv(self.CUSTOM_WEIGHT_FILE, index=False)

        except Exception as e:
            print(f"Error saving weights: {e}")

    def load_weights(self, filename):
        # Default weights if the file does not exist
        default_weights = {
            'CodingExperience': 5.0,
            'ExperienceYears': 6.0,
            'GitFamiliarity': 6.0,
            'PracticedConcepts': 7.0,
            'ProgrammingContext': 10.0,
            'ProgrammingCourses': 5.0,
            'PythonProficiency': 10.0,
        }

        # Load weights from a CSV file
        try:
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                # Create a new file if it does not exist
                weights_csv = pd.DataFrame(list(default_weights.items()), columns=['attribute', 'weight'])
                weights_csv.to_csv(filename, index = False)

                return default_weights

            weights_csv = pd.read_csv(filename)

            if weights_csv.empty:
                # If the file is empty, write default weights to the file
                weights_csv = pd.DataFrame(list(default_weights.items()), columns = ['attribute', 'weight'])
                weights_csv.to_csv(filename, index = False)

                return default_weights
            
            weights = dict(zip(weights_csv['attribute'], weights_csv['weight']))

            return weights
        
        except Exception as e:
            print(f"Error loading weights: {e}")
            return {}

    # Normalize weights to ensure they sum up to 1 and fall within the range 0 to 1
    def normalize_weights(self, weights):

        total_weight = sum(weights.values())

        if total_weight == 0:

            return weights
        
        normalized_weights = {k: v / total_weight for k, v in weights.items()}

        # Ensure weights fall within the range 0 to 1
        min_weight = min(normalized_weights.values())
        max_weight = max(normalized_weights.values())

        if min_weight < 0 or max_weight > 1:

            range_weight = max_weight - min_weight
            normalized_weights = {k: (v - min_weight) / range_weight for k, v in normalized_weights.items()}

        return normalized_weights

    def load_questionnaire_interpreter(self):
        # Load questionnaire interpreter from a JSON file
        try:
            with open(self.INTERPRETER_FILE, 'r') as file:

                return json.load(file)
            
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")

            return {}
        
        except Exception as e:
            print(f"Error loading questionnaire interpreter: {e}")
            return {}
        
    def apply_interpreter(self):
        try:
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

            all_attributes = self.df.columns

            # Define skill attributes
            skill_attributes_keys = self.questionnaire_interpreter.get('SkillLevelAssessment', {}).keys()
            for attribute in all_attributes:
                if attribute in skill_attributes_keys:
                    self.skill_attributes.append(str(attribute))
                else:
                    self.attributes.append(str(attribute))

        except Exception as e:
            print(f"Error applying interpreter: {e}")

    # Take a list of lists and flatten it into a single list by concatenating all sublists
    def flatten_lists(self, lists):
        # Flatten a list of lists
        return [item for sublist in lists for item in (sublist if isinstance(sublist, list) else [sublist])]
        
    def add_homogenous_attribute(self, attribute):
        # Add a homogenous attribute to the list and remove it from the heterogenous list
        if attribute not in self.homogenous_attributes:
            self.homogenous_attributes.append(attribute)

        if attribute in self.heterogenous_attributes:
            self.heterogenous_attributes.remove(attribute)

    def add_heterogenous_attribute(self, attribute):
        # Add a heterogenous attribute to the list and remove it from the homogenous list
        if attribute not in self.heterogenous_attributes:
            self.heterogenous_attributes.append(attribute)

        if attribute in self.homogenous_attributes:
            self.homogenous_attributes.remove(attribute)

    def add_emphasized_attribute(self, attribute):
        # Add an emphasized attribute to the list
        if attribute not in self.emphasized_attributes:
            self.emphasized_attributes.append(attribute)

    def remove_emphasized_attribute(self, attribute):
        # Remove an emphasized attribute from the list
        if attribute in self.emphasized_attributes:
            self.emphasized_attributes.remove(attribute)

            if attribute in self.emphasized_attributes_type:
                del self.emphasized_attributes_type[attribute]

    def remove_attribute(self, attribute):
        # Remove an attribute from both lists
        if attribute in self.homogenous_attributes:
            self.homogenous_attributes.remove(attribute)

        elif attribute in self.heterogenous_attributes:
            self.heterogenous_attributes.remove(attribute)

        if attribute in self.emphasized_attributes:
            self.emphasized_attributes.remove(attribute)

    # Process survey results to merge columns with same name and transform the data
    def process_survey_results(self):
        try:
            column_groups = {}
            other_columns = {}

            for col in self.results_survey.columns:

                # Match columns with the pattern 'base_name[suffix]'
                match = re.match(r'(.+?)\[(.*?)\]$', col)
                if match:
                    base_name, suffix = match.groups()

                    # Check if the suffix is 'other' and group columns accordingly
                    if suffix.lower() == 'other':
                        other_columns[base_name + 'Other'] = col
                    else:
                        # Group columns with the same base name
                        column_groups.setdefault(base_name, []).append(col)
                else:
                    # Group columns with the same name, without a suffix
                    column_groups.setdefault(col, []).append(col)

            for base_name, cols in column_groups.items():

                # The length of the columns should be greater than 1 to merge them
                if len(cols) > 1:

                    # Concatenate the values of the columns with the same base name
                    self.results_survey[base_name] = self.results_survey[cols].apply(lambda x: ', '.join(x.dropna()), axis = 1)

                    # Drop the original columns after merging
                    self.results_survey.drop(columns = cols, inplace = True)

            # Rename columns with 'other' suffix to match the base name
            for new_name, old_name in other_columns.items():
                self.results_survey.rename(columns = {old_name: new_name}, inplace = True)

            return self.results_survey

        except Exception as e:
            print(f"Error processing survey results: {e}")
            return pd.DataFrame()
        
    def reload_survey(self, filepath):
        # Reload the survey results and go through the processing steps again
        self.attributes = []
        self.skill_attributes = []

        self.results_survey = self.load_csv_file(filepath)
        results_survey_transformed = self.process_survey_results()
        results_survey_transformed.to_csv('storage/transformed_results_survey.csv', index = False)
        self.df = pd.read_csv('storage/transformed_results_survey.csv')
        self.apply_interpreter()

    def get_data(self):
        # Return the loaded data
        return self.df

    def get_weights(self):
        # Return the loaded weights
        return self.weights

    def get_normalized_current_weights(self):
        # Return the normalized current weights
        return self.normalize_weights(self.current_weights)

    def get_questionnaire_interpreter(self):
        # Return the loaded questionnaire interpreter
        return self.questionnaire_interpreter

    def get_skill_attributes(self):
        # Return the skill attributes
        return self.skill_attributes

    def get_other_attributes(self):
        # Return all the attributes except the skill attributes
        return sorted(self.attributes)

    def get_homogenous_attributes(self):
        # Return the flattened homogenous attributes
        return self.homogenous_attributes

    def get_heterogenous_attributes(self):
        # Return the flattened heterogenous attributes
        return self.heterogenous_attributes

    def get_emphasized_attributes(self):
        # Return the emphasized attributes
        return self.emphasized_attributes

    def get_emphasized_attributes_type(self):
        # Return the emphasized attributes type
        for attribute in self.emphasized_attributes:
            if attribute in self.homogenous_attributes:
                self.emphasized_attributes_type[attribute] = 'homogenous'
            elif attribute in self.heterogenous_attributes:
                self.emphasized_attributes_type[attribute] = 'heterogenous'
        return self.emphasized_attributes_type

    def get_not_considered_attributes(self):
        # Return the removed attributes
        all_attributes = set(self.flatten_lists([self.skill_attributes, self.attributes]))
        current_attributes = set(self.get_homogenous_attributes() + self.get_heterogenous_attributes())
        return list(all_attributes - current_attributes)