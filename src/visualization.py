import matplotlib.pyplot as plt
import networkx as nx

"""
    The Visualization class is responsible for creating visual representations of the teams formed by the Group Former application.
    It uses the matplotlib and networkx libraries to generate graphs that show the relationships and similarities between team members.

    Key Responsibilities:
    - Initialize with data from the DataProcessor.
    - Retrieve pronouns based on gender.
    - Visualize teams by creating a graph with nodes representing team members and edges representing similarities.
    - Calculate similarity scores between team members based on homogenous attributes.
    - Generate and display the graph using a spring layout.
    - Display team profiles with relevant information in a separate subplot.

    The class interacts with the DataProcessor to retrieve the necessary data and attributes, and uses this information
    to create a visual representation of the teams. It ensures that the graph is displayed with the specified colors and layout.
"""

class Visualization:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.df = data_processor.get_data()

        self.main_color = '#6f12c0'
        self.secondary_color = '#d4c9ef'

    # Handle pronouns based on the given gender pro member
    def get_pronouns(self, gender, gender_other):
        gender = str(gender.lower())

        if gender == 'male':
            return 'He/him/his'
        elif gender == 'female':
            return 'She/her/hers'
        elif gender == 'non-binary':
            return 'They/them/theirs'
        elif gender == 'prefer not to say':
            return 'They/them/theirs'
        elif gender == 'other':
            return gender_other

    # Visualize the teams formed by the Group Former application
    def visualize(self, teams):
        G = nx.Graph()

        # Add nodes with labels containing team members' names
        for team in teams:
            for member in team:
                name = self.df.loc[member, 'Name']
                G.add_node(name)

        # Add edges based on similar answers
        for team in teams:
            for member_index, member in enumerate(team):
                name = self.df.loc[member, 'Name']

                for other_member_index, other_member in enumerate(team):
                    if member_index >= other_member_index:
                        continue

                    other_name = self.df.loc[other_member, 'Name']
                    similarity = Visualization.calculate_similarity(self.df.loc[member], self.df.loc[other_member], self.data_processor.get_homogenous_attributes())

                    if similarity > 0:  # Adjust threshold as needed
                        G.add_edge(name, other_name, weight=similarity)

        # Generate layout and draw the graph
        pos = nx.spring_layout(G)
        edges = G.edges(data = True)
        weights = [edge[2]['weight'] for edge in edges]

        # Create a figure with two subplots: one for the graph and one for the team profiles
        plt.figure(figsize = (16, 12), edgecolor = self.main_color)
        plt.subplot(1, 2, 2, facecolor = self.secondary_color)  # Graph on the right

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color = 'lightblue')

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color = weights, edge_cmap = plt.cm.Blues, width = 2)

        # Draw labels
        for node, (x, y) in pos.items():
            plt.text(x, y, node, fontsize = 14, fontweight = 'bold', ha = 'center')

        plt.subplot(1, 2, 1)  # Profiles on the left
        y_offset = 1.0

        plt.axis('off')

        # Display team profiles with relevant information
        for index, team in enumerate(teams):
            for member in team:

                # First line: Name, age, pronouns
                name = self.df.loc[member, 'Name']
                pronouns = self.get_pronouns(self.df.loc[member, 'Gender'], self.df.loc[member, 'GenderOther'])
                age = self.df.loc[member, 'Age']

                # Second line: Coding experience, primary language, experience years
                coding_experience = self.df.loc[member, 'CodingExperience']
                primary_language = self.df.loc[member, 'PrimaryLanguage']
                primary_language_other = self.df.loc[member, 'PrimaryLanguageOther']
                if str(primary_language.lower()) == 'other':
                    primary_language = primary_language_other

                experience_years = self.df.loc[member, 'ExperienceYears']

                # Third line: Git familiarity, Python proficiency
                git = self.df.loc[member, 'GitFamiliarity']
                python = self.df.loc[member, 'PythonProficiency']

                # Fourth line: Preferred challenge, preferred games
                preferred_challenge = self.df.loc[member, 'PreferredChallenge']
                if str(preferred_challenge.lower()) == 'easy':
                    preferred_games = self.df.loc[member, 'PreferredGamesEasy']
                elif str(preferred_challenge.lower()) == 'medium':
                    preferred_games = self.df.loc[member, 'PreferredGamesMedium']
                elif str(preferred_challenge.lower()) == 'hard':
                    preferred_games = self.df.loc[member, 'PreferredGamesHard']
                
                # Get the preferred games without 'no' entries and join them with a comma
                preferred_games = [entry.strip() for entry in preferred_games.split(',') if str(entry.strip().lower()) != 'no']
                preferred_games = ', '.join(preferred_games)

                # Sixth line: Study field and student status if is student
                study_field = self.df.loc[member, 'StudyField']
                study_field_other = self.df.loc[member, 'StudyFieldOther']
                if str(study_field.lower()) == 'other':
                    study_field = study_field_other
                is_student = self.df.loc[member, 'IsStudent']

                # Add name with pronouns and a line break
                profile_text = f"{name}, {age} ({pronouns}),\n"
                profile_text += f"{coding_experience} in {primary_language} and has {experience_years} of experience." + "\n"
                profile_text += f"Git Familiarity: {git} and in Python they are {python}." + "\n"
                profile_text += f"They prefer a {preferred_challenge} challenge and would like to work on {preferred_games}." + "\n"

                if str(is_student.lower()) == 'yes' and study_field is not None:
                    profile_text += f"Their field of study is {study_field}."

                lines = profile_text.split('\n')

                for line in lines:
                    # Highlight the team member's name
                    if line.startswith(name):
                        plt.text(0.02, y_offset, line, fontsize = 13, fontweight = 'bold', verticalalignment = 'top', horizontalalignment = 'left', color = self.main_color)
                    else:
                        plt.text(0.02, y_offset, line, fontsize = 12, verticalalignment = 'top', horizontalalignment = 'left')
                    y_offset -= 0.04  # Adjust spacing
                y_offset -= 0.06  # Space between teams

        plt.tight_layout(pad=2.0)
        plt.show()

    @staticmethod
    def calculate_similarity(member1, member2, homogenous_attributes):
        # Calculate similarity based on common answers
        common_entries = 0

        for attr in homogenous_attributes:
            if member1[attr] == member2[attr]:
                common_entries += 1

        return common_entries
