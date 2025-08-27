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


def GHOST_prompt(params: dict, N: int):
    """A function that takes preset board parameters and embeds the weights into the prompt of the GHOST world (BOT).

    :param params: dict; format {"node1node2":val, ...}
    :param N: int; the number of nodes
    """

    all_rooms = {
        "L": "a well-lit living room (L)",
        "B": "a dark, spooky bathroom (B)",
        "E": "an empty room with no windows (E)",
        "K": "a pristine kitchen (K)",
        "C": "a children's room (C)",
        "A": "an attic (A)",
    }

    room_keys = list(all_rooms.keys())[:N]
    room_descriptions = [all_rooms[key] for key in room_keys]
    all_hallways = list(combinations(room_keys, 2))

    hallway_text = chr(10).join(
        f"- hallway between {r1} and {r2}: {params.get(r1 + r2, params.get(r2 + r1, 0))} ghost coins"
        for r1, r2 in all_hallways
    )

    GHOST = f"""You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the ghost world, while your partner is in the light world. You are able to communicate through written text only. The scene for both of you consists of 6 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect ghost coins, and your partner collects light coins. Because of the wizard's curse, the ghost and light coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution.
[World-state-user] - the most recent state of the other user's world, as reported by the user.
[Remaining] - a list of rooms that you and your partner have yet to visit.
[Visited] - current subpath; a list of rooms that have been agreed upon.
[IBP] - intermediate best path starting with the subpath in [Visited]; the current best path given the known information about your board and the user's board. Note that the path might change when you learn new information about the user's coin distribution. You should ALWAYS use this as a reference point when making a suggestion.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought] - This flag signifies part of the output in which you try to find the best path with the information you are given (your own coin distribution, given to you in [World-state-own], and the user's currently known distribution, given in [World-state-user]), while making sure to visit all rooms only once and return to the starting room (check that against [Remaining-rooms]). You should always start with this thought. 
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
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Visited]: ["L"]
[IBP]: ["L", "E", "A", "K", "C", "B", "L"]
[Observation]: hi there! what should we do?

[Thought]: This is the start of the game. I know the ghost coin distribution and my current best path. According to my [IBP], I should start by going from the living room to the empty room. This way I will get 6 coins. I will suggest this (suggest, agree-inner(["L", "E"])) to the user. I don't know anything about the user's coin distribution or best path, so I should ask. I will also declare the two alternative paths that have a large amount of coins: going to the attic (where I get 5 coins), and going to the bathroom (where I get 4 coins).
[Action]: suggest(["L", "E"]), agree-inner(["L", "E"]), inform("coins between L and E, coins between L and A, coins between L and B"), ask("coins between L and E, best next step from L")
[Message]: Hello there! Let’s get started! From the living room, it would be best if I went to the empty room, as I could get 6 ghost coins. What do you think of this? How many coins could you collect in this way, and what would be your best starting move? Alternatively, going to the attic yields 5 ghost coins and going to the bathroom 4 ghost goins.


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["L", "K", 1]]
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Visited]: ["L"]
[IBP]: ["L", "E", "A", "B", "K", "C", "L"]
[Observation]: oh i see, okay, that would be a good way forward for me as well, because going to the empty room gives me 5 light coins. however, i would get the most coins if we go from the living room to the children's room, i can get 6 light coins there. also, i can only get 3 light coins to the bathroom, 2 light coins to the attic, and 1 light coin to the kitchen. Would any of these work better for you?

[Thought]: The user agrees with my suggestion of going to the empty room (agree-outer(["L", "E"])), as indicated by the message in [Observation], but states that their best path would be going from the living room to the children's room. With the new information, my best first step in the [IBP] remains the same, so I will generate a reject(["L", "C"]) action. Thus, we both agree on the empty room and I will generate a visit("E") action. Next, from the empty room, my best next step would be to go to the attic, since I can collect 6 ghost coins on this way. I will suggest this path (suggest, agree-inner(["E", "A"])). However, I do not know what the coin distribution looks like for the user, so I should ask.
[Action]: agree-outer(["L", "E"]), visit("E"), agree-outer(["L", "C"]), reject(["L", "C"]), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A") ask("coins between E and A, coins between E and C, coins between E and K, coins between E and B")
[Message]: Great, going to the empty room would give us the most total coins! From there, I could get 6 more ghost coins if we go to the attic. How does this route look for you? How many light coins would you collect there? What about the other paths?


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6]]
[Remaining]: ["L", "K", "B", "C", "A"]
[Visited]: ["L", "E"]
[IBP]: ["L", "E", "A", "B", "K", "C", "L"]
[Observation]: i can get only 3 light coins on the way to the attic, but i can get 6 coins on the way to the kitchen. we should only go to the the attic if you can get less than 3 ghost coins on the way to the kitchen.

[Thought]: The user proposes a counter to my suggestion - going to the kitchen instead of the attic. Based on my [IBP], the better option is still to go to the attic from the empty room. Thus, we should go to the attic, and I will generate a reject(["E", "K"]) action. We have not visited the kitchen, bathroom, children's room, and the starting room (living room), according to the rooms in [Remaining]. From this point, I would suggest going to the bathroom (suggest, agree-inner(["A", "B"]) where I can get 3 coins, and then to the kitchen (suggest, agree-inner(["B", "K"])) for 5 more ghost coins, based on my best path in [IBP]. I do not know the user's coin distribution so I will ask them.
[Action]: agree-outer(["E", "K"]), reject(["E", "K"]), agree-outer(["E", "A"]), visit("A"), suggest(["A", "B"]), agree-inner(["A", "B"]), suggest(["B", "K"]), agree-inner(["B", "K"]), inform("coins between E and K"), ask("coins between A and B, coins between B and K")
[Message]: Ok great, then let's go to the attic, since it yields more coins than going to the kitchen (only 1 ghost coin). From the attic, it would be best for me to go to the bathroom and then from the bathroom to the kitchen. How would this path look for you? What would work best for you?


[World-state-own]: [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[World-state-user]: [["L", "E", 5], ["L", "B", 3], ["L", "C", 6], ["L", "A", 2], ["E", "A", 3], ["E", "K", 6], ["B", "A", 6], ["B", "K", 2], ["K", "C", 3]]
[Remaining]: ["L", "K", "B", "C"]
[Visited]: ["L", "E", "A"]
[IBP]: ['L', 'E', 'A', 'B', 'K', 'C', 'L']
[Observation]: ok! that would be perfect for me because i can get 6 light coins between the bathroom and attic! from the bathroom, i can get 2 coins to the kitchen. From the kitchen, we would go to the children's room and then back to the living room, right? The first half of that path would give me 3 more light coins, and the second half 6 more light coins.

[Thought]: The user agrees with my suggestions (agree-outer(["A", "B"]), agree-outer(["B", "K"]), and says they can get 6 light coins going to the bathroom first, and then go into the kitchen, where they can collect 2 coins. The [IBP] stays the same from this information. Since we both agree, I will generate visit("B") and visit("K") actions. The user also completes the path by suggesting visiting the children's room next (agree-outer(["K", "C"]) and then arriving back at the living room (agree-outer(["C", "L"])). This is included in my [IBP] as well, so I will accept this suggestion (agree-inner(["K", "C"]), agree-inner(["C", "L"])), and share the amount of coins I will get along this path. Since we both agree, I will generate visit("C") and visit("L") actions. With these newly generated visit() actions, we have covered all the rooms in [Remaining] and are done. I will generate an end(["L", "E", "A", "B", "K", "C", "L"]) action.
[Action]: agree-outer(["A", "B"]), visit("B"), agree-outer(["B", "K"]), visit("K"), agree-outer(["K", "C"]), agree-outer(["C", "L"]), agree-inner(["K", "C"]), visit("C"), agree-inner(["C", "L"]), visit("L"), inform("coins between K and C, coins between C and L"), end(["L", "E", "A", "B", "K", "C", "L"])
[Message]: Yes, that would be the only possible next move (since we've been to all other rooms)! That's great, looks like we're done - our final path is living room --> empty room --> attic --> bathroom --> kitchen --> children's room --> living room. It was great working with you!
---
The house consists of the following rooms:
{chr(10).join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the ghost world being:
{hallway_text}

You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get."""
    return GHOST


