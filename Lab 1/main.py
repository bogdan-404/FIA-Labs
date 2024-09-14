from production import forward_chain, backward_chain
from rules import TOURIST_RULES
from question_generator import QuestionGenerator

def ask_yes_no_question(question):
    while True:
        answer = input(f"{question['text']} (yes/no): ").lower()
        if answer in ['yes', 'no']:
            return answer
        else:
            print("Please answer with 'yes' or 'no'.")

def ask_multiple_choice(question):
    print("Multiple Choice Question:")
    print(question['text'])
    for i, option in enumerate(question['options']):
        print(f"{i+1}. {option}")
    while True:
        try:
            answer = int(input("Enter the number of your choice (1-4): ")) - 1
            if 0 <= answer < len(question['options']):
                return answer
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(question['options'])}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("Welcome to the Luna-City Tourist Detection System!")
    print("You will be asked a series of questions to determine if a person is a tourist.")
    print("Some questions will be yes/no, others will be multiple choice.")
    print("Please answer to the best of your ability.\n")
    
    try:
        qg = QuestionGenerator(TOURIST_RULES)
        facts = set()
        
        while True:
            question = qg.get_question()
            
            if question['type'] == 'yes_no':
                answer = ask_yes_no_question(question)
                if answer == 'yes':
                    facts.add(question['condition'])
                    print(f"Added fact: {question['condition']}")
                else:
                    negative_fact = f"NOT ({question['condition']})"
                    facts.add(negative_fact)
                    print(f"Added fact: {negative_fact}")
            elif question['type'] == 'multiple_choice':
                answer = ask_multiple_choice(question)
                selected_fact = question['options'][answer]
                facts.add(selected_fact)
                print(f"Added fact: {selected_fact}")
                for option in question['options']:
                    if option != selected_fact:
                        negative_fact = f"NOT ({option})"
                        facts.add(negative_fact)
                        print(f"Added fact: {negative_fact}")
            
            print("\nCurrent facts:", facts)
            
            # Forward chaining
            new_facts = set(forward_chain(TOURIST_RULES, facts))
            if new_facts != facts:
                print("New facts inferred:")
                for fact in new_facts - facts:
                    print(f"- {fact}")
                facts = new_facts
            else:
                print("No new facts inferred.")
            
            print("All current facts:", facts)
            
            # Check for conclusion
            for fact in facts:
                if "is a" in fact and "tourist" not in fact.lower() and not fact.startswith("NOT"):
                    print(f"\nConclusion reached: {fact}")
                    if "Loonie" not in fact:
                        print("This person is a tourist.")
                    else:
                        print("This person is not a tourist.")
                    return

            # Backward chaining
            tourist_types = ["Earth Businessman", "Mars Colonist", "Jovian Diplomat", "Venusian Artist", "Belter Miner"]
            for tourist_type in tourist_types:
                if backward_chain(TOURIST_RULES, f"(?x) is a {tourist_type}", facts):
                    print(f"\nBased on backward chaining, the person is likely a {tourist_type}.")
                    print("This person is a tourist.")
                    return

            if backward_chain(TOURIST_RULES, "(?x) is a Loonie", facts):
                print("\nBased on backward chaining, the person is likely a Loonie.")
                print("This person is not a tourist.")
                return

            print("\nGathering more information...\n")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        print("Please check your rule definitions and make sure all files are present and correctly formatted.")

if __name__ == '__main__':
    main()