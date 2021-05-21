import re
import requests


async def message_analyzer(incoming_message: str, binance_client, kucoin_client, symbol_dictionary: dict,
                           trade_pair: str):
    if binance_client is not None:
        binance_trade_flag = True
    else:
        binance_trade_flag = False

    if kucoin_client is not None:
        kucoin_trade_flag = True
    else:
        kucoin_trade_flag = False

    selected_symbol = ""
    processed_message = re.sub(r'[^A-Za-z0-9 ]+', '', incoming_message)
    splitted_message = incoming_message.replace("<", "")
    splitted_message = splitted_message.replace(">", "")
    splitted_message = splitted_message.split()
    processed_splitted_message = processed_message.split()
    indicators = ["#", "$"]
    indicator_index = 0

    def finder(find):
        return [wanted_word for wanted_word in splitted_message if find in wanted_word][0]

    """def find_in_binance_url(search_in, is_single_word):
        if not search_in.find("binance.com") == -1:
            if not is_single_word:
                w = finder("binance.com")
            else:
                w = search_in
            t = w.rsplit("/", 1)[-1]
            if not t.find("?layout=basic") == -1:
                tsl = t.replace("?layout=basic", "")
            else:
                tsl = t
            ts = tsl.replace("_", "").upper()
            if ts in symbol_dictionary:
                return ts
            else:
                return ""

    def find_in_kucoin_url(search_in, is_single_word):
        if not search_in.find("trade.kucoin.com") == -1:
            if not is_single_word:
                w = finder("trade.kucoin.com")
            else:
                w = search_in
            ts = w.rsplit("/", 1)[-1]
            ts = ts.upper()
            if ts in symbol_dictionary:
                return temp_symbol
            else:
                return """""

    while indicator_index < len(indicators):
        if not incoming_message.find(indicators[indicator_index]) == -1:
            word = finder(indicators[indicator_index])
            indicator_loc = word.index(indicators[indicator_index])
            if binance_trade_flag:
                temp_symbol = word[indicator_loc + 1:].upper() + trade_pair
            elif kucoin_trade_flag:
                temp_symbol = word[indicator_loc + 1:].upper() + "-" + trade_pair
            else:
                return ""
            if temp_symbol in symbol_dictionary:
                selected_symbol = temp_symbol
                indicator_index += 1
            else:
                indicator_index += 1
        else:
            indicator_index += 1

    if selected_symbol == "":
        current_item = 0
        while current_item < len(processed_splitted_message):
            if binance_trade_flag:
                temp_symbol = processed_splitted_message[current_item].upper() + trade_pair
            elif kucoin_trade_flag:
                temp_symbol = processed_splitted_message[current_item].upper() + "-" + trade_pair
            else:
                return ""
            if not temp_symbol.find("BUY") == -1:
                temp_symbol = ""
            if not temp_symbol.find("NEAR") == -1:
                temp_symbol = ""
            if not temp_symbol.find("GO") == -1:
                temp_symbol = ""
            if temp_symbol in symbol_dictionary:
                selected_symbol = temp_symbol
                current_item += 1
            else:
                current_item += 1
    else:
        pass

    """if selected_symbol == "":
        selected_symbol = find_in_binance_url(incoming_message, is_single_word=False)

    if selected_symbol == "":
        selected_symbol = find_in_kucoin_url(incoming_message, is_single_word=False)

    if selected_symbol == "":
        protocols = ["http://", "https://"]
        for protocol in protocols:
            if not incoming_message.find(protocol) == -1:
                word = finder(protocol)
                session = requests.Session()
                resp = session.head(word, allow_redirects=True)
                word_url = resp.url
                selected_symbol = find_in_binance_url(word_url, is_single_word=True)
                if selected_symbol == "":
                    selected_symbol = find_in_kucoin_url(word_url, is_single_word=True)"""

    if selected_symbol == "":
        if not incoming_message.find("/") == -1:
            indicator_count = incoming_message.count("/")
            indicator_index = 0
            while indicator_index < indicator_count:
                wordlist = [wanted_word for wanted_word in splitted_message if "/" in wanted_word]
                word = wordlist[indicator_index]
                if binance_trade_flag:
                    temp_symbol = word.replace("/", "")
                elif kucoin_trade_flag:
                    temp_symbol = word.replace("/", "-")
                else:
                    return ""
                temp_symbol = temp_symbol.upper()
                if temp_symbol in symbol_dictionary:
                    selected_symbol = temp_symbol
                    break
                else:
                    indicator_index += 1

    return selected_symbol
