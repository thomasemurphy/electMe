import pandas as pd
from random import randint

state_df = pd.read_csv("/Users/macintosh/Documents/Board game stuff/nomination_state_table.csv")

player_list = []
ids = []
phasing_player = 0
voting_states = pd.DataFrame({})

def list_to_str (list):
    joinstr = ", "
    return joinstr.join([str(elem) for elem in list])

def polling (x):                        #User's Econ / Soc score relative to state's, converted to pop points
    if x == 0:
        return 3
    elif abs(x) == 1:
        return 1
    else:
        return 0

def election (state_id):
    winners = []
    losers = []
    winning_score = max(voting_states.iloc[state_id,6:6+len(player_list)])  #get highest score in a given state
    for i in range(6,6+len(player_list)):                                   # look at all columns with scores
        if voting_states.iloc[state_id, i] == winning_score:                # write all players with winning_score to winners
            winners.append(i-6)
    if len(winners) == 1:                                                   #if no tie
        player_df.iloc[winners[0], 3] += 1                                  # +1 fundraising
        player_df.iloc[winners[0], 5] += voting_states.iloc[state_id,4]     # + number of delegates
        print("Player %s won %s, gained +$1M fundraising and %s delegates" % \
              (list_to_str(winners), voting_states.iloc[state_id, 0],voting_states.iloc[state_id, 4]))
    else:
        for n in range(0,len(winners)):
            player_df.iloc[winners[n], 5] += (voting_states.iloc[state_id, 4]) / len(winners)       #if tied just split delegates among winners, no fundraising bump
        print("Players %s tied in %s, each added %s delegates" % \
              (list_to_str(winners), voting_states.iloc[state_id, 0], (voting_states.iloc[state_id, 4] / len(winners))))
    losing_score = min(voting_states.iloc[state_id, 6:6 + len(player_list)])
    if losing_score != winning_score:                                       #if all players get same score, no loser penalty
        for i in range(6, 6 + len(player_list)):                            # look at all columns with scores
            if voting_states.iloc[state_id, i] == losing_score:             # write all players with losing score to losers
                losers.append(i - 6)
        for n in range(0, len(losers)):
            player_df.iloc[losers[n], 3] -= 1                               # -1 fundraising irrespective of ties
        print("Player %s lost %s, lost -$1M fundraising." % (list_to_str(losers), voting_states.iloc[state_id, 0]))



Identity = {
    '[-1, -1]' : "Socialist",
    '[-1, 0]' : "Progressive",
    '[-1, 1]' : "Blue-Collar",
    '[0, -1]' : "Equality",
    '[0, 0]' : "Mainstream",
    '[0, 1]' : "Blue Dog",
    '[1, -1]' : "Neoliberal",
    '[1, 0]' : "Business",
    '[1, 1]' : "Corporate"
    }


print("Welcome to The Nomination!")
num_players = int(input("Choose number of players (2-4):"))
while num_players not in [2,3,4]:
    num_players = int(input("Invalid entry. Choose number of players (2-4):"))

#Make sure players' Econ,Soc combos are unique:
for i in range(0,num_players):
    id = [randint(-1,1),randint(-1,1)]
    while id in ids:
        id = [randint(-1, 1), randint(-1, 1)]
    ids.append(id)

#Create row entries for each player:
for i in range(0,num_players):
    player = ["CPU_" + str(i),ids[i][0],ids[i][1],3,5,0]    # [Name, Econ from IDs, Soc from IDs, 3 starting fundraising, 5 starting cash, 0 delegates]
    player_list.append(player)

player_name = input("Please enter your name:")
player_list[0][0] = player_name

#Create player_df from row entries:
player_df = pd.DataFrame(player_list, columns = ["Name","Econ","Soc","Fundraising","Cash","Delegates"])

#Add scoring columns for each player to state_df:
for i in range(0,num_players):
    column_header = player_df.iloc[i][0]
    state_df[column_header] = 0         #added a row

print("You are the %s candidate." % Identity[str(ids[phasing_player])])
print("Econ Score %s, State Score %s" % (str(ids[phasing_player][0]), str(ids[phasing_player][1])))
#

#BEGINNING OF THE TURN
for current_week in range(1,24):                            #24 election weeks in the game
    print("Beginning Week " + str(current_week))
    player_df["Cash"] += player_df["Fundraising"]           #add fundraising to cash on hand
    print("%s raised $%s million this week, cash on hand now $%s million" \
          % (str(player_df.iloc[phasing_player,0]), str(player_df.iloc[phasing_player,3]), str(player_df.iloc[phasing_player,4])))



    # POLLING

    if(len(state_df[state_df.ELECTION_WEEK == current_week])) > 0:
        print("The following states will vote this week:")
        print(state_df[state_df.ELECTION_WEEK == current_week].STATE_NAME.to_string(index = False))

        for i in range(0,len(player_df.index)):
            player = player_df.iloc[i][0]
            delta_econ = state_df[state_df.ELECTION_WEEK == current_week].ECON_SCORE - player_df.iloc[i][1]   #makes list of each voting state's econ score - user's
            delta_soc = state_df[state_df.ELECTION_WEEK == current_week].SOC_SCORE - player_df.iloc[i][2]     #makes list of each voting state's soc score - user's
            new_player_pop = pd.Series(state_df[state_df.ELECTION_WEEK == current_week][player] + \           #population to add based on polling function of those deltas
                    delta_econ.apply(polling) + delta_soc.apply(polling), name = player)
            state_df.update(new_player_pop)
            for i in range(0,len(new_player_pop)):
                print("%s gained %s popularity in %s due to ideological alignment." % (player,new_player_pop.iloc[i], \
                                                                                       state_df.iloc[new_player_pop.index[i]][0]))

    # VISITS

    print("Choose three states to visit (may visit the same state more than once).")
    visitsthisturn = []
    for i in range(0,3):
        visit_state = input("Visit %s: " % str(i+1))
        while visit_state not in state_df.STATE_NAME.values:
            visit_state = input("State not found. Visit %s: " % str(i+1))
        visit_index = int(state_df[state_df.STATE_NAME == visit_state].index.values)       #get index number of visited state
        state_df.iloc[visit_index,6+phasing_player] += 1                                    #add 1 to phasing player's pop in visited state
        visitsthisturn.append(visit_state)


