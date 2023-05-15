
query = input("Please enter your query: ")

words = query.split()

with open('main_index.txt', 'r+') as f:
    line_num = 0
    found = 0
    for word in words:
        left = 1
        f.seek(0)
        right = int(f.readline()) + 1
        while left <= right:
            mid = (left + right) // 2
            f.seek(mid)
            text = f.readline()
            print(f'ori: {text}')
            print(text.split()[0])
            if f.readline().split()[0] == word:
                found = 1
                line_num = mid
            elif f.readline().split()[0] < word:
                left = mid + 1
            else:
                right = mid - 1
        if not found:
            line_num = left
    print(line_num)

