'''
ELIZA Chatbot
Lydia Noureldin

A class to store keywords for Eliza
each keyword must have a minimum of one regular expression and reassembly rules associatated with it and at most
 2 regular expressions and reassembly rules.

 Attributes:
     string name
     int rank
     int numRegex
     string[] regexLis
     string[][] reasmbLis
     int[][] usedResp
     string[] synonyms

Fucntions:
    __init__
    __str__
    setUsedResp
    setAttr
    updateUsedResp
    addSynonyms

'''


class Keyword:

    # constructor
    def __init__(self, na, ra, reg, rea, reg2=None, rea2=None, reg3=None, rea3=None, reg4=None, rea4=None, \
                 reg5=None, rea5=None, reg6=None, rea6=None, reg7=None, rea7=None, reg8=None, rea8=None, \
                 reg9=None, rea9=None, reg10=None, rea10=None):
        self.name = na  # keyword name
        self.rank = ra  # keyword rank
        self.numRegex = 0  # indicates how many regular expressions are available
        self.regexLis = []  # list that holds the regular expression(s)
        self.reasmbLis = []  # list of lists that holds the responses for the regex
        self.usedResp = []  # list of lists that keeps track of which responses have been used for each regex
        self.synonyms = []  # lis of synonyms of the Keyword's name
        # there are 10 lists because 10 is the maximum number of regular expressions that a keyword can have
        for i in range(10):
            self.usedResp.append([])

        # List of potential attributes, before we set them we need to make sure they're not None
        potentialAttributes = []
        potentialAttributes.extend([reg, rea, reg2, rea2, reg3, rea3, reg4, rea4, reg5, rea5, reg6, rea6, reg7, rea7\
                                   , reg8, rea8, reg9, rea9, reg10, rea10])
        # Now we set regexLis, reasmbLis, usedResp, and numRegex
        for i in range(0, (len(potentialAttributes)), 2):
            self.setAttr(potentialAttributes[i], potentialAttributes[i+1], i)

    # Sets the regexLis, reasmbLis, usedResp, and numRegex
    def setAttr(self, reg, rea, numR):
        if reg is not None and rea is not None:
            self.regexLis.append(reg)
            self.reasmbLis.append(rea)
            # divide numR by 2 becasue in the for loop we are taking steps of 2
            self.setUsedResp(rea, (int(numR/2)))
            self.numRegex += 1

    def setUsedResp(self, reasmb, regExIndex):
        for i in range(len(reasmb)):  # One for each response for that particular regex
            # set the values to 0 because none have been used yet
            self.usedResp[regExIndex].append(0)


    # this fuction updates the usedResp array that is needed to always select the least used response.
    # numArray indicates which usedResp array we need to update. This depends on the regular expression
    # that was matched. listIndex represents the response that was used from the corresponding reasmb array
    def updateUsedResp(self, numArray, respUsedIndex):
        self.usedResp[numArray][respUsedIndex] += 1

    # this is an optional attribute that the user can add to the Keyword
    def addSynonyms(self, synonymsLis):
        self.synonyms = synonymsLis

    # String output for the Keyword object

    def __str__(self):
        output = "\nKeyword name: " + self.name + "\nRank: " + str(self.rank) +\
                 "\nNumber of Regular Expressions: " + str(self.numRegex)
        # add these to the output string if they exist
        for i in range(self.numRegex) :
            output += "\nRegular Expression " + str(i + 1) + ": " + str(self.regexLis[i]) + "\nReasembly " +\
                      str(i + 1) + ": " + str(self.reasmbLis[i]) + "\nUsed Responses " + str(i + 1) +\
                      ": " + str(self.usedResp[i])
        if len(self.synonyms) > 0 :
            output += "\nSynonyms: " + str(self.synonyms)
        output += "\n\n"
        return output





