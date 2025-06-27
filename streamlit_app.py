import streamlit as st
import time
from openai import OpenAI


client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)






def LLM_api_call():
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
    



if "messages" not in st.session_state:
    preprompt="""
    You are an AI that chats with users and is able to show line graphs when needed.
    
    when you want to describe line graphs, please use the following format:
    
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
    
    Only use this format, and include all necessary fields. replace all spaces with _ in the fields.
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
        assistant_response = LLM_api_call()
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})



