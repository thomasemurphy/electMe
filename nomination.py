from random import seed
from random import randint
import csv
with open('nomination_state_table.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    state_table = {row["STATE_NAME"]:dict(row) for row in reader}

for intelement in ["ELECTION_WEEK", "ECON_SCORE", "SOC_SCORE", "DELEGATES", "COST_OF_ADS", "PLAYER_0_POPULARITY", "PLAYER_1_POPULARITY"]:
    for row in state_table:
        state_table[row][intelement] = int(state_table[row][intelement])

def get_identity(player):
    alignment = str(player["EconSoc"])
    return Identity[alignment]
    
def election(s):
    results = []
    for i in range(0,len(players)):
        header = "PLAYER_" + str(i) + "_POPULARITY"
        results.append(state_table[s][header])
    winningscore = max(results)
    winners = []
    for val in results:
        if val == winningscore:
            winners.append(results.index(val))
    if len(winners) == 1:
        winningplayer = players[winners[0]]
        winningplayer["Delegates_Won"] += state_table[s]["DELEGATES"]
        winningplayer["Fundraising"] += 1
        print("%s won %s, earning %s delegates and $1M fundraising." % (winningplayer["Name"], state_table[s]["STATE_NAME"],state_table[s]["DELEGATES"]))
    else:
        for player in winners:
            players[player]["Delegates_Won"] += state_table[s]["DELEGATES"] / len(winners)
        print("The following players tied for the win in %s" % (state_table[s]["STATE_NAME"]))
        for player in winners:
              print(players[player]["Name"])
        print("Each gained %s delegates; none gained fundraising." % (state_table[s]["DELEGATES"] / len(winners)))

    losingscore = min(results)
    if losingscore != winningscore:
        losers = []
        for val in results:
            if val == losingscore:
                losers.append(results.index(val))
        for player in losers:
                players[player]["Fundraising"] += -1
        print("The following player(s) lost in %s:" % (state_table[s]["STATE_NAME"]))
        for player in losers:
            print(players[player]["Name"])
        print("Player(s) lost $1M fundraising.")



user = {"Name" : "Will",
    "Number" : 0,
    "EconSoc" : [randint(-1,1), randint(-1,1)],
    "Fundraising" : 3,
    "Cash_on_Hand" : 5,
    "Delegates_Won" : 0
}

CPU = {"Name" : "Mr. Roboto",
    "Number" : 1,
    "EconSoc" : [randint(-1,1), randint(-1,1)],
    "Fundraising" : 3,
    "Cash_on_Hand" : 5,
    "Delegates_Won" : 0
}

players = [user, CPU]

while user["EconSoc"] == CPU["EconSoc"]:
    CPU["EconSoc"] = [randint(-1,1), randint(-1,1)]

"""for i in range(0,100):
    if user["EconSoc"] == CPU["EconSoc"]:
        CPU["EconSoc"] = [randint(-1,1), randint(-1,1)]
    if user["EconSoc"] != CPU["EconSoc"]:
        break
"""    



Identity = {
    "[-1, -1]" : "Socialist",
    "[-1, 0]" : "Progressive",
    "[-1, 1]" : "Blue-Collar",
    "[0, -1]" : "Equality",
    "[0, 0]" : "Mainstream",
    "[0, 1]" : "Blue Dog",
    "[1, -1]" : "Neoliberal",
    "[1, 0]" : "Business",
    "[1, 1]" : "Corporate"
    }


print("You are the " + get_identity(user) + " Candidate")
print("Economic Score: " + str(user["EconSoc"][0]))
print("Social Score: " + str(user["EconSoc"][1]))
print()
print("Your opponent is the " + get_identity(CPU) + " Candidate")
print("Economic Score: " + str(CPU["EconSoc"][0]))
print("Social Score: " + str(CPU["EconSoc"][1]))
print()

#BEGINNING OF THE TURN
for w in range(1,27):
    currentweek = w
    print("Beginning Week " + str(currentweek))
    for player in players:
        player["Cash_on_Hand"] = player["Cash_on_Hand"] + player["Fundraising"]
        print("%s raised $%s million this week, cash on hand now $%s million" \
              % (str(player["Name"]),str(player["Fundraising"]),str(player["Cash_on_Hand"])))


    #POLLING

    for state in state_table:
        if state_table[state]["ELECTION_WEEK"] == currentweek:
            print("%s will vote this week." % (state_table[state]["STATE_NAME"]))
            state_econ = state_table[state]["ECON_SCORE"]
            state_soc = state_table[state]["SOC_SCORE"]
            for player in players:
                player_econ = player["EconSoc"][0]
                player_soc = player["EconSoc"][1]
                player_pop_chg = 0
                if player_econ - state_econ == 0:
                    player_pop_chg += 3
                elif abs(player_econ - state_econ) == 1:
                    player_pop_chg += 1
                if player_soc - state_soc == 0:
                    player_pop_chg += 3
                elif abs(player_soc - state_soc) == 1:
                    player_pop_chg += 1
                pop_header = "PLAYER_" + str(player["Number"]) + "_POPULARITY"
                state_table[state][pop_header] = state_table[state][pop_header] + player_pop_chg
                
                print("Polling shows %s gains %s popularity due to ideological alignment." \
                      % (str(player["Name"]),str(player_pop_chg)))
                #print("%s total popularity now %s" % (str(player["Name"]),str(state[pop_header])))


    #VISITS

    print("Choose three states to visit this week. You may visit the same state more than once.")
    visit1 = input("State 1:")
    visit2 = input("State 2:")
    visit3 = input("State 3:")
    visits = [visit1, visit2, visit3]
    for visit in visits:
        for state in state_table:
            if state_table[state]["STATE_NAME"] == visit:
                state_table[state]["PLAYER_0_POPULARITY"] += 1
                print(state_table[state]["STATE_NAME"])
    #print("You added 1 popularity in %s for a total of %s" % (visit1,state_table[visit1]["PLAYER_0_POPULARITY"]))


    #POSITIVE ADS

    if currentweek >= 5:
        statesthisturn = [] # will contain adstate for all ads
        statesthisturn_pos = [] # will contain adstate for all positive ads
        statesthisturn_neg = [] # will contain pairs of adtarget,adstate for all negative ads
        for i in range(0,100):
            print("Choose states in which to buy positive ads, or type \"Done\" to finish positive ad buys.")
            adcost = 0
            adstate = input("State name:")
            if adstate.lower() == "done":
                break
            if adstate in statesthisturn:
                print("Already purchased an ad in that state this turn.")
                continue
            for state in state_table:
                if adstate == state_table[state]["STATE_NAME"]:
                    adcost = state_table[state]["COST_OF_ADS"]
                    statenum = state
                    player0 = state_table[state]["PLAYER_0_POPULARITY"]
                    player1 = state_table[state]["PLAYER_1_POPULARITY"]
            if adcost == 0:
                print("State not found.")
            elif adcost > user["Cash_on_Hand"]:
                print("Can't afford it! (Ad cost $%s million, your cash on hand $%s million.)" % (adcost,user["Cash_on_Hand"]))
            else:
                print("Cost of an ad in %s is %s. Your current cash on hand is %s. Are you sure you wish to proceed?" % (adstate, adcost, user["Cash_on_Hand"]))
                choice = input("Enter X to cancel, or just hit Enter to proceed:")
                if choice == "X":
                      continue

                user["Cash_on_Hand"] = user["Cash_on_Hand"] - adcost
                state_table[statenum]["PLAYER_0_POPULARITY"] += 1
                statesthisturn.append(adstate)
                statesthisturn_pos.append(adstate)

    #NEGATIVE ADS

        for i in range(0,100):
            print("Choose states in which to buy negative ads, or type \"Done\" to finish negative ad buys.")
            adcost = 0
            adstate = input("State name:")
            if adstate.lower() == "done":
                break
            if adstate in statesthisturn:
                print("Already purchased an ad in that state this turn.")
                continue
            for state in state_table:
                if adstate == state_table[state]["STATE_NAME"]:
                    adcost = state_table[state]["COST_OF_ADS"]
                    statenum = state
                    player0 = state_table[state]["PLAYER_0_POPULARITY"]
                    player1 = state_table[state]["PLAYER_1_POPULARITY"]
            if adcost == 0:
                print("State not found.")
            elif adcost > user["Cash_on_Hand"]:
                print("Can't afford it! (Ad cost $%s million, your cash on hand $%s million.)" % (adcost,user["Cash_on_Hand"]))
            else:
                print("Cost of an ad in %s is %s. Your current cash on hand is %s. Are you sure you wish to proceed?" % (adstate, adcost, user["Cash_on_Hand"]))
                choice = input("Enter X to cancel, or just hit Enter to proceed:")
                if choice == "X":
                      continue

                for i in range(1,len(players)):
                    print("Type %s to target your negative ad at %s." % (i,players[i]["Name"]))
                adtargetnumber = int(input("Target:"))
                adtarget = players[adtargetnumber]
                adtargetheader = "PLAYER_" + str(adtargetnumber) + "_POPULARITY"
                state_table[statenum][adtargetheader] = max(state_table[statenum][adtargetheader] - 2, 0)
                statesthisturn.append(adstate)
                statesthisturn_neg.append([adtarget,adstate])

    print(state_table)

    #ELECTIONS

    for state in state_table:
        if state_table[state]["ELECTION_WEEK"] == currentweek:
            election(state)

