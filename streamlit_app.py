import streamlit as st
import time
from openai import OpenAI
import re
import matplotlib.pyplot as plt
import ast
import io
import base64

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)






def LLM_api_call():
    #return "Here is a graph LINE_GRAPH_START Graph Title: Graph X-Axis Label: x Y-Axis Label: y Data: x^2 x: [1,2,3,4,5,6,7,8,9] y: [1,4,9,16,25,36,49,64,81] x+3 x: [1,5,8] y: [4,8,11] LINE_GRAPH_END wish you like this"
    output=""
    completion = client.chat.completions.create(
      model="mistralai/mistral-nemotron",
      messages=st.session_state.messages,
      temperature=0.6,
      top_p=0.7,
      max_tokens=4096,
      stream=True
    )
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            output += chunk.choices[0].delta.content
    return output
    

def parse_and_generate_graphs_as_datauri(input_text: str):
    match = re.search(
        r"LINE_GRAPH_START\s+Graph Title: (.*?)\s+X-Axis Label: (.*?)\s+Y-Axis Label: (.*?)\s+Data:(.*?)LINE_GRAPH_END",
        input_text,
        re.DOTALL,
    )

    if match:
        title, x_label, y_label, data_block = match.groups()

    


    
    title = title.strip().replace("_", " ")
    x_label = x_label.strip().replace("_", " ")
    y_label = y_label.strip().replace("_", " ")

    lines = re.findall(
        r"([^\n]+?)\s+x:\s*(\[[^\]]+\])\s*y:\s*(\[[^\]]+\])", data_block
    )

    plt.figure()
    for line_name, x_list, y_list in lines:
        line_name = line_name.strip().replace("_", " ")
        x = ast.literal_eval(x_list)
        y = ast.literal_eval(y_list)
        plt.plot(x, y, label=line_name)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()

    # Convert plot to Data URI
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return f"![Plot](data:image/png;base64,{encoded})"
    










if "messages" not in st.session_state:
    preprompt="""
    You are an AI that chats with users and is able to show line graphs when needed.

    when you want to describe line graphs, please use the following format:

    LINE_GRAPH_START
    Graph Title: <Title of the Graph>
    X-Axis Label: <Label for the x-axis>
    Y-Axis Label: <Label for the y-axis>

    Data:
    <Line Name 1>
    x: [x1, x2, x3, ...]
    y: [y1, y2, y3, ...]

    <Line Name 2>
    x: [x1, x2, x3, ...]
    y: [y1, y2, y3, ...]
    LINE_GRAPH_END

    Only use this format, and include all necessary fields. replace all spaces with _ in the names.
    """
    st.session_state.messages = [{"role": "assistant", "content": preprompt}]


st.write("Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat.")

st.caption("Note that this demo app isn't actually connected to any LLMs. Those are expensive ;)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        shown_responce = ""
        graph_gen = ""
        graphing = False
        assistant_response = LLM_api_call()
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            print (chunk)
            full_response += chunk + " "
            if (chunk =="LINE_GRAPH_START"):
                graphing = True
            if (graphing):
                graph_gen += chunk+ " "
            else:
                shown_responce += chunk + " "
            if (chunk=="LINE_GRAPH_END"):
                graphing=False
                shown_responce += "\n"
                shown_responce += parse_and_generate_graphs_as_datauri(graph_gen)
                shown_responce += "\n"
                graph_gen = ""
            
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(shown_responce + "▌")
        message_placeholder.markdown(shown_responce)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

