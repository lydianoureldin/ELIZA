'''
ELIZA Chatbot
Lydia Noureldin

Attributes:
    dict reflections
    string[][][] psychobabble
    Keyword[] keys
    int[][] usedResponses
    string[] memoryLis

Functions:
    __init__
    reflect
    analyze
    getRankedResponse
    getKey
    leastUsedKeyResp
    getGeneralResponse
    leastUsedResponse
    findPatternIndex
    getHighestRank
    getWords
    Mutators:
        setUsedResponses
        setKeys
'''

import re
import string  # used to get rid of punctuation efficiently
from Keyword import Keyword

class Eliza :

    def __init__(self, refl, psychob):
        self.reflections = refl
        self.psychobabble = psychob  # This is the general psychobabble that is only used if no keywords are matched
        self.keys = []
        self.setKeys()
        self.usedResponses = []
        self.setUsedResponses()  # set the general array that keeps track of the responses in psychobable
        self.memoryLis = []  # the list that will be used to store previous responses, giving Eliza memory

    def reflect(self, fragment):
        tokens = fragment.lower().split()
        for i, token in enumerate(tokens):
            if token in self.reflections:
                tokens[i] = self.reflections[token]
        return ' '.join(tokens)


    def analyze(self, statement):
        statement = statement.split(".")[0]
        words = self.getWords(statement)  # break up the user input by " " in a list called words
        # find the word in the user input with the highest rank if it exists and has reasembly rules that match the user's statement
        maxRankIndex = self.getHighestRank(words, statement)
        if maxRankIndex == -1:  # no keyword was found in the user input
            # check if there is something saved in memory to use
            if len(self.memoryLis) != 0:
                response = self.memoryLis[0]
                self.memoryLis.pop(0)  # removes the response
            # Get general response from  psychobable and updated usedResponses list
            else:
                response = self.getGeneralResponse(statement)
        else:  # Otherwise get a more specific response corresponding to the keyword and updated keys
            # check if the response is worth remembering
            if self.keys[maxRankIndex].rank > 2:
                responseInMemory = self.getRankedResponse(statement, maxRankIndex)
                self.memoryLis.append(responseInMemory)
            response = self.getRankedResponse(statement, maxRankIndex)
        return response


    def getRankedResponse(self, statement, keyIndex):
        # aKey is the keyword in the user's input statement that has the highest rank
        # the keyIndex was determined from getHighestRank function
        aKey = self.keys[keyIndex]
        regExList = aKey.regexLis
        # loop through the list of regular expressions associated with the keyword and see if
        # the statement matches any of them
        for i in range(len(regExList)):
            pattern = regExList[i]  # current regEx pattern
            match = re.match(pattern, statement.rstrip(".!"))
            if match:  # a match was found
                # Get the least used response
                response = self.leastUsedKeyResp(i, keyIndex)
                # Check if it is a goto statement
                tokens = self.getWords(response)
                # this goto statement allows Keyword's to have regular expressions that use reassembly rules from a
                # different Keyword
                if "goto" in tokens :
                    newKeyIndex = self.getKey(tokens[1]) # tokens[1] is the name of the keyword we need to go to
                    self.getRankedResponse(statement, newKeyIndex)
                # return the formatted response
                else:
                    return response.format(*[self.reflect(g) for g in match.groups()])

    # finds the key index of a Keyword supplied its name, returns -1 if no Keyword has that name
    def getKey(self, keyName):
        for i in range(len(self.keys)) :
            if keyName == self.keys[i].name :
                return i
        return -1


    # this returns the response that has been used the least
    #  and updates the Keyword attribute that keeps track of it
    def leastUsedKeyResp(self, patternIndex, keyIndex):
        aKey = self.keys[keyIndex]  # Keyword that was matched
        # usedResp is the list of ints that corresponds to that pattern (regular expression)
        usedResp = aKey.usedResp[patternIndex]  # usedResp is of type int[][] keeps track of which resp have been used
        leastIndex = usedResp.index(min(usedResp))
        resp = aKey.reasmbLis[patternIndex][leastIndex]
        # update the Keywords usedResp list (keeps track of how many times each response is used)
        self.keys[keyIndex].updateUsedResp(patternIndex, leastIndex)
        # return the least used response
        return resp

    # This generates and returns general response from the psychobable
    # Only called if no keywords are found in the user input statement
    def getGeneralResponse(self, statement):
        for pattern, responses in self.psychobabble:
            match = re.match(pattern, statement.rstrip(".!"))
            if match:
                patternIndex = self.findPatternIndex(pattern)
                response = self.leastUsedResponse(patternIndex)
                return response.format(*[self.reflect(g) for g in match.groups()])

    def leastUsedResponse(self, patternIndex):
        leastIndex = self.usedResponses[patternIndex][1].index(min(self.usedResponses[patternIndex][1]))
        self.usedResponses[patternIndex][1][leastIndex] += 1  # update usedResponses because now we are going to use that response
        # return the least used response
        return self.psychobabble[patternIndex][1][leastIndex]

    # Returns the index of the supplied "pattern" (regular expression) in the nested list from the psychobable
    def findPatternIndex(self, pattern):
        for i in range(len(self.psychobabble)):
            if pattern == self.psychobabble[i][0]:
                return i

    # Gets the word with the highest rank that is in the user's input statement
    # Returns the index of the Keyword in keys that has the highest rank or -1 if it does not exist
    def getHighestRank(self, words, statement):
        # Find the keyword with the highest rank in the statment if one exists
        for keyIndex in range(len(self.keys)):
            maxRank = self.keys[keyIndex]
            for aWord in words:
                # check if the word matches the Keyword's name or any of its synonyms
                if (aWord == maxRank.name or aWord in maxRank.synonyms) and self.getRankedResponse(statement, keyIndex) is not None:
                    # this will automatically be the Keyword with the highest rank because
                    # the list is ordered by decreasing rank
                    return keyIndex
        # If no keywords in the sentence return -1
        return -1


    # formats the statement (removes punctuation, and lower case) and splits it into a list of words
    def getWords(self, statement):
        # remove punctuation from statement
        exclude = set(string.punctuation)
        s = ''.join(ch for ch in statement if ch not in exclude)
        lowS = s.lower()
        words = (lowS.split(" "))  # The array with each word from the statement (no punctuation, all lower case)
        return words

    '''
    Initializes the usedResponse list
    For example the first element of psychobable is:
    ['I need (.*)', ['Why do you need {0}?', 'Would it really help you to get {0}?', 'Are you sure you need {0}?']]
    So the stored usedResponses will be:
    ['I need (.*)', [0, 0, 0]]
    Zeroes indicating that none of those responses have been used before

    '''
    def setUsedResponses(self):
        self.usedResponses = []  # list of used responses, this is used to avoid repetitions
        for i in range(len(self.psychobabble)):
            self.usedResponses.append([])
            self.usedResponses[i].append(self.psychobabble[i][0])  # make the frist value of the list the regular expression
            self.usedResponses[i].append([])
            for j in range(len(self.psychobabble[i][1])):  # this is always 2
                self.usedResponses[i][1].append(0)  # set value to 0 because we have not used any of the responses yet

    # this sets up the keyword objects and puts them in a list, the keys attribute
    def setKeys(self):
        xnone = Keyword("xnone", -1, r'(.*)',["I'm not sure I understand you fully.", "Please go on.",
                                        "That is interesting. Please continue.", "Tell me more about that.",
                                        "Does talking about this bother you?"])

        sorry = Keyword("sorry", 0, r'(.*)', [
        "Please don't apologise.",
        "Apologies are not necessary.",
        "I've told you that apologies are not required.",
        "It did not bother me.  Please continue."])

        apologize = Keyword("apologize", 0, r'(.*)', ["goto sorry"])

        remember = Keyword("remember", 5, r'(.*)i remember (.*)', ["Do you often think of {1}?",
                    "Does thinking of {1} bring anything else to mind?",
                    "What else do you recollect?",
                    "Why do you remember {1} just now?",
                    "What in the present situation reminds you of {1}?",
                    "What is the connection between me and {1}?",
                    "What else does {1} remind you of?"],
                           r'(.*)do you remember(.*)',[
                    "Did you think I would forget {1}?",
                    "Why do you think I should recall {1} now?",
                    "What about {1}?",
                    "goto what",
                    "You mentioned {1}?"],
                           r'(.*)you remember(.*)',[
                    "How could I forget {1}?",
                    "What about {1} should I remember?",
                    "goto you"])

        forget = Keyword("forget", 5, r'(.*)i forget(.*)',[
                "Can you think of why you might forget {1}?",
                "Why can't you remember {1}?",
                "How often do you think of {1}?",
                "Does it bother you to forget that?",
                "Could it be a mental block?",
                "Are you generally forgetful?",
                "Do you think you are suppressing {1}?"], r'(.*)did you forget(.*)',[
                "Why do you ask?",
                "Are you sure you told me?",
                "Would it bother you if I forgot {1}?",
                "Why should I recall {1} just now?",
                "goto what",
                "Tell me more about {1}."])

        # capitlilized because "if" is a keyword in Python
        IF = Keyword("if", 3, r'(.*)if(.*)',[
            "Do you think its likely that {1}?",
            "Do you wish that {1}?",
            "What do you know about {1}?",
            "Really, if {1}?",
            "What would you do if {1}?",
            "But what are the chances that {1}?",
            "What does this speculation lead to?"])

        dreamed = Keyword("dreamed", 4, r'(.*)i dreamed(.*)', [
            "Really, {1}?",
            "Have you ever fantasized {1} while you were awake?",
            "Have you ever dreamed {1} before?",
            "goto dream"])

        dream = Keyword("dream", 3, r'(.*)', [
            "What does that dream suggest to you?",
            "Do you dream often?",
            "What persons appear in your dreams?",
            "Do you believe that dreams have something to do with your problem?"])


        perhaps= Keyword("perhaps", 0, r'(.*)', [
            "You don't seem quite certain.",
            "Why the uncertain tone?",
            "Can't you be more positive?",
            "You aren't sure?",
            "Don't you know?",
            "How likely, would you estimate?"])


        name = Keyword("name", 15, r'(.*)', [
            "I am not interested in names."
            "I've told you before, I don't care about names -- please continue."])

        hello = Keyword("hello", 0, r'(.*)', [
            "How do you do.  Please state your problem.",
            "Hi.  What seems to be your problem?"])

        computer = Keyword("computer", 50, r'(.*)', [
            "Do computers worry you?",
            "Why do you mention computers?",
            "What do you think machines have to do with your problem?",
            "Don't you think computers can help people?",
            "What about machines worries you?",
            "What do you think about machines?"])

        am = Keyword("am", 0, r'(.*)am i(.*)', [
            "Do you believe you are {1}?",
            "Would you want to be {1}?",
            "Do you wish I would tell you you are {1}?",
            "What would it mean if you were {1}?",
            "goto what"], r'(.*)i am(.*)',["goto i"])

        are = Keyword("are", 0, r'(.*)are you(.*)',[
            "Why are you interested in whether I am {1} or not?",
            "Would you prefer if I weren't {1}?",
            "Perhaps I am {1} in your fantasies.",
            "Do you sometimes think I am {1}?",
            "goto what",
            "Would it matter to you?",
            "What if I were {1}?"], r'(.*)you are(.*)',[
            "goto you"], r'(.*) are ([a-zA-Z]*) ([a-zA-Z]*) ([a-zA-Z]*) (.*)',[
            "Did you think they might not be {1} {2} {3}?",
            "Would you like it if they were not {1} {2} {3}?",
            "What if they were not {1} {2} {3}?",
            "Are they always {1} {2} {3}?",
                "Possibly they are {1} {2} {3}.",
            "Are you positive they are {1} {2} {3}?"])

        your = Keyword("your", 0, r'(.*)your(.*)',
            ["Why are you concerned over my {1}?",
            "What about your own {1}?",
            "Are you worried about someone else's {1}?",
            "Really, my {1}?",
            "What makes you think of my {1}?",
            "Do you want my {1}?"])

        was = Keyword("was", 2, r'(.*)was i(.*)',[
            "What if you were {1}?",
            "Do you think you were {1}?",
            "Were you {1}?",
            "What would it mean if you were {1}?",
            "What does ' {1} ' suggest to you?",
            "goto what"], r'(.*)i was(.*)',[
            "Were you really?",
            "Why do you tell me you were {1} now?",
            "Perhaps I already know you were {1}."], r'(.*)was you(.*)', [
            "Would you like to believe I was {1}?",
            "What suggests that I was {1}?",
            "What do you think?",
            "Perhaps I was {1}.",
            "What if I had been {1}?"])

        sad = Keyword("sad", 3, r'(.*)i am ([a-zA-Z]*)(.*)',[
            "I am sorry to hear that you are {1}.",
            "Do you think coming here will help you not to be {1}?",
            "I'm sure it's not pleasant to be {1}.",
            "Can you explain what made you {1}?"])

        happy = Keyword("happy", 3, r'(.*)i am ([a-zA-Z]*)(.*)',[
            "How have I helped you to be {1}?",
            "Has your treatment made you {1}?",
            "What makes you {1} just now?",
            "Can you explain why you are suddenly {1}?"])

        want = Keyword("want", 2, r'(.*)i ([a-zA-Z]*)(.*)',[
            "What would it mean to you if you got {2}?",
            "Why do you want {2}?",
            "Suppose you got {2} soon.",
            "What if you never got {2}?",
            "What would getting {2} mean to you?",
            "What does wanting {2} have to do with this discussion?"])


        belief = Keyword("belief", 1,r'(.*)i ([a-zA-Z]*) i(.*)',[
            "Do you really think so?",
            "But you are not sure you {2}.",
            "Do you really doubt you {2}?"], r'(.*)i ([a-zA-Z]*)(.*)you(.*)',["goto you"])


        cannot = Keyword("cannot", 1, r'(.*)i ([a-zA-z]*) (.*)',[
            "How do you know that you can't {2}?",
            "Have you tried?",
            "Perhaps you could {2} now.",
            "Do you really want to be able to {2}?",
            "What if you could {2}?"])

        # capitlize i to avoid confusing since "i" is used as a counter in many loops
        I = Keyword("i", 0, r'(.*)i was(.*)',[
            "goto was"], r'(.*)i am(.*)',[
            "Is it because you are {1} that you came to me?",
            "How long have you been {1}?",
            "Do you believe it is normal to be {1}?",
            "Do you enjoy being {1}?",
            "Do you know anyone else who is {1}?"], r"(.*)i don't(.*)",[
            "Don't you really {1}?",
            "Why don't you {1}?",
            "Do you wish to be able to {1}?",
            "Does that trouble you?"], r'(.*)i feel(.*)',[
            "Tell me more about such feelings.",
            "Do you often feel {1}?",
            "Do you enjoy feeling {1}?",
            "Of what does feeling {1} remind you?"], r'(.*)i(.*)you(.*)',
                    ["Perhaps in your fantasies we {1} each other.",
            "Do you wish to {1} me?",
            "You seem to need to {1} me.",
            "Do you {1} anyone else?"], r'(.*)', [
            "You say {0}?",
            "Why do you say {0}?",
            "Can you elaborate on that?",
            "Do you say {0} for some special reason?",
            "That's quite interesting."])

        you = Keyword("you", 0, r'(.*)you remind me of(.*)',["goto alike"], r'(.*)you are(.*)',
                      ["What makes you think I am {1}?",
            "Does it please you to believe I am {1}?",
            "Do you sometimes wish you were {1}?",
            "Perhaps you would like to be {1}."], r'(.*)you(.*) me(.*)',["Why do you think I {1} you?",
            "You like to think I {1} you -- don't you?",
            "What makes you think I {1} you?",
            "Really, I {1} you?",
            "Do you wish to believe I {1} you?",
            "Suppose I did {1} you -- what would that mean?",
            "Does someone else believe I {1} you?"], r'(.*)you(.*)',[
            "We were discussing you -- not me.",
            "Oh, I {1}?",
            "You're not really talking about me -- are you?",
            "What are your feelings now?"])

        yes = Keyword("yes", 0, r'(.*)', [
            "Please go on.",
            "Please tell me some more about this.",
            "Why don't you tell me a little more about this.",
            "I see.",
            "I understand."])

        no = Keyword("no", 0, r'(.*)no one(.*)',[
            "Are you sure, no one {1}?",
            "Surely someone {1}.",
            "Can you think of anyone at all?",
            "Are you thinking of a very special person?",
            "Who, may I ask?",
            "You have a particular person in mind, don't you?",
            "Who do you think you are talking about?"], r'(.*)', [
            "Are you saying no just to be negative?",
            "Does this make you feel unhappy?",
            "Why not?",
            "Why 'no'?"])

        family = Keyword("family", 3, r'(.*)my ([a-zA-Z]*)(.*)', [
            "Tell me more about your family.",
            "Who else in your family {2}?",
            "Your {1}?",
            "What else comes to mind when you think of your {1}?"])

        my = Keyword("my", 2, r'(.*)my(.*)',[
            "Your {1}?",
            "Why do you say your {1}?",
            "Does that suggest anything else which belongs to you?",
            "Is it important to you that your {1}?",
            "Let's discuss further why your {1}.",
            "Earlier you said your {1}.",
            "But your {1}.",
            "Does that have anything to do with the fact that your {1}?"])

        can = Keyword("can", 0, r'(.*)can you(.*)',["You believe I can {1} don't you?",
            "goto what",
            "You want me to be able to {1}.",
            "Perhaps you would like to be able to {1} yourself."], r'(.*)can i(.*)',["Whether or not you can {1} depends on you more than on me.",
            "Do you want to be able to {1}?",
            "Perhaps you don't want to {1}.",
            "goto what"])

        what = Keyword("what", 0, r'(.*)', [
            "Why do you ask?",
            "Does that question interest you?",
            "What is it you really want to know?",
            "Are such questions much on your mind?",
            "What answer would please you most?",
            "What do you think?",
            "What comes to mind when you ask that?",
            "Have you asked such questions before?",
            "Have you asked anyone else?"])

        who = Keyword("who", 0, r'who(.*)',[
            "goto what"])

        when = Keyword("when", 0, r'when(.*)',[
            "goto what"])

        where = Keyword("where", 0, r'where(.*)',["goto what"])

        how = Keyword("how", 0, r'how(.*)',["goto what"])

        because = Keyword("because", 0, r'(.*)', [
            "Is that the real reason?",
            "Don't any other reasons come to mind?",
            "Does that reason seem to explain anything else?",
            "What other reasons might there be?"])

        why = Keyword("why", 0, r"(.*)why don't you(.*)",["Do you believe I don't {1}?",
            "Perhaps I will {1} in good time.",
            "Should you {1} yourself?",
            "You want me to {1}?",
            "goto what"], r"(.*)why can't i(.*)",["Do you think you should be able to {1}?",
            "Do you want to be able to {1}?",
            "Do you believe this will help you to {1}?",
            "Have you any idea why you can't {1}?",
            "goto what"], r'(.*)', [
            "goto what"])

        everyone = Keyword("everyone", 2, r'(.*) everyone (.*)',
            ["Really, {1}?",
            "Surely not {1}.",
            "Can you think of anyone in particular?",
            "Who, for example?",
            "Are you thinking of a very special person?",
            "Who, may I ask?",
            "Someone special perhaps?",
            "You have a particular person in mind, don't you?",
            "Who do you think you're talking about?"])

        everybody = Keyword("everybody", 2, r'(.*)', [
            "goto everyone"])

        nobody = Keyword("nobody", 2, r'(.*)', [
            "goto everyone"])

        noone = Keyword("noone", 2, r'(.*)', [
            "goto everyone"])

        always = Keyword("always", 1, r'(.*)', [
            "Can you think of a specific example?",
            "When?",
            "What incident are you thinking of?",
            "Really, always?"])

        alike = Keyword("alike", 10, r'(.*)', [
            "In what way?",
            "What does that similarity suggest to you?",
            "What do you suppose that resemblence means?",
            "What is the connection, do you suppose?",
            "Could there really be some connection?",
            "How?"])

        like = Keyword("like", 10, r'(.*) ([a-zA-Z]*)like (.*)',
            ["goto alike"])

        different = Keyword("different", 0, r'(.*)', [
            "How is it different?",
            "What differences do you see?",
            "What does that difference suggest to you?",
            "What other distinctions do you see?",
            "What do you suppose that disparity means?",
            "Could there be some connection, do you suppose?",
            "How?"])

        # add synonyms to each

        sorry.addSynonyms(["remorseful", "regretful"])
        remember.addSynonyms(["reminded","recall","memorize","look back"])
        dreamed.addSynonyms(["delusion","fantasy","imagination","thought"])
        perhaps.addSynonyms(["maybe", "for all one knows", "it could be", "it may be", "it's possible", "possibly", "conceivably", "perchance"])
        hello.addSynonyms(["hi","hey","howdy","greetings"])
        sad.addSynonyms(["depressed","unhappy", "sorrowful", "dejected", "depressed", "downcast", "miserable", "despondent", "despairing", "disconsolate", "desolate", "wretched", "glum", "gloomy", "doleful", "dismal", "melancholy", "mournful", "woebegone", "forlorn", "crestfallen", "heartbroken", "inconsolable"])
        happy.addSynonyms(["cheerful", "cheery", "merry", "joyful", "jovial", "jolly", "jocular", "gleeful", "carefree", "untroubled", "delighted", "smiling", "beaming", "grinning", "lighthearted", "pleased", "contented", "content", "satisfied", "gratified", "buoyant", "radiant", "sunny", "blithe", "joyous", "beatific", "thrilled", "elated", "exhilarated", "ecstatic", "blissful", "euphoric", "overjoyed", "exultant", "rapturous", "jubilant"])
        because.addSynonyms(["since"])
        always.addSynonyms(["consistently", "invariably", "regularly", "habitually", "unfailingly"])
        alike.addSynonyms(["similar", "indistinguishable", "identical", "uniform", "interchangeable"])
        different.addSynonyms(["dissimilar", "unalike", "unlike", "contrasting", "contrastive", "divergent", "differing", "varying", "disparate", "mismatched", "conflicting", "clashing", "unfamiliar", "unconventional","uncommon"])
        family.addSynonyms(["boyfriend","girlfriend","mother","mom","mama","father","dad","dada","papa","sister","siblings","brother","brothers","sister","grandma","grandmother","grandfather","granparents","parents","son","daughter","neice","nephew","cousin","husband","wife","fiancee","partner","soulmate","relatives","children","child"])
        want.addSynonyms(["desire","need","must","wish","longing","yearn"])
        belief.addSynonyms(["trust","believe","fancy","suppose","presume","understand"])
        cannot.addSynonyms(["can't","won't","cant","wont"])
        # Add all of these Keyword objects to a list called keys.
        self.keys.extend([xnone, sorry, apologize, remember, forget, dreamed, dream, IF, perhaps, name, hello, computer,
                          am, are, your, was, sad, happy, I, you, yes, no, my, can, what, who, when, where, how,
                          because, why, everyone, everybody, nobody, noone, always, alike, like, different, family, want, belief,cannot])
        # sort in decreasing order of rank because it makes it more efficient when looking for
        # matches to Keywords with the highest rank.
        self.keys.sort(key=lambda x: x.rank, reverse=True)
