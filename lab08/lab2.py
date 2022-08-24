"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.

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


def equal(args):
    '''
    =?
    Should evaluate to true if all of its arguments are equal to each other.
    '''
    for i in range(len(args)-1):
        if args[i] != args[i+1]:
            return False
    return True

def greater(args):
    '''
    >
    Should evaluate to true if its arguments are in decreasing order.
    '''
    for i in range(len(args)-1):
        if args[i] <= args[i+1]:
            return False
    return True

def geq(args):
    '''
    >=
    Should evaluate to true if its arguments are in nonincreasing order.
    '''
    for i in range(len(args)-1):
        if args[i] < args[i+1]:
            return False
    return True

def less(args):
    '''
    >
    Should evaluate to true if its arguments are in increasing order.
    '''
    for i in range(len(args)-1):
        if args[i] >= args[i+1]:
            return False
    return True

def leq(args):
    '''
    <=
    Should evaluate to true if its arguments are in nondecreasing order.
    '''
    for i in range(len(args)-1):
        if args[i] > args[i+1]:
            return False
    return True

def opposite(arg):
    '''
    not built-in 
    returns the opposite of arg   
    '''
    if not arg or len(arg) > 1:
        raise CarlaeEvaluationError
    if evaluate(arg[0]):
        return False
    return True

def create_pair(args):
    '''
    Creates a Pair instance with args passed in
    '''
    if len(args) != 2:
        raise CarlaeEvaluationError
    else:
        return Pair(args[0], evaluate(args[1]))

def get_head(obj):
    '''
    Retrieve first element of Pair obj
    '''
    if len(obj) != 1 or not isinstance(obj[0], Pair):
        raise CarlaeEvaluationError
    return obj[0].head

def get_tail(obj):
    '''
    Retrieve second element of Pair obj
    '''
    if len(obj) != 1 or not isinstance(obj[0], Pair):
        raise CarlaeEvaluationError
    return obj[0].tail

def create_list(args):
    '''
    Pass in a list, create a Pair representation of the list
    '''
    if len(args) == 0:
        return ''
    else:
        return Pair(args[0], create_list(args[1:]))

def islist(obj):
    '''
    Check to see if the obj is a list
    '''
    if not isinstance(obj, list):
        obj = obj
    else:
        obj = obj[0]
    if obj == '':
        return '@t'
    if not isinstance(obj, Pair):
        return '@f'
    else:
        return islist(obj.tail)

def find_length(elt):
    '''
    Finding the length of the elt passed in
    '''
    if not isinstance(elt, list):
        pair = elt
    else:
        pair = elt[0]
        
    # Base Case
    if pair == '' or pair == 'nil':
        return 0
    if not isinstance(pair, Pair):
        raise CarlaeEvaluationError
    elif not isinstance(pair.tail, Pair) and pair.tail != '':
        raise CarlaeEvaluationError
    # Recursion
    else:
        return 1 + find_length(pair.tail)

def nth(elt, level=0):
    '''
    Find the head at index given when a list of [pair, index] is passed in
    '''
    pair = elt[0]
    index = elt[1]
    # not a pair obj
    if pair == '' or not isinstance(pair, Pair):
        raise CarlaeEvaluationError
    # Base case
    if index == level:
        return pair.head
    # Recursion
    else:
        return nth([pair.tail, index], level+1)


def get_nth(elt, level=0):
    '''
    Find the Pair at index given when a list of [pair, index] is passed in
    '''
    pair = elt[0]
    index = elt[1]
    if not isinstance(pair, Pair):
        raise CarlaeEvaluationError
    # Base Case
    if index == level:
        return pair
    # Recursion
    else:
        return get_nth([pair.tail, index], level+1)
    
def copy(pair):
    '''
    Create a copy of the Pair obj passed in 
    '''
    if pair == '' or pair =='nil':
        return ''
    elif not isinstance(pair, Pair):
        raise CarlaeEvaluationError
    return Pair(pair.head, copy(pair.tail))

def copies(lists):
    new_lists = []
    for l in lists:
        new_lists.append(copy(l))
    return new_lists
def concat(lists):
    '''
    Should take an arbitrary number of lists as arguments
    and return a new list concatenting the lists
    '''
    if isinstance(lists, Pair):
        return lists
    if len(lists) == 0:
         return ''
    elif len(lists) == 1:
        return copy(lists[0])
    
    # deep copy lists
    new_lists = copies(lists)
    ran = len(lists) -1
    for i in range(ran):
        # find the len of the lists for the indexing 
        length = find_length(lists[i])
        # skip if empty
        if lists[i] == '':
             return concat(new_lists[i+1])
        # get the pair at that index
        pair = get_nth([new_lists[i], length-1])
        # set the new tail as the link
        try:
            pair.tail = new_lists[i+1]
        except:
            raise CarlaeEvaluationError
    return new_lists[0]

def check_args(args):
    '''
    Check if the arguments passed in to mapping, filtering, and reducing are proper types
    '''
    if not callable(args[0]) or islist(args[1]) == '@f':
        raise CarlaeEvaluationError

def mapping(args):
    '''
    Takes a function and a list as arguments, 
    returns a new list containing the results of applying 
    the given function to each element of the given list.
    '''
    check_args(args)
    func = args[0]
    L = args[1]
    if L == '':
        return ''
    else:
        return Pair(func([L.head]), mapping([func, L.tail]))

def filtering(args):
    '''
    Takes a function and a list as arguments, 
    returns a new list containing only the elements of the given list for which the given function returns true.
    '''
    check_args(args)
    func = args[0]
    L = args[1]
    if L == '':
        return ''
    else:
        if func([L.head]):
            return Pair(L.head, filtering([func, L.tail]))
        else:
            return filtering([func, L.tail])

