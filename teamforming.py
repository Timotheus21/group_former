class TeamForming:
    def __init__(self, data_processor):
        # Initialize the TeamFormation class with data from the data_processor
        self.data_processor = data_processor
        self.df = data_processor.get_data()
        self.skill_attributes = [
            'ProgrammingExperience', 'ProgrammingCourses', 
            'PythonProficiency', 'ProgrammingExperienceYears',
            'ProgrammingContext', 'PracticedConcepts', 'GitFamiliarity'
        ]
        self.questionnaire_interpreter = data_processor.get_questionnaire_interpreter()
        self.teams = []

    def calculate_individual_scores(self):
        self.normalized_current_weights = self.data_processor.get_normalized_current_weights()
        # Calculate individual scores for each member based on their skill attributes
        scores = {}
        for member in self.df.index:
            print(f"Calculating score for index {member}, name: {self.df.loc[member, 'Name']}...")
            score = 0
            for attribute in self.skill_attributes:
                try:
                    values = self.df.loc[member, attribute].split(', ')
                    for value in values:
                        print(f"Processing attribute: {attribute}, entry: {value}")
                        scale_info = self.questionnaire_interpreter['SkillLevelAssessment'].get(attribute, {})
                        scale = scale_info.get('scale', {}) if isinstance(scale_info, dict) else {}
                        if isinstance(scale, dict):
                            for key, val in scale.items():
                                if isinstance(val, list) and value in val:
                                    print(f"Value {key} x Weight {self.normalized_current_weights.get(attribute, 1)}")
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    print(f"Score: {score}")
                                    break
                                if val == value:
                                    print(f"Value {key} x Weight {self.normalized_current_weights.get(attribute, 1)}")
                                    score += int(key) * self.normalized_current_weights.get(attribute, 1)
                                    print(f"Score: {score}")
                                    break
                        elif isinstance(scale, list) and value in scale:
                            score += (scale.index(value) + 1) * self.normalized_current_weights.get(attribute, 1)
                except KeyError as e:
                    print(f"Error processing attribute {attribute} for member {member}: {e}")
            scores[member] = score
            print(f"Index: {member}, Total Score: {score} \n")
        return scores

    def calculate_team_score(self, team, individual_scores):
        # Calculate the total score for a team by summing individual scores
        try:
            return sum(individual_scores[member] for member in team)
        except KeyError as e:
            print(f"Error calculating team score: {e}")
            return 0

    def generate_teams(self, team_size=4):
        individual_scores = self.calculate_individual_scores()
        # Generate teams with narrow-range mixed-ability
        members = list(self.df.index)
        members.sort(key=lambda x: individual_scores[x])
        teams = []
        
        while len(members) >= team_size:
            team = []
            for i in range(team_size):
                if i % 2 == 0:
                    team.append(members.pop(0))  # Take from the lower end
                else:
                    team.append(members.pop(-1))  # Take from the higher end
            teams.append((team, self.calculate_team_score(team, individual_scores)))
        
        # Handle remaining members if any
        while len(members) > 0:
            if len(members) == 2:
                # Merge the last two members with the last team if possible
                if len(teams) > 0:
                    last_team, last_score = teams.pop()
                    last_team.extend(members)
                    teams.append((last_team, self.calculate_team_score(last_team, individual_scores)))
                else:
                    # If no teams exist yet, create a team of 2
                    teams.append((members, self.calculate_team_score(members, individual_scores)))
                break
            elif len(members) >= 5:
                team_size = 5
            else:
                team_size = 3
            team = []
            for i in range(team_size):
                if i % 2 == 0:
                    team.append(members.pop(0))  # Take from the lower end
                else:
                    team.append(members.pop(-1))  # Take from the higher end
            teams.append((team, self.calculate_team_score(team, individual_scores)))
        
        teams.sort(key=lambda x: x[1], reverse=True)
        self.set_teams(teams)
        return teams

    def set_teams(self, teams):
        # Set the teams attribute with the generated teams
        self.teams = teams

    def print_teams(self):
        # Print the teams and their scores
        for idx, (team, score) in enumerate(self.teams):
            print(f"Generating team {idx + 1}...")
            print(f"Team {idx + 1}:")
            for member in team:
                try:
                    name = self.df.loc[member, 'Name']
                    print(f"  - {name}")
                except KeyError as e:
                    print(f"Error retrieving name for member {member}: {e}")
            print(f"Team Score: {score:.4f}\n")