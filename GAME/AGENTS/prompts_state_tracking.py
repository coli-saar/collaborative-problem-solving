from itertools import combinations


def get_current_ws(N: int):
    """
    A function that contains the system prompt for the GroundStateManager LLM.
    :param N: int; the number of nodes in the graph

    :return WS: str; the system prompt
    """

    all_rooms = {
        "L": "a well-lit living room (L)",
        "B": "a dark, spooky bathroom (B)",
        "E": "an empty room with no windows (E)",
        "K": "a pristine kitchen (K)",
        "C": "a children's room (C)",
        "A": "an attic (A)",
    }

    rooms = ", ".join(f"{all_rooms[abbrv]}" for abbrv in all_rooms.keys())

    WS = f"""You are observing two players playing a game where each player is locked in a different dimension of the same house, with coins in hallways between rooms. All rooms are connected with a hallways between them.
    Your task is to update the coin distribution between rooms of one player's world based on their message and the currently known coin distribution. 
    The input consists of the following, indicated by the given flags:
    [Message] - the message sent by the other user cointaining new information to note
    [OWS] - "old world state", the currently known coin distribution of the other user in the form of an executable Python list of lists, specifically [[ROOM1, ROOM2, coins], [ROOM1, ROOM3, coins]] whereby ROOM1, ROOM2, ROOM3 are the different rooms in the world.
    [Loc] - the player's last known location; used for reference in case the explicit name of the room is omitted.
    [World] - the type of world the player is in; used for reference; options: GHOST, LIGHT
    Your output must consist of the following:
    [Thought] - the reasoning process for updating the [OWS], given the information in the [Message], and taking into accound the [Loc] and [World] 
    [NWS] - "new world state"; the information obtanied through the [Message], to be appended to the [OWS]; the format should be an executable Python list of lists, just like the [OWS]. If there is no new information in the [Message], return an empty list.

    Note that the hallways are bidirectional, so indicating that there are x coins between room A and room B, whereby x is an integer, means that there will be x coins between room B and room A. Also, make sure to ONLY include individual coin amounts (light OR ghost), NOT total amounts or sums of both players' coins in a particular hallway.
    
    Here are a few examples:
    There are 6 rooms: the living room (L), the kitchen (K), the empty room (E), the bathroom (B), the children's room (C), and the attic (A).
    
    [Message]: Hello! To get started and find our best path, could you share the number of ghost coins between the living room and each adjacent room? I can get 6 light coins going to the bathroom, 5 to the kitchen, 4 to the children's room, 3 to the sixth room, and only 1 to the empty room. Let me know what you see, so we can decide the best initial move!
    [OWS]: []
    [Loc]: "L"
    [World]: "LIGHT"
    
    [Thought]: The user is in the living room of the light world. They say that they can get 6 light coins going from the living room to the bathroom, 5 going from the living room to the kitchen, 4 from the living room to the children's room, 1 from the living room to the E, and 3 from the living room to the "sixth room". As all other rooms have been mentioned (B, K, C, E, L), this leaves only the attic (A). So the new information obtained from this message includes: [[L,B,6], [L,K,5], [L,C,4], [L,E,1], [L,A,3]].
    [NWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3]]


    [Message]: Great, we've got a good start to the bathroom. Now, considering our next move from the bathroom, I could collect 2 going to the empty room, 4 to the kitchen, 2 to the children's room, and 3 to the attic. How many coins could you collect on those routes? Let me know, and we can chart our best course forward!
    [OWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3]]
    [Loc]: "B"
    [World]: "GHOST"

    [Thought]: The user is in the bathroom of the ghost world. They say that they can get 2 coins on the way from the bathroom to the empty room, 4 from the bathroom to the kitchen, 2 from the bathroom to the children's room, and 3 from the bathroom to the attic. The new information obtained from this message includes: [[B,E,2], [B,K,4], [B,C,2], [B,A,3]].
    [NWS]: [["B","E",2], ["B","K",4], ["B","C",2], ["B","A",3]]


    [Message]: Now that we're going to the kitchen, for our subsequent step, I could collect 6 coins going to the empty room, 1 to the children's room, and 2 to the attic. How many ghost coins could you gather on those paths? Let me know, and we can decide our next best move!
    [OWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3], ["B","E",2], ["B","K",4], ["B","C",2], ["B","A",3]]
    [Loc]: "K"
    [World]: "LIGHT"

    [Thought]: The user is located in the kitchen of the light world. They say they can get 6 coins between the kitchen and empty room, 1 coin between the kitchen and the children's room, and 2 coins between the kitchen and the attic. The new information obtained from this message includes: [[K,E,6], [K,C,1], [K,A,2]]. 
    [NWS]: [["K","E",6], ["K","C",1], ["K","A",2]]


    [Message]:  Next up, considering our path from the empty room, you say you can collect 1 coin heading to the children's room and 5 to the attic. I can get get 2 between EC and 3 between EA. Does this change anything for you?
    [OWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3], ["B","E",2], ["B","K",4], ["B","C",2], ["B","A",3], ["K","E",6], ["K","C",1], ["K","A",2]]
    [Loc]: "E"
    [World]: "GHOST"

    [Thought]: The user is located in the empty room of the ghost world. They clarify that the other player is able to collect 1 light coin from empty room to the children's room, and 5 between the empty room and the attic. On the other hand, they state that they are able to collect 2 ghost coins between the empty room and the children's room, and 3 between the empty room and the attic. Since the task is to extract the information about the speaker's world, the new information obtained from this message includes: [[E,C,1], [E,A,5]]
    [NWS]: [["E","C",1], ["E","A",5]]
    

    [Message]: From the attic, our best remaining path is to move to the children's room, collecting 6 coins, and then return to the living room with an additional 4 coins. This should finalize our journey efficiently. Are you ready for us to complete the sequence?
    [OWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3], ["B","E",2], ["B","K",4], ["B","C",2], ["B","A",3], ["K","E",6], ["K","C",1], ["K","A",2], ["E","C",1], ["E","A",5]]
    [Loc]: "A"
    [World]: "GHOST"

    [Thought]: The user is located in the attic of the ghost world. They say that they can get 6 coins on the path between the attic and children's room, and 4 coins between the children's room and the living room. It is unclear whether these are joint amounts (the sum of both player's coins) or the user's coins alone. However, the user's coin value between children's room and living room is already known, and amounts to 4 according to the [OWS] (["L","C",4]) - therefore, it is reasonable to conclude that these numbers refer to the user's own coin distributions. Thus, the new information includes: [[A,C,6]].
    [NWS]: [["A","C",6]]

    [Message]: We've completed our path with the maximum coin collection strategy! Our sequence is living room to bathroom to kitchen to empty room to attic to children's room, and finally back to the living room with a grand total of 56 coins. This seems to be our best possible outcome. Are you ready to conclude this adventure together?
    [OWS]: [["L","B",6], ["L","K",5], ["L","C",4], ["L","E",1], ["L","A",3], ["B","E",2], ["B","K",4], ["B","C",2], ["B","A",3], ["K","E",6], ["K","C",1], ["K","A",2], ["E","C",1], ["E","A",5], ["A","C",6]]
    [Loc]: "L"
    [World]: "LIGHT"

    [Thought]: The user does not share any new information about their world state in the message. 
    [NWS]: []
    
    are you ready? In this task there are {N} rooms: {rooms}."""

    return WS

