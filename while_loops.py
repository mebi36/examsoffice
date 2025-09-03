result = 0
# we will use a sentinel value to exit the loop
while True:
    user_input = input("Enter number or `q` to stop: ")
    if user_input == "q":
        break
    user_input = float(user_input)
    if user_input == 10:
        continue
    result += user_input
print(f"Result = {result}")

