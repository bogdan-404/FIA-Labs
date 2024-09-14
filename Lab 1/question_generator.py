import random
from production import AND, OR, NOT

class QuestionGenerator:
    def __init__(self, rules):
        self.rules = rules
        self.questions = self._generate_questions()

    def _generate_questions(self):
        questions = []
        for rule in self.rules:
            if isinstance(rule._conditional, AND):
                for condition in rule._conditional._conditions:
                    questions.append(self._create_question(condition))
            elif isinstance(rule._conditional, str):
                questions.append(self._create_question(rule._conditional))
        return questions

    def _create_question(self, condition):
        condition = condition.replace('(?x)', 'the person')
        
        # Yes/No question
        if random.random() < 0.5:
            verb = 'Does'
            if condition.startswith('the person has'):
                verb = 'Has'
            elif condition.startswith('the person is'):
                verb = 'Is'
            return {
                'type': 'yes_no',
                'text': f"{verb} {condition}?",
                'condition': condition
            }
        
        # Multiple choice question
        else:
            return self._create_multiple_choice(condition)

    def _create_multiple_choice(self, condition):
        options = [condition]
        rule_conditions = self._get_all_rule_conditions()
        while len(options) < 4:
            random_condition = random.choice(rule_conditions)
            if random_condition not in options:
                options.append(random_condition)
        random.shuffle(options)
        return {
            'type': 'multiple_choice',
            'text': f"Which of the following is true?",
            'options': options,
            'correct': options.index(condition),
            'condition': condition
        }

    def _get_all_rule_conditions(self):
        conditions = []
        for rule in self.rules:
            if isinstance(rule._conditional, AND):
                conditions.extend([cond.replace('(?x)', 'the person') for cond in rule._conditional._conditions])
            elif isinstance(rule._conditional, str):
                conditions.append(rule._conditional.replace('(?x)', 'the person'))
        return conditions

    def get_question(self):
        return random.choice(self.questions)