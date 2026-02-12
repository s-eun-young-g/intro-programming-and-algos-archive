"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3

# import pickle
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """
    Takes in raw_data, a list of tuples structured as (actor_1, actor_2, and film).

    Returns a more efficient/useful structure: a dictionary containing thre entries:
    A dictionary of actors as keys and their coactors as values, a dictionary or
    actors as keys and their films as values, and a dictionary of films as keys and its
    actors as values.
    """
    # dictionary of actors as keys and coactors as values
    connected_actors = {}
    # dictionary of actors as keys and films they appeared in as values
    actors_in_films = {}
    # dictionary of films as keys and actors that appear in it as values
    films_with_actors = {}

    for actor_1, actor_2, film in raw_data:
        # check if actor has an existing entry
        if actor_1 not in connected_actors:
            # if not, create an entry and an empty set
            connected_actors[actor_1] = set()
            # check if actor 2 is already in actor 1's set
        if actor_2 not in connected_actors[actor_1]:
            connected_actors[actor_1].add(actor_2)  # if not, add to set

        if actor_2 not in connected_actors:  # same for actor 2
            connected_actors[actor_2] = set()
        if actor_1 not in connected_actors[actor_2]:
            connected_actors[actor_2].add(actor_1)

        if actor_1 not in actors_in_films:  # check if actor has an e axisting entry
            actors_in_films[actor_1] = set()  # if not, create an entry and an empty set
        actors_in_films[actor_1].add(film)  # add film to set

        if actor_2 not in actors_in_films:  # same for actor 2
            actors_in_films[actor_2] = set()
        actors_in_films[actor_2].add(film)

        if film not in films_with_actors:  # check if film has an existing entry
            films_with_actors[film] = set()  # if not, create entry
        if actor_1 not in films_with_actors[film]:  # add actors to values
            films_with_actors[film].add(actor_1)
        if actor_2 not in films_with_actors[film]:
            films_with_actors[film].add(actor_2)

    transformed = {  # return dictionary of dictionaries of sets
        "connected_actors": connected_actors,
        "actors_in_films": actors_in_films,
        "films_with_actors": films_with_actors,
    }

    return transformed


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Takes in the transformed data base and the ID numbers of two actors.
    Returns true if the two actors have acted in a movie together.
    Returns false otherwise.
    Edge case: returns true if the two actor IDs inputted are the same.
    """
    if actor_id_1 == actor_id_2:  # case in which input is the same actor
        return True

    # check both IDs are in the database in the first place
    if actor_id_1 in transformed_data["connected_actors"]:
        if actor_id_2 in transformed_data["connected_actors"]:
            return actor_id_2 in transformed_data["connected_actors"][actor_id_1]
        
    return False


def actors_with_bacon_number(transformed_data, n):
    """
    Takes in transformed data base and a designated Bacon number, n.
    Returns IDs of actors with that Bacon number.
    """

    kevin_bacon = 4724  # establishing Bacon's ID

    connected_actors = transformed_data["connected_actors"]

    bacon_numbers = {
        kevin_bacon: 0
    }  # initializing dictionary of bacon numbers with the one and only
    current_level = {kevin_bacon}  # initializing the first level of BFS tree

    for current_bacon_number in range(1, n + 1): 
        next_level = set()  # initializing new set for next level of BFS tree
        for actor in current_level:
            coactors = connected_actors.get(
                actor
            )  # getting coactors for each actor in current level
            for coactor in coactors:
                if (coactor not in bacon_numbers):  # checking is coactor is already in Bacon number dictionary
                    bacon_numbers[coactor] = (current_bacon_number)  # setting Bacon number to current Bacon number (aka level)
                    next_level.add(coactor)  # adding to next level set to be iterated through on next iteration of loop
        current_level = next_level # updating level
        if not current_level:
            break  # breaks out of loop when all actors have been iterated through

    result = {
        actor for actor, bacon_number in bacon_numbers.items() if bacon_number == n
    }

    return result


def bacon_path(transformed_data, actor_id):
    """
    Takes in the transformed data base and the ID of a target actor.
    Returns the (or one of the) shortest paths between Kevin Bacon and that actor.
    """

    kevin_bacon = 4724  # establishing Bacon's ID

    if actor_id == kevin_bacon:  # checking if input actor is Bacon himself
        return {kevin_bacon}

    def goal_test_function_1(current_actor):
        return current_actor == actor_id

    result = actor_path(transformed_data, kevin_bacon, goal_test_function_1)

    return result


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Takes in the transformed data base and the ID of a
    starting actor and target actor.
    Returns the (or one of the) shortest path of
    actors between the starting and the target actor.
    """

    if actor_id_1 == actor_id_2: # checking if actor 1 is the same as actor 2
        return [actor_id_1]

    def goal_test_function_2(current_actor):
        return current_actor == actor_id_2

    result = actor_path(transformed_data, actor_id_1, goal_test_function_2)

    return result


