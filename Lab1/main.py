import re
import random


# Convert a template string with variables to regex
def AIStringToRegex(s):
    s = re.sub(r'\(\?([a-zA-Z][a-zA-Z0-9_]*)\)', r'(?P<\1>.+)', s)
    return '^' + s + '$'

# Match a template with variables with a string
def match(template, string):
    pattern = AIStringToRegex(template)
    m = re.match(pattern, string)
    # If match is succesful then we return a disctionary of variables   
    if m:
        return m.groupdict()
    else:
        return None

# Replace variables in template string with values from the bindings dictionary
def populate(template, bindings):
    s = template
    for var, value in bindings.items():
        s = s.replace('(?%s)' % var, value)
    return s

# Extract variable names from a template string (s = '(?x) wears (?y)' returns {'x', 'y'})
def variables(s):
    return set(re.findall(r'\(\?([a-zA-Z][a-zA-Z0-9_]*)\)', s))

def instantiate(template, bindings):
    return populate(template, bindings)


class IF(object):
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        if isinstance(consequent, THEN):
            self.consequent = consequent
        else:
            self.consequent = THEN(consequent)
        
    # Return a string representation of the rule in format IF antecedent THEN consequent    
    def __str__(self):
        return "IF %s THEN %s" % (self.antecedent, self.consequent)
        
    def __repr__(self):
        return str(self)

class AND(list):
    def __init__(self, *args):
        super().__init__(args)
    
    # Return a string in format AND(condition1, condition2, ...)
    def __str__(self):
        return "AND(%s)" % ', '.join(map(str, self))
        
    def __repr__(self):
        return str(self)

class OR(list):
    def __init__(self, *args):
        super().__init__(args)
        
    # Return a string in format OR(condition1, condition2, ...)    
    def __str__(self):
        return "OR(%s)" % ', '.join(map(str, self))
        
    def __repr__(self):
        return str(self)

class THEN(list):
    def __init__(self, *args):
        super().__init__(args)
        
    def __str__(self):
        return "THEN(%s)" % ', '.join(map(str, self))
        
    def __repr__(self):
        return str(self)


def forward_chain(rules, data):
    inferred = set(data)
    added = True
    while added:
        added = False
        for rule in rules:
            # Find variable bindings that satisfy the rule antecedent based on the current inferred facts
            bindings_list = match_antecedent(rule.antecedent, inferred)
            for bindings in bindings_list:
                for conclusion in rule.consequent:
                    # Instantiate the conclusion using the variable bindings
                    consequent = instantiate_consequent(conclusion, bindings)
                    if consequent not in inferred:
                        inferred.add(consequent)
                        added = True
    # Return the set of inferred facts after no more can be added
    return inferred

# Find variable bindings that satisfy the antecedent of a rule based on the current set of inferred facts
def match_antecedent(antecedent, data):
    # Check if the antecedent is a simple string condition
    if isinstance(antecedent, str):
        bindings_list = []
        for fact in data:
            bindings = match(antecedent, fact)
            if bindings is not None:
                bindings_list.append(bindings)
        # Return the list of bindings that satisfy the antecedent        
        return bindings_list
    # If the antecedent is an AND of conditions
    elif isinstance(antecedent, AND):
        # Start with empty bindings dictionary
        bindings_list = [{}]
        for condition in antecedent:
            new_bindings_list = []
            for bindings in bindings_list:
                condition_inst = instantiate(condition, bindings)
                matches = match_antecedent(condition_inst, data)
                # For each matching binding found
                for match_bindings in matches:
                    merged_bindings = bindings.copy()
                    merged_bindings.update(match_bindings)
                    # Add the merged bindings to the new list
                    new_bindings_list.append(merged_bindings)
            bindings_list = new_bindings_list
        return bindings_list
    # If the antecedent is an OR of conditions
    elif isinstance(antecedent, OR):
        bindings_list = []
        for condition in antecedent:
            matches = match_antecedent(condition, data)
            # Add all matching bindings to the list
            bindings_list.extend(matches)
        return bindings_list
    else:
        # Return emtpy if no matches
        return []

# Instantiate the consequent/conclusion of a rule using the variable bindings obtained from matching the antecedent
def instantiate_consequent(consequent, bindings):
    return populate(consequent, bindings)


def backward_chain(rules, hypothesis, inferred=None):
    if inferred is None:
        inferred = set()
    # Check if hypothesis has already been processed to avoid infinite loops    
    if hypothesis in inferred:
        return []
    goal_tree = []
    for rule in rules:
        for conclusion in rule.consequent:
            # Attempt to match the conclusion with the hypothesis
            bindings = match(conclusion, hypothesis)
            # If a match is found
            if bindings is not None:
                # Retrieve the antecedent of the rule
                antecedent = rule.antecedent
                sub_goals = backward_chain_antecedent(rules, antecedent, bindings, inferred)
                goal_tree.append((rule, sub_goals))
    # If no rules were found
    if not goal_tree:
        # Add the hypothesis to the inferred set
        inferred.add(hypothesis)
        # Treat the hypothesis as a fact
        goal_tree.append((hypothesis, []))
    return goal_tree

