import itertools

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
        # Calculate individual scores for each member based on their skill attributes
        scores = {}
        for member in self.df.index:
            score = 0
            for attribute in self.skill_attributes:
                try:
                    # Split attribute values if they are comma-separated
                    values = self.df.loc[member, attribute].split(', ')
                    for value in values:
                        # Get scale information for the attribute
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
        compatibility_score = 0
        # Calculate compatibility score based on homogenous and heterogenous attributes
        for attribute in self.homogenous_attributes:
            if self.df.loc[member1, attribute] == self.df.loc[member2, attribute]:
                compatibility_score += 1
        for attribute in self.heterogenous_attributes:
            if self.df.loc[member1, attribute] != self.df.loc[member2, attribute]:
                compatibility_score += 2
        return compatibility_score

    def all_combinations(self, members, min_size, max_size):
        # Generate all possible combinations of members with sizes ranging from min_size to max_size
        combinations = []
        for size in range(min_size, max_size + 1):
            combinations.extend(itertools.combinations(members, size))
        return combinations

    def calculate_total_scores(self, combination, individual_scores, compatibility_scores):
        # Calculate the total score for a given combination of members
        total_score = 0
        # Add individual scores of each member in the combination
        for member in combination:
            total_score += individual_scores[member]
        # Add compatibility scores between each pair of members in the combination
        for member in range(len(combination)):
            for other_member in range(member + 1, len(combination)):
                total_score += compatibility_scores[combination[member]][combination[other_member]]
        return total_score

    def refine_teams(self, teams, emphasized_attributes):
        # Refine the generated teams based on emphasis attributes
        emphasized_attributes_type = self.data_processor.get_emphasized_attributes_type()
        print(f"Refining teams based on emphasized attributes: {emphasized_attributes} Types: {emphasized_attributes_type}")
        refined_teams = []
        for team in teams:
            refined_team = []
            for member in team:
                # Check if any emphasis attributes are present in the team
                for attribute in emphasized_attributes:
                    attribute_type = emphasized_attributes_type.get(attribute)
                    if attribute_type == 'homogenous' and all(self.df.loc[m, attribute] == self.df.loc[member, attribute] for m in team):
                        # Add the member to the refined team if the attribute is homogenous
                        refined_team.append(member)
                    elif attribute_type == 'heterogenous' and any(self.df.loc[m, attribute] != self.df.loc[member, attribute] for m in team):
                        # Add the member to the refined team if the attribute is heterogenous
                        refined_team.append(member)
            # Add the refined team to the list of refined teams
            if refined_team:
                refined_teams.append(refined_team)
        print(f"Refined teams: {refined_teams}")
        return refined_teams

    def generate_teams(self, desired_size, min_size, max_size):
        emphasized_attributes = self.data_processor.get_emphasized_attributes()
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
                print(f"No best team found for {members}. Reiterating with remaining members...")

                # Handle any remaining members that were not assigned to a team
                while unassigned_members:
                    remaining_member = unassigned_members.pop(0)
                    best_score = None
                    best_team = None

                    # Iterate over the teams to find the best team to add the remaining member to
                    for team in teams:
                        if len(team) < max_size:
                            combination = list(team) + [remaining_member]
                            team_score = self.calculate_total_scores(combination, individual_scores, compatibility_scores)
                            print(f"Team {team} score: {team_score}")

                            if best_score is None or team_score > best_score:
                                best_score = team_score
                                best_team = team

                    # Add the remaining member to the best team
                    if best_team:
                        member_name = self.df.loc[remaining_member, 'Name']
                        print(f"Adding remaining member {member_name} to team {best_team}")
                        best_team_index = teams.index(best_team)
                        best_team = list(best_team)
                        best_team.append(remaining_member)
                        # Update the teams list and replace with the new team
                        teams[best_team_index] = tuple(best_team)
                        print(f"Updated team: {best_team}")
                        print(f"All teams: {teams}")
                        members.remove(remaining_member)

                break

            # Refine the teams if there are any emphasized attributes
        if emphasized_attributes:
            self.refine_teams(teams, emphasized_attributes)

        print(f"Remaining members: {members}")
        return teams, members

    def set_teams(self, teams):
        # Set the teams attribute with the generated teams
        self.teams = teams

    def print_teams(self):
        # Print the teams and their scores
        for idx, (team) in enumerate(self.teams):
            print(f"Generating team {idx + 1}...")
            print(f"Team {idx + 1}:")
            for member in team:
                try:
                    name = self.df.loc[member, 'Name']
                    print(f"  - {name} (Score: {self.calculate_individual_scores()[member]:.4f})")
                except KeyError as e:
                    print(f"Error retrieving name for member {member}: {e}")