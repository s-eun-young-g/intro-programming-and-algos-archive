"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import sys

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS

# helper functions

def update_cnf(formula, var, t_f):
    """
    Update formula given a variable and a True/False
    value to set it to. Iterates through formula and does
    two things: remove a clause once it is satisifed (i.e.
    the literal (var, t_f) appears in the clause) or
    removes the opposite of a literal from a clause (i.e.
    removes (var, not t_f) from all clauses)

    Arguments:
        formula: current formula
        var: variable (as a string)
        t_f: True or False (boolean)

    Returns:
        an updated formula according to the operation
        described above
    """
    new_formula = []
    for clause in formula:
        if (var, t_f) in clause:
            # clause is satisfied if literal is in it
            # so don't include it in the new cnf
            continue
        else:
            # remove opposite of literal from clause
            # add rest of clause to new cnf
            new_clause = [literal for literal in clause if literal != (var, not t_f)]
            new_formula.append(new_clause)
            
    return new_formula

def find_unit_clauses(formula):
    """
    Iterates through a formula and returns
    all the unit clauses as a set
    """
    unit_clause_set = set()
    for clause in formula:
        if len(clause) == 1:
            unit_clause_set.add(clause[0])
    return unit_clause_set

def recur_combinations(students_list, n):
    """
    Recursive helper function that generates all
    possible combinations of students who
    prefer a room of length of the capacity of the room + 1.
    This will later be used to generate clauses stating
    at least 1 student in the list cannot be in the room.
    """
    if n == 0:
        # base case
        return [[]]
    if len(students_list) < n:
        # edge case: n is greater than length
        # of student list, so no
        # combinations can be created
        return []
    combinations = []
    for i in range(len(students_list)):
        first = students_list[i] # pick one student
        rest = students_list[i + 1:]
        # recursively generate combinations between first student
        # and rest of students
        sub_combinations = recur_combinations(rest, n - 1)
        for sub_combination in sub_combinations:
            combinations.append([first] + sub_combination)
    return combinations


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> T, F = True, False
    >>> x = satisfying_assignment([[('a', T), ('b', F), ('c', T)]])
    >>> x.get('a', None) is T or x.get('b', None) is F or x.get('c', None) is T
    True
    >>> satisfying_assignment([[('a', T)], [('a', F)]])
    """
    
    def recur_satisfy(formula, assignments):
    
        # base case: formula is empty or contains any empty lists
        if not formula: 
            return assignments
        # contradiction: formula contains an empty clause
        if any(clause == [] for clause in formula):
            return None
        
        # get an initial set of unit clauses
        units = find_unit_clauses(formula) 

        # first, iterate through all unit clauses that arise
        while units:
            literal = units.pop()
            var, t_f = literal
            # check if var is already
            # in assignments list
            if var in assignments:
                # if so, check if value
                # is consistent
                if assignments[var] != t_f:
                    return None
                else:
                    continue
            # unit clauses: var must have given val
            assignments[var] = t_f
            formula = update_cnf(formula, var, t_f)
            # if formula is empty, return assignment list
            if not formula: 
                return assignments
            # check if we've found a contradiction
            if any(clause == [] for clause in formula):
                return None
            # update unit clause set with new unit clause arisen
            units = units | find_unit_clauses(formula)

        # get remaining variables list
        remaining_vars = set(literal[0] for clause in formula for literal in clause)
       
        if not remaining_vars: # if no more remaining vars
            return assignments
        var = next(iter(remaining_vars)) # get next var arbitrarily
        for t_f in [True, False]: # two options
            # make copy in case of needing to backtrack
            assignments_copy = assignments.copy() 
            assignments_copy[var] = t_f
            new_formula = update_cnf(formula, var, t_f)
            result = recur_satisfy(new_formula, assignments_copy)
            if result is not None:
                return result
        return None
    
    result = recur_satisfy(formula, {})
    return result


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    formula = []

    # constraint 1: each student is assigned to a room they prefer
    # aka each student is not assigned to a room they DON'T prefer
    for student in student_preferences:
        clause = []
        for room in student_preferences[student]:
            # conventional variable name
            var = f'{student}_{room}'
            clause.append((var, True))
        formula.append(clause)
    

    # constraint 2: each student is assigned to exactly one room
    for student, preferences in student_preferences.items():
        # at least one room
        clause = []
        for room in preferences:
            var = f"{student}_{room}"
            clause.append((var, True))
        formula.append(clause) 
        # at most one room
        # generate all pairs of preferred rooms
        preferences_list = list(preferences) # need it ordered
        for i in range(len(preferences_list)):
            for j in range(i + 1, len(preferences_list)):
                room1 = preferences_list[i]
                room2 = preferences_list[j]
                var1 = f"{student}_{room1}"
                var2 = f"{student}_{room2}"
                # add the clause stating the
                # student is not in both rooms at the same time
                formula.append([(var1, False), (var2, False)])

                

    # constraint 3: no room is over capacity
    for room, capacity in room_capacities.items():
        students_prefer_room = []
        for student, preferences in student_preferences.items():
            if room in preferences:
                students_prefer_room.append(student)
        # if less students prefer room than capacity of the room,
        # all is dandy
        if len(students_prefer_room) <= capacity:
            continue
        # get all possible combinations of students
        student_combinations = recur_combinations(students_prefer_room, capacity + 1)
        for combination in student_combinations:
            clause = []
            for student in combination:
                var = f"{student}_{room}"
                # this makes it so at least one student
                # in the combination is not in the room
                # preventing it from being over capacity
                clause.append((var, False))
            formula.append(clause)
    print(formula)

    return formula

"""
if __name__ == "__main__":
    #_doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags

    formula = [
    [('a', True), ('b', True), ('c', True)],
    [('a', False), ('f', True)],
    [('d', False), ('e', True), ('a', True), ('g', True)],
    [('h', False), ('c', True), ('a', False), ('f', True)],
    ]
    var1 = 'a'
    t_f1 = True
    new_formula1 = update_cnf(formula, var1, t_f1)
    #print(new_formula1)
    var2 = 'a'
    t_f2 = False
    new_formula2 = update_cnf(formula, var2, t_f2)
    #print(new_formula2)
    var3 = 'f'
    t_f3 = True
    new_formula3 = update_cnf(new_formula1, var3, t_f3)
    #print(new_formula3)
    var4 = 'f'
    t_f4 = False
    new_formula4 = update_cnf(new_formula1, var4, t_f4)
    #print(new_formula4)

    formula2 = [
    [('a', False), ('b', False)],
    [('a', True), ('d', False)],
    [('a', True)],
    [('a', False), ('e', True), ('f', False), ('g', True)],
    [('b', True), ('c', True), ('f', True)],
    [('b', False), ('f', True), ('g', False)]
    ]

    satisfying_assignment(formula2)
    comb1 = recur_combinations(["Alex", "Blake", "Chris", "Dana"], 2)
    comb2 = recur_combinations(["Alex", "Blake", "Chris", "Dana"], 3)
    print(comb1)
    print(comb2)

    bool_ex = boolify_scheduling_problem({'Alex': {'basement', 'penthouse'},
                            'Blake': {'kitchen'},
                            'Chris': {'basement', 'kitchen'},
                            'Dana': {'kitchen', 'penthouse', 'basement'}},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4})
"""

    