def reduce(args):
    '''
    Takes a function, a list, and an initial value as inputs. 
    It produces its output by successively applying the given function to the elements in the list, 
    maintaining an intermediate result along the way. 
    '''
    check_args(args)
    func = args[0]
    L = args[1]
    initial_val = args[2]
    length = find_length(L)
    result = initial_val
    for i in range(length):
        result = func([result, nth([L, i])])
    return result
    
def begin(args):
    '''
    Return last argument of arbitrary expressions evaluated
    '''
    # for arg in args:
    #     result = evaluate(arg, environment=Environment({}, built_env))
    # return result
    return args[-1]
carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])), 
    '*': lambda args: args[0] if len(args) == 1 else (args[0] * carlae_builtins['*'](args[1:])),
    '/': lambda args: 1/args[0] if len(args) == 1 else (args[0] / carlae_builtins['*'](args[1:])),
    '=?': equal,
    '>': greater,
    '>=': geq,
    '<': less,
    '<=': leq,
    '@t': True,
    '@f': False,
    'not': opposite,
    'pair': create_pair,
    'head': get_head,
    'tail': get_tail,
    'list': create_list,
    'list?': islist,
    'length': find_length,
    'nth': nth,
    'concat': concat,
    'map': mapping,
    'filter': filtering,
    'reduce': reduce,
    'begin': begin,
}

###########
# Classes #
########### 

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
    def get_var_env(self, name):
        try:
            # attempt to retrieve the value of the variable
            return self.mapping[name], Environment(self.mapping, self.parent)
        except:
            # try to find it in parent class, or if no parent return None
            if self.parent == None:
                raise CarlaeNameError('parent not found')
            return self.parent.get_var_env(name)
    def set_var(self, name, val):
        # store variable values in dictionary
        self.mapping[name] = val

built_env = Environment(carlae_builtins)


class Function:
    '''
    Represents a Function 
    '''
    def __init__(self, expr, parameters, environment):
        self.expr = expr
        self.parameters = parameters
        self.environment = environment

    def __call__(self, arguments):
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

class Conditionals:
    '''
    Represents conditionals
    '''
    def __init__(self, condition, true_exp, false_exp, environment):
        self.condition = condition
        self.true_exp = true_exp
        self.false_exp = false_exp
        self.environment = environment

    # use check to see if condition is true or false and return expression accordingly
    def check(self):
        print(self.condition)
        result = evaluate(self.condition, self.environment)
        if result == True or result == '@t':
            return evaluate(self.true_exp, self.environment)
        else:
           return evaluate(self.false_exp, self.environment)

class Pair:
    '''
    Represents ordered pairs consisting of two values
    '''
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
    

##############
# Evaluation #
##############

count = 0
def evaluate(tree, environment=Environment({}, built_env)):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # def increment():
    #     global count
    #     count +=1
    #     return count
    # print( '    count', increment())
    print(' mapping', environment.mapping)
    if isinstance(tree, int) or isinstance(tree, float) or isinstance(tree, Function) or isinstance(tree, Pair):
        return tree
    elif tree == 'nil' or tree == '':
        return ''
    elif tree == []:
        raise CarlaeEvaluationError


    # if a variable, look it up
    elif isinstance(tree, str):
        val = environment.get_var(tree)
        if val == None:
            raise CarlaeNameError('variable '+tree+' not found') 
        return val
    

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
    


    # and expression
    elif tree[0] == 'and':
        for exp in tree[1:]:
            # as soon as one is false, return false
            if not evaluate(exp, environment):
                return False
        return True
    # or expression
    elif tree[0] == 'or':
        for exp in tree[1:]:
            # as soon as one is true, return true
            if evaluate(exp, environment):
                return True
        return False



    # deleting, binding, and updating variables
    elif tree[0] == 'del':
        result = environment.mapping.pop(tree[1],'')
        if result == '':
            raise CarlaeNameError('variable '+tree[1]+' not found') 
        return result
    elif tree[0] == 'let':
        new_environment = Environment({}, environment)
        for elt in tree[1]:
            new_environment.set_var(elt[0], evaluate(elt[1], environment))    
        return evaluate(tree[2], new_environment)
    elif tree[0] == 'set!':
        val = evaluate(tree[2], environment)
        old_val, new_environment = environment.get_var_env(tree[1])
        new_environment.set_var(tree[1], val)
        return val

    # if or function expressions
    elif tree[0] == 'if':
        return Conditionals(tree[1], tree[2], tree[3], environment).check()
    # if the tree has a 'function' then create a Function object
    elif tree[0] == 'function' or 'function' in tree:
        return Function(tree[2], tree[1], environment)
    
    # S expression
    else:  
        L = []
        # evaluate each expression
        for exp in tree:
            L.append(evaluate(exp, environment))
        # if a function, just call it with the rest of the list passed in
        if callable(L[0]) or isinstance(L[0], Pair):
            return L[0](L[1:])
        # not a function, raise an error
        else:
            raise CarlaeEvaluationError

         
def result_and_env(tree, environment=None):
    if environment ==None:
        environment = Environment({}, built_env)
    # returns evalulate result and the environment associated with it
    return evaluate(tree, environment), environment
    

def evaluate_file(filename, environment=Environment({}, built_env)):
    f = open(filename, 'r')
    # print(f.read().splitlines())
    return evaluate(parse(tokenize(f.read())), environment)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    doctest.testmod()
    environment=Environment({}, built_env)
    lab_name = sys.argv[0]
    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        evaluate_file(filename,environment)

    user_input = input('in> ')
    
    while user_input != 'EXIT':
        try:
            print('   out> ', evaluate(parse(tokenize(user_input)), environment))
        except Exception as e:
            print('input invalid')
            print(e)
            pass
        user_input = input('in> ')
