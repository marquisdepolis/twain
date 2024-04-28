# %%
import os
import re
import openai
from openai import OpenAI
import time
import json
from dotenv import load_dotenv
from llms.llms import llm_call_gpt, llm_call_claude, llm_call_ollama

load_dotenv()

with open('info.json', 'r') as file:
    data = json.load(file)

instructions = data.get('instructions')
GPT = data.get('GPT_4')
CLAUDE = data.get('CLAUDE_OPUS')
OLLAMA = data.get('OLLAMA')

def get_llm_response(input_str, llm_type='claude'):
    if llm_type == 'openai':
        return llm_call_gpt(input_str, GPT)
    elif llm_type == 'claude':
        return llm_call_claude(input_str, CLAUDE)
    elif llm_type == 'ollama':
        return llm_call_ollama(input_str, OLLAMA)

def get_chars(input):
    messages = f"To solve this input, we need a list of characters and descriptions, both major and minor, who will have key parts to play. Write this in detail. {input}. Do not give any response other than what's asked for. No yapping."
    chars = get_llm_response(messages)
    if isinstance(chars, list):
        chars = chars[0]
    print(f"The characters in the story are: \n {chars}")
    return chars

def get_story(input, chars):
    messages = f"From the given prompt, generate a 6-part structure for a story, where each part has a 1 sentence description of what exactly happens in that part. Please start each part with Part X: {input}. The key characters for the overall story are {chars}. No extra yapping, only do the task assigned with no explanation otherwise."
    response = get_llm_response(messages)
    print(f"The structure of the story as returned: \n {response}")
    if isinstance(response, list) and len(response) == 1:
        response = response[0]
    # Split the string into parts based on 'Part \d+:'
    storyline_parts = re.split(r'Part \d+:', response)[1:]
    return [part.strip() for part in storyline_parts]

def write_chapters(chars, storyline_parts):
    with open('stories/story.txt', 'w', encoding='utf-8') as story_file:
        for index, part in enumerate(storyline_parts):
            print(f"{index}: {part}")
        for index, chapter_summary in enumerate(storyline_parts):
            messages = f"For this chapter, write the story and dialogue to explore it fully and bring the chapter to life. {chapter_summary}. The key characters for the overall story are {chars}. No extra yapping, only do the task assigned with no other explanation or preamble."
            chapter_content = get_llm_response(messages)
            if isinstance(chapter_content, list):
                chapter_content = chapter_content[0]

            # Save chapter to file
            story_file.write(f'Chapter {index + 1}\n\n')
            story_file.write(chapter_content)
            story_file.write('\n\n')

if __name__ == "__main__":
    input_text = "Write a story in the style of Neal Stephenson about asteroid mining, that is believable."
    chars = get_chars(input_text)
    storyline = get_story(input_text, chars)
    write_chapters(chars, storyline)
    print("Story has been written to 'story.txt'")


