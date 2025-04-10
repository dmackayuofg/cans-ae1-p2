def stripComments(programText):
    split = programText.split(" ")
    split = "\n".join(split)
    split = split.split("\n")
    while "" in split:
        split.remove("")
    while "(" in split:
        for i, token in enumerate(split):
            if token == "(":
                split.pop(i)
                while split[i] != ")":
                    split.pop(i)
                split.pop(i)
                break
    return " ".join(split)


programText = """ |0100 ;array LDA ;array ( comment2 ) #01 ADD LDA ADD ;print JSR2 BRK ( comment ) @print #18 DEO JMP2r @array 11 22 33 """
programText2 = """
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
#print(programText)
print(stripComments(programText))
print(stripComments(programText2))