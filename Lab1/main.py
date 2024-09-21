import random

class Node:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type  # 'and', 'or', 'characteristic', 'tourist'
        self.value = value  # For 'characteristic', value is (characteristic_name, expected_value)
        self.children = children or []

class Characteristic:
    def __init__(self, name, ctype='binary', options=None):
        self.name = name  # e.g., 'have ears', 'be telepathic', 'wear hat'
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
}

# Adjusted 'is tourist' characteristic for proper grammar
characteristics['is tourist'] = Characteristic('a tourist', 'binary')

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
                        Node('tourist', 'Earth Tourist')
                    ]),
                    # Mars Tourist
                    Node('and', children=[
                        Node('characteristic', ('intellect', '<=60')),
                        Node('characteristic', ('wear sneakers', 'yes')),
                        Node('characteristic', ('have ears', 'yes')),
                        Node('tourist', 'Mars Tourist')
                    ]),
                ])
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
                        Node('tourist', 'Gliese Tourist')
                    ]),
                    # Kepler Tourist
                    Node('and', children=[
                        Node('characteristic', ('be telepathic', 'no')),
                        Node('characteristic', ('have ears', 'no')),
                        Node('characteristic', ('skin color', 'blue')),
                        Node('tourist', 'Kepler Tourist')
                    ]),
                    # Cancri Tourist
                    Node('and', children=[
                        Node('characteristic', ('be telepathic', 'yes')),
                        Node('characteristic', ('communication method', 'gesture')),
                        Node('characteristic', ('favorite food', 'light')),
                        Node('tourist', 'Cancri Tourist')
                    ]),
                ])
            ]),
        ])
    ]),
    # Loonie Branch (Not a Tourist)
    Node('and', children=[
        Node('characteristic', ('is tourist', 'no')),
        Node('characteristic', ('origin', 'Solar System')),
        Node('characteristic', ('intellect', '>60')),
        Node('tourist', 'Loonie')
    ])
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

def can_satisfy(node, known_answers):
    if node.node_type == 'characteristic':
        char_name, expected_value = node.value
        if char_name in known_answers:
            answer = known_answers[char_name]
            return evaluate_condition(answer, expected_value, char_name)
        else:
            return True  # We don't know yet, so it's possible
    elif node.node_type == 'and':
        for child in node.children:
            if not can_satisfy(child, known_answers):
                return False
        return True
    elif node.node_type == 'or':
        for child in node.children:
            if can_satisfy(child, known_answers):
                return True
        return False
    elif node.node_type == 'tourist':
        return True
    return False

def forward_chaining(node, known_answers):
    if node.node_type == 'characteristic':
        char_name, expected_value = node.value
        if char_name in known_answers:
            answer = known_answers[char_name]
        else:
            answer = ask_question(char_name)
            known_answers[char_name] = answer
        if evaluate_condition(answer, expected_value, char_name):
            return True
        else:
            return False
    elif node.node_type == 'and':
        for child in node.children:
            result = forward_chaining(child, known_answers)
            if not result:
                return False
        return True
    elif node.node_type == 'or':
        children = node.children[:]
        random.shuffle(children)
        for child in children:
            if not can_satisfy(child, known_answers):
                continue  # Skip this branch due to conflict
            result = forward_chaining(child, known_answers)
            if result:
                return True
        return False
    elif node.node_type == 'tourist':
        print(f"\nThe visitor is classified as: {node.value}")
        return True
    return False

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
        known_answers = {}
        result = forward_chaining(tree, known_answers)
        if not result:
            print("\nThe visitor type is unknown based on the provided information.")
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
