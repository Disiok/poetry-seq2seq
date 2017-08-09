import random

letters = list("abcdefghijklmnopqrstuvxyz\n")

for i in range(10):
    for i in range(15):
        print(random.choice(letters), end="", flush=True)
