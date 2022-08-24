# *carlae*

## Introduction

In this lab, you will implement an interpreter for a dialect of LISP, one of the earliest high-level programming languages (it was invented by John McCarthy at MIT in 1958!). Because this language will in some ways be quite small compared to Python, we'll call it carlae, after Leptotyphlops carlae. Its syntax is simpler than Python's, and the complete interpreter will fit in a single Python file. However, despite its small size, the language we will implement here will be Turing Complete, i.e., in theory, it will be able to solve any possible computational problem (so it would be possible, for example, to implement the HyperMines program from week 4 in carlae).

## LISP and carlae
As with most LISP dialects, the syntax of carlae is far simpler than that of Python. All-in-all, we can define the syntax of carlae as follows:
- *carlae programs* consist solely of expressions. There is no statement/expression distinction
- Numbers (e.g. 1) and symbols (e.g. x) are called atomic expressions; they cannot be broken into pieces. These are similar to their Python counterparts, except that in carlae, operators such as + and > are symbols, too, and are treated the same way as x and fib.
- Everything else is an S-expression: an opening round bracket (, followed by zero or more expressions, followed by a closing round bracket ). The first subexpression determines what it means:
  - An S-expression starting with a keyword, e.g. (if ...), is a special form; the meaning depends on the keyword.
  - An S-expression starting with a non-keyword, e.g. (fn ...), is a function call, where the first element in the expression is the function to be called, and the remaining subexpressions represent the arguments to that function.

And that's it! The whole syntax is described by the three bullet points above. For example, consider the following definiion of a function that computes Fibonacci numbers in Python:
```
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
```
We could write an equivalent program in carlae:
```
(define fib 
  (lambda (n)
    (if (<= n 1)
      n
      (+ (fib (- n 1)) (fib (- n 2)))
    )
  )
)
```
Using so many parentheses might take some getting used to, but it helps to keep the language simple and consistent. Some people have joked that LISP stands for "Lots of Insipid and Silly Parentheses," though some might argue instead that it stands for "Lisp Is Syntactically Pure" :)

## Interpreter Design
Despite its small size, the interpreter for carlae will still be rather complicated. To help manage this complexity, we'll start with a very small language, and we'll gradually add functionality until we have a fully-featured language. As with most interpreters, we will think of our carlae interpreter as consisting of three parts:

- A *tokenizer*, which takes a string as input and produces a list of tokens, which represent meaningful units in the programming language.
- A *parser*, which takes the output of the lexer as input and produces a structured representation of the program as its output.
- An *evaluator*, which takes the output of the parser as input, and actually handles running the program.

## Tokenizer
Our first job is lexing (or tokenizing). In carlae, we'll have exactly three kinds of tokens: opening round brackets (, closing round brackets ), and everything else (separated by whitespace). Your first task for the lab is to write a function called tokenize, which takes a single string representing a program as its input and outputs a list of tokens. For example, calling tokenize("(foo (bar 3.14))") should give us the following result: ['(', 'foo', '(', 'bar', '3.14', ')', ')']

Unlike in Python, whitespace does not matter, so, for example, the tokenize function should produce exactly the same output for both of the following programs:
```
(define circle-area
  (lambda (r)
    (* 3.14 (* r r))
  )
)
```
```
(define circle-area (lambda (r) (* 3.14 (* r r))))
```