# Try to satisfy the antecedent of a rule during backward chaining by recursively applying backward chaining to its conditions
def backward_chain_antecedent(rules, antecedent, bindings, inferred):
    # If the antecedent is simple condition
    if isinstance(antecedent, str):
        # Instantiates the condition with the current bindings
        instantiated = populate(antecedent, bindings)
        inferred.add(instantiated)
        # Recursively apply backward chaining to the instantiated condition
        sub_goals = backward_chain(rules, instantiated, inferred)
        # Return condition and its subgoals
        return [(instantiated, sub_goals)]
    # If the antecedent is an AND of conditions
    elif isinstance(antecedent, AND):
        sub_goals = []
        for condition in antecedent:
            instantiated = populate(condition, bindings)
            sub_sub_goals = backward_chain(rules, instantiated, inferred)
            sub_goals.append((instantiated, sub_sub_goals))
        return sub_goals
    elif isinstance(antecedent, OR):
        sub_goals = []
        for condition in antecedent:
            instantiated = populate(condition, bindings)
            sub_sub_goals = backward_chain(rules, instantiated, inferred)
            sub_goals.append((instantiated, sub_sub_goals))
        return sub_goals
    else:
        return []


class Features:
    wears_traditional_earth_clothes = '(?x) wear traditional Earth clothes'
    wears_modern_fashion = '(?x) wear modern fashion'
    wears_spacesuit = '(?x) wear spacesuit'
    wears_colorful_clothes = '(?x) wear colorful clothes'
    wears_traditional_cancri_clothes = '(?x) wear traditional Cancri clothes'
    wears_lunar_clothes = '(?x) wear lunar clothes'
    has_earth_accent = '(?x) has Earth accent'
    has_mars_accent = '(?x) has Mars accent'
    has_robotic_speech = '(?x) has robotic speech'
    has_hissing_accent = '(?x) has hissing accent'
    has_lunar_accent = '(?x) has lunar accent'
    takes_pictures_frequently = '(?x) take pictures frequently'
    supports_earth_moon_unification = '(?x) support Earth-Moon unification'
    supports_mars_independence = '(?x) support Mars independence'
    dislikes_loud_noises = '(?x) dislike loud noises'
    interested_in_lunar_culture = '(?x) is interested in lunar culture'
    walks_fast = '(?x) walk fast'
    walks_slowly = '(?x) walk slowly'
    has_antennae = '(?x) has antennae'
    has_tentacles = '(?x) has tentacles'
    has_multiple_eyes = '(?x) has multiple eyes'

class EarthOriginTourist:
    conclusion = '(?x) is an Earth-origin tourist'
    
class MarsOriginTourist:
    conclusion = '(?x) is a Mars-origin tourist'
    
class AlienTourist:
    conclusion = '(?x) is an alien tourist'
    
class EarthTourist:
    conclusion = '(?x) is an Earth Tourist'
    
class MarsTourist:
    conclusion = '(?x) is a Mars Tourist'
    
class GlieseTourist:
    conclusion = '(?x) is a Gliese Tourist'
    
class KeplerTourist:
    conclusion = '(?x) is a Kepler Tourist'
    
class CancriTourist:
    conclusion = '(?x) is a Cancri Tourist'
    
class Loonie:
    conclusion = '(?x) is a Loonie'


TOURIST_RULES = [
    IF(AND(Features.wears_modern_fashion,
           Features.has_earth_accent),
       THEN(EarthOriginTourist.conclusion)),
       
    IF(AND(Features.wears_modern_fashion,
           Features.has_mars_accent),
       THEN(MarsOriginTourist.conclusion)),
       
    IF(Features.has_antennae,
       THEN(AlienTourist.conclusion)),
       
    IF(Features.has_tentacles,
       THEN(AlienTourist.conclusion)),
       
    IF(Features.has_multiple_eyes,
       THEN(AlienTourist.conclusion)),
       
    IF(AND(Features.wears_lunar_clothes,
           Features.has_lunar_accent),
       THEN(Loonie.conclusion)),
       
    IF(AND(EarthOriginTourist.conclusion,
           Features.takes_pictures_frequently,
           Features.supports_earth_moon_unification),
       THEN(EarthTourist.conclusion)),
       
    IF(AND(MarsOriginTourist.conclusion,
           Features.walks_fast,
           Features.supports_mars_independence),
       THEN(MarsTourist.conclusion)),
       
    IF(AND(AlienTourist.conclusion,
           Features.wears_spacesuit,
           Features.has_robotic_speech),
       THEN(GlieseTourist.conclusion)),
       
    IF(AND(AlienTourist.conclusion,
           Features.wears_colorful_clothes,
           Features.walks_slowly,
           Features.interested_in_lunar_culture),
       THEN(KeplerTourist.conclusion)),
       
    IF(AND(AlienTourist.conclusion,
           Features.wears_traditional_cancri_clothes,
           Features.has_hissing_accent,
           Features.dislikes_loud_noises),
       THEN(CancriTourist.conclusion)),
]

