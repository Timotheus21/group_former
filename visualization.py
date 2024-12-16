import matplotlib.pyplot as plt
import networkx as nx

class Visualization:
    def __init__(self, df):
        self.df = df
        self.main_color = '#5d33bd'

    def get_pronouns(self, gender):
        gender = gender.lower()
        if gender == 'male':
            return 'He/him/his'
        elif gender == 'female':
            return 'She/her/hers'
        else:
            return 'They/them/their'

    def visualize(self, teams):
        G = nx.Graph()

        # Add nodes with labels
        for team in teams:
            for member in team:
                name = self.df.loc[member, 'Name']
                coding_experience = self.df.loc[member, 'CodingExperience']
                experience_years = self.df.loc[member, 'ExperienceYears']
                study_field = self.df.loc[member, 'StudyField']
                label = f"{coding_experience}, {experience_years}\n{study_field}"
                G.add_node(name, label=label)

        # Add edges based on similar answers
        for team in teams:
            for i, member in enumerate(team):
                name = self.df.loc[member, 'Name']
                for j, other_member in enumerate(team):
                    if i >= j:
                        continue
                    other_name = self.df.loc[other_member, 'Name']
                    similarity = Visualization.calculate_similarity(self.df.loc[member], self.df.loc[other_member])
                    if similarity > 0:  # Adjust threshold as needed
                        G.add_edge(name, other_name, weight=similarity)

        # Generate layout and draw the graph
        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        edges = G.edges(data=True)
        weights = [edge[2]['weight'] for edge in edges]

        plt.figure(figsize=(16, 12))
        plt.subplot(1, 2, 2)  # Graph on the right

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue')

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color=weights, edge_cmap=plt.cm.Blues, width=2)

        # Draw labels
        for node, (x, y) in pos.items():
            plt.text(x, y, node, fontsize=12, fontweight='bold', ha='center')
            plt.text(x, y - 0.09, labels[node], fontsize=12, ha='center')

        plt.subplot(1, 2, 1)  # Profiles on the left
        y_offset = 1.0
        plt.axis('off')
        for index, team in enumerate(teams):
            for member in team:
                name = self.df.loc[member, 'Name']
                pronouns = self.get_pronouns(self.df.loc[member, 'Gender'])
                coding_experience = self.df.loc[member, 'CodingExperience']
                primary_language = self.df.loc[member, 'PrimaryLanguage']
                experience_years = self.df.loc[member, 'ExperienceYears']
                git = self.df.loc[member, 'GitFamiliarity']
                python = self.df.loc[member, 'PythonProficiency']
                learning = self.df.loc[member, 'PreferredLearning']
                learning_entries = [entry.strip() for entry in learning.split(',') if entry.strip().lower() != 'no']
                study_field = self.df.loc[member, 'StudyField']
                is_student = self.df.loc[member, 'IsStudent']

                # Add name with pronouns and a line break
                profile_text = f"{name} ({pronouns}),\n"
                profile_text += f"{coding_experience} in {primary_language} with {experience_years} years of experience." + "\n"
                profile_text += f"Git Familiarity: {git} and in Python they are {python}." + "\n"
                if learning_entries and learning_entries not in ['none', 'no', 'n/a']:
                    profile_text += f"They hope to learn {', '.join(learning_entries)}." + "\n"
                if is_student.lower() == 'yes' and study_field is not None:
                    profile_text += f"Their field of study is {study_field}."

                lines = profile_text.split('\n')
                for line in lines:
                    if line.startswith(name):
                        plt.text(0.02, y_offset, line, fontsize=12, fontweight='bold', verticalalignment='top', horizontalalignment='left', color=self.main_color)
                    else:
                        plt.text(0.02, y_offset, line, fontsize=12, verticalalignment='top', horizontalalignment='left')
                    y_offset -= 0.04  # Adjust spacing
                y_offset -= 0.06  # Space between teams

        plt.tight_layout(pad=2.0)
        plt.show()

    @staticmethod
    def calculate_similarity(member1, member2):
        # Calculate similarity based on common answers
        common_entries = 0
        for attr in member1.index:
            if member1[attr] == member2[attr]:
                common_entries += 1
        return common_entries
