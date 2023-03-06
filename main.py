import gradio as gr
import openai
from fastapi import FastAPI

openai.api_key_path = ".env"
CUSTOM_PATH = "/chat"

app = FastAPI(description="ChatGPT API Demo")

config = {
    "instruction": {
        "system": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. Knowledge cutoff: {knowledge_cutoff} Current date: {current_date}"
    }
}


def ask_bot(prompt, dialogue):
    dialogue.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=dialogue
    )
    result = response["choices"][0]["message"]["content"]
    dialogue.append({"role": "assistant", "content": result})

    return parse_text(result)


def parse_text(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "```" in line:
            items = line.split('`')
            if items[-1]:
                lines[i] = f'<pre><code class="{items[-1]}">'
            else:
                lines[i] = f'</code></pre>'
        else:
            if i>0:
                line = line.replace("<", "&lt;")
                line = line.replace(">", "&gt;")
                lines[i] = '<br/>'+line.replace(" ", "&nbsp;")
    return "".join(lines)


def chat(inputs, history, dialogue):
    history = history or []
    output = ask_bot(inputs, dialogue)
    history.append((inputs, output))
    return history, history


def reset():
    return [], [], [{"role": "system", "content": config["instruction"]["system"]}]


with gr.Blocks(css="style.css") as demo:
    gr.Markdown("""<h1><center>ChatGPT API Demo</center></h1>""")
        
    chatbot1 = gr.Chatbot(elem_id="chatbot", show_label=False).style(color_map=("blue", "white"))
    dialogue = gr.State([{"role": "system", "content": config["instruction"]["system"]}])
    state = gr.State([])
    message = gr.Textbox(placeholder="Chat here", label="Human: ")
    message.submit(chat, inputs=[message, state, dialogue], outputs=[chatbot1, state])
    message.submit(lambda: "", None, message)

    submit = gr.Button("SEND")
    submit.click(chat, inputs=[message, state, dialogue], outputs=[chatbot1, state])
    submit.click(lambda: "", None, message)
    
    submit = gr.Button("RESET")
    submit.click(reset, outputs=[chatbot1, state, dialogue])
    submit.click(lambda: "", None, message)


@app.get("/")
def read_main():
    return {"message": "This is the main app"}


app = gr.mount_gradio_app(app, demo, path=CUSTOM_PATH)
