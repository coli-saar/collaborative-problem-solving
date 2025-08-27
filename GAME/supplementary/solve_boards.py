import json

import tsp_utils
from AGENTS.prompts_problem_solving import BotInstance

# import jsbeautifier


# options = jsbeautifier.default_options()
# options.preserve_newlines = False
# options.keep_array_indentation = False
# options.brace_style = "collapse"

for n in range(4, 7):
    boards = json.load(open(f"boards/boards_{n}.json"))

    optimal = {}

    for i in range(1, 7):
        setup = boards[str(i)]
        bot = BotInstance(
            BASE_PROMPT="", MODEL="", SEED=0, MAXTOKENS=0, BOARD=setup["BOT"]
        )
        bot.update_total_board(setup["USER"])

        g = tsp_utils.board_to_graph(bot.total_board)
        tsp_utils.validate_graph(g)
        IBPS, IBC = tsp_utils.solve(g, get_all_tours=True)

        IBPS = [tour + [tour[0]] for tour in IBPS]

        optimal[i] = {
            "BOT": setup["BOT"],
            "USER": setup["USER"],
            "OPTIMAL": IBPS + [IBC],
        }

    with open(f"boards/boards_{n}.json", "w") as f:
        f.write("{\n")
        for i in range(1, 7):
            f.write(f'\t"{i}": {{\n')
            f.write(f'\t\t"BOT": {json.dumps(optimal[i]["BOT"])},\n')
            f.write(f'\t\t"USER": {json.dumps(optimal[i]["USER"])},\n')
            f.write(f'\t\t"OPTIMAL": {json.dumps(optimal[i]["OPTIMAL"])}\n')
            f.write(f"\t}}{',' if i != 6 else ''}\n")
        f.write("}\n")
