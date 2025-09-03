# 1, get NIN number
# 2, confirm that NIN is valid
# 3, confirm that the person has not voted before
# 4, collect the person's vote and add to the
# appropriate candidate

verified_voters = []
obi_vote_count = 0
atiku_vote_count = 0
abacha_vote_count = 0


def get_nin_number():
    """Return the NIN number of the voter."""
    nin = input("Please enter your NIN: ")
    return nin

def nin_is_valid(nin):
    """Check whether `nin` is valid.
    A valid nin will have:
    - a length of 10
    - should only contain numbers***
    """
    if len(nin) == 10:
        return True
    else:
        return False

def voter_already_verified(nin):
    if nin in verified_voters:
        return True
    else:
        return False

def get_voters_selection():
    vote = int(input(
        "1 > Atiku\n"
        "2 > Obi\n"
        "3 > Abacha\n"
        "Enter Selection: "
    ))
    return vote

def update_verified_voters_list(nin):
    verified_voters.append(nin)

def update_vote_count(vote):
    global atiku_vote_count
    global obi_vote_count
    global abacha_vote_count

    if vote == 1:
        atiku_vote_count += 1
        print("A vote for Atiku")
    elif vote == 2:
        obi_vote_count += 1
        print("A vote for Obi")
    elif vote == 3:
        abacha_vote_count += 1
        print("A vote for Abacha")
    else:
        print("Invalid vote!!!")

def handle_single_voter():
    nin = get_nin_number()
    if nin_is_valid(nin):
        if voter_already_verified(nin):
            print("Voter already verified and voted!")
        else:
            voter_selection = get_voters_selection()
            update_vote_count(voter_selection)
            update_verified_voters_list(nin)
    else:
        print("Invalid NIN!")

def get_winner():
    winner_name = "Null"
    winner = 0
    if atiku_vote_count > 0:
        winner = atiku_vote_count
        winner_name = "Atiku"
    if obi_vote_count > 0:
        if obi_vote_count > winner:
            winner = obi_vote_count
            winner_name = "Obi"
        elif obi_vote_count == winner:
            winner_name = "Tie"
    if abacha_vote_count > 0:
        if abacha_vote_count > winner:
            winner = abacha_vote_count
            winner_name = "Abacha"
        elif abacha_vote_count == winner:
            winner_name = "Tie"
    return winner_name

def start_election():
    while True:
        user_input = input(
            "Press any button to continue. Enter q to end voting: "
        )
        if user_input == "q":
            break
        else:
            handle_single_voter()
    print(
        f"Election results:\n"
        f"Atiku: {atiku_vote_count}\n"
        f"Obi: {obi_vote_count}\n"
        f"Abacha: {abacha_vote_count}\n"
        f"The winner is: {get_winner()}"
    )

start_election()