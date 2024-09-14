import re

def AIStringToRegex(AIStr):
    return re.sub(r'\(\?(\w+)\)', r'(?P<\1>.*?)', AIStr) + '$'

def match(template, AIStr):
    regex = AIStringToRegex(template)
    match = re.match(regex, AIStr)
    return match.groupdict() if match else None