from uwuipy import uwuipy
import re
import sys

debug = True

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#    > Script to UwUify localization files for Warhammer 40,000 Darktide mods
#    > Author: Backup158
#    > Initial creation: 2024-12-24
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# GLOBAL VARIABLES
# Regex values
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# doing '(regex)' means the delimiter stays in the list    
# doing '(?:regex)' means match but don't include delimiter

# ### Reusable Regex Groups ###
regexColoredVar = '[a-zA-Z|_|\.|0-9]*'        # variables include alphabet (up and lower), numbers, _, and .
regexWhitespace = '(\s)*?'        # at the start of the line, match whitespace which may or may not be there
regexSingleQuote = '(\")'
regexNotNewline = '([^\n])'

# ### Entire Lines ###
# Judging from the start
regexEn = regexWhitespace + 'en = '        # 

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

##################################
# Print Seperators and Lists
##################################
def printSep(indent):
    string = '==============='
    for i in range(indent) : string += string
    print(string)
    
def printList(list, indent):
    printSep(indent)
    for i in list:
        space = ''
        for j in range(indent) : space += '\t'
        print(f'{space}>{i}')
    printSep(indent)
    
################################
# Cleans up uwuified text
################################
def cleanuwu(uwutext):
    if debug: print('cleaning uwu text')

    # Double tilde must come first
    # ~~-~~-~~- needs to be ~~, not ~~~ (which happens if you only remove ~- first)
    # replacing "- would normally cause issues with bullet points, so i did the mass replacement with tilde before processing
    # ˝ is that whackass diacritic from earlier versions
    # for \\, it's to avoid stammering with escape characters. hypens need no escape so we good
    # quotation mark, curly brace, period, comma, whackass diacritc, asterisk, double tilde, tilde, backslash, forward slash, paranthesis
    charsToExclude = ['"', '{', '.', ',', '˝', '*', '~~', '~', '\\', '/', '(']
    newuwu = uwutext
    for i in charsToExclude:
        exclusion = i + '-'
        # if debug: print(f'\treplacing {exclusion}')
        newuwu = newuwu.replace(exclusion, '')

    newuwu = newuwu.replace("***breaks into your house and aliases neofetch to rm -rf --no-preserve-root /*** ", '')        # removes funny root action because that fucks my formatting
    newuwu = newuwu.replace(" ***breaks into your house and aliases neofetch to rm -rf --no-preserve-root /***", '')        # in case the space is on the wrong side
    return newuwu

################################
# Clear None
# Given a list of strings and string saying what the name is (purely for debug printing)
# Removes 'bad' values from the list:
#    None
#    empty strings
# Returns the list without these values
################################
def clearNone(substrings, which):
    if debug: print(f'== == Cleaning {which} == ==')
    # add substrings if they are not None, empty string, or only whitespace
    # exceptions for newline (fucks up formatting if not included) and single spaces (which are put between variables)
    substringsCleaned = [i for i in substrings if i is not None and i != '' and (i.isspace() == False or i == '\n' or i == ' ')]
    if debug: printList(substringsCleaned,1)
    return substringsCleaned

#################################################################
# Split En
# given a line that begins with en = "<words>",
# returns a list of substrings: en = 
#                               "
#                               <words>
#                               "
#                               ,
#################################################################
def substringsEnSplit(line):
    substrings = re.split('(")', line)
    if debug: printList(substrings,0)
    
    substrings = clearNone(substrings, 'SplitLocal')

    if debug: 
        print('++ ++ ++ Split Local')
        printList(substrings,1)
    return substrings

#################################################################
# Parse Line
# given list of strings, coming from a line that's been broken into substrings
#    given uwuifier to use
#    given position of the quoted text
# returns a string that will be used to replace the original line
#################################################################
#def parseLine(substrings, uwu):
def parseLine(substrings, uwu, textPos):
    finalLine = ''
    for i in range(len(substrings)):
        if debug: print(f'+++ Processing {substrings[i]}')
        
        if i == textPos:
            if debug: print(f'uwuifying!!!\n\t{substrings[i]}')
            uwutext = uwu.uwuify(substrings[i])
            uwutext = cleanuwu(uwutext)
            if debug: print(f'\t vvvvvvv \n\t{uwutext}')
            finalLine += uwutext
        else:
            finalLine += substrings[i]
            
    if debug: print(f'\tFinal line is {finalLine}')
    return finalLine
    
####################
# Parse Line - En
# given a string: line of localization for english
# splits and uwuifies it
#    en = 
#   "
#    - quoted text                << position 2
#    "
#    ,
# returns a string that will be used to replace the original line
####################
def parseLineEn(line, uwu):
    
    substrings = substringsEnSplit(line)
    finalLine = parseLine(substrings, uwu, 2)
    
    return finalLine

#################################################################
# File Replacement
# given a file to read and temporary file to write to
# reads file line by line and writes its replacement to the writeFile
#    copies old line if not replacable
#    uses new string if replacable
#################################################################
def replace(fileRead, fileWrite):
    input_file = open(fileRead, "r")    
    output_file = open(fileWrite, "w")
    lineCount = 0

    uwu = uwuipy(None, 0.33, 0, 0.22, 1, True)        # seed, stutterChance, faceChance, actionChance, exclamationsChance, nsfw, 
    #uwu = uwuipy(None, 0.33, 0, 0.22, 1, True, 1)     # power 1-4. only on v0.1.9
    #uwu2 = Uwuipy(None, 0.33, 0, 0.22, 1, True, 2)
    #uwuSuper = Uwuipy(None, 0.33, 0, 0.22, 1, True, 4)
    
    for line in input_file:
        lineCount = lineCount + 1
        if debug: print(f'############# New Line {lineCount}!!!! #############')
        # Checking line to see if it's one of those that contains quoted text
        # re.match checks the BEGINNING
        match_en = re.match(regexEn, line)                # line is en = "asdfhasl",
        if match_en:
            cleanedUwu = parseLineEn(line, uwu)
            if debug: print(f'{lineCount}: found the line: {line}\n\treplacing with: {cleanedUwu}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            output_file.write(cleanedUwu)
        else:
            if debug: print(f'{lineCount}: doesnt match any known regex')
            output_file.write(line)
            
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# main execution
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
if __name__ == "__main__":
    ### terminal argument method ###
    # first argument is this script
    # iterates through all other arguments
    for i in range(1, len(sys.argv)):
        if debug: print(f'replacing {sys.argv[i]}')
        replace(sys.argv[i], f'uwu_{sys.argv[i]}')
    
    ### input method ###
    #fileName = input('Input the name of the file you want to replace: ')
    #replace(fileName, "res.lua")
