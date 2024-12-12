import itertools

class TeamForming:
    def __init__(self, data_processor):
        # Initialize the TeamFormation class with data from the data_processor
        self.data_processor = data_processor
        self.df = data_processor.get_data()
        self.skill_attributes = data_processor.get_skill_attributes()
        self.questionnaire_interpreter = data_processor.get_questionnaire_interpreter()
        self.teams = []

    def calculate_individual_scores(self):
        self.normalized_current_weights = self.data_processor.get_normalized_current_weights()
        # Calculate individual scores for each member based on their skill attributes
        scores = {}
        for member in self.df.index:
            #print(f"Calculating score for index {member}, name: {self.df.loc[member, 'Name']}...")
            score = 0
            for attribute in self.skill_attributes:
                try:
                    values = self.df.loc[member, attribute].split(', ')
                    for value in values:
                        #print(f"Processing attribute: {attribute}, entry: {value}")
                        scale_info = self.questionnaire_interpreter['SkillLevelAssessment'].get(attribute, {})
                        scale = scale_info.get('scale', {}) if isinstance(scale_info, dict) else {}
                        if isinstance(scale, dict):
                            for key, val in scale.items():
                                if isinstance(val, list) and value in val:
                                    #print(f"Value {key} x Weight {self.normalized_current_weights.get(attribute, 1)}")
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    #print(f"Score: {score}")
                                    break
                                if val == value:
                                    #print(f"Value {key} x Weight {self.normalized_current_weights.get(attribute, 1)}")
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    #print(f"Score: {score}")
                                    break
                        elif isinstance(scale, list) and value in scale:
                            score += (scale.index(value) + 1) * self.normalized_current_weights.get(attribute, 1)
                except KeyError as e:
                    print(f"Error processing attribute {attribute} for member {member}: {e}")
            scores[member] = score
            #print(f"Index: {member}, Total Score: {score} \n")
        return scores
    
    def calculate_compatibility_scores(self, member1, member2):
        self.homogenous_attributes = self.data_processor.get_homogenous_attributes()
        self.heterogenous_attributes = self.data_processor.get_heterogenous_attributes()
        compatibility_score = 0
        try:
            for attribute in self.homogenous_attributes:
                if self.df.loc[member1, attribute] == self.df.loc[member2, attribute]:
                    compatibility_score += 1
            for attribute in self.heterogenous_attributes:
                if self.df.loc[member1, attribute] != self.df.loc[member2, attribute]:
                    compatibility_score += 2
        except KeyError as e:
            print(f"No homogenous or heterogenous attributes found: {e}")
        return compatibility_score
    
    def all_combinations(self, members, min_size, max_size):
        combinations = []
        for size in range(min_size, max_size + 1):
            combinations.extend(itertools.combinations(members, size))
        return combinations
    
    def calculate_total_scores(self, combination, individual_scores, compatibility_scores):
        total_score = 0
        for member in combination:
            total_score += individual_scores[member]
        for member in range(len(combination)):
            for other_member in range(member + 1, len(combination)):
                total_score += compatibility_scores[combination[member]][combination[other_member]]
        return total_score
    
    def generate_teams(self):
        individual_scores = self.calculate_individual_scores()
        members = list(self.df.index)
        print(f"DEBUG: Members: {members}")
        compatibility_scores = {member1: {member2: self.calculate_compatibility_scores(member1, member2) for member2 in members} for member1 in members}
        print(f"DEBUG: Compatibility Scores: {compatibility_scores}")
        teams = []

        while members:
            best_score = None
            best_team = None

        # Iterate over team sizes from 4 to 3
            for size in [4, 5, 3]:
                # Iterate over all possible team combinations for team sizes of 3 to 5
                for combination in self.all_combinations(members, size, size):
                    print(f"Evaluating combination: {combination}...")
                    # Calculate total score for the combination
                    total_score = self.calculate_total_scores(combination, individual_scores, compatibility_scores)
                    print(f"Total Score: {total_score}")

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
            else:
                print("No best team found, breaking out of loop...")
                break

        return teams

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
                    print(f"  - {name} (Score: {self.calculate_individual_scores()[member]})")
                except KeyError as e:
                    print(f"Error retrieving name for member {member}: {e}")