import random

class Node:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type  # 'and', 'or', 'characteristic', 'tourist'
        self.value = value  # For 'characteristic', value is (characteristic_name, expected_value)
        self.children = children or []

class Characteristic:
    def __init__(self, name, ctype='binary', options=None):
        self.name = name  # E.g., 'have ears', 'be telepathic', 'wear hat'
        self.ctype = ctype  # 'binary', 'multiple_choice', 'percentage'
        self.options = options or []

# Define characteristics
characteristics = {
    'have ears': Characteristic('have ears', 'binary'),
    'be telepathic': Characteristic('be telepathic', 'binary'),
    'wear hat': Characteristic('wear hat', 'binary'),
    'wear sneakers': Characteristic('wear sneakers', 'binary'),
    'intellect': Characteristic('intellect', 'percentage'),
    'origin': Characteristic('origin', 'multiple_choice', ['Solar System', 'New Horizon System']),
    'number of eyes': Characteristic('number of eyes', 'multiple_choice', ['two', 'three', 'many']),
    'skin color': Characteristic('skin color', 'multiple_choice', ['green', 'blue', 'red', 'pale']),
    'body type': Characteristic('body type', 'multiple_choice', ['humanoid', 'insectoid', 'energy-based']),
    'communication method': Characteristic('communication method', 'multiple_choice', ['verbal', 'telepathic', 'gesture']),
    'favorite food': Characteristic('favorite food', 'multiple_choice', ['pizza', 'rocks', 'light']),
    'is tourist': Characteristic('a tourist', 'binary'),
}

# Build the decision tree with 3-4 levels of subgoals and AND/OR logic
tree = Node('or', children=[
    # Tourist Branch
    Node('and', children=[
        Node('characteristic', ('is tourist', 'yes')),
        Node('or', children=[
            # Solar System Tourists
            Node('and', children=[
                Node('characteristic', ('origin', 'Solar System')),
                Node('or', children=[
                    # Earth Tourist
                    Node('and', children=[
                        Node('characteristic', ('intellect', '>60')),
                        Node('characteristic', ('wear hat', 'yes')),
                        Node('characteristic', ('have ears', 'yes')),
                        Node('tourist', 'Earth Tourist'),
                    ]),
                    # Mars Tourist
                    Node('and', children=[
                        Node('characteristic', ('intellect', '<=60')),
                        Node('characteristic', ('wear sneakers', 'yes')),
                        Node('characteristic', ('have ears', 'yes')),
                        Node('tourist', 'Mars Tourist'),
                    ]),
                ]),
            ]),
            # New Horizon System Tourists
            Node('and', children=[
                Node('characteristic', ('origin', 'New Horizon System')),
                Node('or', children=[
                    # Gliese Tourist
                    Node('and', children=[
                        Node('characteristic', ('be telepathic', 'yes')),
                        Node('characteristic', ('have ears', 'no')),
                        Node('characteristic', ('number of eyes', 'many')),
                        Node('tourist', 'Gliese Tourist'),
                    ]),
                    # Kepler Tourist
                    Node('and', children=[
                        Node('characteristic', ('be telepathic', 'no')),
                        Node('characteristic', ('have ears', 'no')),
                        Node('characteristic', ('skin color', 'blue')),
                        Node('tourist', 'Kepler Tourist'),
                    ]),
                    # Cancri Tourist
                    Node('and', children=[
                        Node('characteristic', ('be telepathic', 'yes')),
                        Node('characteristic', ('communication method', 'gesture')),
                        Node('characteristic', ('favorite food', 'light')),
                        Node('tourist', 'Cancri Tourist'),
                    ]),
                ]),
            ]),
        ]),
    ]),
    # Loonie Branch (Not a Tourist)
    Node('and', children=[
        Node('characteristic', ('is tourist', 'no')),
        Node('characteristic', ('origin', 'Solar System')),
        Node('characteristic', ('intellect', '>60')),
        Node('tourist', 'Loonie'),
    ]),
])

def generate_question(char_name):
    c = characteristics[char_name]
    if c.ctype == 'binary':
        question = f"Is the visitor {c.name}? (yes/no): "
    elif c.ctype == 'multiple_choice':
        options = ', '.join(c.options)
        question = f"What is the visitor's {c.name}? ({options}): "
    elif c.ctype == 'percentage':
        question = f"What is the visitor's {c.name} level? (0-100): "
    return question

def ask_question(char_name):
    c = characteristics[char_name]
    while True:
        question = generate_question(char_name)
        answer = input(question).strip()
        if c.ctype == 'binary':
            if answer.lower() in ['yes', 'no']:
                return answer.lower()
            else:
                print("Please answer 'yes' or 'no'.")
        elif c.ctype == 'multiple_choice':
            if answer in c.options:
                return answer
            else:
                print(f"Please choose from: {', '.join(c.options)}.")
        elif c.ctype == 'percentage':
            try:
                value = int(answer)
                if 0 <= value <= 100:
                    return value
                else:
                    print("Please enter a number between 0 and 100.")
            except ValueError:
                print("Please enter a valid number between 0 and 100.")

