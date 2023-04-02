# required installations:

# pip install streamlit
# pip install clarifai-grpc
# pip install pandas
# pip install pillow
import os
import openai
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import pandas as pd

load_dotenv()
openai.api_key = os.getenv("APIkey")


def chat(user_input):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{user_input}",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )

    message = response.choices[0].text.strip()
    return message


st.title("Nutri:orange[Ai]d")

st.header("Introducing Nutri:orange[Ai]d – your ultimate nutrition partner! "
          "Whether you’re aiming to hit specific macros or sticking to a meal budget, "
          "Nutri:orange[Ai]d has got you covered. Now you can Aid, you can plan, cook, and track your meals with ease, "
          "ensuring that you always stay on track towards your health goals.")

st.markdown("Nutri:orange[Ai]d is your ultimate solution for achieving your health goals with a healthy and balanced diet. "
            "With Nutri:orange[Ai]d, all you need to do is take a photo of your ingredients and answer a few questions asked by "
            "our AI-powered chatbot to get customized diet plans tailored to your specific dietary needs. "
            "But Nutri:orange[Ai]d doesn’t stop there – it takes meal planning to the next level by providing macro tracking "
            "and analysis of your daily food intake. Our chatbot helps you balance your macronutrients and "
            "gives insights into your nutritional habits, so you can stay on track with your health goals without "
            "having to spend hours searching for recipes. Say goodbye to boring meals and hello to a variety of tasty "
            "and healthy dishes with Nutri:orange[Ai]d. Experience the future of food and nutrition right at your fingertips!")

# 2) Input Files
file_data = st.file_uploader("Upload Image - jpg", type=['jpg', 'jpeg'])

if file_data == None:
    st.warning("Error: No file detected")
    st.stop()
else:
    image = Image.open(file_data)
    st.image(image)

# 3) Predict contents from an Image
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

CLARIFAI_API_KEY = "be9e7f2af35d416a8247cac074e8927e"
APPLICATION_ID = "streamlit-app"
# SAMPLE_URL = "https://samples.clarifai.com/metro-north.jpg"

# This is how you authenticate.
# metadata = (('authorization", f"Key'.format(key)),)
# metadata = (('authorization', 'Key ' + CLARIFAI_API_KEY),)
metadata = (("authorization", f"Key {CLARIFAI_API_KEY}"),)

request = service_pb2.PostModelOutputsRequest(
    # This is the model ID of a publicly available General model. You may use any other public or custom model ID.
    model_id="general-image-recognition",
    user_app_id=resources_pb2.UserAppIDSet(app_id=APPLICATION_ID),
    inputs=[
        resources_pb2.Input(
            data=resources_pb2.Data(image=resources_pb2.Image(base64=file_data.getvalue()))
        )
    ],
)
response = stub.PostModelOutputs(request, metadata=metadata)

if response.status.code != status_code_pb2.SUCCESS:
    print(response)
    raise Exception(f"Request failed, status code: {response.status}")

names = []
confidences = []

for concept in response.outputs[0].data.concepts:
    # st.write("%12s: %.2f" % (concept.name, concept.value))
    if concept.name != "no person":
        names.append(concept.name)
        confidences.append(concept.value)

# df = pd.DataFrame ({
#     "Concept Name":names,
#     "Model Confidence:":confidences
# })
# st.dataframe(df)

# Keywords
st.header("Keywords found:")
x = ", ".join(names)
st.write(x)

user_input = st.text_input("Ask Nutri:orange[Ai]d a question")
if st.button("Submit"):
    response = chat(user_input)
    st.write(response)
