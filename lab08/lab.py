#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest



# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
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
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    >>> tokenize(':= x 3')
    [':=', 'x', '3']
    """

    tokens = []
    elt = ''
    skip = False

    # if there is only one symbol, return a list of it
    if len(source) == 1:
        return [source]
    # if str is a number, return it
    if source.isnumeric():
        return [source]

    # for each character
    for char in source:
        # code over separate lines are still read as one line
        if char == '\n':
            skip = False
            
        if not skip:
            # parenthesis
            if char =='(':
                tokens.append(char)
            elif char == ')':
                if elt:
                    tokens.append(elt)
                    elt = ''
                tokens.append(char)
            # if a comment line, then skip it
            elif char == '#':
                skip = True
            # keep adding characters for digits of a number until a space is reached
            elif char != ' ' and char != '\n':
                elt+=char
            # if it's a space, then add the elt of the digits in
            elif char == ' ' or char == '\n' :
                if elt:
                    tokens.append(elt)
                    elt = ''
    # add elt into tokens
    if elt:
        tokens.append(elt)
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    >>> s = tokenize('(:= circle-area (function (r) (* 3.14 (* r r))))')
    >>> parse(s)
    [':=', 'circle-area', ['function', ['r'], ['*', 3.14, ['*', 'r', 'r']]]]
    """

    def parse_expression(index):
        '''
        To convert each symbol in the list to an instance of Symbol or BinOp
        '''
        token = tokens[index]
        
        open_paren = tokens.count('(')
        closed_paren = tokens.count(')')

        # parenthesis number does not match, then raise error
        if open_paren != closed_paren:
            raise CarlaeSyntaxError

        # if just one expression, then add it and return it
        if open_paren == 0 and len(tokens) != 1:
            expression = []
            for elt in tokens:
                expression.append(number_or_symbol(elt))
            return expression

        # if is a number, wrap as number
        if token != '(' and token != ')':
            return number_or_symbol(token), index+1

        # open parenthesis, then parse sub expressions separately
        elif token == '(':
            expression = []
            next_index = index+1

            while tokens[next_index] != ')':
                subexpression, next_index = parse_expression(next_index)
                expression.append(subexpression)
       

            return expression, next_index+1
    try:
        parsed_expression, next_index = parse_expression(0)
    except:
        raise CarlaeSyntaxError
    return parsed_expression



######################
# Built-in Functions #
######################

def mult(args):
    '''
    Take in a list of arguments and multiply all of elts
    '''
    # if length is 1
    result = 1
    if len(args) == 1:
        return arg
    # multiply all
    else:
        for arg in args:
            result = result*arg
        return result

def div(args):
    '''
    Take in a list of arguments and divide all elts
    '''
    result = args[0]
    # if length is 1
    if len(args) == 1:
        return args
    # divide all
    else:
        for i in range(1, len(args)):
            result = result/args[i]
        return result

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])), 
    '*': mult,
    '/': div
}

class Environment:
    '''
    Represents an environment
    '''
    def __init__(self, mapping={}, parent=None):
        self.mapping = mapping
        self.parent = parent

    def get_var(self, name):
        try:
            # attempt to retrieve the value of the variable
            return self.mapping[name]
        except:
            # try to find it in parent class, or if no parent return None
            if self.parent == None:
                return None
            return self.parent.get_var(name)
    
    def set_var(self, name, val):
        # store variable values in dictionary
        self.mapping[name] = val

built_env = Environment(carlae_builtins)




##############
# Evaluation #
##############
def evaluate(tree, environment=Environment({}, built_env)):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
   
    # if number, return it
    if isinstance(tree, int) or isinstance(tree, float):
        return tree
    # if a variable, look it up
    elif isinstance(tree, str):
        val = environment.get_var(tree)
        if val == None:
            raise CarlaeNameError('variable '+tree+' not found') 
        return val
    # if a function return it
    elif isinstance(tree, Function):
        return tree
    
    # binding functions or variables
    elif tree[0] == ':=':
        if isinstance(tree[1], list):
            # simplified version as a list, create a Function object 
            result = Function(tree[2], tree[1][1:], environment)
            # save function in environment
            environment.set_var(tree[1][0], result)
        elif len(tree) == 3:
            # if the rest of the tree is an integer, just pass that in
            result = evaluate(tree[2], environment)
            environment.set_var(tree[1], result)
        else:
            # else if rest of tree a list, pass it in
            result = evaluate(tree[2:], environment)
            environment.set_var(tree[1], result)
        return result

    # if the tree has a 'function' then create a Function object
    elif tree[0] == 'function' or 'function' in tree:
        return Function(tree[2], tree[1], environment)
        
    else:  
        L = []
        # evaluate each expression
        for exp in tree:
            L.append(evaluate(exp, environment))
        # if a function, just call it with the rest of the list passed in
        if callable(L[0]):
            return L[0](L[1:])
        # if a Function object, use .call() and pass in rest of the list as arguments
        elif isinstance(L[0], Function):
            return L[0].call(L[1:])
        # not a function, raise an error
        else:
            raise CarlaeEvaluationError

         
def result_and_env(tree, environment=None):
    if environment ==None:
        environment = Environment({}, built_env)
    # returns evalulate result and the environment associated with it
    return evaluate(tree, environment), environment
    
class Function:
    '''
    Represents a Function 
    '''
    def __init__(self, expr, parameters, environment):
        self.expr = expr
        self.parameters = parameters
        self.environment = environment

    def call(self, arguments):
        # raise error if parameters and arguments are not equal
        if len(self.parameters) != len(arguments):
            raise CarlaeEvaluationError

        # evalulate each argument
        L = []
        for argument in arguments:
            L.append(evaluate(argument))

        # create a new environment 
        new_environment = Environment({}, self.environment)
        for parameter, arg in zip(self.parameters, L):
            # binding arguments to parameters
            new_environment.set_var(parameter, arg)
    
        return evaluate(self.expr, new_environment)

        
if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    doctest.testmod()
    
    

    user_input = input('in> ')
    
    while user_input != 'EXIT':
        try:
            print('   out> ', evaluate(parse(tokenize(user_input))))
        except Exception as e:
            print('input invalid')
            print(e)
            pass
        user_input = input('in> ')
