import threading
import time
from github import Github
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as pltc
from random import sample
import tkinter

class Visualiser:
    def __init__(self,user,repo,authKey):
        self.g = None
        try:
            self.g = Github(authKey)
            print("Authentication Success!")
        except:
            print("Authentication Failed. Limited Access")
            self.g = Github()
            quit()
        self.user = user
        self.repo_name = repo
        self.repo_location = self.user + '/' + self.repo_name
        self.repo = self.g.get_repo(self.repo_location)
        self.data_head = {'SHA':[], 'ETAG':[], 'Author':[], 'Username':[], 'Additions':[], 'Deletions':[], 'Total':[], 'Date':[]}
        self.df_additions = []
        self.df = pd.DataFrame(self.data_head)
        self.pie_data = []
        self.colors = [k for k,v in pltc.cnames.items()]
       
    
    def fetch_data(self):
       commits = self.repo.get_commits()
       threads = []
       for commit in commits:
           thread = threading.Thread(target = self.threaded_insert, args = (commit,), daemon=True)
           threads.append(thread)
       batch_size = 10
       batch = 0
       threads_remaining = len(threads)
       while threads_remaining > 0:
           start = (batch_size) * batch
           if threads_remaining < batch_size:
               end = (batch_size) * batch + threads_remaining
           else:
               end = (batch_size) * batch + batch_size
           for thread in threads[start:end]:
               thread.start()
           while not self.check_threads_complete(threads[start:end]):
               time.sleep(0.01)
           for thread in threads[start:end]:
               thread.join()
           for row in self.df_additions:
               self.df = self.df.append(row, ignore_index=True)
           self.df_additions = []
           batch += 1
           threads_remaining = threads_remaining - batch_size
           self.df.to_csv('commit_data.csv', index=False)
    def check_threads_complete(self, threads):
        for thread in threads:
            if thread.is_alive():
                return False
        return True

    def threaded_insert(self, commit):
        data = commit.raw_data
        try:
            name = data['commit']['author']['name']
            username = data['author']['login']
        except:
            name = ''
            username = ''
        row = {
            'SHA': data['sha'],
            'ETAG': None,
            'Author': name,
            'Username': username,
            'Additions': data['stats']['additions'],
            'Deletions': data['stats']['deletions'],
            'Total': data['stats']['total'],
            'Date': commit.stats.last_modified
        }
        self.df_additions.append(row)

        return 0

    def get_developers_data(self):
        dev_users = self.df['Username'].drop_duplicates()
        devs_dict = {}
        for i, user in enumerate(dev_users):
            user_stats = self.df.loc[self.df['Username'] == user]
            author_names = user_stats['Author']
            name = ''
            for n in author_names:
                name = n
            if user_stats.shape[0] != 0:
                devs_dict[i] = {'Username': user, 'Name': name, 'Commits': user_stats.shape[0], 'Changes': user_stats['Total'].sum()}
        return devs_dict

    def visualize_authors(self):
        self.fetch_data()
        devs = self.get_developers_data()
        data = pd.DataFrame.from_dict(devs, orient='index', columns=["Username", "Name", "Commits", "Changes"])
        users_commits = data.sort_values(by=['Commits'], ascending=False)
        plot = sns.barplot(data=users_commits[0:5], x='Name', y='Commits', palette='tab10')
        plot.set_title("Top 5 authors in terms of commits.")
        return plot   

    def visualize_language(self):
        self.lan = self.repo.get_languages()
        languages = []
        values = []
        for x in self.lan:
            languages.append(x)
            values.append(self.lan[x])
        colours = sample(self.colors,len(languages))
        plt.barh(languages,values,align='center',color=colours)
        plt.ylabel('Language')
        plt.xlabel('Lines of Code')
        plt.title('Languages present in Github Repository')
        plt.plot()
        xd = plt.savefig('codechart.png', bbox_inches='tight')
        plt.show()
        return xd