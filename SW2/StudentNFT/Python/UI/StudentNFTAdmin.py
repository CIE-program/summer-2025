#StudentNFTAdmin.py
import streamlit as st
import requests
from datetime import date
import json
import pandas as pd


API_URL = "http://127.0.0.1:5000"

badgeTypes = ["TopQuizzer", "PitchMaster", "TopInnovator"]
studentWallets = {}
with open("./StudentWalletMapping.json") as f:
    studentWallets = json.load(f)

# Formatting the data to print the Table for the Minted/Granted Badges
def format_data_for_display(raw_data):
    formatted_data = []
    for item in raw_data:
        cert_url = item.get('metadata_uri', '')

        formatted_item = {
            "Student Name": item.get("student_name", ""),
            "Class/Semester": item.get("class_semester", ""),
            "Badge Type": item.get("badge_type", ""),
            "Grant Date": item.get("grant_date", ""),
            "University": item.get("university", ""),
            "Metadata URL": item.get('metadata_uri', '')
        }
        formatted_data.append(formatted_item)
    return formatted_data

# Sidebar navigation
page = st.sidebar.radio("Menu", ["🏠 Home", "🪙 Mint Badge NFT", "🎖️ View Granted Badges"], index=0)

st.title("🎓 Student Badge Admin Panel")

if page == "🏠 Home":
    # --- Summary Page (Main Landing Page) ---
    st.header("Summary")
    st.markdown("""
        Welcome to the **Student Badge Admin Panel**!  
        Here you can:
    - Mint new badges for students
    - View badges assigned to students
    - Monitor badge counts
    Use the sidebar to access admin functions.
    """)

    st.subheader("Minted Badges Count")
    mintedCount = []
    for bType in badgeTypes:
        url = f"{API_URL}/getMintedCount/{bType}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            mintedCount.append({
            "Badge Type": bType,
            "Minted Counts": data["minted_count"]
            })
            #print(mintedCount)

    if len(mintedCount) > 0:
        df = pd.DataFrame(mintedCount)
        #df.columns = ['Badge Type', 'Minted Count']
        #st.table(df)
        st.bar_chart(df.set_index('Badge Type'))
    else:
        st.write("No Badges Created yet")        

if page == "🪙 Mint Badge NFT":
    #Let us now Mint a New Badge
    st.header("Mint a New Badge")
    badge_type = st.selectbox("Select Badge Type", badgeTypes)
    student = st.selectbox("Select a Student", list(studentWallets.keys()))
    student_address = studentWallets[student]

    # Student Name, Class, University, Badge Type to be created
    studentClass = st.text_input("Class/Semester", placeholder="Enter Class/Semester")
    studentUniversity = st.text_input("University", placeholder="Enter University Name")

    submitButton = st.button("Mint Badge NFT")
    if submitButton:
        # Call the API to mint the badge
        payload = {
            "student_name": student,
            "class_semester": studentClass,
            "university": studentUniversity,
            "badge_type": badge_type
        }

        response = requests.post(f"{API_URL}/uploadMetadata", json=payload)
        if response.status_code == 200:
            metaDataURI = response.json().get("metadata_uri")
            st.success(f"Metadata uploaded successfully! IPFS URI: {metaDataURI}")
            #Now Mint the Badge on the Blockchain - Call /mintBadge
            badgeData = {
                    "recipient": student_address,
                    "badge_type": badge_type,
                    "token_uri": metaDataURI
                }
            mintStatus = requests.post(f"{API_URL}/mintBadge", json=badgeData)
            if mintStatus.status_code == 200:
                mintHash = mintStatus.json().get("tx_hash")
                st.success(f"The New Badge is Minted successfully! Transaction Hash: {mintHash}")
            else:
                st.error(f"Error Minting the Badge - mintBadge API returned Error: {mintStatus.text}")                

        else:
            st.error("Error Minting the Badge - Upload Meta Data Filed. Please check the details.")


if page == "🎖️ View Granted Badges":
    st.header("View Granted Badges")
    # Let us Get the Count of Badges Minted on this Platform
    url = f"{API_URL}/list_minted_badges"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data == 0:
            st.write("No Badges Granted yet")
        else:    
            #formattedData = format_data_for_display(data)
            cols_order = ["Student Name", "Badge Grant Date", "Badge Type", "Class or Semester", "University", "Certificate URL"]
            df = pd.DataFrame(data)
            df = df[cols_order]
            st.table(df)
            #st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(f"No Badges Granted yet - {response.content}")
    


