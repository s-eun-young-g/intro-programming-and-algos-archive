#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def no_more_comments(source):
    """
    Helper function to clean a source
    of any comments.
    """
    # split into lines
    lines = source.split("\n")
    lines_without_comments = []

    for line in lines:
        # find() returns index of substring
        # if found and -1 if not
        comment_index = line.find(";")
        if comment_index != -1:
            line = line[:comment_index]  # remove trailing comment
        lines_without_comments.append(line)

    clean_source = ""
    for line in lines_without_comments:
        clean_source = clean_source + line + "\n"
    return clean_source


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    clean_source = no_more_comments(source)
    tokens = []
    # current_token tracks of an accumulation
    # of sequential characters
    # as elements are either separated by whitespace
    # or parentheses
    current_token = ""
    for char in clean_source:
        if char == "(" or char == ")":
            if current_token != "":
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        elif char.isspace():
            if current_token != "":
                tokens.append(current_token)
                current_token = ""
            # ignore whitespace
        else:
            current_token += char  # accumulate characters into current token
    if current_token != "":
        tokens.append(current_token)  # add any remaining token
    return tokens


def parse_expression(tokens):
    """
    Helper function that does the heavy lifting for parsing expression. Refactored
    so it can be called on its own in file reading/evaluating.
    """
    if len(tokens) == 0:
        raise SchemeSyntaxError

    token = tokens.pop(0)
    if token == "(":
        # initialize a sublist
        expression_list = []
        if len(tokens) == 0:
            raise SchemeSyntaxError
        while tokens[0] != ")":
            # recursively collect expression inside parentheses
            expression_list.append(parse_expression(tokens))
            if len(tokens) == 0:
                raise SchemeSyntaxError
        tokens.pop(0)  # remove the closing parenthesis
        return expression_list
    elif token == ")":
        raise SchemeSyntaxError
    else:
        # helper function
        return number_or_symbol(token)


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    copied = tokens[:]
    expr = parse_expression(copied)
    if copied:
        raise SchemeSyntaxError
    return expr


######################
# Built-in Functions #
######################


def calc_sub(*args):
    if len(args) == 0:
        raise SchemeEvaluationError
    if len(args) == 1:
        return -args[0]
    first_num, *rest_nums = args
    return first_num - sum(rest_nums)


def calc_mul(*args):
    if len(args) == 0:
        raise SchemeEvaluationError
    result = 1
    # multiply all numbers in expression
    for arg in args:
        result *= arg
    return result


def calc_div(*args):
    if len(args) == 0:
        raise SchemeEvaluationError
    # case one: one argument, return 1/arg
    elif len(args) == 1:
        return 1 / args[0]
    # case two: more than one argument, return arg_1 divided by rest
    else:
        result = args[0]
        for arg in args[1:]:
            result /= arg
        return result


###########################
# Boolean and Comparisons #
###########################


def scheme_boolean(val):
    """
    Returns True or False
    """
    return True if val else False


def equal_question(*args):
    """
    Checks if arguments are equals
    """
    if len(args) < 2:
        return True  # trivially true if there's 1 or 0 arguments
    first = args[0]
    for arg in args[1:]:
        if arg != first:
            return False
    return True


def greater_than(*args):
    """
    Checks if arguments are increasing
    """
    for i in range(len(args) - 1):
        if not (args[i] > args[i + 1]):
            return False
    return True


def greater_equal(*args):
    """
    Checks if arguments are increasing or equal to previous argument
    """
    for i in range(len(args) - 1):
        if not args[i] >= args[i + 1]:
            return False
    return True


def less_than(*args):
    """
    Checks if arguments are decreasing
    """
    for i in range(len(args) - 1):
        if not args[i] < args[i + 1]:
            return False
    return True


def less_equal(*args):
    """
    Checks if arguments are decreasing or equal to previous argument
    """
    for i in range(len(args) - 1):
        if not args[i] <= args[i + 1]:
            return False
    return True


def not_func(*args):
    """
    Not. Raises an error if more than 2 arguments are given
    """
    if len(args) != 1:
        raise SchemeEvaluationError
    return scheme_boolean(not scheme_boolean(args[0]))


###################
# Pairs and Lists #
###################


class Pair:
    """
    Representation of a pair in Scheme.
    """

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


def cons_func(*args):
    """
    Constructs a pair.
    """
    if len(args) != 2:
        raise SchemeEvaluationError
    return Pair(args[0], args[1])


