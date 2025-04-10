#! Comments of this style (`#!` or `#!!`) indicate code that needs completing or changing
#! A `#!!` "should" or means "must"; `#!` means "could"
#! "should" or "must" means you'll lose marks if you don't do it
#! "could" or "(optional)" means you can get extra marks for doing it, but you don't lose marks for not doing it

from enum import Enum
import sys

#! Your program could set these flags on command line
WW = False
V = False # Verbose, explain a bit what happens
VV = False # More verbose, explain in more detail what happens
DBG = False # Debug info

TRACE = 0

#!! Your program must take the path to an abitrary `.tal` file on command line and
programFile=sys.argv[1]

if len(sys.argv) > 1:
    if "V" in sys.argv[1:]:
        V = True
    if "VV" in sys.argv[1:]:
        VV = True
    if "DBG" in sys.argv[1:]:
        DBG = True
    
print(WW, V, VV, DBG)
#!! read the program text
print(programFile)
exit()

programText = """
|0100
;array LDA
;array #01 ADD LDA
ADD
;print JSR2
BRK

@print
    #18 DEO
JMP2r

@array 11 22 33
"""

# These are the different types of tokens
class T(Enum):
    MAIN = 0 # Main program
    LIT = 1 # Literal
    INSTR = 2 # Instruction
    LABEL = 3 # Label
    ABSREF = 4 # Address reference (rel=1, abs=2)
    RELREF = 5 # Address reference (rel=1, abs=2)
    RAW = 6 # Raw values (i.e. not literal)
    ABSPAD = 7 # Address (absolute padding)
    RELPAD = 8 # Relative padding)
    EMPTY = 9 # Memory is filled with this by default

# We use an object to group the data structures used by the Uxn interpreter
class Uxn:
    memory = [(T.EMPTY,)] * 0x10000 # The memory stores *tokens*, not bare values
    stacks = ([],[]) # ws, rs # The stacks store bare values as tuples (value, size)
    # where size is the size in bytes (1=byte, 2=short)
    progCounter = 0
    symbolTable={}
    # First unused address, only used for verbose
    free = 0

#!! Complete the parser
def parseToken(tokenStr):
    if tokenStr[0] == '#':
        valStr=tokenStr[1:]
        val = int(valStr,16)
        if len(valStr)==2:
            return (T.LIT,val,1)
        else:
            return (T.LIT,val,2)
    if tokenStr[0] == '"':
        chars =list(tokenStr[1:])
        return list(map(lambda c: (T.LIT, ord(c),1),chars))
    elif tokenStr[0] == ';':
        val = tokenStr[1:]
        return (T.ABSREF,val,2)
#!! Handle relative references `,&`
    elif tokenStr[0:2] == ',&':
        val = tokenStr[2:]
        return (T.RELREF,val,1)
    elif tokenStr[0] == '@':
        val = tokenStr[1:]
        return (T.LABEL,val)
#!! Handle relative labels `&`
    elif tokenStr[0] == '&':
        val = tokenStr[1:]
        return (T.LABEL,val)
    elif tokenStr == '|0100':
        return (T.MAIN,)
#! Handle absolute padding (optional)
    elif tokenStr[0] == '|':
        val = tokenStr[1:]
        return (T.ABSPAD,val,2)
#! Handle relative padding
    elif tokenStr[0] == '$':
        val = tokenStr[1:]
        return (T.RELPAD,val,1)
    elif tokenStr[0].isupper():
        # Any token string starting with an uppercase letter is considered an instruction
        if len(tokenStr) == 3:
            return (T.INSTR,tokenStr[0:len(tokenStr)],1,0,0)
        elif len(tokenStr) == 4:
            if tokenStr[-1] == '2':
                return (T.INSTR,tokenStr[0:len(tokenStr)-1],2,0,0)
            elif tokenStr[-1] == 'r':
                return (T.INSTR,tokenStr[0:len(tokenStr)-1],1,1,0)
            elif tokenStr[-1] == 'k':
                return (T.INSTR,tokenStr[0:len(tokenStr)-1],1,0,1)
        elif len(tokenStr) == 5:
            # Order must be size:stack:keep
            if tokenStr[len(tokenStr)-2:len(tokenStr)] == '2r':
                return (T.INSTR,tokenStr[0:len(tokenStr)-2],2,1,0)
            elif tokenStr[len(tokenStr)-2:len(tokenStr)] == '2k':
                return (T.INSTR,tokenStr[0:len(tokenStr)-2],2,0,1)
            elif tokenStr[len(tokenStr)-2:len(tokenStr)] == 'rk':
                return (T.INSTR,tokenStr[0:len(tokenStr)-2],1,1,1)
        elif len(tokenStr) == 6:
            return (T.INSTR,tokenStr[0:len(tokenStr)-1],2,1,1)
    else:
        # we assume this is a 'raw' byte or short
        return (T.RAW,int(tokenStr,16))

