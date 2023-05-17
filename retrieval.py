import json
import time

query = ''
print("   ########## ##########")
print("WELCOME TO OUR SEARCH ENGINE")
while True:
    query = input("> ").lower()
    start_time = time.time()
    if query == '!quit':
        break
    # sort words for query
    words = sorted(query.split())

    byte_pos = dict()
    with open('main_index.txt', 'r+') as f:
        text = f.readline()
        pointer = 0
        last = text.split()[1]
        while text != '' and (pointer < len(words)):
            token = text.split()[0]

            # Comparison between tokens, save the byte position
            if token == words[pointer]:
                byte_pos[words[pointer]] = text.split()[1]
                pointer += 1
                continue
            elif token > words[pointer]:
                byte_pos[words[pointer]] = last
                pointer += 1
                continue
            last = text.split()[1]
            text = f.readline()
        # If not found, all append last position
        while pointer < len(words):
            byte_pos[words[pointer]] = last
            pointer += 1
    # List of docID sets
    ID_sets = set()
    # print(byte_pos)
    f2 = open('index.txt')
    for k, v in byte_pos.items():
        # print(f"inside {k},{v}")
        f2.seek(int(v))
        token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        # print(token_tuple)
        while len(token_tuple) != 0 and token_tuple[0] < k:
            # print(token_tuple[0],k)
            # print("1")
            token_tuple = tuple(f2.readline().rstrip('\n').split('---'))
        if token_tuple[0] == k:
            corr_dict = eval(token_tuple[1]).keys()
            # Intersecting while adding to the set
            # print(corr_dict)
            if len(ID_sets) == 0:
                ID_sets = set(corr_dict)
            else:
                ID_sets = ID_sets.intersection(set(corr_dict))
        else:
            ID_sets = set()
            break
        # print(token_dt)
    f2.close()
    # print(ID_sets)

    if len(ID_sets) != 0:
        print(f"{len(ID_sets)} Results in ", end="")
        print("%s ms:" % round((time.time() - start_time) * 1000, 2))
        # generate URLs
        f = open('urls.json')
        ID_dict = json.load(f)
        rank = 1
        for i in ID_sets:
            print(f'{rank}: {ID_dict[str(i)]}')
            rank += 1
            if rank > 10:
                break
        f.close()
    else:
        print('No Result')
        print("--- %s ms ---" % round((time.time() - start_time) * 1000, 2))