def car_func(*args):
    """
    Retrieves car of a pair.
    """
    if len(args) != 1:
        # car can only be called on a single pair
        raise SchemeEvaluationError
    pair = args[0]  # get arg
    if not isinstance(pair, Pair):
        raise SchemeEvaluationError
    return pair.car  # return car


def cdr_func(*args):
    """
    Retrieves cdr of a pair.
    """
    if len(args) != 1:
        # cdr can only be called on a single pair
        raise SchemeEvaluationError
    pair = args[0]  # get arg
    if not isinstance(pair, Pair):
        raise SchemeEvaluationError
    return pair.cdr  # return cdr


def list_func(*args):
    res = []
    for val in reversed(args):
        # create linked lists by looping
        # in reverse
        res = Pair(val, res)
    return res


def is_list(obj):
    """
    Checks if something is a valid list.
    """
    if obj == []:  # empty list is a valid list
        return True
    if isinstance(obj, Pair):
        # recursively get to bottom of linked list
        # loop into cdrs to see if it ends in an empt list
        return is_list(obj.cdr)
    return False


def length_func(*args):
    """
    Get the length of a list. Raise an error if input is not a list.
    """
    if len(args) != 1:  # takes one list as input
        raise SchemeEvaluationError
    length_list = args[0]
    if not is_list(length_list):  # if not valid list raise error
        raise SchemeEvaluationError
    count = 0
    current = length_list
    while isinstance(current, Pair):
        # looping through linked lists and counting each car
        count += 1
        current = current.cdr
    return count  # return car count


def list_ref_func(*args):
    """
    Takes in cons cell and index. Return item at index, but raise error
    if item is not in the car of its pair.
    """
    if len(args) != 2:  # two args
        raise SchemeEvaluationError
    ref_list, idx = args
    if not isinstance(idx, int) or idx < 0:
        # can't parse negative indices
        raise SchemeEvaluationError
    current = ref_list
    for _ in range(idx):
        # loop into linked lists
        if current == []:  # empty list
            raise SchemeEvaluationError
        if not isinstance(current, Pair):
            # must be pair
            raise SchemeEvaluationError
        current = current.cdr  # loop further
    if current == []:
        raise SchemeEvaluationError
    if isinstance(current, Pair):
        return current.car  # return car
    raise SchemeEvaluationError


def append_func(*args):
    """
    Appends a list of lists together. All arguments must be lists. Returns
    an empty list if no args are passed in.
    """
    if len(args) == 0:
        # return an empty list if no arguments are provided
        return []

    def copy_list(list_copy):
        """
        Helper function to create shallow copies of lists.
        """
        if list_copy == []:
            return []
        assert isinstance(list_copy, Pair)
        return Pair(list_copy.car, copy_list(list_copy.cdr))

    def check_list(arg):
        """
        Helper function to check if arg is a valid list.
        """
        if not is_list(arg):
            raise SchemeEvaluationError

    def append_to_result(result, append_list):
        """
        Helper function to append a list to the current result list.
        """
        end = result
        while isinstance(end.cdr, Pair):
            # navigate to the end of the result list
            end = end.cdr

        if append_list == []:
            return  # nothing to append if the current list is empty

        check_list(append_list)
        end.cdr = copy_list(append_list)

    # initialize the result list
    result = []

    for i, append_list in enumerate(args):
        if not result:
            # if result is empty, start with the first valid list
            if append_list == []:
                result = []
            else:
                check_list(append_list)
                result = copy_list(append_list)
        else:
            # append the current list to the result
            append_to_result(result, append_list)

    return result


#########################
# Boolean Special Forms #
#########################


def scheme_bool_to_value(bool_val):
    """
    Boolean to value. But make is Scheme.
    """
    return True if bool_val else False


def evaluate_if(expr, frame):
    """
    Scheme if.
    """
    if len(expr) != 4:
        raise SchemeEvaluationError
    # 4 arguments become...
    _, pred, true_expr, false_expr = expr
    # get predicate
    pred_val = evaluate(pred, frame)
    if scheme_boolean(pred_val):
        # return (evaluated) True expression if true and vice versa
        return evaluate(true_expr, frame)
    else:
        return evaluate(false_expr, frame)


def evaluate_and(expr, frame):
    """
    Scheme and.
    """
    if len(expr) == 1:
        # if there are no args, return True by default
        return True
    for subexpr in expr[1:]:
        # evaluate each sub-expression
        val = evaluate(subexpr, frame)
        if not scheme_boolean(val):
            # if anything is False, return False
            return False
    return True


