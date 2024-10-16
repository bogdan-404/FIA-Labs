import openai
import os


api_key = "sk-UOUvH9VdusyJqR0z5nmyPigslYPXT-xV-ZbVjyUo_3T3BlbkFJOztB2wkUcJhNue1mAC7D8apT0MfiKTFS9TmAAlWkMA"  

# Function to interact with GPT
def chat_with_gpt(prompt):
    openai.api_key = "sk-UOUvH9VdusyJqR0z5nmyPigslYPXT-xV-ZbVjyUo_3T3BlbkFJOztB2wkUcJhNue1mAC7D8apT0MfiKTFS9TmAAlWkMA"  
    
    try:
        response = openai.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Terminal-based loop for chatting with GPT
def main():
    print("Chat with GPT! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        response = chat_with_gpt(user_input)
        print(f"GPT: {response}\n")

if __name__ == "__main__":
    main()