#ADS (only after Week 5)
    if current_week >= 5:
        statesthisturn = [] # will contain adstate for all ads
        statesthisturn_pos = [] # will contain adstate for all positive ads
        statesthisturn_neg = [] # will contain pairs of adtarget,adstate for all negative ads


    #POSITIVE ADS:
        ad_state = ""
        while ad_state != "Done":
            print("Choose states in which to buy positive ads, or type \"Done\" to finish positive ad buys.")
            ad_state = input("State name: ")
            while ad_state not in state_df.STATE_NAME.values and ad_state.lower() != "done":
                ad_state = input("State not found. Ad state: ")
            if ad_state.lower() == "done":
                break
            while ad_state in statesthisturn:
                ad_state = input("Invalid: already purchased ad there this turn. Ad state: ")
            ad_index = int(state_df[state_df.STATE_NAME == ad_state].index.values)
            ad_cost = state_df.iloc[ad_index,5]
            if ad_cost > player_df.iloc[phasing_player,4]:
                print("Insufficient funds. (Ads in %s cost %s, you have %s.)" % \
                      (ad_state, str(ad_cost),str(player_df.iloc[phasing_player,5])))
                continue
            state_df.iloc[ad_index,6+phasing_player] += 1  #adding popularity
            player_df.iloc[phasing_player,4] -= ad_cost  #reducing player's cash
            statesthisturn.append(ad_state)
            statesthisturn_pos.append(ad_state)
            """print("%s's popularity in %s now %s, %s's cash on hand now $%sM." %
                  (player_df.iloc[phasing_player,0],ad_state,state_df.iloc[ad_index,6+phasing_player],
                  player_df.iloc[phasing_player,0],player_df.iloc[phasing_player,4]))
            """

    #NEGATIVE ADS
        while ad_state != "Done":
            print("Choose states in which to buy negative ads, or type \"Done\" to finish positive ad buys.")
            ad_state = input("State name: ")
            while ad_state not in state_df.STATE_NAME.values and ad_state.lower() != "done":
                ad_state = input("State not found. Ad state: ")
            if ad_state.lower() == "done":
                break
            while ad_state in statesthisturn:
                ad_state = input("Invalid: already purchased ad there this turn. Ad state: ")
            ad_index = int(state_df[state_df.STATE_NAME == ad_state].index.values)
            ad_cost = state_df.iloc[ad_index, 5]
            if ad_cost > player_df.iloc[phasing_player, 4]:
                print("Insufficient funds. (Ads in %s cost %s, you have %s.)" % \
                      (ad_state, str(ad_cost), str(player_df.iloc[phasing_player, 5])))
                continue

            print("Select target for your negative ad")
            for i in range(1,len(player_list)):
                print("%s : %s" % (i, player_df.iloc[i,0]))
            target = int(input("Target: "))
            while target not in range(1,len(player_list)):
                target = input("Invalid selection. Target:")

            if state_df.iloc[ad_index,6+target] > 2:
                state_df.iloc[ad_index,6+target] -= 2
            else:
                state_df.iloc[ad_index,6+target] == 0
            player_df.iloc[phasing_player, 4] -= ad_cost  # reducing player's cash
            statesthisturn.append(ad_state)
            statesthisturn_neg.append(ad_state)

    #TURN REPORT
    print("Weekly Report:")
    print("You visited %s, adding one popularity per state." % list_to_str(visitsthisturn))
    if(len(statesthisturn_pos)) > 0:
        print("You bought positive ads in %s, adding one popularity per state." % list_to_str(statesthisturn_pos))
    if(len(statesthisturn_neg)) > 0:
        print("You bought negative ads in %s, reducing opponents' popularity by 2 per state." % list_to_str(statesthisturn_neg))


    #ELECTIONS
    voting_states = state_df[state_df.ELECTION_WEEK == current_week]
    voting_states.reset_index()
    if(len(voting_states) > 0):
        for i in range(0,len(voting_states)):
            election(i)

    #CHECK IF ALL PLAYERS ARE STILL IN

    for i in range(0,len(player_list)):
        if player_df.iloc[i,4 < 0]:
            print("Player %s has run out of steam. Their fundraising has dried up. They are eliminated.")
            if i = 0:
                game_over = 1
            else:
                player_df.drop(player_df.index[i])
    if game_over = 1:
        break