def evaluate_or(expr, frame):
    """
    Scheme or.
    """
    if len(expr) == 1:
        # if there are no args, return False by default
        return False
    for subexpr in expr[1:]:
        val = evaluate(subexpr, frame)
        if scheme_boolean(val):
            # if a True value is found, return it
            return val
    return False


######################
# begin special form #
######################


def evaluate_begin(expr, frame):
    """
    Returns the last argument in an expression.
    """
    if len(expr) < 2:
        # at least one expression needed
        raise SchemeEvaluationError
    val = None  # placehoder for val
    for subexpr in expr[1:]:
        # eval each sub expression
        val = evaluate(subexpr, frame)
    return val


################################
# del, let, set! special forms #
################################


def evaluate_del(expr, frame):
    """
    Delete variable bindings in current frame
    """
    if len(expr) != 2:
        raise SchemeEvaluationError
    var = expr[1]  # get var to be deleted
    # edge cases
    if not isinstance(var, str):
        raise SchemeEvaluationError
    if var not in frame.assignments:
        raise SchemeNameError
    val = frame.assignments[var]  # get value of var
    del frame.assignments[var]  # delete var
    return val  # return value of var (formerly)


def evaluate_let(expr, frame):
    """
    Create local variable definitions
    """
    if len(expr) != 3:
        # let needs exactly three args: bindings and body
        raise SchemeEvaluationError
    bindings = expr[1]  # get list of bindings
    body = expr[2]  # get body
    if not isinstance(bindings, list):
        raise SchemeEvaluationError
    new_bindings = []  # initialize list for new bindings
    for b in bindings:
        if not (isinstance(b, list) and len(b) == 2):
            # bindings must be list of var, val
            raise SchemeEvaluationError
        var, val_expr = b
        if not isinstance(var, str):
            # variable names must be strings
            raise SchemeEvaluationError
        # evaluate expresion
        val = evaluate(val_expr, frame)
        new_bindings.append((var, val))
    # create new frame
    let_frame = Frame(parent=frame)
    for var, val in new_bindings:
        # define new bindings in new frame
        let_frame.define(var, val)
    return evaluate(body, let_frame)


def evaluate_set(expr, frame):
    """
    Change value of exisiting variable
    """
    if len(expr) != 3:
        # requires three things: set! call, var and new val
        raise SchemeEvaluationError
    var = expr[1]  # get var
    val_expr = expr[2]  # get new value expression
    if not isinstance(var, str):
        # variable names must be strings
        raise SchemeEvaluationError
    # evaluate new val in current frame
    val = evaluate(val_expr, frame)
    current_frame = frame
    while current_frame is not None:
        # loop through frames to find where var is
        # originaly defined
        if var in current_frame.assignments:
            # update var through frames if it exists there
            current_frame.assignments[var] = val
            return val
        current_frame = current_frame.parent
    raise SchemeNameError


#################
# evaluate_file #
#################


def evaluate_file(filename, frame=None):
    """
    Evaluate the expressions in a Scheme file.
    """
    if frame is None:
        frame = make_initial_frame()  # create an initial frame if none is provided

    with open(filename, "r") as f:
        source = f.read()

    # tokenize file
    tokens = tokenize(source)
    val = None
    while tokens:
        # parse file
        expr = parse_expression(tokens)
        # evaluate
        val = evaluate(expr, frame)

    return val


#########
# Frame #
#########


class Frame:
    """
    A frame represents an environment in which expressions are evaluated.

    It holds bindings from variable names to values and has an optional parent frame.

    Attributes: assignments (dictionary mapping variables to values), parent (parent frame)
    """

    def __init__(self, parent=None):
        self.assignments = {}  # dictionary to store variable bindings
        self.parent = parent  # reference to the parent frame (potential built-in)

    def define(self, name, value):
        # assign a val to a name in the current frame.
        self.assignments[name] = value

    def lookup(self, name):
        # look up a name in the current frame or its parent frames
        # if necessary, return correct value assigned to name
        if name in self.assignments:
            return self.assignments[name]
        # might find value in parent frame
        elif self.parent is not None:
            return self.parent.lookup(name)  # recursive lookup in parent frames
        else:
            raise SchemeNameError  # name has no value anywhere

    def __iter__(self):
        # allow iteration over variable names in the frame
        return iter(self.assignments)

    def __str__(self):
        return f"Frame assignments={self.assignments}"


###################
# scheme_builtins #
###################