Your tokenize function should also handle comments. Comments in carlae are prefixed with a semicolon (;), instead of the octothorpe (#) used by Python. If a line contains a semicolon, the tokenize function should not consider that semicolon or the characters that follow it on that line to be part of the input program.

## Parser

Our next job is parsing the list of tokens into an abstract syntax tree, a structured representation of the expression to be evaluated. Implement the parse function in lab.py. parse should take a single input (a list of tokens as produced by tokenize) and should output a representation of the expression, where:

- a number is represented as an instance of int or float
- a symbol is represented as a string
- an S-expression is represented as a list of its parsed subexpressions
For example, the program above that defined circle-area should parse as follows:
```
['define', 'circle-area', ['lambda', ['r'], ['*', 3.14, ['*', 'r', 'r']]]]
```
Note that the structure of the parser's output is such that a recursive solution is likely the "path of least resistance."

In the case that parentheses are mismatched in the input, the function should raise a SyntaxError.

## Evaulator
We'll hold off on implementing variables, lists, conditionals, and functions for a little while; for now, we'll start by implementing a small calculator that can handle the + and - operations.

Note that we have provided a dictionary called carlae_builtins in lab.py, which maps the names + and - to functions. Each of these functions takes a list as an argument and returns the appropriate value.

Define a function evaluate, which takes as its sole input an expression of the same form as the parser's output. evaluate should return the value of the expression:

- If the expression is a symbol of a name in carlae_builtins, it should return the associated object.
- If the expression is a number, it should return that number.
- If the expression is a list (representing an S-expression), each of the elements in the list should be evaluated, and the result of evaluating the first element (a function) should be called with the remaining elements passed in. The overall result of evaluating such a function is the return value of that function call.
- If the expression is a symbol that is not in carlae_builtins, or is a list whose first element is not a function, it should raise an EvaluationError exception.

## Testing: REPL
It is kind of a pain to have to type out all of the arguments to evaluate each time we call it. As such, we'll implement a REPL (a "Read, Evaluate, Print Loop) for carlae. A REPL has a simple job: it continually prompts the user for input until they type QUIT. Until then, it:

- accepts input from the user,
- tokenizes and parses it,
- evaluates it, and
- prints the result
If an error occurs during any of these steps, an error message should be displayed and that expression may be ignored, but the program should not exit.

To implement the REPL, we can make use of Python's built-in input function. input takes an argument representing a prompt to be displayed to the user and returns the string that they type (it is returned when they hit enter).

The following shows one possible interaction with a REPL, with a particular prompt and output formatting (you are welcome to use whatever formatting you like!):
```
in> (+ 2 3)
  out> 5

in> (+ 2 (- 3 4))
  out> 1

in> (- 3.14 1.14 1)
  out> 1.0000000000000004

in> (+ 2 (- 3 4 5))
  out> -4

in> QUIT
```
Implement a REPL for carlae and use it to test your evaluator. The REPL can/should be one of your main means of testing moving forward; feel free to try things out using the REPL as you work through the remainder of the lab. The functionality of your REPL will not be tested automatically; rather, it will be tested during the checkoff. The REPL should only start when the lab is run directly, not when lab.py is imported from another script.

## Variables
Next, we will implement our first special form: variable definition using the define keyword.

A variable definition has the following syntax: (define NAME EXPR), where NAME is a symbol and EXPR is an arbitrary expression. When carlae evaluates a define expression, it should associate the name NAME with the value that results from evaluating EXPR. In addition, the define expression should evaluate to the result of evaluating EXPR.

The following transcript shows an example interaction using the define keyword:
```
in> (define pi 3.14)
  out> 3.14

in> (define radius 2)
  out> 2

in> (* pi radius radius)
  out> 12.56

in> QUIT
```
Note that define differs from the function calls we saw earlier. It is a special form that does not evaluate the symbol that follows it; it only evaluates the expression the follows the name. As such, we will have to treat it differently from a normal function call.

In addition, in order to think about how to implement define, we will need to talk about the notion of environments.

## Environments
Admitting variable definition into our language means that we need to be, in some sense, more careful with the process by which expressions are evaluated. We will handle the complexity associated with variable definition by maintaining structures called environments. An environment consists of bindings from variable names to values, and possibly a parent environment, from which other bindings are inherited. One can look up a name in an environment, and one can bind names to values in an environment.

The environment is crucial to the evaluation process, because it determines the context in which an expression should be evaluated. Indeed, one could say that expressions in a programming language do not, in themselves, have any meaning. Rather, an expression acquires a meaning only with respect to some environment in which it is evaluated. Even the interpretation of an expression as straightforward as (+ 1 1) depends on an understanding that one is operating in a context in which + is the symbol for addition. Thus, in our model of evaluation we will always speak of evaluating an expression with respect to some environment.

To describe interactions with the interpreter, we will suppose that there is a "global" environment, consisting of bindings of the names of built-in functions and constants to their associated values. For example, the idea that + is the symbol for addition is captured by saying that the symbol + is bound in this global environment to the primitive addition procedure we defined above.

One necessary operation on environments is looking up the value to which a given name is bound. To do this, we can follow these steps:
- If the name has a binding in the environment, that value is returned.
- If the name does not have a binding in the environment and the environment has a parent, we look up the name in the parent environment (following these same steps).
- If the name does not have a binding in the environment and the environment does not have a parent, an EvaluationError is raised.
Note that looking up a name in an environment is similar to looking up a key in a dictionary, except that if the key is not found, we continue looking in parent environments until we find the key or we run out of parents to look in.

In order to make variables work properly, you will need to implement the kind of lookup described above in Python. It is up to you to decide how to implement environments and the associated lookups; your implementation will not be tested directly by the automatic checker, but rather will be tested by looking at the end-to-end behavior of your evaluator. Regardless of how you implement environments, you should make sure your environment representation can handle variables with arbitrary names, and you should be prepared to discuss your implementation during the checkoff.

## Booleans and Comparisons
In order to implement if, we will need a way to represent Boolean values in carlae. This decision is up to you, but no matter your choice of representation, you should make these values available inside of carlae as literals #t and #f, respectively. We will also need several additional functions, all of which should take arbitrarily-many arguments:

- =? should evaluate to true if all of its arguments are equal to each other.
- > should evaluate to true if its arguments are in decreasing order.
- >= should evaluate to true if its arguments are in nonincreasing order.
- < should evaluate to true if its arguments are in increasing order.
- <= should evaluate to true if its arguments are in nondecreasing order.
As well as the following Boolean combinators:

- and should be a special form that takes arbitrarily many aguments and evaluates to true if all of its arguments are true. It should only evaluate the arguments it needs to evaluate to determine the result of the expression.
- or should be a special form that takes arbitrarily many arguments and evaluates to true if any of its arguments is true. It should only evaluate the arguments it needs to evaluate to determine the result of the expression.
- not should be a function that takes a single argument and should evaluate to false if its argument is true, and true if its argument is false.
After implementing these functions, modify your evaluate function so that it properly handles the if special form. Once you have done so, your code should pass all 34 tests in test.py.

With this addition, your interpreter should be able to handle recursion! Try running the following pieces of code from your REPL to check that this is working:

```
in> (define (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))
in> (factorial 6)
```
