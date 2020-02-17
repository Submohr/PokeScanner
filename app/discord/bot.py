import os
import discord
from app.data import data, helpers
from app.pokemon import constants
from config import Config
from datetime import datetime

logger = Config.LOGGER
client = discord.Client()


def get_client():
    return client


@client.event
async def on_read():
    print("Loaded.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author == client.get_user(509192464456876032):
        # other bot
        return
    logger.debug(f"Received message; {message.content}")

    # this isn't the right way, really, but will keep it for speed purposes
    if str(message.channel) == Config.DISCORD_SIZE_CHANNEL:
        msg_dict = parse_size_message(message, command=False)
    else:
        msg_dict = parse_generic_command(message)

    msg = msg_dict["msg"]

    if msg is not None:
        await send_message(message, msg)


def parse_size_message(message, command=True):
    if command:
        content = message.content[1:].strip()
    else:
        content = message.content
    params = content.split()
    if len(params) == 0:
        return {"code": 1, "msg": f"{message.author.mention}, please include a Pokemon name in your query."}

    pokes = generate_pokemon_list(params)
    size_messages = []
    for poke in pokes:
        size_messages.append(create_size_message(poke))
    msg = "\n\n".join(size_messages)

    return {"code": 0, "msg": msg}


def default_message(message, command=False):
    return {"code": 0, "msg": f"Sorry, {message.author.mention}, I didn't understand that request."}


def parse_generic_command(message):
    switch = {
        's': parse_size_message
    }
    func = switch.get(message.content[0].lower(), default_message)
    return func(message, command=True)


async def send_message(message, pre_msg):
    msg = f"{message.author.mention},\n" + pre_msg
    max_length = Config.DISCORD_MAX_MESSAGE_LENGTH
    count = 0
    if Config.DISCORD_DEBUG_MODE:
        channel = client.get_channel(Config.DISCORD_DEBUG_CHANNEL)
    else:
        channel = message.channel
    while (len(msg)) > max_length and count < 70:
        last_break = msg[:max_length].rfind('\n\n')
        cur_msg = msg[:last_break]
        await channel.send("\n\n" + cur_msg)
        msg = msg[last_break:]
        count += 1

    await channel.send(msg)


def create_size_message(pokemon):
    if pokemon.startswith("!"):
        return f"I don't recognize {pokemon[1:]} as a Pokemon name."
    msg = ""
    try:
        extremes = data.get_all_extremes(pokemon.capitalize(),loose=False, include_null_data=2)
        print(extremes)
        heavy = helpers.weight_int_to_str(extremes['self'][0])
        tall = helpers.height_int_to_str(extremes['self'][1])
        light = helpers.weight_int_to_str(extremes['self'][2])
        small = helpers.height_int_to_str(extremes['self'][3])
        msg = msg + f"{pokemon:<16} - Light: **{light: >10}**    Small: **{small: >7}**    Heavy: **{heavy: >10}**" \
                    f"    Tall: **{tall: >7}**"
        try:
            time = extremes['timestamp']
            formatted_time = datetime.strftime(time,"%m-%d-%Y")
            msg = msg + f"  ::: {formatted_time:<11}"
        except:
            pass
        if extremes["evos"] is not None:
            heavies = []
            talls = []
            lights = []
            smalls = []
            for evo in extremes["evos"].values():
                heavies.append(evo[0])
                talls.append(evo[1])
                lights.append(evo[2])
                smalls.append(evo[3])
            evo_heavy =  helpers.weight_int_to_str(min(heavies))
            evo_tall = helpers.height_int_to_str(min(talls))
            evo_light =  helpers.weight_int_to_str(max(lights))
            evo_small = helpers.height_int_to_str(max(smalls))
            msg = msg + f"\n{'Evos':<16} - Light: **{evo_light: >10}**    Small: **{evo_small: >7}**    " \
                        f"Heavy: **{evo_heavy: >10}**    Tall: **{evo_tall: >7}**"


    except:
        msg = f"{pokemon} - Cannot find data."
    return msg


def generate_pokemon_list(params):
    ret = []
    i = 0
    found_count = 0
    while i < len(params):
        if i > 0:
            if len(ret) == found_count:
                ret.append(f"!{params[i - 1]}")
            found_count = len(ret)
        try:
            search_term = params[i].capitalize()
            if search_term in ["Alola", "Alolan"]:
                try:
                    i = i + 1
                    search_term = params[i].capitalize()
                    if search_term in constants.ALOLAN_NAMES:
                        ret.append(f"Alolan {search_term}")
                    else:
                        for name in constants.ALOLAN_NAMES:
                            if search_term in name:
                                ret.append("Alolan " + name.capitalize())
                except:
                    ret.extend([f"Alolan {name}" for name in constants.ALOLAN_NAMES])
            elif search_term in ["Galar", "Galarian"]:
                try:
                    i = i + 1
                    search_term = params[i].capitalize()
                    if search_term in constants.GALARIAN_NAMES:
                        ret.append(f"Galarian {search_term}")
                    else:
                        for name in constants.GALARIAN_NAMES:
                            if search_term in name:
                                ret.append("Galarian " + name.capitalize())
                except:
                    ret.extend([f"Galarian {name}" for name in constants.GALARIAN_NAMES])
            else:
                if search_term in constants.POKEMON_NAMES:
                    if search_term == "Castform":
                        for nm in constants.CASTFORM_NAMES:
                            ret.append(" ".join(w.capitalize() for w in nm.split()))
                    else:
                        ret.append(search_term)
                elif search_term in constants.ALOLAN_SHORTFORMS:
                    ret.append(f"Alolan {search_term[1:].capitalize()}")
                elif search_term in constants.GALARIAN_SHORTFORMS:
                    ret.append(f"Galarian {search_term[1:].capitalize()}")
                elif search_term in constants.CASTFORM_SHORTFORMS:
                    ret.append(" ".join(w.capitalize for w in constants.
                                        CASTFORM_NAMES[constants.CASTFORM_SHORTFORMS.index(search_term)].split()))
                else:
                    for name in constants.POKEMON_NAMES:
                        if search_term in name:
                            if name == "Castform":
                                for nm in constants.CASTFORM_NAMES:
                                    ret.append(" ".join(w.capitalize() for w in nm.split()))
                            else:
                                ret.append(name)
                    if search_term in "Mime":
                        ret.append("Mr. mime")
                    for name in constants.ALOLAN_SHORTFORMS:
                        if search_term in name:
                            ret.append(f"Alolan {name[1:].capitalize()}")
                    for name in constants.GALARIAN_NAMES:
                        if search_term in name:
                            ret.append(f"Galarian {name[1:].capitalize()}")

            i = i + 1
        except:
            i = i + 1
            continue

    if len(ret) == found_count:
        ret.append(f"!{params[-1]}")

    return remove_dupes(ret)


def remove_dupes(i: list):
    seen = set()
    return [item for item in i if not (item in seen or seen.add(item))]