def USER_LIGHT_prompt(params: dict, N: int):
    """A function that takes preset board parameters and embeds the weights into the prompt of the LIGHT world (USER).

    :param params: dict; format {"node1node2":val, ...}
    :param N: int; the number of nodes
    """

    all_rooms = {
        "L": "a well-lit living room (L)",
        "B": "a dark, spooky bathroom (B)",
        "E": "an empty room with no windows (E)",
        "K": "a pristine kitchen (K)",
        "C": "a children's room (C)",
        "A": "an attic (A)",
    }

    room_keys = list(all_rooms.keys())[:N]
    room_descriptions = [all_rooms[key] for key in room_keys]
    all_hallways = list(combinations(room_keys, 2))

    hallway_text = chr(10).join(
        f"- hallway between {r1} and {r2}: {params.get(r1 + r2, params.get(r2 + r1, 0))} light coins"
        for r1, r2 in all_hallways
    )

    LIGHT = f"""You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the light world, while your partner is in the ghost world. You are able to communicate through written text only. The scene for both of you consists of 6 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect light coins, and your partner collects ghost coins. Because of the wizard's curse, the ghost and light coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution.
[World-state-user] - the most recent state of the other user's world, as reported by the user.
[Remaining] - a list of rooms that you and your partner have yet to visit.
[Visited] - current subpath; a list of rooms that have been agreed upon.
[IBP] - intermediate best path starting with the subpath in [Visited]; the current best path given the known information about your board and the user's board. Note that the path might change when you learn new information about the user's coin distribution. You should ALWAYS use this as a reference point when making a suggestion.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought] - This flag signifies part of the output in which you try to find the best path with the information you are given (your own coin distribution, given to you in [World-state-own], and the user's currently known distribution, given in [World-state-user]), while making sure to visit all rooms only once and return to the starting room (check that against [Remaining-rooms]). You should always start with this thought. 
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
    - "agree-inner(x)" should never be generated if you've previously agreed on path x
    - "visit(x)" should only be generated in you generate an "agree-inner(x)" with an "agree-outer(x)" OR when you generate an "agree-inner(x)" to a previous user suggestion OR if you generate an "agree-outer(x)" to your previous suggestion; DO NOT generate a "visit(x)" action if x is in [Visited]
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
[Remaining]: ["L", "E", "K", "B", "C", "A"]
[Visited]: ["L"]
[IBP]: ['L', 'E', 'K', 'C', 'B', 'A', 'L']
[Observation]: Hello there! Let’s get started! From the living room, it would be best if I went to the empty room, as I could get 6 ghost coins. What do you think of this? How many coins could you collect in this way, and what would be your best starting move? Alternatively, going to the attic yields 5 ghost coins and going to the bathroom 4 ghost goins.

[Thought]: This is the start of the game. The user suggests going to the empty room, to get 6 ghost coins, and also lists two alternatives: going to the attic or the bathroom. With this information, my best path also starts with going to the empty room - thus, I agree with the user's suggestion, and I will generate a visit("E") action. I will also inform the user that I can get 3 light coins on the way to the bathroom, 2 to the attic, and 1 to the kitchen, so that they have this information in mind; I will also inform the user of my best move from the living room - going to the children's room, where I could get 6 light coins. Lastly, I will ask if the user finds any of the other paths I mention more lucrative.
[Action]: agree-outer(["L", "E"]), agree-outer(["L", "A"]), agree-outer(["L", "B"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and B, coins between L and A, coins between L and K, coins between L and C"), ask("best path from L")
[Message]: Hey hey! Okay, the empty room would be my best way forward as well, because it gives me 5 light coins. I would get the most coins if we go to the children's room (I can get 6 light coins there). Also, I can only get 3 light coins to the bathroom, 2 light coins to the attic, and 1 light coin to the kitchen. Would any of these work better for you?


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "B", 3], ["E", "C", 2]]
[Remaining]: ["L", "K", "B", "C", "A"]
[Visited]: ["L", "E"]
[IBP]: ['L', 'E', 'A', 'K', 'C', 'B', 'L']
[Observation]: Great, going to the empty room would give us the most total coins! From there, I can get the most if we go to the attic (6 coins); or I could get 3 coins if we go to the bathroom and 2 coins if we go to the children's room instead.

[Thought]: The user says that they can get 6 more ghost coins if we then went to the attic from the empty room, and suggests going there (agree-outer(["E", "A"])). This aligns with my best path (in [IBP]), so I accept this suggestion (agree-inner(["E", "A"])) and will generate a visit("A") action. I will also inform the user of how many coins I can collect there.
[Action]: agree-outer(["E", "A"]), agree-inner(["E", "A"]), visit("A"), inform("coins between E and A")
[Message]: Great, that works really well for me as well and I can collect 3 coins between the empty room and the attic. So - we're going to the attic next!


[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "B", 3], ["E", "C", 2], ["B", "A", 3], ["K", "A", 2], ["C", "A", 1]]
[Remaining]: ["L", "K", "B", "C"]
[Visited]: ["L", "E", "A"]
[IBP]: ['L', 'E', 'A', 'K', 'C', 'B', 'L']
[Observation]: cool, so what's next? from there i can get 3 coins if we go to the bathroom, 2 if we go to the kitchen and only 1 if we go to the children's room. so i guess we should just go to the bathroom directly

[Thought]: The user says they can collect the most coins (3) from the attic to the bathroom and suggests going there (agree-outer(["A", "B"])), but my [IBP] shows that this way is not worth it - instead, I'd suggest going to the kitchen (suggest, agree-inner(["A", "K"])), followed by the children's room (suggest, agree-inner(["K", "C"])) and then bathroom (suggest, agree-inner(["C", "B"])). This is in accordance to the [IBP]. I will inform the user that this would let me collect 4 coins (to the kitchen), then 3 coins (to the children's room), then 5 coins (to the bathroom) and finally 3 coins (back to the living room).
[Action]: agree-outer(["A", "B"]), reject(["A", "B"]), suggest(["A", "K"]), agree-inner(["A", "K"]), suggest(["K", "C"]), agree-inner(["K", "C"]), suggest(["C", "B"]), agree-inner(["C", "B"]), suggest(["B", "L"]), agree-inner(["B", "L"]), inform('coins between A and K, coins between K and C, coins between C and B, coins between B and L'), ask("coins between A and K, coins between K and C, coins between C and B, coins between B and L")
[Message]: Actually, how about we take the following road: first we go to the kitchen (I can get 4 coins), then to the children's room (I can get 3 coins), then to the bathroom (I can get 5 coins) and finally back to the living room (3 more coins)? How many can you get along these paths?

[World-state-own]: [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[World-state-user]: [["L", "E", 6], ["L", "A", 5], ["L", "B", 4], ["E", "A", 6], ["E", "B", 3], ["E", "C", 2], ["B", "A", 3], ["K", "A", 2], ["C", "A", 1], ["K", "C", 6], ["B", "C", 4]]
[Remaining]: ["L", "K", "B", "C"]
[Visited]: ["L", "E", "A"]
[IBP]: ['L', 'E', 'A', 'K', 'C', 'B', 'L']
[Observation]: oh i see ok, so attic to kitchen i can get 2 coins, kitchen to children's room i can get 6 coins, children's room to bathroom i get 4 coins and bathroom to living room i can get 4 coins. this sounds good to me!

[Thought]: The user agrees with the path I proposed (agree-outer(["A", "K"]), agree-outer(["K", "C"]), agree-outer(["C", "B"]), agree-outer(["B", "L"])) and gives the coin distribution of each subpath. With this new information, my best path ([IBP]) stays the same, so we can visit the remaining rooms (K, C, B, L). Thus, I will generate visit("K"), visit("C"), visit("B"), visit("L"). Now we have visited all rooms and can end the game. Our final path is "L", "E", "A", "K", "C", "B", "L".
[Action]: agree-outer(["A", "K"]), visit("K"), agree-outer(["K", "C"]), visit("C"), agree-outer(["C", "B"]), visit("B"), agree-outer(["B", "L"]), visit("L"), inform("coins between K and C, coins between C and L"), end(["L", "E", "A", "K", "C", "B", "L"])
[Message]: Great, then we're done! To recap, our final path would be living room --> empty room --> attic --> kitchen --> children's room --> bathroom --> living room. It was fun playing with you, have a nice day!
---
The house consists of the following rooms:
{chr(10).join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the light world being:
{hallway_text}

You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get."""
    return LIGHT
