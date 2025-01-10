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

        # Get emphasized attributes and their types
        emphasized_attributes = self.data_processor.get_emphasized_attributes()
        emphasized_attributes_type = self.data_processor.get_emphasized_attributes_type()

        compatibility_score = 0
        # Calculate compatibility score based on homogenous and heterogenous attributes
        for attribute in self.homogenous_attributes:
            if self.df.loc[member1, attribute] == self.df.loc[member2, attribute]:
                compatibility_score += 1

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

    def check_for_names(self, teams, max_size, min_size, individual_scores, compatibility_scores):
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

                    if isinstance(known_participants, str):
                        known_participants = known_participants.split(', ')
                    else:
                        known_participants = []

                    if group_importance.lower() == 'completely' and 'joining friends that participate: completely' in motivations.lower():
                        specific_motivation = 'Group Importance: Completely and Joining Friends: Completely' if 'joining friends that participate: completely' in motivations.lower() and group_importance.lower() == 'completely' else 'Group Importance: Completely'
                        # Place the member in a team with known participants
                        for participant in known_participants:
                            for other_team in teams:
                                if participant in [self.df.loc[member, 'Name'] for member in other_team]:
                                    if member not in other_team and len(other_team) < max_size:
                                        if len(team) > min_size:
                                            team.remove(member)
                                            other_team.append(member)
                                            print(f"Placing {name} in team with {participant}, because of {specific_motivation}")
                                            break

                    elif 'meeting new people: completely' in motivations.lower() or 'meeting new people: to a large extent' in motivations.lower():
                        specific_motivation = 'meeting new people: completely' if 'meeting new people: completely' in motivations.lower() else 'meeting new people: to a large extent'
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
                                    print(f"Placing {name} in other team without known participants, because of {specific_motivation}")
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
                print(f"\nNo best team found for {members}. Reiterating with remaining members...")

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
                        print(f"All teams: {teams}\n")
                        members.remove(remaining_member)

                break

        # Check for names with high GroupImportance values and KnownParticipants
        self.check_for_names(teams, max_size, min_size, individual_scores, compatibility_scores)

        print(f"Remaining members: {members}\n")
        return teams, members

    def set_teams(self, teams):
        # Set the teams attribute with the generated teams
        self.teams = teams

    def print_teams(self):
        # Print the teams and their scores
        for idx, (team) in enumerate(self.teams):
            print(f"Generating team {idx + 1}...")
            print(f"Team {idx + 1}:")

            same_attributes = {}
            different_attributes = {}

            homogenous_count = 0
            heterogenous_count = 0

            for member in team:
                try:
                    name = self.df.loc[member, 'Name']
                    print(f"  - {name} (Score: {self.calculate_individual_scores()[member]:.4f})")

                    for attribute in self.homogenous_attributes + self.heterogenous_attributes:
                        value = self.df.loc[member, attribute]
                        if attribute not in same_attributes:
                            same_attributes[attribute] = value
                            different_attributes[attribute] = set()

                        if same_attributes[attribute] != value:
                            different_attributes[attribute].add(value)
                            different_attributes[attribute].add(same_attributes[attribute])
                            same_attributes[attribute] = None

                except KeyError as e:
                    print(f"Error retrieving name for member {member}: {e}")

            print("\nSame attributes:")
            for attribute, value in same_attributes.items():
                if value is not None:
                    print(f"  - {attribute}: {value}")
                    if attribute in self.homogenous_attributes:
                        homogenous_count += 1

            print("Different attributes:")
            for attribute, values in different_attributes.items():
                filtered_values = [str(value) for value in values if value is not None]
                if filtered_values:
                    print(f"  - {attribute}: {', '.join(filtered_values)}\n")
                    if attribute in self.heterogenous_attributes:
                        heterogenous_count += 1

            print(f"Total true homogenous attributes: {homogenous_count}")
            print(f"Total true heterogenous attributes: {heterogenous_count}\n")
            print("--------------------------------------------------\n\n")