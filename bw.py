import sys

class BlockWorldProblem:
    def __init__(self, start_state, target_state):
        self.start_state = start_state
        self.target_state = target_state

    # Ελέγχει αν η τρέχουσα κατάσταση είναι η επιθυμητή κατάσταση
    def check_goal(self, current_state):
        return self.target_state.issubset(current_state)

    # Δημιουργεί τις επόμενες πιθανές καταστάσεις από την τρέχουσα
    def generate_next_states(self, current_state):
        possible_states = []
        for block in current_state:
            if block.startswith('ON'):
                block_a, block_b = block[3:].split()
                if f"CLEAR {block_a}" in current_state and f"CLEAR {block_b}" in current_state:
                    new_state = current_state.copy()
                    new_state.remove(block)
                    new_state.add(f"ON {block_a} TABLE")
                    possible_states.append(new_state)
        return possible_states

    # Υπολογίζει την ευρετική συνάρτηση (πόσα βήματα μένουν)
    def heuristic_function(self, current_state):
        return len(self.target_state - current_state)

    # Αναζήτηση πρώτα σε πλάτος (breadth-first search)
    def breadth_first_search(self):
        queue = [self.start_state]
        visited = set()
        while queue:
            state = queue.pop(0)
            if self.check_goal(state):
                return state
            visited.add(frozenset(state))
            for next_state in self.generate_next_states(state):
                if frozenset(next_state) not in visited:
                    queue.append(next_state)
        return None

    # Αναζήτηση πρώτα σε βάθος (depth-first search)
    def depth_first_search(self):
        stack = [self.start_state]
        visited = set()
        while stack:
            state = stack.pop()
            if self.check_goal(state):
                return state
            visited.add(frozenset(state))
            for next_state in self.generate_next_states(state):
                if frozenset(next_state) not in visited:
                    stack.append(next_state)
        return None

    # Αναζήτηση πρώτα στο καλύτερο (best-first search)
    def best_first_search(self):
        priority_queue = [(self.heuristic_function(self.start_state), self.start_state)]
        visited = set()
        while priority_queue:
            _, state = priority_queue.pop(0)
            if self.check_goal(state):
                return state
            visited.add(frozenset(state))
            for next_state in self.generate_next_states(state):
                if frozenset(next_state) not in visited:
                    priority_queue.append((self.heuristic_function(next_state), next_state))
                    priority_queue.sort()
        return None

    # Αναζήτηση με τον αλγόριθμο Α*
    def a_star_search(self):
        priority_queue = [(self.heuristic_function(self.start_state), 0, self.start_state)]
        costs = {}
        while priority_queue:
            _, current_cost, state = priority_queue.pop(0)
            if self.check_goal(state):
                return state
            costs[frozenset(state)] = current_cost
            for next_state in self.generate_next_states(state):
                new_cost = current_cost + 1
                if frozenset(next_state) not in costs or new_cost < costs[frozenset(next_state)]:
                    priority_queue.append((new_cost + self.heuristic_function(next_state), new_cost, next_state))
                    costs[frozenset(next_state)] = new_cost
                    priority_queue.sort()
        return None

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python bw.py <method> <input_file> <output_file>")
        sys.exit(1)

    search_method = sys.argv[1]
    input_filename = sys.argv[2]
    output_filename = sys.argv[3]

    # Διαβάζει την είσοδο από το αρχείο
    with open(input_filename, "r") as file:
        file_lines = file.readlines()

    initial = set()
    goal = set()
    reading_init = False
    reading_goal = False

    for line in file_lines:
        line = line.strip().upper()
        if line.startswith(":INIT"):
            reading_init = True
        elif line.startswith(":GOAL"):
            reading_init = False
            reading_goal = True
        elif line.startswith(")"):
            reading_goal = False
        elif reading_init:
            if line.startswith("("):
                initial.add(line[1:-1])
        elif reading_goal:
            if line.startswith("("):
                goal.add(line[1:-1])

    problem = BlockWorldProblem(initial, goal)

    # Επιλέγει τον αλγόριθμο αναζήτησης
    if search_method == "depth":
        result = problem.depth_first_search()
    elif search_method == "breadth":
        result = problem.breadth_first_search()
    elif search_method == "best":
        result = problem.best_first_search()
    elif search_method == "astar":
        result = problem.a_star_search()
    else:
        print("Invalid method. Choose from: depth, breadth, best, astar.")
        sys.exit(1)

    # Γράφει τη λύση στο αρχείο εξόδου
    with open(output_filename, "w") as output_file:
        if result:
            output_file.write("Solution:\n")
            for step in result:
                output_file.write(step + "\n")
        else:
            output_file.write("No solution found.")
