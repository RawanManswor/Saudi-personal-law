from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Create a class to handle the chatbot logic
class SaudiPersonalLawAssistant:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("ASSISTANT_ID")

        self.client = OpenAI(api_key=self.api_key)
        self.messages = []
        self.start_chat = False
        self.thread = None

    def wait_for_complete(self, run, thread):
        # Wait until the chat run is complete
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def process_replies(self, replies):
        paragraphs = []
        citations = []

        for r in replies:
            if r.role == "assistant":
                message_content = r.content[0].text
                annotations = message_content.annotations

                # Replace annotations with placeholders and handle citations
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(
                        annotation.text, f" [{index}]"
                    )

                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = self.client.files.retrieve(file_citation.file_id)
                        citations.append(
                            f"[{index}] {file_citation.quote} from {cited_file.filename}"
                        )
                    elif file_path := getattr(annotation, "file_path", None):
                        cited_file = self.client.files.retrieve(file_path.file_id)
                        citations.append(
                            f"[{index}] Click <a href='{cited_file.url}'>here</a> to download {cited_file.filename}"
                        )

                # Split the message content into paragraphs
                paragraphs.extend(message_content.value.split("\n\n"))

        # Join paragraphs with line breaks
        paragraphs_with_line_breaks = "<br>".join(paragraphs)
        full_response = paragraphs_with_line_breaks + "<br>" + "<br>".join(citations)
        return full_response

    def chat_input(self, prompt):
        if prompt:
            self.messages.append({"role": "user", "content": prompt})

            # Create a new thread and add user message to it
            self.thread = self.client.beta.threads.create()
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=prompt,
            )

            # Run the chat conversation
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
            )

            run = self.wait_for_complete(run, self.thread)
            replies = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )

            processed_response = self.process_replies(replies)
            self.messages.append({"role": "assistant", "content": processed_response})

    def run(self):
        if self.client:
            self.start_chat = True

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     chatbot = SaudiPersonalLawAssistant()
#     if request.method == 'POST':
#         message = request.form['message']
#         chatbot.chat_input(message)
#     return render_template('chat.html', messages=chatbot.messages)

# @app.route('/get', methods=['POST'])
# def get_bot_response():
#     chatbot = SaudiPersonalLawAssistant()
#     if request.method == 'POST':
#         message = request.form['msg']
#         chatbot.chat_input(message)
#         response = chatbot.messages[-1]['content']
#         return jsonify(response)
#     return jsonify('Error: Invalid request')

# if __name__ == "__main__":
#     app.run(debug=False)