# These are the actions related to the various Uxn instructions

# Memory operations
# STA
def store(args,sz,uxn):
    uxn.memory[args[0]] = ('RAW',args[1],0)

# LDA
def load(args,sz, uxn):
    return uxn.memory[args[0]][1] # memory has tokens, stacks have values

# Control operations
# JSR
def call(args,sz,uxn):
    # print("CALL:",args[0],uxn.progCounter)
    uxn.stacks[1].append( (uxn.progCounter,2) )
    uxn.progCounter = args[0]-1
# JMP
def jump(args,sz,uxn):
    uxn.progCounter = args[0]
# JCN
def condJump(args,sz,uxn):
    if args[1] == 1 :
        uxn.progCounter = args[0]-1

# Stack manipulation operations
# STH
def stash(rs,sz,uxn):
    uxn.stacks[1-rs].append(uxn.stacks[rs].pop())

#!! Implement POP (look at `swap`)
#! def pop(rs,sz,uxn):
    #! ...

# SWP
def swap(rs,sz,uxn):
        b = uxn.stacks[rs].pop()
        a = uxn.stacks[rs].pop()
        uxn.stacks[rs].append(b)
        uxn.stacks[rs].append(a)

# This implementation of NIP checks if the words on the stack match the mode (short or byte)
#! Your implementations of the other stack operations don't need to do this
def nip(rs,sz,uxn): # a b -> b
        b = uxn.stacks[rs].pop()
        if b[1]==sz:
            a = uxn.stacks[rs].pop()
            if a[1]==sz:
                uxn.stacks[rs].append(b)
            else:
                print("Error: Args on stack for NIP",sz,"are of wrong size")
                exit()
        elif b[1]==2 and sz==1:
            bb = b[0]&0xFF
            uxn.stacks[rs].append( (bb,1) )
        elif b[1]==1 and sz==2:
            print("Error: Args on stack for NIP",sz,"are of wrong size")
            exit()

#!! Implement ROT (look at `swap`)
#! def rot(rs,sz,uxn): # a b c -> b c a
    #! ...

def dup(rs,sz,uxn):
        a = uxn.stacks[rs][-1]
        uxn.stacks[rs].append(a)

def over(rs,sz,uxn): # a b -> a b a
        a = uxn.stacks[rs][-2]
        uxn.stacks[rs].append(a)

# ALU operations
# ADD
def add(args,sz,uxn):
    return args[0] + args[1]

#!! Implement SUB, MUL, DIV, INC (similar to `ADD`)
#! def sub(args,sz,uxn):
#!    ...
# def mul(args,sz,uxn):
#!    ...
# def div(args,sz,uxn):
#!    ...

#!! Implement EQU, NEQ, LTH, GTH (similar to `ADD`)
#! def equ(args,sz,uxn):
#!    ...
# def neq(args,sz,uxn):
#!    ...
# def lth(args,sz,uxn):
#!    ...
# def gth(args,sz,uxn):
#!    ...

callInstr = {
#!! Add SUB, MUL, DIV, INC; EQU, NEQ, LTH, GTH
    'ADD' : (add,2,True),
    'DEO' : (lambda args,sz,uxn : print(chr(args[1]),end=''),2,False),
    'JSR' : (call,1,False),
    'JMP' : (jump,1,False),
    'JCN' : (condJump,2,False),
    'LDA' : (load,1,True),
    'STA' : (store,2,False),
    'STH' : (stash,0,False),
    'DUP' : (dup,0,False),
    'SWP' : (swap,0,False),
    'OVR' : (over,0,False),
    'NIP' : (nip,0,False)
#!! Add POP, ROT

}

