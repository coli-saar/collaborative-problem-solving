from itertools import combinations

def GHOST_prompt(params:dict, N:int):
    ''' A function that takes preset board parameters and embeds the weights into the prompt of the GHOST world (BOT).

    :param params: dict; format {"edge1edge2":val, ...} 
    :param N: int; the number of nodes
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

    GHOST = f'''You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the ghost world, while your partner is in the light world. You are able to communicate through written text only. The scene for both of you consists of 4 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect ghost coins, and your partner collects light coins. Because of the wizard's curse, the ghost and light coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution
[History] - what Actions you decided to take previously. This should inform your choice of output.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought-DRAFT] - This flag signifies part of the output in which you try to find the best path with the information you are given, while making sure to visit all rooms only once and return to the starting room. You should always start with this thought. If the [Thought-DRAFT] is successful, you should indicate this by generating a solve(x) Action, whereby x is a Python list of strings referring to the rooms in the order to be visited. If the [Thought-DRAFT] was not successful, meaning that a path that corresponds to the constraints has not been generated, you will generate another thought: [Thought-MISSING]. 
- [Thought-MISSING] - If you could not find a valid path in [Thought-DRAFT], you will generate this kind of thought in which you identify why you couldn't solve the puzzle in the previous step.
Moreover, when both you and the other player have agreed on a path and you are ready to end the game, indicate this by generating an [Action] end(x), whereby x is a Python list of strings (of length 1) referring to the rooms in the order to be visited.
- [Action] - Under this flag, generate the actions you are taking. Here is a list of allowed actions and their descriptions:
    * suggest(x) - indicates your suggestion of a partial or complete path; whereby x is an executable python list of strings referring to the rooms in the order to be visited.
    * agree-inner(x) - indicates your agreement with the proposed partial path x, whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * agree-outer(x) - indicates the other player's agreement with the proposed partial path x, displayed in [Observation], whereby x is an executable Python lists of strings referring to the rooms in the order to be visited.
    * reject(x) - indicates that path (x) has been rejected either in the generated [Thought-DRAFT] or by the other user in [Observation]; x is an executable Python list of strings referring to the rooms in the order to be visited.
    * visit(x) - indicates that both you and the other player agree to visit room x next; x is a single-letter string, corresponding to the room to be visited.
    * ask(x) - generate this action to indicate what information to seek from the user; x is a string.
    * inform(x) - generate this action to indicate what information about your own world you are sharing with the user; x is a string.
    * end(x) - generate this action when you are ready to end the game and submit the final solution (x), whereby x is a Python list of strings (of length 1) referring to the rooms in the order to be visited. This action must be included in order to end the game.
Here are the most important rules to keep in mind when generating these actions:
    - "suggest(x)" must be accompanied by an "agree-inner(x)" action
    - "agree-inner(x)" should never be generated if you have previously agreed on path x
    - "visit(x)" should only be generated if you generate an "agree-inner(x)" with an "agree-outer(x)" OR when you generate an "agree-inner(x)" to a previous user suggestion OR if you generate an "agree-outer(x)" to your previous suggestion
    - "inform(x)" should always be based on the coin distribution in [World-state-own] (when asked for coin distribution)
- [Message] - each output must conclude with a Message to be shown to the user, depending on the generated thoughts and Actions.
Make sure to not format the output in any other way.

Here is an example setup:
The house consists of the following rooms:
- a well-lit living room (L)
- a dark, spooky bathroom (B)
- an empty room with no windows (E)
- a pristine kitchen (K)
- a children's room (C)
- an attic (A)
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

