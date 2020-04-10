from math import floor
from random import randint
import csv


##I THINK THIS SHOULD BE ITS OWN DOCUMENT, BUT I DON'T KNOW HOW TO 'CALL' IT IN ANOTHER SCRIPT
##like I think it should be "classes.py" and then this should say import classes.py but i couldn't get that to work
##anyway

class Player:
    def __init__(self, id, name, econ, soc, fundraising, cash_on_hand, delegates):
        self.id = id
        self.name = name
        self.econ = econ
        self.soc = soc
        self.fundraising = fundraising
        self.cash_on_hand = cash_on_hand
        self.delegates = delegates

    def __repr__(self):
        return self.name

    def visit(self, state):
        state.player_pop[self.id] += 1
        print("Added 1 popularity in {}, total now {}".format(state.name, state.player_pop[self.id]))

    def positive_ad(self, state):
        if self.cash_on_hand >= state.cost_of_ads:
            self.cash_on_hand -= state.cost_of_ads
            state.player_pop[self.id] += 1
            print("Added 1 popularity in {}, total now {}".format(state.name, state.player_pop[self.id]))
            print("Ad cost {}, cash remaining {}.".format(state.cost_of_ads,self.cash_on_hand))
        else:
            print("Insufficient funds to purchase ads in " + state.name)

    def negative_ad(self, state, target):
        if self.cash_on_hand >= state.cost_of_ads:
            self.cash_on_hand -= state.cost_of_ads
            state.player_pop[target.id] -= 2
            print("Removed 2 popularity from {} in {}, their total now {}".format(target.name, state.name, state.player_pop[target.id]))
            print("Ad cost {}, cash remaining {}.".format(state.cost_of_ads,self.cash_on_hand))
        else:
            print("Insufficient funds to purchase ads in " + state.name)



class State:
    def __init__(self, name, election_week, econ, soc, delegates, cost_of_ads):
        self.name = name
        self.election_week = election_week
        self.econ = econ
        self.soc = soc
        self.delegates = delegates
        self.cost_of_ads = cost_of_ads

        self.player_pop = []
        for i in range(0,num_players):
            self.player_pop.append(0)

    def election(self):
        winners = [p for p in player_list if self.player_pop[p.id] == max(self.player_pop)]
        losers = [p for p in player_list if self.player_pop[p.id] == min(self.player_pop)] if (
            max(self.player_pop) != min(self.player_pop)) else []

        if len(winners) == 1:
            winners[0].delegates += self.delegates
            winners[0].fundraising += 1
            print("{} won {}, gaining {} delegates and $1M fundraising.".format(
                winners[0].name,self.name,self.delegates
            ))
        else:
            for i in range(0,len(winners)):
                winners[i].delegates += floor(self.delegates / len(winners))
            print("{} tied in {}, gaining {} delegates each.".format(
                winners,self.name,floor((self.delegates / len(winners)))
            ))

        for i in range(0,len(losers)):
            losers[i].fundraising -= 1
        print("{} lost in {}, losing $1M fundraising.".format(
            losers,self.name)) if len(losers) > 0


    def polling(self):
        for player in player_list:
            delta_econ = player.econ - self.econ
            delta_soc = player.soc - self.soc
            delta_pop = 0
            if delta_econ == 0:
                delta_pop += 3
            elif abs(delta_econ) == 1:
                delta_pop += 1
            if delta_soc == 0:
                delta_pop += 3
            elif abs(delta_soc) == 1:
                delta_pop += 1
            self.player_pop[player.id] += delta_pop


###SAME WITH THIS MAYBE?

def visit_phase():
    i = 0
    while i < 3:
        visit_state = []
        visit_input = input("Visit %s: " % str(i + 1))
        visit_state = [state for state in state_list if state.name == visit_input]
        if visit_state != []:
            player_list[0].visit(visit_state[0])
            visits_this_turn.append(visit_state)
            i += 1
        else:
            print("Invalid selection.")


def ad_phase(pos_or_neg):
    ad_input = ""
    while ad_input.lower() != "done":
        ad_state = []
        print("Choose states in which to buy positive ads, or type \"Done\" to finish positive ad buys.") if pos_or_neg == "positive" else print(
            "Choose states in which to buy negative ads, or type \"Done\" to finish negative ad buys.")
        ad_input = input("State name: ")
        if ad_input.lower() == "done": break
        ad_state = [state for state in state_list if state.name == ad_input]
        if ad_state == []:
            print("Invalid selection.")
            continue
        elif ad_state[0] in ads_this_turn:
            print("Invalid selection, already bought an ad there this turn.")
            continue
        else:
            if pos_or_neg == "positive":
                player_list[0].positive_ad(ad_state[0])
                ads_this_turn.extend(ad_state)
            else:
                print("Choose the target for your negative ad.")
                for i in range(1, len(player_list)):
                    print("%s : %s" % (i, player_list[i].name))
                target_id = int(input("Target: "))
                while target_id not in range(1, len(player_list)):
                    target_id = input("Invalid selection. Target:")

                player_list[0].negative_ad(ad_state[0],player_list[target_id])
                ads_this_turn.extend(ad_state)

def end_of_turn():
    game_over = 0
    for i in range(0,len(player_list)):
        if player_list[i].fundraising < 0:
            print("{}\'s fundraising has dropped below zero. They are eliminated.".format(player_list[i].name))
            if i == 0:
                print("Game over.")
                return True
        else:
            print("{} ends the round with ${}M on hand and {} delegates.".format(
                player_list[i].name, player_list[i].cash_on_hand, player_list[i].delegates
        ))
    return False



#OK LET'S START THE GAME:

print("Welcome to The Nomination!")
print()
user_name = input("What\'s your name? ")
num_players = int(input("Choose number of players (2-4): "))
while num_players not in [2,3,4]:
    num_players = int(input("Invalid entry. Choose number of players (2-4):"))



#Create states from CSV

state_list = []

with open('nomination_state_table.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        state_list.append(State(row[0],int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])))



#Create unique Econ-Soc pairs for all players:
ids = []
for i in range(0,num_players):
    id = [randint(-1,1),randint(-1,1)]
    while id in ids:
        id = [randint(-1, 1), randint(-1, 1)]
    ids.append(id)



#Create players:
player_list = [Player(0,user_name,ids[0][0],ids[0][1],3,5,0)] + [
    Player(i,"CPU_" + str(i),ids[i][0], ids[i][1], 3, 5, 0) for i in range(1,num_players)]


#Turn:
for current_week in range(8,25):
    print("Beginning Week " + str(current_week))
    for player in player_list:
        player.cash_on_hand += player.fundraising
    print("You raised ${} million dollars, now have ${} million on hand.".format(
        player_list[0].fundraising, player_list[0].cash_on_hand))


    states_this_week = [state for state in state_list if state.election_week == current_week]


    #Polling:
    print("The following states will vote this week: {}".format(
        [state.name for state in states_this_week]))
    for state in states_this_week:
        state.polling()
        print("After polling based on ideological alignment, popularity in {} now {}.".format(state.name,state.player_pop))

    #Visits:
    print("Choose three states to visit (may visit the same state more than once).")
    visits_this_turn = []
    visit_phase()

    #Ads
    if current_week >= 5:
        ads_this_turn = []
        ad_phase("positive")
        ad_phase("negative")

    #Elections
    for state in states_this_week:
        state.election()

    #End of Turn
    end_of_turn()
    if end_of_turn():
        break