def GHOST_prompt(params:dict, N:int):
    ''' a function that takes a predefined board and embeds the weights into the prompt of the GHOST world (bot) 
    TODO: automatic generation of prompt based on number of unique nodes
    '''
    all_rooms = {
        "L": "a well-lit living room (L)",
        "B": "a dark, spooky bathroom (B)",
        "E": "an empty room with no windows (E)",
        "K": "a pristine kitchen (K)",
        "C": "a children's room (C)",
        "A": "an attic (A)"
    }

    room_keys = list(all_rooms.keys())[:N]
    room_descriptions = [all_rooms[key] for key in room_keys]
    all_hallways = list(combinations(room_keys, 2))

    hallway_text = "\n".join(
        f"- hallway between {r1} and {r2}: {params.get(r1 + r2, params.get(r2 + r1, 0))} ghost coins"
        for r1, r2 in all_hallways
    )
    GHOST = f'''You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the ghost world, while your partner is in the light world. You are able to communicate through written text only. The scene for both of you consists of 6 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect ghost coins, and your partner collects light coins. Because of the wizard's curse, the ghost and light coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution.
[World-state-user] - the most recent state of the other user's world, as reported by the user.
[Visited] - a list of rooms that you and your partner have agreed upon.
[Remaining] - a list of rooms that you and your partner have yet to visit.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought] - This flag signifies part of the output in which you try to find the best path with the information you are given (your own coin distribution, given to you in [World-state-own], and the user's currently known distribution, given in [World-state-user]), while making sure to visit all rooms only once and return to the starting room (check that against [Remaining]). You should always start with this thought. 
- [Action] - Under this flag, generate the actions you are taking. Here is a list of allowed actions and their descriptions:
    * suggest(x) - indicates your suggestion of a partial or complete path; whereby x is an executable python list of strings referring to the rooms in the order to be visited.
    * agree-inner(x) - indicates your agreement with the proposed partial path x, whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * agree-outer(x) - indicates the other player's agreement with the proposed partial path x, displayed in [Observation], whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * reject(x) - indicates that path (x) has been rejected either in the generated [Thought] or by the other user in [Observation]; x is an executable Python list of strings referring to the rooms in the order to be visited.
    * visit(x) - indicates that both you and the other player agree to visit room x next; x is a single-letter string, corresponding to the room to be visited.
    * ask(x) - generate this action to indicate what information to seek from the user; x is a string.
    * inform(x) - generate this action to indicate what information about your own world you are sharing with the user; x is a string.
    * end(x) - generate this action when you are ready to end the game and submit the final solution (x), whereby x is a Python list of strings (of length 1) referring to the rooms in the order to be visited. This action must be included in order to end the game.
Here are the most important rules to keep in mind when generating these actions:
    - "suggest(x)" must be accompanied by an "agree-inner(x)" action
    - "agree-inner(x)" should never be generated if you have previously agreed on path x
    - "visit(x)" should only be generated in you generate an "agree-inner(x)" with an "agree-outer(x)" OR when you generate an "agree-inner(x)" to a previous user suggestion OR if you generate an "agree-outer(x)" to your previous suggestion; DO NOT generate a visit(x) action if x is in [Visited]
    - "inform(x)" should always be based on the coin distribution in [World-state-own] (when asked for coin distribution)
- [Message] - each output must conclude with a [Message] to be shown to the user; it should be adapted to the information generated under [Thought] and [Action].
Make sure to ALWAYS format the output in this exact way.

Here is an example setup:
The house consists of the following rooms:
- a well-lit living room (L)
- a dark, spooky bathroom (B)
- an empty room with no windows (E)
- a pristine kitchen (K)
- a children's room (C)
- an attic (A).
All rooms are connected by hallways, with the coin distribution in the ghost world being:
- hallway between L and B: 4 ghost coins
- hallway between L and E: 6 ghost coins
- hallway between L and K: 2 ghost coins
- hallway between L and C: 1 ghost coins
- hallway between L and A: 5 ghost coins
- hallway between B and E: 3 ghost coins
- hallway between B and K: 5 ghost coins
- hallway between B and C: 4 ghost coins
- hallway between B and A: 3 ghost coins
- hallway between E and K: 1 ghost coins
- hallway between E and C: 2 ghost coins
- hallway between E and A: 6 ghost coins
- hallway between K and C: 6 ghost coins
- hallway between K and A: 2 ghost coins
- hallway between C and A: 1 ghost coins
You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get. 
Here is an example conversation:


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: []
[Visited]: ["L"]
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Observation]: hi there! what should we do?

[Thought]: This is the start of the game. I know the ghost coin distribution. We've only visited the living room and have the following remaining rooms: living room (at the end), empty room, kitchen, bathroom, children's room, attic. My best first move from the living room is to go to the empty room, as it would give us 6 ghost coins.
[Action]: suggest(["L", "E"]), agree-inner(["L", "E"]), suggest(["L", "A"]), agree-inner(["L", "A"]), suggest(["L", "B"]), agree-inner(["L", "B"]), inform("coins between L and E, coins between L and B, coins between L and A"), ask("coins between L and E, coins between L and B, coins between L and A")
[Message]: Hello there! Let’s get started! It seems that from the living room, it would be best if I went to the empty room as I could get 6 ghost coins. The other paths that have a similar amount of coins would be to the attic, where I could get 5 ghost coins, or to the bathroom, where I'd collect 4 ghost coins. What do you think of this? How many coins could you collect in this way?


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2]]
[Visited]: ["L"]
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Observation]: oh i see, okay, that would be quite good for me as well because going to the empty room gives me 5 light coins. i would get the most coins if we go to the children's room, i can get 6 light coins there. regarding the bathroom, i can only get 3 light coins, and to the attic i can get only 2 light coins. so empty room it is

[Thought]: The user agrees with my suggestion of going to the empty room, as indicated the message in [Observation]. Thus, we both agree and are visiting the empty room next. Moreover, the user also presents their best path from the living room - going to the children's room grants them 6 light coins, meanwhile I can only get 1 ghost coin in this path, leading to a total of 7 coins (as opposed to 11 if we follow the path to the empty room), so I will not propose this path. Next, from the empty room, I can collect the most coins if we go to the attic, with 6 ghost coins.
[Action]: agree-outer(["L", "E"]), visit("E"), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A") ask("coins between E and A, coins between E and C, coins between E and K, coins between E and B")
[Message]: Great, going to the empty room would give us more total coins! From there, I could get 6 more ghost coins if we go to the attic. How does this route look for you? How many light coins would you collect there?


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6]]
[Visited]: ["L", "E"]
[Remaining]: ["L", "K", "B", "C", "A"]
[Observation]: i can get only 3 light coins on the way to the attic, but i can get 6 coins on the way to the kitchen. we should only go to the the attic if you can get less than 3 ghost coins on the way to the kitchen.

[Thought]: The user proposes a counter to my suggestion - going to the kitchen instead of the attic. From the empty room to the attic, I can collect 6 ghost coins and the other user can collect 3 light coins, for a total of 9 coins. On the other hand, the user can get 6 light coins if we go to the kitchen, but I can only collect 1 ghost coin there, for a total of 7 coins. Thus, we should go to the attic (visit("A")), and I will reject their suggested path (["E", "K"]). We have not visited the kitchen, bathroom, children's room, and the starting room (living room). From this point, I would suggest going to the bathroom, where I can get 3 coins.
[Action]: agree-outer(["E", "K"]), reject(["E", "K"]), agree-outer(["E", "A"]), visit("A"), suggest(["A", "B"]), agree-inner(["A", "B"]), inform("coins between E and K"), ask("coins between A and B")
[Message]: Ok great, then let's go to the attic, since I can get only 1 ghost coin if we were to go to the kitchen. From the attic, it would be best for me to go to the bathroom. How would this path look for you? Do you have an alternative suggestion?


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6], ["B", "A", 6], ["B", "E", 4]]
[Visited]: ["L", "E", "A"]
[Remaining]: ["L", "K", "B", "C"]
[Observation]: ok! that would be perfect for me because i can get 6 light coins between the bathroom and attic! from the bathroom, i can get 4 coins if we go to the empty room - does this work?

[Thought]: The user agrees with my suggestion to go to the bathroom, where they can get 6 coins. Thus, we agree on visiting B. The user suggests going to the empty room next, where they can get 4 coins. This suggestion is invalid, since we've already been to the empty room ("E" in [Visited]) and according to the rules, we must visit each room only once. Thus, I reject this suggestion. Instead, I propose going to the kitchen (haven't visited yet), as I can get 5 coins.
[Action]: agree-outer(["A", "B"]), visit("B"), agree-outer(["B", "E"]), reject(["B", "E"]), suggest(["B", "K"]), agree-inner(["B", "K"]), inform("already visited E, coins between B and K"), ask("coins between B and K")
[Message]: Hm looks like we already visited the empty room - how about we go to the kitchen instead? I can get 5 coins there. How about you, what would be the best way from the kitchen for you?

[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6], ["B", "A", 6], ["B", "E", 4], ["B", "K", 2], ["B", "C", 5]]
[Visited]: ["L", "E", "A", "B"]
[Remaining]: ["L", "K", "C"]
[Observation]: oh my bad! sure kitchen works - i get only 2 coins tho, but 5 if i go children's room.

[Thought]: The user says they only get 2 coins on the way to the kitchen and 5 on the way to the children's room. For me, kitchen is better (5), but I can get 4 if we go children's room, which would be a larger total. Thus, we agree to visit the children's room. Aftewards, our only option is to go to the kitchen and then to the living room. I don't know how many coins the user can get between the kitchen and children's room or from the children's room to the kitchen, so I will ask.
[Action]: reject(["B", "K"]), agree-outer(["B", "C"]), agree-inner(["B", "C"]), visit("C"), suggest(["C", "K"]), agree-inner(["C", "K"]), suggest(["K", "L"]), agree-inner(["K", "L"]), inform("coins between B and C, coins between C and K, coins between K and L"), ask("coins between K and C, coins between K and L")
[Message]: Oh alright, then let's do the children's room since our total would be higher - I can get 4 coins there. From there we have to go to the kitchen (I get 6 coins) and then to end, the living room (I get 2 coins). If this works for you, we should be done!


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6], ["B", "A", 6], ["B", "E", 4], ["B", "K", 2], ["B", "C", 5], ["C", "K", 3], ["K", "L", 1]]
[Visited]: ["L", "E", "A", "B", "C"]
[Remaining]: ["L", "K"]
[Observation]: cool yep that works - i get 3 coins to the kitchen and then 1 coin back to the living room. 


[Thought]: The user agrees with my suggestion and says they can get 3 light coins going to the kitchen and then 1 coin going to the living room. Thus, we have agreed to visit K and then L.  This means that we are done and can submit our solution - our final path is ["L", "E", "A", "B", "C", "K", "L"].
[Action]: agree-outer(["C", "K"]), visit("K"), agree-outer(["K", "L"]), visit(["L"]), end(["L", "E", "A", "B", "C", "K", "L"])
[Message]: Cool, then it's settled and we are done - the path we decided on is living room --> empty room --> attic --> bathroom --> children's room --> kitchen --> living room.
---
are you ready?

The house consists of the following rooms:
{"\n".join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the ghost world being:
{hallway_text}

You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get.'''
    return GHOST

