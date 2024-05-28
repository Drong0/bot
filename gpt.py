from openai import OpenAI


class ChatSession:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.dialogues = []

    def update_dialogue(self, user_msg, bot_msg=None):
        self.dialogues.append({'user': user_msg, 'bot': bot_msg})
        print("Dialogue updated", self.dialogues)

    def generate_prompt(self, topic, level, current_message):
        prompt = f"User ({level}): Your main task as an advanced chatbot assistant is to help users on the {topic.lower()} as effectively as possible. Your communication should be very informal, like chatting with friends. This may include answering questions, providing useful information, or performing tasks based on user data. To help users effectively, it is important to be detailed and thorough in your responses. Use examples and evidence to back up your point of view and justify your recommendations or decisions. Don't forget to always prioritize user needs and satisfaction. Your ultimate goal is to provide the user with a useful and enjoyable experience. If a user asks you about programming or asks you to write code, do not answer his question, ask to write code, do not answer his question. Answer only in English language, suitable for a {level.lower()} level of English!\n\n"
        prompt += "Chat History:\n"
        for dialogue in self.dialogues:
            if dialogue['user']:
                prompt += f"User: {dialogue['user']}\n"
            if dialogue['bot']:
                prompt += f"Assistant: {dialogue['bot']}\n"
        prompt += f"\nUser: {current_message}\nAssistant: "
        return prompt

    def generate_prompt_essay(self, current_message):
        prompt = f"Your main task as an advanced chatbot assistant is to help users on the check each error and explain it available to a beginner in the format in their IELTS essay. Give some hints and suggestions to make better the essay  Use examples and evidence to back up your point of view and justify your recommendations or decisions. Don't forget to always prioritize user needs and satisfaction. Your ultimate goal is to provide the user with a useful and enjoyable experience. If a user asks you about programming or asks you to write code, do not answer his question, ask to write code, do not answer his question. Answer only in English language\n\n"
        prompt += f"\nUser: {current_message}\nAssistant: "
        print(prompt)
        return prompt

    def get_response_from_gpt(self, prompt):
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
