"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    """
    Base class. All other classes inherit from Expr.
    """
    def eval(self, mapping):
        # evaluate the expression given a mapping from variable names to values
        raise NotImplementedError  # to be implemented in subclasses

    def __eq__(self, other):
        # check whether two expressions are equal
        raise NotImplementedError

    def deriv(self, var):
        # compute the derivative with respect to var
        raise NotImplementedError

    def simplify(self):
        # simplify the expression
        return self  # Num and Var don't need simplification, base case

    def _get_precedence(self):
        # return the precedence of the operator
        return float("inf")  # numbers and variables have highest precedence, base case

    # operator overloading to allow expressions like Var('x') + Num(2)
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)


class Var(Expr):
    """
    Instances of Var represent variables (such as x or y)
    """
    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"
    
    # note on polymorphisms to avoid isinstance checks:
    # Num and Var define their own version of eval
    # and are trusted to know how to eval themselves
    def eval(self, mapping):
        # evaluate the variable by looking up its value in the mapping
        if self.name in mapping:
            return mapping[self.name]
        else:
            # if var not in dictionary, raise error
            raise NameError

    def __eq__(self, other):
        # check if other is a Var with the same name
        return isinstance(other, Var) and self.name == other.name

    def deriv(self, var):
        # derivative of variable with respect to var
        if self.name == var:
            return Num(1)  # derivative of x with respect to x is 1
        else:
            return Num(0)  # derivative of x with respect to y is 0


class Num(Expr):
    """
    Instances of Num represent numbers within symbolic expressions.
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        # evaluate a number: return its value
        return self.n

    def __eq__(self, other):
        # check if other is a Num with the same value
        return isinstance(other, Num) and self.n == other.n

    def deriv(self, var):
        # derivative of a number is 0
        return Num(0)


class BinOp(Expr):
    """
    Class representing abinary operation in the expression tree.

    Vars:
        left (Expr): The left operand of the operation.
        right (Expr): The right operand of the operation.
    """

    def __init__(self, left, right):
        # checking types of left and right, converting to
        # a number or variable when appropriate
        # this initializer makes it so there isn't
        # a need for isinstance/type checking in subclasses
        if not isinstance(left, Expr):
            if isinstance(left, (float, int)):
                left = Num(left)
            elif isinstance(left, str):
                left = Var(left)
            else:
                raise TypeError
        if not isinstance(right, Expr):
            if isinstance(right, (int, float)):
                right = Num(right)
            elif isinstance(right, str):
                right = Var(right)
            else:
                raise TypeError
        # store right and left
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def __str__(self):
        left = str(self.left)
        right = str(self.right)

        # call helper function to check 
        # if parens are needed
        if self._check_parens(self.left, is_right=False):
            left = f"({left})"

        if self._check_parens(self.right, is_right=True):
            right = f"({right})"
            
        # call on op, an attribute of subclasses Add, Sub, etc
        return f"{left} {self.op} {right}"

    def _get_precedence(self):
        # helper function to get precendence
        # which is an attribute of subclasses
        return self.precedence

    def _check_parens(self, child, is_right):
        if child._get_precedence() < self._get_precedence():
            return True  # lower precedence, needs parentheses
        elif is_right and self._parenthesize_right_on_equal_precedence():
            if child._get_precedence() == self._get_precedence():
                if isinstance(self, (Sub, Div)):
                    # if B represents a subtraction or a division and B.right
                    # represents an expression with the same precedence as B,
                    # wrap B.right's string representation in parentheses.
                    return True
        return False  # no parentheses needed

    def _parenthesize_right_on_equal_precedence(self):
        return False


class Add(BinOp):
    """
    Addition.

    Attributes:
        op (str): The operator symbol ('+').
        precedence (int): The precedence level of addition (2).
    """

    op = "+"
    precedence = 2

    def eval(self, mapping):
        # Evaluate addition
        return self.left.eval(mapping) + self.right.eval(mapping)

    def deriv(self, var):
        # derivative of sum is the sum of derivatives
        return Add(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        # simplify addition
        left = self.left.simplify()
        right = self.right.simplify()
        # if both operands are numbers, compute the sum
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n + right.n)
        # if one of the operands is 0, return the other
        if isinstance(left, Num) and left.n == 0:
            return right
        if isinstance(right, Num) and right.n == 0:
            return left
        # else, return simplified Add
        return Add(left, right)

    def __eq__(self, other):
        # Check if other is an Add with equal operands
        return (
            isinstance(other, Add)
            and self.left == other.left
            and self.right == other.right
        )


class Sub(BinOp):
    """
    Subtraction.

    Attributes:
        op (str): The operator symbol ('-').
        precedence (int): The precedence level of subtraction (2).
    """

    op = "-"
    precedence = 2

    def eval(self, mapping):
        # evaluate subtraction
        return self.left.eval(mapping) - self.right.eval(mapping)

    def _parenthesize_right_on_equal_precedence(self):
        return True

    def deriv(self, var):
        # derivative of difference is the difference of derivatives
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        # simplify subtraction
        left = self.left.simplify()
        right = self.right.simplify()
        # if both operands are numbers, compute the sum
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n - right.n)
        # if second operand is 0, return the other
        if isinstance(right, Num) and right.n == 0:
            return left
        # else, return simplified Sub
        return Sub(left, right)

    def __eq__(self, other):
        # Check if other is an Sub with equal operands
        return (
            isinstance(other, Sub)
            and self.left == other.left
            and self.right == other.right
        )