def evaluate_condition(answer, expected_value, char_name):
    c = characteristics[char_name]
    if c.ctype == 'percentage':
        operator = expected_value[:2] if expected_value[:2] in ['<=', '>='] else expected_value[0]
        expected_number = int(expected_value[2:] if operator in ['<=', '>='] else expected_value[1:])
        if operator == '<':
            return answer < expected_number
        elif operator == '>':
            return answer > expected_number
        elif operator == '<=':
            return answer <= expected_number
        elif operator == '>=':
            return answer >= expected_number
        elif operator == '=':
            return answer == expected_number
    else:
        return answer == expected_value

def collect_all_characteristics(node, chars_set):
    if node.node_type == 'characteristic':
        char_name, _ = node.value
        chars_set.add(char_name)
    elif node.children:
        for child in node.children:
            collect_all_characteristics(child, chars_set)

def possible_paths(node, known_answers):
    if node.node_type == 'tourist':
        return [[node]]
    elif node.node_type == 'characteristic':
        char_name, expected_value = node.value
        if char_name in known_answers:
            answer = known_answers[char_name]
            if evaluate_condition(answer, expected_value, char_name):
                return [[]]
            else:
                return []
        else:
            return [[node]]
    elif node.node_type == 'and':
        paths = [[]]
        for child in node.children:
            child_paths = possible_paths(child, known_answers)
            if not child_paths:
                return []
            new_paths = []
            for path in paths:
                for cpath in child_paths:
                    new_paths.append(path + cpath)
            paths = new_paths
        return paths
    elif node.node_type == 'or':
        paths = []
        for child in node.children:
            child_paths = possible_paths(child, known_answers)
            paths.extend(child_paths)
        return paths
    else:
        return []

def select_next_question(possible_paths, asked_questions):
    char_counts = {}
    for path in possible_paths:
        for node in path:
            if node.node_type == 'characteristic':
                char_name, _ = node.value
                if char_name not in asked_questions:
                    char_counts[char_name] = char_counts.get(char_name, 0) + 1
    if not char_counts:
        return None
    # Randomly select from the characteristics with the highest count
    max_count = max(char_counts.values())
    candidates = [char for char, count in char_counts.items() if count == max_count]
    return random.choice(candidates)

def forward_chaining_random(node):
    known_answers = {}
    asked_questions = set()
    # Collect all characteristics from the tree
    all_chars = set()
    collect_all_characteristics(node, all_chars)
    all_chars = list(all_chars)
    # Randomly select the first question from all characteristics
    if all_chars:
        first_question = random.choice(all_chars)
        answer = ask_question(first_question)
        known_answers[first_question] = answer
        asked_questions.add(first_question)
    while True:
        paths = possible_paths(node, known_answers)
        if not paths:
            print("\nThe visitor type is unknown based on the provided information.")
            return
        # Check if we have reached a conclusion
        for path in paths:
            if all(node.node_type != 'characteristic' for node in path) and path[-1].node_type == 'tourist':
                print(f"\nThe visitor is classified as: {path[-1].value}")
                return
        # Select next question
        next_char = select_next_question(paths, asked_questions)
        if not next_char:
            print("\nThe visitor type is unknown based on the provided information.")
            return
        answer = ask_question(next_char)
        known_answers[next_char] = answer
        asked_questions.add(next_char)

def backward_chaining(node, goal, path):
    if node.node_type == 'tourist' and node.value == goal:
        path.append(node)
        return True
    elif node.node_type == 'and':
        path.append(node)
        for child in node.children:
            if not backward_chaining(child, goal, path):
                while path and path[-1] != node:
                    path.pop()
                return False
        return True
    elif node.node_type == 'or':
        path.append(node)
        for child in node.children:
            if backward_chaining(child, goal, path):
                return True
        while path and path[-1] != node:
            path.pop()
        path.pop()
        return False
    elif node.node_type == 'characteristic':
        path.append(node)
        return True
    return False

def print_backward_chaining_result(goal, path):
    print(f"\nTo identify a {goal}, the following characteristics and expected answers are considered:")
    subgoal_conditions = []
    for node in path:
        if node.node_type == 'characteristic':
            char_name, expected_value = node.value
            c = characteristics[char_name]
            subgoal_conditions.append(f"{char_name} = {expected_value}")
            question = generate_question(char_name).split("?")[0]
            print(f"- {question}? Expected answer: {expected_value}")
        elif node.node_type == 'tourist':
            print(f"- Identified visitor type: {node.value}")
    if subgoal_conditions:
        subgoal_description = " and ".join(subgoal_conditions)
        print(f"- Subgoal: Visitor {subgoal_description}")

def main():
    print("Welcome to the Luna-City Tourist Expert System!")
    mode = input("Choose mode (1 for Forward Chaining, 2 for Backward Chaining): ").strip()

    if mode == "1":
        print("\nStarting Forward Chaining...")
        forward_chaining_random(tree)
    elif mode == "2":
        goal = input("Enter the visitor type you want to check: ").strip()
        print(f"\nBackward Chaining to determine if the visitor is a {goal}...")
        path = []
        if backward_chaining(tree, goal, path):
            print_backward_chaining_result(goal, path)
        else:
            print(f"\nCould not find a path to confirm that the visitor is a {goal}.")
    else:
        print("Invalid mode selected.")

if __name__ == "__main__":
    main()
