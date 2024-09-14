import re
from utils import AIStringToRegex, match

class IF:
    def __init__(self, conditional, action):
        self._conditional = conditional
        self._action = action

    def apply(self, facts):
        if test_condition(self._conditional, facts):
            return self._action.apply(facts)
        return facts

    def __str__(self):
        return f"IF({self._conditional}, {self._action})"

class AND:
    def __init__(self, *conditions):
        self._conditions = conditions

    def test_matches(self, facts):
        return all(test_condition(cond, facts) for cond in self._conditions)

class OR:
    def __init__(self, *conditions):
        self._conditions = conditions

    def test_matches(self, facts):
        return any(test_condition(cond, facts) for cond in self._conditions)

class NOT:
    def __init__(self, condition):
        self._condition = condition

    def test_matches(self, facts):
        return not test_condition(self._condition, facts)

class THEN:
    def __init__(self, *actions):
        self._actions = actions

    def apply(self, facts):
        new_facts = set(facts)
        for action in self._actions:
            if isinstance(action, NOT):
                new_facts.add(f"NOT ({action._condition})")
            else:
                new_facts.add(action)
        return new_facts

def test_condition(condition, facts):
    if isinstance(condition, str):
        if condition.startswith("NOT (") and condition.endswith(")"):
            return condition in facts or not any(match(condition[5:-1], fact) for fact in facts if not fact.startswith("NOT"))
        return condition in facts or any(match(condition, fact) for fact in facts)
    return condition.test_matches(facts)

def forward_chain(rules, facts, verbose=False):
    while True:
        new_facts = set(facts)
        for rule in rules:
            new_facts = rule.apply(new_facts)
        if new_facts == facts:
            break
        facts = new_facts
    return facts

def backward_chain(rules, goal, facts=None):
    if facts is None:
        facts = set()
    
    def helper(goal):
        if goal in facts:
            return True
        if f"NOT ({goal})" in facts:
            return False
        
        for rule in rules:
            if isinstance(rule._action, THEN):
                consequents = rule._action._actions
            else:
                consequents = [rule._action]
            
            for consequent in consequents:
                if isinstance(consequent, str) and match(consequent, goal):
                    antecedents = rule._conditional
                    if isinstance(antecedents, AND):
                        if all(helper(ant) for ant in antecedents._conditions):
                            facts.add(goal)
                            return True
                    elif test_condition(antecedents, facts):
                        facts.add(goal)
                        return True
        return False

    return helper(goal)