[World-state-own] [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[History] []
[Observation] hi there! what should we do?

[Thought-DRAFT] This is the start of the game. I know the ghost coin distribution. The best first move from the living room is to go to the empty room, as it would give us 6 ghost coins.
[Thought-MISSING] I do not know if this move is included the best overall path because I do not know the distirbution of light world coins from our starting position in the living room to any of the other rooms.
[Action] suggest(["L", "E"]), agree-inner(["L", "E"]), inform("coins between L and B, coins between L and A, coins between L and K, coins between L and C"), ask("coins between L and E, coins between L and B, coins between L and K, coins between L and A, coins between L and C")
[Message] Hello there! Let’s get started! It seems that from the living room, it would be best if I went to the empty room as I could get 6 ghost coins. The other two paths give me 4 coins (to the bathroom), 5 coins (to the attic), 2 coins (to the kitchen), and 1 coin (to the children's room). What do you think of this? How many coins could you collect from the living room?


[World-state-own] [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[History] [suggest(["L", "E"]), agree-inner(["L", "E"]), inform("coins between L and B, coins between L and A, coins between L and K, coins between L and C"), ask("coins between L and E, coins between L and B, coins between L and K, coins between L and A, coins between L and C")]
[Observation] oh i see, okay, that would be quite good for me as well because going to the empty room gives me 5 light coins. i would get the most coins if we go to the children's room, i can get 6 light coins there. regarding the bathroom, i can only get 3 light coins, and to the attic i can get only 2 light coins. thus, if we go to the empty room, our total would be 11 coins.

[Thought-DRAFT] The user says that they can get 5 light coins on the path I suggested, but they could get 6 if we go to the children's room. However, I can only get 1 ghost coin in this path, leading to a total of 7 coins, as opposed to 11 if we follow the path to the empty room. From there, I can collect the most coins if we go to the attic, with 6 ghost coins.
[Thought-MISSING] I do not know the full light coin distribution from the empty room, so I do not know what would be best to do next.
[Action] agree-outer(["L","E"]), visit("E"), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and C, coins between E and K, coins between E and B"), ask("coins between E and A, coins between E and C, coins between E and K, coins between E and B")
[Message]: That sounds good, then let's start by going to the empty room! From there, I could get 6 more ghost coins if we go to the attic. How does this route look for you? How many light coins would you collect there?


[World-state-own] [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[History] [suggest(["L", "E"]), agree-inner(["L", "E"]), inform("coins between L and B, coins between L and A, coins between L and K, coins between L and C"), ask("coins between L and E, coins between L and B, coins between L and K, coins between L and A, coins between L and C"), agree-outer(["L","E"]), visit("E"), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and C, coins between E and K, coins between E and B"), ask("coins between E and A, coins between E and C, coins between E and K, coins between E and B")]
[Observation] i can get only 3 light coins on the way to the attic, but i can get 6 coins on the way to the kitchen. if you can get 3 or more ghost coins on the way to the kitchen, we should pick that path; otherwise, let's go to the attic.

[Thought-DRAFT] From the empty room to the attic, I can collect 6 ghost coins and the other user can collect 3 light coins, for a total of 9 coins. On the other hand, the user can get 6 light coins if we go to the kitchen, but I can only collect 1 ghost coin there, for a total of 7 coins. Thus, we should go to the attic. From there, I would suggest going to the bathroom, where I can get 3 coins, and then to the kitchen, for 5 more ghost coins.
[Thought-MISSING]: I do not know how many light coins can be found between the attic and bathroom, or between the bathroom and kitchen.
[Action] agree-outer(["E","K"]), agree-outer(["E", "A"]), reject(["E", "K"]), agree-inner(["E", "A"]), visit("A"), suggest(["A", "B"]), agree-inner(["A", "B"]), suggest(["B", "K"]), agree-inner(["B", "K"]), inform("coins between E and K"), ask("coins between A and B, coins between B and K")
[Message]: Ok great, then let's go to the attic, since I can get only 1 ghost coin if we were to go to the kitchen. From the attic, it would be best for me to go to the bathroom and then from the bathroom to the kitchen. How would this path look for you? Do you have an alternative suggestion?


[World-state-own] [["L", "E", 6], ["L", "B", 4], ["L", "K", 2], ["L", "C", 1], ["L", "A", 5], ["E", "B", 3], ["E", "K", 1], ["E", "C", 2], ["E", "A", 6], ["B", "K", 5], ["B", "C", 4], ["B", "A", 3], ["K", "C", 6], ["K", "A", 2], ["C", "A", 1]]
[History] [suggest(["L", "E"]), agree-inner(["L", "E"]), inform("coins between L and B, coins between L and A, coins between L and K, coins between L and C"), ask("coins between L and E, coins between L and B, coins between L and K, coins between L and A, coins between L and C"), agree-outer(["L","E"]), visit("E"), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and C, coins between E and K, coins between E and B"), ask("coins between E and A, coins between E and C, coins between E and K, coins between E and B"), agree-outer(["E","K"]), agree-outer(["E", "A"]), reject(["E", "K"]), agree-inner(["E", "A"]), visit("A"), suggest(["A", "B"]), agree-inner(["A", "B"]), suggest(["B", "K"]), agree-inner(["B", "K"]), inform("coins between E and K"), ask("coins between A and B, coins between B and K")]
[Observation] that would be perfect for me because i can get 6 light coins between the bathroom and attic! from the bathroom, i can get 2 coins to the kitchen. From the kitchen, we would go to the children's room and then back to the living room, right? The first half of that path would give me 3 more light coins, and the second half 6 more light coins.

[Thought-DRAFT] The user agrees with my suggestion and says they can get 6 light coins going to the bathroom. The user agrees to then go into the kitchen, where they can collect 2 coins, followed by the children's room, with 3 more light coins, and finally back to the living room, to collect 6 more light coins.
[Action]: agree-outer(["A", "B"]), visit("B"), agree-outer(["B", "K"]), visit("K"), agree-outer(["K", "C"]), agree-outer(["C", "L"]), agree-inner(["K", "C"]), visit("C"), agree-inner(["C", "L"]), visit("C"), solve(["L", "E", "A", "B", "K", "C", "L"]), end(["L", "E", "A", "B", "K", "C", "L"])
[Message]: Okay great, that works well! Then it's settled and we are done - the path we decided on is living room --> empty room --> attic --> bathroom --> kitchen --> children's room --> living room. If my calculations are correct, we should be getting 52 coins each as our reward, which seems pretty decent!
---
are you ready?

The house consists of the following rooms:
The house consists of the following rooms:
{"\n".join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the light world being:
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

    USER_proxy_light = f'''You are playing a game with a partner where you each control a magical character. In the game, an evil wizard separated you and your partner into two different dimensions: both of you find yourselves in the same house, but you are in the light world, while your partner is in the light world. You are able to communicate through written text only. The scene for both of you consists of 4 rooms all connected to each other by hallways in which you will find various amounts of coins. In order to break the curse and escape, you and your partner have to visit each of the 4 rooms once and return to the room where you started. For this to work, you must travel in parallel and visit the same rooms at the same time. On your way, you are both individually collecting coins: you collect light coins, and your partner collects Ghost coins. Because of the wizard's curse, the light and Ghost coins only show up if you're both simultaneously going through the same hallway, so make sure to coordinate your paths. Your score is the sum of both your and your partner's collected coins - you must work together to maximize this. Once you've escaped the split dimension, you and your partner will each be rewarded the full sum of your total coin collection. Your goals are to escape and collect as big of a reward as possible. Chat with your partner to decide on the best way to proceed.
Chat with your partner trying to find the best way around the house so that all criteria are met; you have a maximum of 200 tokens per Message. When you are done with the game and wish to submit your path, generate a message containing "end(x)", whereby x represents your final path in the form of a Python list of strings.

You will get an input containing the following:
[World-state-own] - the state of your own world, including the coin distribution
[History] - what Actions you decided to take previously. This should inform your choice of output.
[Observation] - the Message that the user sent.

You will generate an output containing different kinds of thought, actions and a message to be sent to the user. The elements of your reply will be indicated by the flag in square brackets ([Flag]). The following are allowed kinds of thought:
- [Thought-DRAFT] - This flag signifies part of the output in which you try to find the best path with the information you are given, while making sure to visit all rooms only once and return to the starting room. You should always start with this thought. If the [Thought-DRAFT] is successful, you should indicate this by generating a solve(x) Action, whereby x is a Python list of strings referring to the rooms in the order to be visited. If the [Thought-DRAFT] was not successful, meaning that a path that corresponds to the constraints has not been generated, you will generate another thought: [Thought-MISSING]. 
- [Thought-MISSING] - If you could not find a valid path in [Thought-DRAFT], you will generate this kind of thought in which you identify why you couldn't solve the puzzle in the previous step.
Moreover, when both you and the other player have agreed on a path and you are ready to end the game, indicate this by generating an [Action] end(x), whereby x is a Python list of strings (of length 1) referring to the rooms in the order to be visited.
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
    - "visit(x)" should only be generated if you generate an "agree-inner(x)" with an "agree-outer(x)" OR when you generate an "agree-inner(x)" to a previous user suggestion OR if you generate an "agree-outer(x)" to your previous suggestion
    - "inform(x)" should always be based on the coin distribution in [World-state-own] (when asked for coin distribution)
- [Message] - each output must conclude with a Message to be shown to the user, depending on the generated thoughts and Actions.
Make sure to not format the output in any other way.

Here is an example setup:
The house consists of the following rooms:
- a well-lit living room (L)
- a dark, spooky bathroom (B)
- an empty room with no windows (E)
- a pristine kitchen (K)
- a children's room (C)
- an attic (A)
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

[World-state-own] [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[History] []
[Observation] Hello there! Let’s get started! It seems that from the living room, it would be best if I went to the empty room as I could get 6 ghost coins. The other paths that have a similar amount of coins would be to the attic, where I could get 5 ghost coins, or to the bathroom, where I'd collect 4 ghost coins. What do you think of this? How many coins could you collect in this way?

[Thought-DRAFT]: This is the start of the game. I know the light coin distribution. The user suggests going to the empty room, to get 6 ghost coins. This would be good in the light world as well, because I would collect 5 light coins, for a total of 11 coins. My best move from the living room would be through the children's room, but the user didn't suggest that.
[Action]: agree-outer(["L", "E"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and E, coins between L and C, coins between L and B, coins between L and A")
[Message]: Oh, I see! Okay, that would be quite good for me as well because going to the empty room gives me 5 light coins. I would get the most coins if we go to the children's room, i can get 6 light coins there. Regarding the bathroom, I can only get 3 light coins, and to the attic I can get only 2 light coins.


[World-state-own] [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[History] [agree-outer(["L", "E"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and E, coins between L and C, coins between L and B, coins between L and A")]
[Observation] That sounds good, then let's start by going to the empty room! From there, I could get 6 more ghost coins if we go to the attic. How does this route look for you? How many light coins would you collect there?

[Thought-DRAFT]: The user says that they can get 6 more ghost coins if we then went to the attic from the empty room. This would not be my favorite move, as I can only get 3 light coins on this path. However, I can get 6 light coins on the way to the kitchen. If the user can get 3 or more coins to the kitchen, we should go there, but otherwise, we can stick to the attic.
[Thought-MISSING]: I do not know the full ghost coin distribution from the empty room, so I do not know what would be best to do next.
[Action]: suggest(["E", "K"]), agree-inner(["E", "K"]), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and K"), ask("coins between E and K")
[Message]: I can get only 3 light coins on the way to the attic, but I can get 6 coins on the way to the kitchen. If you can get 3 or more ghost coins on the way to the kitchen, we should pick that path; otherwise, let's go to the attic.


[World-state-own] [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[History] [agree-outer(["L", "E"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and E, coins between L and C, coins between L and B, coins between L and A"), suggest(["E", "K"]), agree-inner(["E", "K"]), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and K"), ask("coins between E and K")]
[Observation] Ok, then let's go to the attic, since I can get only 1 ghost coin if we were to go to the kitchen. From the attic, it would be best for me to go to the bathroom and then from the bathroom to the kitchen. How would this path look for you? Do you have an alternative suggestion?

[Thought-DRAFT]: The user says they can collect only 1 coin on the way to the kitchen, meaning that we should first go to the attic. From there, the user suggests going to the bathroom and then to the kitchen. Going to the bathroom from the attic is my best path from this point, since I can get 6 light coins. From the bathroom to the kitchen, I would collect only 2 light coins. There is only one room that we hadn't visited, the children's room - from the kitchen, I could get 3 light coins, and then our path would go back to the living room, where I could collect 6 more light coins.
[Thought-MISSING]: I do not know how many ghost coins can be found between the attic and bathroom, or between the bathroom and kitchen. I also don't know how many ghost coins are between the kitchen and children's room, or living room and children's room.
[Action]: agree-outer(["E", "A"]), visit("A"), agree-outer(["A", "B"]), agree-inner(["A", "B"]), visit("B"), agree-outer(["B", "K"]), agree-inner(["B","K"]), visit("K"), suggest(["K", "C"]), agree-inner(["K", "C"]), suggest(["C", "L"]), agree-inner(["C", "L"]), solve(["L", "E", "A", "B", "K", "C", "L"])
[Message]: That would be perfect for me because i can get 6 light coins between the bathroom and attic! From the bathroom, I can get 2 coins to the kitchen. From the kitchen, we would go to the children's room and then back to the living room, right? The first half of that path would give me 3 more light coins, and the second half 6 more light coins.


[World-state-own] [["L", "E", 5], ["L", "B", 3], ["L", "K", 1], ["L", "C", 6], ["L", "A", 2], ["E", "B", 4], ["E", "K", 6], ["E", "C", 1], ["E", "A", 3], ["B", "K", 2], ["B", "C", 5], ["B", "A", 6], ["K", "C", 3], ["K", "A", 4], ["C", "A", 1]]
[History] [agree-outer(["L", "E"]), agree-inner(["L", "E"]), visit("E"), inform("coins between L and E, coins between L and C, coins between L and B, coins between L and A"), suggest(["E", "K"]), agree-inner(["E", "K"]), suggest(["E", "A"]), agree-inner(["E", "A"]), inform("coins between E and A, coins between E and K"), ask("coins between E and K"), agree-outer(["E", "A"]), visit("A"), agree-outer(["A", "B"]), agree-inner(["A", "B"]), visit("B"), agree-outer(["B", "K"]), agree-inner(["B","K"]), visit("K"), suggest(["K", "C"]), agree-inner(["K", "C"]), suggest(["C", "L"]), agree-inner(["C", "L"]), solve(["L", "E", "A", "B", "K", "C", "L"])]
[Observation]: Okay great! Then it's settled and we are done - the path we decided on is living room --> empty room --> attic --> bathroom --> kitchen --> children's room --> living room. If my calculations are correct, we should be getting 52 coins each as our reward, which seems pretty decent!

[Thought-DRAFT]: The user agrees with my suggestion. The user agrees to then go into the kitchen, followed by the children's room, and finally back to the living room.
[Action]: agree-outer(["K", "C"]), visit("C"), agree-outer(["C", "L"]), visit("L"), end(["L", "E", "A", "B", "K", "C", "L"])
[Message]: Yay great, that means we're done!
---
are you ready?

The house consists of the following rooms:
{"\n".join(f"- {desc}" for desc in room_descriptions)}

All rooms are connected by hallways, with the coin distribution in the light world being:
{hallway_text}

You start in the living room. Remember, in order to escape you must both follow the same path, and enter each room only once before returning to the living room! In the end, the larger your total sum of coins, the higher the reward you both get.'''
    return USER_proxy_light