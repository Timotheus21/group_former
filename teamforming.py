import itertools

"""
    The TeamForming class is responsible for forming teams based on the data provided by the DataProcessor.
    It uses various attributes and weights to calculate individual and compatibility scores for team members,
    and generates teams that optimize these scores.

    Key Responsibilities:
    - Initialize with data from the DataProcessor.
    - Calculate individual scores for each member based on their skill attributes and weights.
    - Calculate compatibility scores between members based on homogenous and heterogenous attributes.
    - Generate teams that optimize the individual and compatibility scores.
    - Provide methods to retrieve and manipulate the generated teams.

    The class interacts with the DataProcessor to retrieve the necessary data and weights, and uses this information
    to form balanced and compatible teams. It ensures that the teams are formed based on the specified criteria and
    provides methods to access and manage the generated teams.
"""

class TeamForming:
    def __init__(self, data_processor):
        # Initialize the TeamForming class with data from the data_processor
        self.data_processor = data_processor
        self.df = data_processor.get_data()  # DataFrame containing member data
        self.skill_attributes = data_processor.get_skill_attributes()  # List of skill attributes
        self.questionnaire_interpreter = data_processor.get_questionnaire_interpreter()  # Interpreter for questionnaire data
        self.teams = []  # List to store generated teams

    def calculate_individual_scores(self):
        # Get normalized weights for current skills
        self.normalized_current_weights = self.data_processor.get_normalized_current_weights()

        # Calculate individual scores for each member based on their skill attributes and weights
        scores = {}

        for member in self.df.index:
            score = 0
            for attribute in self.skill_attributes:
                try:
                    # Split attribute values if they are comma-separated
                    values = self.df.loc[member, attribute].split(', ')

                    for value in values:
                        # Get scale information for the attribute from the questionnaire interpreter under 'SkillLevelAssessment'
                        scale_info = self.questionnaire_interpreter['SkillLevelAssessment'].get(attribute, {})
                        scale = scale_info.get('scale', {}) if isinstance(scale_info, dict) else {}

                        if isinstance(scale, dict):
                            # Check if the value is in the scale dictionary
                            for key, val in scale.items():
                                if isinstance(val, list) and value in val:
                                    # Add score based on the scale and weight
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    break
                                if val == value:
                                    # Add score based on the scale and weight
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    break

                        elif isinstance(scale, list) and value in scale:
                            # Add score based on the index in the scale list and weight
                            score += (scale.index(value) + 1) * self.normalized_current_weights.get(attribute, 1)

                except KeyError as e:
                    # Handle missing attributes
                    print(f"Error processing attribute {attribute} for member {member}: {e}")

            # Store the calculated score for the member
            scores[member] = score

        return scores

    def calculate_compatibility_scores(self, member1, member2):
        # Get homogenous and heterogenous attributes
        self.homogenous_attributes = self.data_processor.get_homogenous_attributes()
        self.heterogenous_attributes = self.data_processor.get_heterogenous_attributes()

        # Get emphasized attributes and their types
        emphasized_attributes = self.data_processor.get_emphasized_attributes()
        emphasized_attributes_type = self.data_processor.get_emphasized_attributes_type()

        compatibility_score = 0

        # Calculate compatibility score based on homogenous and heterogenous attributes
        for attribute in self.homogenous_attributes:
            if self.df.loc[member1, attribute] == self.df.loc[member2, attribute]:
                compatibility_score += 1

                # Check if the attribute is emphasized and homogenous to give additional score
                if attribute in emphasized_attributes and emphasized_attributes_type.get(attribute) == 'homogenous':
                    if self.df.loc[member1, attribute] == self.df.loc[member2, attribute]:
                        compatibility_score += 4

        for attribute in self.heterogenous_attributes:
            if self.df.loc[member1, attribute] != self.df.loc[member2, attribute]:
                compatibility_score += 2

                if attribute in emphasized_attributes and emphasized_attributes_type.get(attribute) == 'heterogenous':
                    if self.df.loc[member1, attribute] != self.df.loc[member2, attribute]:
                        compatibility_score += 6

        return compatibility_score

    def all_combinations(self, members, min_size, max_size):
        # Generate all possible combinations of members with sizes ranging from min_size to max_size
        combinations = []

        for size in range(min_size, max_size + 1):
            combinations.extend(itertools.combinations(members, size)) # Itertools is used to generate all combinations

        return combinations

    def calculate_total_scores(self, combination, individual_scores, compatibility_scores):
        # Calculate the total score for a given combination of members
        total_score = 0

        # Add individual scores of each member in the combinations
        for member in combination:
            total_score += individual_scores[member]

        # Add compatibility scores between each pair of members in the combination
        for member in range(len(combination)):
            for other_member in range(member + 1, len(combination)):
                total_score += compatibility_scores[combination[member]][combination[other_member]]

        return total_score

    # Check for names with high GroupImportance values and KnownParticipants and place them in teams accordingly
    def check_for_names(self, teams, max_size, min_size, individual_scores, compatibility_scores):

        # Convert the teams to lists for easier manipulation
        for i, team in enumerate(teams):
            teams[i] = list(team)

        # Check if the members have high GroupImportance values and check for KnownParticipants
        for team in teams:
            for member in team[:]:
                try:
                    name = self.df.loc[member, 'Name']
                    group_importance = self.df.loc[member, 'GroupImportance']
                    known_participants = self.df.loc[member, 'KnownParticipants']
                    motivations = self.df.loc[member, 'Motivations']

                    # Split the KnownParticipants string into a list to handle multiple participants
                    if isinstance(known_participants, str):
                        known_participants = known_participants.split(', ')
                    else:
                        known_participants = []

                    # Check for high GroupImportance values and KnownParticipants
                    if group_importance.lower() == 'completely' and 'joining friends that participate: completely' in motivations.lower():

                        # Place the member in a team with known participants
                        for participant in known_participants:
                            for other_team in teams:
                                if participant in [self.df.loc[member, 'Name'] for member in other_team]:
                                    if member not in other_team and len(other_team) < max_size:
                                        if len(team) > min_size:
                                            team.remove(member)
                                            other_team.append(member)
                                            break

                    # Check for the other extreme when they want to meet new people
                    elif 'meeting new people: completely' in motivations.lower() or 'meeting new people: to a large extent' in motivations.lower():
                        
                        current_team = team
                        best_team = current_team
                        best_score = self.calculate_total_scores(current_team, individual_scores, compatibility_scores)


                        # Check if the known participants are in the same team and split them
                        for other_team in teams:
                            if other_team != current_team and len(other_team) < max_size:
                                if not any(participant in [self.df.loc[member, 'Name'] for member in other_team] for participant in known_participants):
                                        if member not in other_team:
                                            combination = other_team + [member]
                                            total_score = self.calculate_total_scores(combination, individual_scores, compatibility_scores)

                                            if total_score > best_score:
                                                best_score = total_score
                                                best_team = other_team

                                if best_team != current_team and len(current_team) > min_size:
                                    current_team.remove(member)
                                    best_team.append(member)
                                    break

                except KeyError as e:
                    print(f"Error seperating member {member}: {e}")
            
        return teams


    def generate_teams(self, desired_size, min_size, max_size):
        # Calculate individual scores for all members
        individual_scores = self.calculate_individual_scores()
        # Get a list of all members
        members = list(self.df.index)

        # Calculate compatibility scores between all pairs of members
        compatibility_scores = {
            member1: {
                member2: self.calculate_compatibility_scores(member1, member2)
                for member2 in members
            }
            for member1 in members
        }
        teams = []
        unassigned_members = members.copy()

        while members:
            best_score = None
            best_team = None

            # Iterate over team sizes
            for size in [desired_size, min_size]:
                # Iterate over all possible team combinations for team sizes
                for combination in self.all_combinations(members, size, size):
                    # Calculate total score for the combination
                    total_score = self.calculate_total_scores(combination, individual_scores, compatibility_scores)

                    # If the score is better than the best score so far, update the best score and team
                    if best_score is None or total_score > best_score:
                        best_score = total_score
                        best_team = combination

                # If a best team is found for the current team size, break out of the loop
                if best_team:
                    break

            # After evaluating all team sizes, add the best team to the list of teams and remove the members from the pool
            if best_team:
                teams.append(best_team)
                members = [member for member in members if member not in best_team]
                unassigned_members = [member for member in unassigned_members if member not in best_team]
            else:

                # Handle any remaining members that were not assigned to a team
                while unassigned_members:
                    # Get the first remaining member and find the best team to add them to
                    remaining_member = unassigned_members.pop(0)
                    best_score = None
                    best_team = None

                    # Iterate over the teams to find the best team to add the remaining member to similar to the previous loop
                    for team in teams:
                        if len(team) < max_size:
                            combination = list(team) + [remaining_member]
                            team_score = self.calculate_total_scores(combination, individual_scores, compatibility_scores)

                            if best_score is None or team_score > best_score:
                                best_score = team_score
                                best_team = team

                    # Add the remaining member to the best team
                    if best_team:

                        best_team_index = teams.index(best_team)
                        best_team = list(best_team)
                        best_team.append(remaining_member)
                        # Update the teams list and replace with the new team
                        teams[best_team_index] = tuple(best_team)

                        members.remove(remaining_member)

                break

        # Check for names with high GroupImportance values and KnownParticipants
        self.check_for_names(teams, max_size, min_size, individual_scores, compatibility_scores)

        return teams, members

    def set_teams(self, teams):
        # Set the teams attribute with the generated teams
        self.teams = teams