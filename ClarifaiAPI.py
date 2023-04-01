
# required installations:

# pip install streamlit
# pip install clarifai-grpc
# pip install pandas
# pip install pillow

import streamlit as st
from PIL import Image
import pandas as pd

st.title("Upload Image - jpg")

# 1) API Enter app key - COMMENTED OUT / NO NEED
# st.header("Enter app key: ")
# key = st.text_input("App Key")

# if (key == ""):
#     st.warning("Error: No app key detected")
#     st.stop()
# else:
#     st.write("An app key has been uploaded")

# 2) Input Files
file_data = st.file_uploader("Upload Image", type=['jpg', 'jpeg'])

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
    names.append(concept.name)
    confidences.append(concept.value)

df = pd.DataFrame ({
    "Concept Name":names,
    "Model Confidence:":confidences
})
st.dataframe(df)