def executeInstr(token,uxn):
    global TRACE
    TRACE=TRACE+1

    _t,instr,sz,rs,keep = token
    if instr == 'BRK':
        if V:
            print("\n",'*** DONE *** ')
        else:
            print('')
        if VV:
            print('PC:',uxn.progCounter,' (WS,RS):',uxn.stacks)
        exit('TRACE'+str(TRACE))
    action,nArgs,hasRes = callInstr[instr]
    if nArgs==0: # means it is a stack manipulation
        action(rs,sz,uxn)
    else:
        args=[]
        for i in reversed(range(0,nArgs)):
            if keep == 0:
                arg = uxn.stacks[rs].pop()
                if arg[1]==2 and sz==1 and (instr != 'LDA' and instr!= 'STA'):
                    if WW:
                        print("Warning: Args on stack for",instr,sz,"are of wrong size (short for byte)")
                    uxn.stacks[rs].append( (arg[0]>>8,1) )
                    args.append((arg[0]&0xFF))
                else: # either 2 2 or 1 1 or 1 2
                    args.append(arg[0]) # works for 1 1 or 2 2
                    if arg[1]==1 and sz==2:
                        arg1 = arg
                        arg2 = uxn.stacks[rs].pop()
                        if arg2[1]==1 and sz==2:
                            arg = (arg2[0]<<8) + arg1[0]
                            args.append(arg) # a b 
                        else:
                            print("Error: Args on stack are of wrong size (short after byte)")
                            exit()
            else:
                arg = uxn.stacks[rs][i]
                if arg[1]!= sz and (instr != 'LDA' and instr!= 'STA'):
                    print("Error: Args on stack are of wrong size (keep)")
                    exit()
                else:
                    args.append(arg[0])
        if VV:
            print('EXEC INSTR:',instr, 'with args', args)
        if hasRes:
            res = action(args,sz,uxn)
            if instr == 'EQU' or instr == 'NEQ' or instr == 'LTH' or instr == 'GTH':
                uxn.stacks[rs].append( (res,1) )
            else:
                uxn.stacks[rs].append( (res,sz) )
        else:
            action(args,sz,uxn)

#!! Tokenise the program text using a function `tokeniseProgramText`
#! That means splitting the string `programText` on whitespace
#! You must remove any comments first, I suggest you use a helper function stripComments
#! which should return the program text without comments
def stripComments(programText):
    #! ...
    return [] #! replace this with the actual code
#! `tokenStrings` is a list of all tokens as strings
def tokeniseProgramText(programText):
    #! ...
    return [] #! replace this with the actual code

def populateTokens(tokensWithStrings):
    global TRACE
    TRACE=TRACE+1    
    tokens=[]
    #! ...
    return tokens

# This is the first pass of the assembly process
# We store the tokens in memory and build a dictionary
# uxn.symbolTable: label => address
def populateMemoryAndBuildSymbolTable(tokens,uxn):
    global TRACE
    TRACE=TRACE+1

    pc = 0
    for token in tokens:
        if token == (T.MAIN,):
            pc = 0x0100
        elif token[0] == T.ABSPAD:
            pc = token[1]
        elif token[0] == T.RELPAD: # relative only
            pc = pc + token[1]
        elif token[0] == T.LABEL:
            labelName = token[1]
            uxn.symbolTable[labelName]=pc
        else:
            uxn.memory[pc]=token
            pc = pc + 1
    uxn.free = pc

# Once the symbol table has been built, replace every symbol by its address
#!! Implement the code to replace every label reference by an address
#! Note that label references are `*REF` tokens and the memory stores the symbolTable as `LIT` tokens
#! Loop over all tokens in `uxn.memory``. If a token is `*REF`, look it up in `uxn.symbolTable`` and create a `LIT` token that contains its address. Write that to the memory.
#! (This is what happens in Uxn: `;label` is the same as `LIT2 =label` and that gets replaced by `LIT2 address`)

def resolveSymbols(uxn):
    global TRACE
    TRACE=TRACE+1    
    #!  ...

# Running the program mean setting the program counter `uxn.progCounter` to the address of the first token;
#  - read the token from memory at that address
# - if the token is a LIT, its *value* goes on the working stack
# - otherwise it is an instruction and it is executed using `executeInstr(token,uxn)`
# - then we increment the program counter
#!! Implement the above functionality
def runProgram(uxn):  
    if VV:
        print('*** RUNNING ***')
    uxn.progCounter = 0x100 # all programs must start at 0x100
    while True:
#!! read the token from memory at that address
        #! token = ...
        if DBG:
            print('PC:',uxn.progCounter,' TOKEN:',token)
        #! You can use an if/elif if you prefer; there are only two cases (and an optional third to catch potential errors)
        #! because the program at this point consists entirely of instructions and literals
        #! match ...:
        #!     case ...:
        #!         ...
        #!     case ...:
        #!         ...
#!! Increment the program counter
        #! ...
        if DBG:
            print('(WS,RS):',uxn.stacks)

uxn = Uxn()
programText_noComments = stripComments(programText)
tokenStrings = tokeniseProgramText(programText_noComments)
tokensWithStrings = map(parseToken,tokenStrings)
tokens = populateTokens(tokensWithStrings)

populateMemoryAndBuildSymbolTable(tokens,uxn)

resolveSymbols(uxn)

if DBG:
    for pc in range(256,uxn.free):
        print(pc,':',uxn.memory[pc])
    print('')
if VV:
    print(programText)

runProgram(uxn)

