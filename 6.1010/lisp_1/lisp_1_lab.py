"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

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
            line = line[:comment_index] # remove trailing comment
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
    current_token = ''
    for char in clean_source:
        if char == '(' or char == ')':
            if current_token != '':
                tokens.append(current_token)
                current_token = ''
            tokens.append(char)
        elif char.isspace():
            if current_token != '':
                tokens.append(current_token)
                current_token = ''
            # Ignore whitespace
        else:
            current_token += char  # Accumulate characters into current token
    if current_token != '':
        tokens.append(current_token)  # Add any remaining token
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    def parse_expression():
        if len(tokens) == 0:
            raise SchemeEvaluationError
        token = tokens.pop(0)
        if token == '(':
            # initialize a sublist
            expression_list = []
            while tokens[0] != ')':
                # recursively collect expression inside parentheses
                expression_list.append(parse_expression())
                if len(tokens) == 0:
                    raise SchemeEvaluationError
            tokens.pop(0)  # remove the closing parenthesis
            return expression_list
        elif token == ')':
            raise SchemeEvaluationError
        else:
            # helper function
            return number_or_symbol(token)
        
    return parse_expression()



######################
# Built-in Functions #
######################

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins['+'](*rest_nums)

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


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
}



##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    if frame is None:
        frame = make_initial_frame() # create an initial frame if none is provided
    
    # general checks
    if isinstance(tree, (int, float)):
        return tree # base case: number, float
    elif isinstance(tree, str):
        return frame.lookup(tree) # look up built ins
    elif isinstance(tree, list): 
        if len(tree) == 0:
            raise SchemeEvaluationError
        
        first_el = tree[0] # get first elements

        # case one: defining vars/functions
        if first_el == "define":
            if len(tree) != 3:
                raise SchemeEvaluationError # define requires two args
            name = tree[1]
            val_expr = tree[2]

            if isinstance(name, str):
                # assign variable, easy peasy
                val = evaluate(val_expr, frame) # get val recursively
                frame.define(name, val)
                return val
            if isinstance(name, list):
                # this means it's a function
                if len(name) == 0: # empty function name
                        raise SchemeEvaluationError
                func_name = name[0]
                parameters = name[1:]
                body = val_expr
                lambda_expr = ['lambda', parameters, body]
                function = evaluate(lambda_expr, frame) # recursive call (see below)
                frame.define(func_name, function)
                return function
            else:
                raise SchemeEvaluationError

        # case two: lambda functions
        elif first_el == "lambda":
            if len(tree) != 3:
                raise SchemeEvaluationError # need two args
            parameters = tree[1]
            body = tree[2]
            if not isinstance(parameters, list):
                raise SchemeEvaluationError # lambda parameters must be a list
            return Function(parameters, body, frame) # call Function
        
        else:
            # case 3: calculator    
            operator = evaluate(tree[0], frame) # get operator (consider built-ins)
            # get arguments recursively
            args = [evaluate(arg, frame) for arg in tree[1:]]
            if not callable(operator):
                raise SchemeEvaluationError
            try:
                return operator(*args)  # apply operator to arguments
            except SchemeError:
                raise 
        
    # tree isn't any of the above
    else:
        raise SchemeEvaluationError

##########
# Frames #
##########

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
            raise SchemeNameError # name has no value anywhere

    def __iter__(self):
        # allow iteration over variable names in the frame
        return iter(self.assignments)

    def __str__(self):
        return f"Frame assignments={self.assignments}"

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
        self.body = body # body expression
        self.frame = frame  # frame where the function was defined

    def __call__(self, *args):
        # check that number of parameters and args match up
        if len(args) != len(self.parameters):
            raise SchemeEvaluationError

        # create a new frame for the function call
        call_frame = Frame(parent=self.frame)

        #assign arguments to parameters in the new frame
        for param, arg in zip(self.parameters, args):
            call_frame.define(param, arg)

        # evaluate the function body in the new frame
        return evaluate(self.body, call_frame)

    def __str__(self):
        return f"Function parameters={self.parameters} body={self.body}"

"""

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=False, verbose=False).cmdloop()

    #print(tokenize("(cat (dog (tomato)))"))
    #print(evaluate(['+', 3, 7, 2]))
    #print(parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']))

"""

