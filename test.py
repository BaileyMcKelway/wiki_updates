que = []

hour = 0

cycle = 1
rotation = 0
while True:

    if len(que) == 5:
        cur = que.pop(0)

    que.append(str(rotation) + '-' + str(cycle))

    if cycle == 5:
        cycle = 0
        rotation += 1

    cycle += 1
