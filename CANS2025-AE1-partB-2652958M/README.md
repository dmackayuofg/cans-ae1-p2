# Status report

## Overview and usage
My uxntal interpreter script is able to read in an arbitrary .tal file through the command line, in the format `python .\uxntal-interpreter.py .\some_program.tal`.  
There are optional command line arguments available.  
- WW
- V
- VV
- DBG
WW will print a warning for incompatible stack size operations.  
V will print verbose info.  
VV will print very verbose info.  
DBG will print extra debug info like stack state at every instruction.  

## Test cases  
The interpreter passes each of the tests, returning the same result as an official uxntal assembler and cli.  

## Arbitrary program  
Included is also a non trivial uxntal program that I wrote. It's purpose is to print the string "Five Times Table", and then print out the five times table. Necessary functions created for this task are a hexadecimal to ascii converter (2 digit max), and a modulus operator function, as uxntal does not provide one.  
Credit for the title print string goes to the provided file ex10_hello-world.tal.  

## Issues
My interpreter currently has no issues that I have directly encountered. Any issues I found when I ran the tests or wrote my program have since been fixed. However, I made little attempt to explicitly implement operation size checking (checking that the current instruction has correct size type for the arguments on the stack). Although this did not cause me any issues when writing my program / running the tests.  