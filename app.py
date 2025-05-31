# # import streamlit as st
# # import pandas as pd



# # with st.form("page"):
# #     data = st.file_uploader("Upload a csv", accept_multiple_files=False, type=["csv"], )
# #     if data == None:
# #         data = st.text_input("Enter Text", disabled=True)
# #     st.form_submit_button("Submit")

# # # st.camera_input("Camera")

# # if data:
# #     df = pd.read_csv(data, index_col=0)
# #     st.dataframe(df.head(5))
# import socket

# # get the hostname of the socket
# hostname = socket.gethostname()
# # get the IP address of the hostname
# ip_address = socket.gethostbyname(hostname)
# print('IP Address:{}'.format(ip_address))
import streamlit as st
st.title("UZ Info Bot 🤖")
st.logo("uz.jpg", link="https://www.uz.ac.zw", size="large")