def _raise_error():
    """
    Helper function that ensures the correct error type is raised
    in cases mapped in the scheme builtins dict below
    """
    raise SchemeEvaluationError


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
    "equal?": lambda *args: scheme_bool_to_value(equal_question(*args)),
    ">": lambda *args: scheme_bool_to_value(greater_than(*args)),
    ">=": lambda *args: scheme_bool_to_value(greater_equal(*args)),
    "<": lambda *args: scheme_bool_to_value(less_than(*args)),
    "<=": lambda *args: scheme_bool_to_value(less_equal(*args)),
    "not": not_func,
    "cons": cons_func,
    "car": car_func,
    "cdr": cdr_func,
    "list": list_func,
    "list?": lambda *args: (
        scheme_bool_to_value(is_list(args[0])) if len(args) == 1 else (_raise_error())
    ),
    "length": length_func,
    "list-ref": list_ref_func,
    "append": append_func,
    "#t": True,
    "#f": False,
    "error": lambda *args: (_raise_error()),
}


def make_initial_frame():
    """
    Creates an initial frame with built-in functions.
    """
    builtins_frame = Frame()
    for name, func in scheme_builtins.items():
        builtins_frame.define(name, func)
    return Frame(parent=builtins_frame)


#############
# Functions #
#############


class Function:
    """
    A user-defined (lambda) function in Scheme.

    Attributes: parameters and body of the function, frame where function
    was
    """

    def __init__(self, parameters, body, frame):
        self.parameters = parameters  # parameter names (strings)
        self.body = body  # body expression
        self.frame = frame  # frame where the function was defined

    def __call__(self, *args):
        # check that number of parameters and args match up
        if len(args) != len(self.parameters):
            raise SchemeEvaluationError

        # create a new frame for the function call
        call_frame = Frame(parent=self.frame)

        # assign arguments to parameters in the new frame
        for param, arg in zip(self.parameters, args):
            call_frame.define(param, arg)

        # evaluate the function body in the new frame
        return evaluate(self.body, call_frame)

    def __str__(self):
        return f"Function parameters={self.parameters} body={self.body}"


#################
# special forms #
#################

special_forms = {
    "if": lambda tree, frame: evaluate_if(tree, frame),
    "and": lambda tree, frame: evaluate_and(tree, frame),
    "or": lambda tree, frame: evaluate_or(tree, frame),
    "begin": lambda tree, frame: evaluate_begin(tree, frame),
    "del": lambda tree, frame: evaluate_del(tree, frame),
    "let": lambda tree, frame: evaluate_let(tree, frame),
    "set!": lambda tree, frame: evaluate_set(tree, frame),
    "lambda": lambda tree, frame: Function(tree[1], tree[2], frame),
    "define": lambda tree, frame: evaluate_define(tree, frame),
}


#####################
# Evaluate function #
#####################


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = make_initial_frame()  # create an initial frame if none is provided

    if isinstance(tree, (int, float, bool)):
        return tree  # base case: number, float OR bool
    if isinstance(tree, str):
        return frame.lookup(tree)  # look up built ins
    if tree == []:  # empty list
        return []
    if not isinstance(tree, list) or len(tree) == 0:  # invalid
        raise SchemeEvaluationError

    first_el = tree[0]  # get first element
    # check first_el is a string, then look it up in special forms
    if isinstance(first_el, str) and first_el in special_forms:
        return special_forms[first_el](tree, frame)

    # case 3: calculator
    operator = evaluate(first_el, frame)  # get operator (consider built-ins)
    # get arguments recursively
    args = [evaluate(arg, frame) for arg in tree[1:]]
    if not callable(operator):
        raise SchemeEvaluationError
    return operator(*args)


def evaluate_define(tree, frame):
    """
    Helper function for refactoring the logic for "define"
    """
    # case one: defining vars/functions
    if len(tree) != 3:
        raise SchemeEvaluationError  # define requires two args
    name = tree[1]
    val_expr = tree[2]

    if isinstance(name, str):
        # assign variable, easy peasy
        val = evaluate(val_expr, frame)  # get val recursively
        frame.define(name, val)
        return val
    elif isinstance(name, list):
        # this means it's a function
        if len(name) == 0:  # empty function name
            raise SchemeEvaluationError
        func_name = name[0]
        parameters = name[1:]
        body = val_expr
        lambda_expr = ["lambda", parameters, body]
        function = evaluate(lambda_expr, frame)  # recursive call (see below)
        frame.define(func_name, function)
        return function
    else:
        raise SchemeEvaluationError


if __name__ == "__main__":
    import os
    import schemerepl

    initial_frame = make_initial_frame()
    for filename in sys.argv[1:]:
        evaluate_file(filename, initial_frame)
    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, repl_frame=initial_frame
    ).cmdloop()