# Used to retreieve all class variables from a class
def get_class_field_values(cls):
    values = [value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(getattr(cls, key))]
    return values


class Choices:
    def __init__(self):
        #Retrieve all feature strings from Features class
        self.features = get_class_field_values(Features)
        # Remove duplicates
        self.features = list(set(self.features))
        self.statements = [feature.replace('(?x) ', '') for feature in self.features]
        # Convert the statements into questions
        self.questions = [self.statement_to_question(statement) for statement in self.statements]
        
        self.conclusions = [
            EarthTourist.conclusion,
            MarsTourist.conclusion,
            GlieseTourist.conclusion,
            KeplerTourist.conclusion,
            CancriTourist.conclusion,
            Loonie.conclusion
        ]
        
    def statement_to_question(self, statement):
        if statement.startswith('wear'):
            return f'Do you {statement}?'
        elif statement.startswith('has'):
            return f'Do you have {statement[4:]}?'
        elif statement.startswith('take'):
            return f'Do you {statement}?'
        elif statement.startswith('support'):
            return f'Do you {statement}?'
        elif statement.startswith('dislike'):
            return f'Do you {statement}?'
        elif statement.startswith('is interested in'):
            return f'Are you interested in {statement[16:]}?'
        elif statement.startswith('walk'):
            return f'Do you {statement}?'
        elif statement.startswith('is'):
            return f'Are you{statement[2:]}?'
        else:
            return f'Do you {statement}?'
    
    def forward(self, name):
        print("Please answer the following questions:")
        facts = []
        indices = list(range(len(self.questions)))
        random.shuffle(indices)
        for index in indices:
            question = self.questions[index]
            answer = input(f"{question} (yes/no)\n")
            if answer.lower() == 'yes':
                fact = self.features[index].replace('(?x)', name)
                facts.append(fact)
            elif answer.lower() == 'no':
                continue
            else:
                print("Invalid answer, please answer 'yes' or 'no'.")
                continue
        inferred_facts = forward_chain(TOURIST_RULES, facts)
        tourist_types = []
        for conclusion in self.conclusions:
            populated_conclusion = conclusion.replace('(?x)', name)
            if populated_conclusion in inferred_facts:
                tourist_types.append(populated_conclusion)
        if tourist_types:
            print("Based on your answers, you are:")
            for tourist_type in tourist_types:
                print(tourist_type)
        else:
            print("Based on your answers, we could not identify your tourist type.")
    
    def backward(self, name):
        print("Please choose the tourist type to check:")
        for index, conclusion in enumerate(self.conclusions):
            print(f"{index + 1}. {conclusion.replace('(?x)', name)}")
        selected = input("Enter the number corresponding to your choice:\n")
        try:
            selected_index = int(selected) - 1
            if 0 <= selected_index < len(self.conclusions):
                goal = self.conclusions[selected_index].replace('(?x)', name)
                goal_tree = backward_chain(TOURIST_RULES, goal)
                if goal_tree:
                    print(f"To be identified as {goal}, you need to satisfy the following conditions:")
                    self.print_goal_tree(goal_tree)
                else:
                    print(f"No rules found to support that {goal}.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
    
    def print_goal_tree(self, goal_tree, indent=0):
        for (rule, sub_goals) in goal_tree:
            indent_str = ' ' * indent
            if isinstance(rule, IF):
                antecedent = rule.antecedent
                if isinstance(antecedent, str):
                    question = self.statement_to_question(antecedent.replace('(?x) ', ''))
                    print(f"{indent_str}- {question}")
                elif isinstance(antecedent, AND):
                    for condition in antecedent:
                        question = self.statement_to_question(condition.replace('(?x) ', ''))
                        print(f"{indent_str}- AND - {question}")
                elif isinstance(antecedent, OR):
                    for condition in antecedent:
                        question = self.statement_to_question(condition.replace('(?x) ', ''))
                        print(f"{indent_str}- OR - {question}")
                else:
                    pass
            elif isinstance(rule, str):
                question = self.statement_to_question(rule.replace('(?x) ', ''))
                print(f"{indent_str}- {question}")
            else:
                pass
            if sub_goals:
                self.print_goal_tree(sub_goals, indent + 2)


if __name__ == '__main__':
    print("Welcome to the Luna-City Tourist Expert System!")
    print("-----------------------------------------------")
    name = input("Please enter your name:\n")
    print(f"Hello, {name}!")
    choices = Choices()
    while True:
        print("Choose the algorithm you want to use:")
        algorithm = input("Enter 1 for Forward Chaining, 2 for Backward Chaining:\n")
        if algorithm == '1':
            choices.forward(name)
        elif algorithm == '2':
            choices.backward(name)
        else:
            print("Invalid choice.")
        continue_choice = input("Do you want to continue? (yes/no)\n")
        if continue_choice.lower() != 'yes':
            print("Goodbye!")
            break