def movies_connect_actors(transformed_data, actor_id_1, actor_id_2):
    """
    Takes in the transformed data base and the ID of a starting actor
    and target actor. Returns the (or one of the) shortest
    paths of shared films between the starting actor
    and target actor. This of shared films can be illustrated as so:
    If actor A was in a movie with actor B, who is on the path to the
    target actor, that movie is added to the list. Then, if actor B was
    in a movie with actor C, who is on the path to the target actor,
    that movie is then added and so on and so forth.
    """
    if actor_id_1 == actor_id_2:
        return []

    connected_actors = transformed_data["connected_actors"]
    actors_in_films = transformed_data["actors_in_films"]

    def get_coactors(actor_id):  # helper function to get coactors of a given actor
        return connected_actors.get(actor_id, set())

    # helper function to get films both actors appeared in
    def get_shared_films(actor_id_1, actor_id_2):
        films_1 = actors_in_films.get(actor_id_1, set())
        films_2 = actors_in_films.get(actor_id_2, set())
        return films_1 & films_2

    agenda = [(actor_id_1, [])]  # initializing agenda with starting ID
    visited = set([actor_id_1])  # initializing visited with starting ID

    while agenda:
        current_actor, current_movies = agenda.pop(0)
        coactors = get_coactors(current_actor)

        for coactor_id in coactors:
            if coactor_id not in visited:
                # get the films connecting current_actor and coactor_id
                shared_films = get_shared_films(current_actor, coactor_id)
                if not shared_films:  # making sure they actually have movies in common
                    continue

                film_id = next(
                    iter(shared_films)
                )  # choose one film actors both appeared in
                new_movies = current_movies + [film_id]

                if coactor_id == actor_id_2:
                    return get_id_name(new_movies, movies)  # return the list of movies

                visited.add(coactor_id)  # add coactor to visited
                # add coactor and subsequent list of movies to agenda
                agenda.append((coactor_id, new_movies))

    return None  # returns none if agenda reaches 0 (no path was found)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Generalized function that takes in the transformed data base, the ID
    of a starting actor, and a function to be used as our goal test.
    This function should take a single actor ID as input, and it
    should return True if that actor represents a valid
    ending location for the path, and False otherwise.
    Returns a list of actor IDs representing the shortest path
    from the starting actor ID to any actor that satisfies
    the goal-test function. If no path can be found to an
    actor that satisfies the goal condition, returns None.
    """
    if goal_test_function(actor_id_1):
        return [actor_id_1]  # return true if the starting actor satisfies the goal test

    connected_actors = transformed_data["connected_actors"]

    def get_coactors(actor_id):
        # helper function to get coactors (similar to get_neighbors)
        return connected_actors.get(actor_id, set())

    agenda = [(actor_id_1, [actor_id_1])]  # initializing agenda with starting ID
    visited = set([actor_id_1]) # initializing visited set with starting ID

    while agenda:
        # get current actor, the path to current actor, and remove from agenda
        current_actor, path = agenda.pop(0) 
        coactors = get_coactors(current_actor) # get coactors

        for coactor_id in coactors: # iterating through coactors
            if coactor_id not in visited: # checking if actor has already been visited
                visited.add(coactor_id) # if not, add to visited list
                new_path = path + [coactor_id] # adding to a path

                if goal_test_function(coactor_id):
                    # return true when you find an actor satisfying the goal test
                    return new_path

                agenda.append((coactor_id, new_path)) # adding coactor and its path to the agenda

    return None  # returns none if agenda reaches 0 (no path was found)


def actors_connecting_films(transformed_data, film1, film2):
    """
    Takes in the transformed data base and the ID of a starting film and
    target film. Returns the (or one of the) shortest paths of shared
    actors between the starting film and target film. This of shared
    films can be illustrated as so: If actor A was in a movie A and
    movie B, and movie B is on the path to the target
    film, that actor is added to the list. So on and so forth.
    """
    # to start us off, some thorough, thorough edge case checks
    films_with_actors = transformed_data["films_with_actors"]
    
    return check_none(film1, film2, films_with_actors)

    def get_cast(film):  # helper function to get actors in a film
        cast = films_with_actors.get(film, set())
        return cast

    cast1 = get_cast(film1)
    cast2 = get_cast(film2)

    # another edge case check — if either of the films does not have a cast, return None
    if not cast1 or not cast2:
        return None

    # goal function: checking if the actor is in the cast of the target movie
    def goal_test_function(actor_id):
        return actor_id in cast2

    shortest_path = None
    shortest_length = None

    for start_actor_id in cast1:
        # use actor_path to find a path from start_actor_id to any actor in actors_in_film2
        path = actor_path(transformed_data, start_actor_id, goal_test_function)
        if path:
            path_length = len(path)
            # update the shortest path if this path is shorter
            if shortest_length is None or path_length < shortest_length:
                shortest_path = path
                shortest_length = path_length
            # if the path length is 1, we've found an actor who is in both films
            if path_length == 1:
                # shortest_path.append(start_actor_id)
                shortest_path = [start_actor_id]
                break  # Cannot find a shorter path

    return shortest_path


# HELPER FUNCTIONS


def get_name_id(name, name_database):
    """
    Helper function to get the ID of an actor given their name.
    """
    return name_database[name]


def get_id_name(ids, name_database):
    """
    Helper function to get the names of actors given their IDs.
    """
    id_to_name = {id: name for name, id in name_database.items()}

    actor_names = []
    for current_id in ids:
        name = id_to_name.get(current_id)
        actor_names.append(name)

    return actor_names

def check_none(film1, film2, films_with_actors):
    if film1 is None or film2 is None:
        print("none")
        return None 
    if film1 == film2:
        if film1 in films_with_actors:
            cast = films_with_actors.get(film1, set())
            if cast:
                print("none")
                return [next(iter(cast))]
            else:
                print("none")
                return []
        else:
            print("none")
            return None
    pass

"""
if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
        transformed_data = transform_data(smalldb)
    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)
        transformed_tiny = transform_data(tinydb)
    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)
        transformed_large = transform_data(largedb)
    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)
        #print(get_id_name(actors_with_bacon_number(transformed_large, 6), names))
        # print(acted_together(transformed_data, get_name_id("David Stevens", names), get_name_id("Scott Subiono", names)))
        # print(acted_together(transformed_data, get_name_id("Darren Dalton", names), get_name_id("Joseph McKenna", names)))
        # bacon_to_anita = bacon_path(transformed_large, get_name_id("Anita Barnes", names))
        # print(get_id_name(bacon_to_anita, names))
        # cannons_to_heizer = actor_to_actor_path(transformed_large, get_name_id("John Cannons", names), get_name_id("Miles Heizer", names))
        # print(cannons_to_heizer)
        # print(get_id_name(cannons_to_heizer, names))
    with open("resources/movies.pickle", "rb") as f:
        movies = pickle.load(f)
        # blackehart_to_turk = movies_connect_actors(transformed_large, get_name_id("Stephen Blackehart", names), get_name_id("Vjeran Tin Turk", names))
        # print(blackehart_to_turk)
    # print(bacon_path(transformed_tiny, 1640))
    # print(get_name_id("John Cannons", names))
    # print(get_name_id("Miles Heizer", names))
   
    # print(actors_with_bacon_number(transformed_tiny, 1))
    # print(actors_with_bacon_number(transformed_tiny, 2))
    # print(actors_with_bacon_number(transformed_tiny, 3))

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
"""