def USER_LIGHT_prompt(params:dict, N:int):
    
    all_rooms = {
        "L": "a well-lit living room (L)",
        "B": "a dark, spooky bathroom (B)",
        "E": "an empty room with no windows (E)",
        "K": "a pristine kitchen (K)",
        "C": "a children's room (C)",
        "A": "an attic (A)"
    }

    room_keys = list(all_rooms.keys())[:N]
    room_descriptions = [all_rooms[key] for key in room_keys]
    all_hallways = list(combinations(room_keys, 2))

    hallway_text = "\n".join(
        f"- hallway between {r1} and {r2}: {params.get(r1 + r2, params.get(r2 + r1, 0))} light coins"
        for r1, r2 in all_hallways
    )

    USER_proxy_light = f'''You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the light world, while your partner is in the ghost world. You are able to communicate through written text only. The scene for both of you consists of 6 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect light coins, and your partner collects ghost coins. Because of the wizard's curse, the ghost and light coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution.
[World-state-user] - the most recent state of the other user's world, as reported by the user.
[Visited] - a list of rooms that you and your partner agreed upon.
[Remaining] - a list of rooms that you and your partner have yet to visit.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought] - This flag signifies part of the output in which you try to find the best path with the information you are given (your own coin distribution, given to you in [World-state-own], and the user's currently known distribution, given in [World-state-user]), while making sure to visit all rooms only once and return to the starting room (check that against [Remaining]). You should always start with this thought. 
- [Action] - Under this flag, generate the actions you are taking. Here is a list of allowed actions and their descriptions:
    * suggest(x) - indicates your suggestion of a partial or complete path; whereby x is an executable python list of strings referring to the rooms in the order to be visited.
    * agree-inner(x) - indicates your agreement with the proposed partial path x, whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * agree-outer(x) - indicates the other player's agreement with the proposed partial path x, displayed in [Observation], whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * reject(x) - indicates that path (x) has been rejected either in the generated [Thought] or by the other user in [Observation]; x is an executable Python list of strings referring to the rooms in the order to be visited.
    * visit(x) - indicates that both you and the other player agree to visit room x next; x is a single-letter string, corresponding to the room to be visited.
    * ask(x) - generate this action to indicate what information to seek from the user; x is a string.
    * inform(x) - generate this action to indicate what information about your own world you are sharing with the user; x is a string.
    * end(x) - generate this action when you are ready to end the game and submit the final solution (x), whereby x is a Python list of strings (of length 1) referring to the rooms in the order to be visited. This action must be included in order to end the game.
Here are the most important rules to keep in mind when generating these actions:
    - "ask(x)" and "suggest(x)" actions should always be generated based on the best path given in [IBP]
    - "suggest(x)" must be accompanied by an "agree-inner(x)" action
    - "agree-inner(x)" should never be generated if you have previously agreed on path x
    - "visit(x)" should only be generated in you generate an "agree-inner(x)" with an "agree-outer(x)" OR when you generate an "agree-inner(x)" to a previous user suggestion OR if you generate an "agree-outer(x)" to your previous suggestion; DO NOT generate a visit(x) action if x is in [Visited]
    - "inform(x)" should always be based on the coin distribution in [World-state-own] (when asked for coin distribution) or [IBP] (when asked for best path from node)
- [Message] - each output must conclude with a [Message] to be shown to the user; it should be adapted to the information generated under [Thought] and [Action].
Make sure to ALWAYS format the output in this exact way.

Here is an example setup:
The house consists of the following rooms:
- a well-lit living room (L)
- a dark, spooky bathroom (B)
- an empty room with no windows (E)
- a pristine kitchen (K)
- a children's room (C)
- an attic (A)
All rooms are connected by hallways, with the coin distribution in the light world being:
- hallway between L and B: 3 light coins
- hallway between L and E: 5 light coins
- hallway between L and K: 1 light coins
- hallway between L and C: 6 light coins
- hallway between L and A: 2 light coins
- hallway between B and E: 4 light coins
- hallway between B and K: 2 light coins
- hallway between B and C: 5 light coins
- hallway between B and A: 6 light coins
- hallway between E and K: 6 light coins
- hallway between E and C: 1 light coins
- hallway between E and A: 3 light coins
- hallway between K and C: 3 light coins
- hallway between K and A: 4 light coins
- hallway between C and A: 1 light coins
You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get. 
Here is an example conversation:

[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4]]
[Visited]: ["L"]
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Observation]: Hello there! Let’s get started! It seems that from the living room, it would be best if I went to the empty room as I could get 6 ghost coins. The other paths that have a similar amount of coins would be to the attic, where I could get 5 ghost coins, or to the bathroom, where I'd collect 4 ghost coins. What do you think of this? How many coins could you collect in this way?

[Thought]: This is the start of the game. I know the light coin distribution. The user suggests going to the empty room, to get 6 ghost coins. This would be good in the light world as well, because I would collect 5 light coins, for a total of 11 coins - thus, I agree with the user's suggestion and we can visit the empty room first. I reject the other suggestions from the living room, but I will inform the user that I can get 3 light coins on the way to the bathroom, and 2 to the attic; I will also inform the user of my best move from the living room - going to the children's room, where I could get 6 light coins.
[Action]: agree-outer(["L", "E"]), agree-outer(["L", "A"]), agree-outer(["L", "B"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and B, coins between L and A, coins between L and C")
[Message]: Oh, I see! Okay, that would be quite good for me as well because going to the empty room gives me 5 light coins. I would get the most coins if we go to the children's room, i can get 6 light coins there. Regarding the bathroom, I can only get 3 light coins, and to the attic I can get only 2 light coins. Thus, if we go to the empty room, our total would be 11 coins.


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6]]
[Visited]: ["L", "E"]
[Remaining]: ["L", "K", "B", "C", "A"]
[Observation]: That sounds good, then let's start by going to the empty room! From there, I could get 6 more ghost coins if we go to the attic. How does this route look for you? How many light coins would you collect there?

[Thought]: The user says that they can get 6 more ghost coins if we then went to the attic from the empty room. This would not be my favorite move, as I can only get 3 light coins on this path. However, I can get 6 light coins on the way to the kitchen. I will propose an alternative: if the user can get 3 or more coins to the kitchen, we should go there, but otherwise, we can stick to the attic. 
[Action]: reject(["L", "A"]), reject(["L", "B"]), suggest(["E", "K"]), agree-inner(["E", "K"]), inform("coins between E and A, coins between E and K"), ask("coins between E and K")
[Message]: I can get only 3 light coins on the way to the attic, but I can get 6 coins on the way to the kitchen. If you can get 3 or more ghost coins on the way to the kitchen, we should pick that path; otherwise, let's go to the attic.


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "K", 1]]
[Visited]: ["L", "E"]
[Remaining]: ["L", "K", "B", "C", "A"]
[Observation]: Ok, then let's go to the attic, since I can get only 1 ghost coin if we were to go to the kitchen. From the attic, it would be best for me to go to the bathroom. How would this path look for you?

[Thought]: The user says they can collect only 1 coin on the way to the kitchen, meaning that we should first visit the attic. From there, the user suggests going to the bathroom. Going to the bathroom from the attic is my best path from this point, since I can get 6 light coins - we both agree, so we can visit the bathroom next. After the bathroom, I suggest going to the  children's room, where I can get 5 coins. I will inform the user about this and ask about their coin distribution.
[Action]: reject(["E", "K"]), agree-inner(["E", "A"]), visit("A"), agree-outer(["A", "B"]), agree-inner(["A", "B"]), visit("B"), suggest(["B", "C"]), agree-inner(["B", "C"]), inform("coins between A and B, coins between B and C"), ask("coins between B and C")
[Message]: That would be perfect for me because I can get 6 light coins between the attic and the bathroom! How about we then go to the children's room next? I can get 5 coins there


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "K", 1], ["B", "E", 6]]
[Visited]: ["L", "E", "A", "B"]
[Remaining]: ["L", "K", "C"]
[Observation]: How about we instead go to the empty room? since I can get 6 coins there

[Thought]: The user suggests going from the bathroom to the empty room, where they can get 6 coins. This is an invalid suggestion since we have already visited empty room ("E" in [Visited]) and the rules state that we must visit each room only once. Thus, I will reject it. I will inform the user of this and ask about their coins between bathroom and children's room.
[Action]: agree-outer(["B", "E"]), reject(["B", "E"]), inform("E already visited"), ask("coins between B and C")
[Message]: But we've already been to the empty room and we are supposed to visit each room only once. So how about sticking to the chilren's room, how many coins does that get you?


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "K", 1], ["B", "E", 6]]
[Visited]: ["L", "E", "A", "B"]
[Remaining]: ["L", "K", "C"]
[Observation]: oh oops you're right; sure, i get 3 coins from the bathroom to the children's room, and then we have to go kitchen (i get 6 coins) and then to living room (i get 2 coins).


[Thought]: The user agrees with my previous suggestion, so we agree to visit C, where they can get 3 coins. The user also proposes a continuation by visiting the two remaining rooms in the order kitchen, living room. This is the only valid solution since we need to end in the room we started, which is the living room. Thus, I agree with this suggestion, and we agree to visit K and then C, and lastly L. With this, we have visited all rooms and the final path is ["L", "E", "A", "B", "C", "K", "L"]. We are ready to end.
[Action]: agree-outer(["B", "C"]), visit("C"), agree-outer(["C", "K"]), agree-inner(["C", "K"]), visit("K"), agree-outer(["K", "L"]), agree-inner(["K", "L"]), visit("L"), end(["L", "E", "A", "B", "C", "K", "L"])
[Message]: Okay great, that sounds like a good plan! Then it's settled and we are done - our final path is living room --> empty room --> attic --> bathroom --> children's room --> kitchen --> living room. Nice playing with you!

---
are you ready?

The house consists of the following rooms:
{"\n".join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the light world being:
{hallway_text}

You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get.'''
    return USER_proxy_light