class Mul(BinOp):
    """
    Multiplication.

    Attributes:
        op (str): The operator symbol ('*').
        precedence (int): The precedence level of multiplication (3).
    """

    op = "*"
    precedence = 3

    def eval(self, mapping):
        # Evaluate addition
        return self.left.eval(mapping) * self.right.eval(mapping)

    def deriv(self, var):
        # time to use the product rule
        return Add(Mul(self.right, self.left.deriv(var)), Mul(self.left, self.right.deriv(var)))

    def simplify(self):
        # simplify
        left = self.left.simplify()
        right = self.right.simplify()
        # if both operands are numbers, compute the product
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n * right.n)
        # if one of the operands is 0, return 0
        if isinstance(left, Num) and left.n == 0:
            return Num(0)
        if isinstance(right, Num) and right.n == 0:
            return Num(0)
        # if one of the operands in 1, return the other
        if isinstance(left, Num) and left.n == 1:
            return right
        if isinstance(right, Num) and right.n == 1:
            return left
        # else, return simplified Mul
        return Mul(left, right)

    def __eq__(self, other):
        # Check if other is an Mul with equal operands
        return (
            isinstance(other, Mul)
            and self.left == other.left
            and self.right == other.right
        )


class Div(BinOp):
    """
    Division.

    Attributes:
        op (str): The operator symbol ('/').
        precedence (int): The precedence level of division (3).
    """

    op = "/"
    precedence = 3

    def _parenthesize_right_on_equal_precedence(self):
        return True

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)

    def deriv(self, var):
        # time to use the product rule
        numerator = Sub(Mul(self.right, self.left.deriv(var)), Mul(self.left, self.right.deriv(var)))
        denominator = Mul(self.right, self.right)
        return Div(numerator, denominator)

    def simplify(self):
        # simplify addition
        left = self.left.simplify()
        right = self.right.simplify()
        # if both operands are numbers, compute the sum
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n / right.n)
        # if numerator is zero, return 0
        if isinstance(left, Num) and left.n == 0:
            return Num(0)
        # if denominator is 1, return numerator
        if isinstance(right, Num) and right.n == 1:
            return left
        # else, return simplified Div
        return Div(left, right)

    def __eq__(self, other):
        # check if other is an Mul with equal operands
        return (
            isinstance(other, Div)
            and self.left == other.left
            and self.right == other.right
        )


def tokenize(s):
    """
    Splits the input string into a list of tokens.

    Examples:
    >>> tokenize("(x * (2 + 3))")
    ['(', 'x', '*', '(', '2', '+', '3', ')', ')']
    """
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        # is c an operand?
        if c in "()+-*/":
            # wait! a "-" can be the start of a negative number
            if (
                c == "-"
                and (i + 1) < len(s)
                and (s[i + 1].isdigit() or s[i + 1] == ".")
            ):
                num = c # initialize number c, traverse through it
                i += 1 # til you reach a non-digit/decimal point
                while i < len(s) and (s[i].isdigit() or s[i] == "."):
                    num += s[i]
                    i += 1
                tokens.append(num)
            else:
                tokens.append(c)
                i += 1
        # decimals
        elif c.isdigit() or c == ".":
            num = c  # initialize number
            i += 1 # traverse through number
            while i < len(s) and (s[i].isdigit() or s[i] == "."):
                num += s[i]
                i += 1
            tokens.append(num)
        elif c.isalpha():
            tokens.append(c)  # append variable name
            i += 1
        elif c.isspace():
            i += 1  # skip whitespace
        else:
            raise ValueError  # edge case
    return tokens


def parse(tokens):
    """
    Parses the list of tokens into an expression tree.

    Examples:
    >>> tokens = ['(', 'x', '*', '(', '2', '+', '3', ')', ')']
    >>> parse(tokens)
    Mul(Var('x'), Add(Num(2.0), Num(3.0)))
    """

    def recursive_helper(i):
        if i >= len(tokens):
            raise ValueError # edge case, tokens has no length
        # get current token
        current_token = tokens[i] 
        if current_token == "(":
            # open parenthesis recursive call
            # function returns left expression
            # and new index to start back up at
            left_expr, next_i = recursive_helper(i + 1)
            if next_i >= len(tokens):
                raise ValueError
            op = tokens[next_i]
            # after a lefthand side is finished, next
            # token should be an operance
            if op not in "+-*/":
                raise ValueError
            # same as left expression—recursively retrieve
            # righthand expression
            right_expr, next_i = recursive_helper(next_i + 1)
            # now, it's expected to have a closed parenthesis
            if next_i >= len(tokens) or tokens[next_i] != ")":
                raise ValueError
            next_i += 1 # move along
            # match operand to class
            if op == "+":
                return Add(left_expr, right_expr), next_i
            elif op == "-":
                return Sub(left_expr, right_expr), next_i
            elif op == "*":
                return Mul(left_expr, right_expr), next_i
            elif op == "/":
                return Div(left_expr, right_expr), next_i
        else:
            # if not a parenthesis, could be a number
            # or a var
            try:
                value = float(current_token)
                return Num(value), i + 1
            except ValueError: # so, not a number
                if current_token.isalpha():
                    return Var(current_token), i + 1
                else:
                    raise ValueError # so, neither a number nor letter

    expression, next_i = recursive_helper(0)
    # lastly, make sure we actually reached end of tokens list
    if next_i != len(tokens): 
        raise ValueError
    return expression


def make_expression(s):
    # put it all together yippee
    tokens = tokenize(s)
    return parse(tokens)


if __name__ == "__main__":
    pass
