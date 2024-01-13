# Writes and displays the story in a gradio output box. Now deprecated.
import gradio as gr
import re
import openai
import os
import time
import dotenv

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


os.environ["OPENAI_API_KEY"] = open_file('openai_api_key.txt')
openai.api_key = open_file('openai_api_key.txt')
openai_api_key = openai.api_key


class Writer():
    @staticmethod
    def ask_gpt3(prompt, max_retries=3, delay=2):
        retries = 0
        while retries < max_retries:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=prompt,
                )
                assistant_message = {
                    "role": "assistant",
                    "content": response.choices[0].message["content"]
                }
                prompt.append(assistant_message)
                return assistant_message["content"]
            except openai.error.OpenAIError as e:
                print(f"Error occurred during API call: {e}")
                retries += 1
                if retries < max_retries:
                    time.sleep(delay)  # Delay between retries
                else:
                    raise

    def get_chars(self, input):
        messages = [{"role": "system", "content": "To solve this input, we need a list of characters and descriptions, both major and minor, who will have key parts to play. Help me write this please."}]
        user_message = {"role": "user", "content": input}
        messages.append(user_message)
        chars = self.ask_gpt3(messages)
        return chars

    def get_story(self, input, chars):
        messages = [
            {"role": "system",
                "content": "From the given prompt, generate a 6-part structure for a novella, where each part has a 1 sentence description of what exactly happens in that part. Please start each part with Part X:"},
            {"role": "user", "content": input},
            {"role": "user", "content": f"The key characters for the overall story are {chars}"}
        ]
        response = self.ask_gpt3(messages)
        storyline_parts = re.split(r'Part \d+:', response)[1:]
        return [part.strip() for part in storyline_parts]

    def write_chapters(self, chars, storyline_parts):
        with open('story.txt', 'w', encoding='utf-8') as story_file:
            for index, part in enumerate(storyline_parts):
                print(f"{index}: {part}")
            for index, chapter_summary in enumerate(storyline_parts):
                messages = [
                    {"role": "system", "content": "For this chapter, write the story and dialogue to explore it fully and bring the chapter to life"}]
                user_message = {"role": "user", "content": chapter_summary}
                char_message = {
                    "role": "user", "content": f"The key characters for the overall story are {chars}"}
                messages.append(user_message)
                messages.append(char_message)
                chapter_content = self.ask_gpt3(messages)

                # Save chapter to file
                story_file.write(f'Chapter {index + 1}\n\n')
                story_file.write(chapter_content)
                story_file.write('\n\n')


def main(input_text):
    writer = Writer()
    chars = writer.get_chars(input_text)
    storyline = writer.get_story(input_text, chars)
    writer.write_chapters(chars, storyline)
    with open('story.txt', 'r', encoding='utf-8') as story_file:
        return story_file.read()


if __name__ == "__main__":
    iface = gr.Interface(fn=main, inputs="text", outputs="text",
                         title="Story Generator", description="Generate a story based on your input.")
    iface.launch(share=True)

# if __name__ == "__main__":
#     writer = Writer()
#     input_text = "Write a short story in the style of Haruki Murakami about a machine just trying to live life in a complex world."
#     chars = writer.get_chars(input_text)
#     storyline = writer.get_story(input_text, chars)
#     writer.write_chapters(chars, storyline)
#     print("Story has been written to 'story.txt'")
