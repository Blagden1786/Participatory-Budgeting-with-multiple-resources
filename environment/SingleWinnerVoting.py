candidates = ["Rishi", "Nigel", "Keir", "Ed", "Donald", "Kamala"]


def gatherVotes(candidates: list):
    votes = [0 for i in candidates]
    while True:
        print(candidates)
        vote = input("Select the candidate you want: ")

        if vote == "x":
            break
        else:
            votes[int(vote)] += 1
    return votes


def get_winner(votes: list):
    max_num_votes = max(votes)

    winners = []
    for i in range(len(votes)):
        # Gather the candidates who all have the most votes
        if votes[i] == max_num_votes:
            winners.append(i)
    return winners


def run_election(candidates: list):
    # Voting stage
    votes = gatherVotes(candidates)

    # Calculate winner(s)
    winners = get_winner(votes)

    print(f"The winner of the election is: {[candidates[i] for i in winners]}")


run_election(candidates)
