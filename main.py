from Visualiser import Visualiser
import seaborn as sns
import streamlit as st

def start(user,repo,key):
    try:
        st.subheader("Loading...")
        print("Attempting Authentication to Github API")
        v = Visualiser(user, repo,key)
        print("Github API Authentication Successful.")
    except:
        st.subheader("Error Connecting to GitHub API.")
    else:
        v.visualize_language()
        commits_over_time = v.visualize_authors()
        commits_over_time.figure.savefig("commits.png",bbox_inches='tight')
        subheader = user + '/' + repo
        st.subheader(subheader)
        st.image("codechart.png")
        st.image("commits.png")

def main():
    sns.set_theme()
    st.header("Github Statistics Visualiser")
    user = st.text_input("Github user")
    repo = st.text_input("Repository")
    key = st.text_input("Personal Github Token")
    button = st.button("Enter")
    if button:
        start(user,repo,key)

if __name__ == "__main__":
    main()