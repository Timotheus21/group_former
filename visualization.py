import matplotlib.pyplot as plt
import networkx as nx

class Visualization:
    @staticmethod
    def visualize(team, df):
        G = nx.Graph()
        
        # Add nodes to the graph with additional attributes
        for member in team:
            name = df.loc[member, 'Name']
            programming_proficiency = df.loc[member, 'CodingExperience']
            programming_experience_years = df.loc[member, 'ExperienceYears']
            study_field = df.loc[member, 'StudyField']
            label = f"{programming_proficiency}, {programming_experience_years}\n{study_field}"
            G.add_node(name, label=label)
        
        # Add edges based on similar answers
        for i, member in enumerate(team):
            name = df.loc[member, 'Name']
            for j, other_member in enumerate(team):
                if i >= j:
                    continue
                other_name = df.loc[other_member, 'Name']
                similarity = Visualization.calculate_similarity(df.loc[member], df.loc[other_member])
                if similarity > 0:  # Adjust threshold as needed
                    G.add_edge(name, other_name, weight=similarity)

        # Generate layout and draw the graph
        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        edges = G.edges(data=True)
        weights = [edge[2]['weight'] for edge in edges]
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue')
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color=weights, edge_cmap=plt.cm.Blues)
        
        # Draw labels
        for node, (x, y) in pos.items():
            plt.text(x, y, node, fontsize=14, fontweight='bold', ha='center')
            plt.text(x, y-0.12, labels[node], fontsize=12, ha='center')
        
        plt.show()

    @staticmethod
    def calculate_similarity(member1, member2):
        # Calculate similarity based on common answers
        common_entries = 0
        for attr in member1.index:
            if member1[attr] == member2[attr]:
                common_entries += 1
        return common_entries