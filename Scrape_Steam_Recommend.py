import urllib2
import re
from bs4 import BeautifulSoup
import time
import pandas
# Function that scrapes steam and returns
# 1) Game name list (game_list)
# 2) Game hours list (game_hours_list)
# 3) Friends url (friends_url)
def scrape_website(overall_dict,stack):
    games_url_base = "/games/?tab=all"
    friends_url_base = "/friends/"
    games_page = stack[-1]+games_url_base
    page = urllib2.urlopen(games_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('script',attrs={'language': 'javascript'})
    if name_box is None:
        stack.pop()
        return(overall_dict,stack,None,None)
    name = name_box.text
    p = re.compile('"name":"(.*?)"')
    game_list = p.findall(name)
    p = re.compile('"hours_forever":"(.*?)"')
    game_hours_list = p.findall(name)
    for i in range(0,len(game_hours_list)):
        game_hours_list[i] = float(str(game_hours_list[i]).replace(",",""))
    friends_page = stack[-1]+friends_url_base
    page = urllib2.urlopen(friends_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find("div" ,id="BG_bottom")
    if name_box is None:
        stack.pop()
        return(overall_dict,stack,None,None)
    name = name_box.find_all('a')
    p = re.compile('href="(.*?)"')
    friends_url = p.findall(str(name))
    stack.pop()
    # Start filling the hash table / stack
    for i in friends_url:
        if i not in overall_dict:
            stack.append(i)
        overall_dict[i] = 1
    return(overall_dict,stack,game_list,game_hours_list)

#INIT
game_list = []
game_hours_list = []
overall_dict = {}
overall_dict["http://steamcommunity.com/profiles/76561198044207310/games/?tab=all"] = 1
stack = ["http://steamcommunity.com/profiles/76561198044207310/games/?tab=all"]
count = -1
cleaned_initial_list = []
ratio_of_hours = []
pairs_dict = {}
# Create  hash table with all urls
# Call function for each url in stack
# Add to stack for each friends url if
# friend not in hash table
# repeat until stack is empty or 10,000
# users have been queried
while(len(stack)!= 0 and count != 0):
    overall_dict, stack, game_list,game_hours_list = scrape_website(overall_dict,stack)
    # To not DDOS steam
    print("Count:" + str(count))
    if(game_list is not None and game_hours_list is not None):
        for i in range(0,min([len(game_list),len(game_hours_list)])):
            # Organize the data: should be fields [player,game,hoursplayed]
            cleaned_initial_list.append([count,game_list[i],game_hours_list[i]])
            # Create a ratio of total hours played for a game
            # over sum of total hours played by all games by a
            # user.
            ratio_of_hours.append([count,game_list[i],(game_hours_list[i]/sum(game_hours_list))])
        # Create 10C2 of top 10 games played and pair them
        # with another game (for 45? combinations). Make a
        # count of the highest paired games
        temp_list = []
        for i in range(0,10):
            for j in range(0,10):
                if (i < j and i < len(game_list) and j < len(game_list)):
                    temp_list = [game_list[i],game_list[j]]
                    temp_list.sort()
                    if (temp_list[0]+","+temp_list[1]) not in pairs_dict:
                        pairs_dict[(temp_list[0]+","+temp_list[1])]=1
                    else:
                        pairs_dict[(temp_list[0]+","+temp_list[1])]+=1
        count += 1

# Changed to pandas dataframe
# init
pandas_dict_init = {}
pandas_dict_init["user"] = []
pandas_dict_init["game_name"] = []
pandas_dict_init["game_hours"] = []
for i in cleaned_initial_list:
    pandas_dict_init["user"].append(i[0])
    pandas_dict_init["game_name"].append(i[1])
    pandas_dict_init["game_hours"].append(i[2])
df_init = pandas.DataFrame(data=pandas_dict_init)
# Ratio of hours
pandas_dict_ratio = {}
pandas_dict_ratio["user"] = []
pandas_dict_ratio["game_name"] = []
pandas_dict_ratio["ratio_played"] = []
for i in ratio_of_hours:
    pandas_dict_ratio["user"].append(i[0])
    pandas_dict_ratio["game_name"].append(i[1])
    pandas_dict_ratio["ratio_played"].append(i[2])
df_ratio = pandas.DataFrame(data=pandas_dict_ratio)
# 10c2
pandas_choose_two = {}
pandas_choose_two["games"] = []
pandas_choose_two["count"] = []
for i in pairs_dict.keys():
    pandas_choose_two["games"].append(i)
    pandas_choose_two["count"].append(pairs_dict[i])
df_c2 = pandas.DataFrame(data=pandas_choose_two)
#df_init.to_csv("Initial_CSV2.csv")
df_ratio.to_csv("Addendum.csv")
#df_c2.to_csv("C2_CSV2.csv")
