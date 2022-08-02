class fileManager: # class to manage the files (reading and writing), and to removes the comments (Single line and Inline)
    def __init__(self, fileName): # Constructor
        self.fileName = fileName

    def readLines(self): # Read lines from a file
        with open(self.fileName, "r") as file:
            lines = file.readlines()
            newLines = list(map(lambda x: x.strip(), lines)) # Removing the leading and lagging spaces
            return newLines
    
    def writeLines(self, lines): # Write lines to a file from a list with type ('parser'(p) or ' tokenizer'(t))
        with open(self.fileName.replace(".jack", "T.xml"), "w") as file:
            for line in lines:
                file.write(line)

    def removeComments(self, lines):
        filteredLines = [] # Empty list to store filtered lines
        for i in lines:
            if (len(i.strip()) > 0):
                filteredLines.append(i.split("//")[0].strip()) # Removing comment part from the line
        return filteredLines # Return the filtered lines

class tokenManager: # class to manage the tokens (seperate each token and return a list)
    def __init__(self, fileName): # Constructor
        self.fileName = fileName
        self.symbols = ["(", ")", "[", "]", "{", "}", ".", ",", ";", "+", "-", "*", "/", "=", ">", "<", "!", "&", "|", "~", "^", ":", "\"", "'", "\\"]
        self.keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]

    def tokenise(self, lines):
        temp = "" # temperory string to store each token and reset when next token starts
        newLines = [] # list to store tokens
        commentFlag = False # flag for removing multiline comments
        stringFlag = False # flag for joining string seperated with space or any other symbol
        for line in lines: # for each line in the jack code
            for c in range(len(line)): # for each character in the line
                if stringFlag and line[c] == "\"": # Checking whetehr string has ended
                    stringFlag = False
                    continue
                elif line[c] == "\"": # Checking whether string has started
                    stringFlag = True
                elif line[c] == '/': # Checking whether comment has started
                    try:
                        if line[c+1] == '*': # Confirming it is a comment
                            commentFlag = True
                            continue
                    except Exception:
                        continue
                elif line[c] == "*": # Checking whether comment has ended
                    try:
                        if line[c+1] == '/': # Confirming it is a comment
                            commentFlag = False
                            i += 1
                            continue
                    except Exception:
                        continue
                if (stringFlag == False): # checking string flag
                    if (commentFlag == False): # checking comment flag
                        if (line[c] in self.symbols or line[c] == " "): # if the character is a symbol or space
                            if (len(temp) > 0): # add if there is a token in temp
                                newLines.append(temp)
                                temp = ""
                            if (line[c] != " "):
                                newLines.append(line[c])
                        else:
                            if (line[c] != " "):
                                temp += line[c]
                else:
                    temp += line[c]
        if (len(temp) > 0): # adding the last token if anything is there in temp
            newLines.append(temp.strip())
            temp = ""
        return newLines # returns the list of tokens

    def tagConverter(self, lines):
        writingLines =[] # list to store lines to be written to file
        writingLines.append("<tokens>\n") # heading of the file
        for i in lines: # each token
            if (i in self.keywords): # if keyword
                writingLines.append("\t<keyword> " + i + " </keyword>\n")
            elif (i in self.symbols): # if symbol
                temp = i
                if (i == "<"):
                    temp = "&lt;"
                elif (i == ">"):
                    temp = "&gt;"
                elif (i == "&"):
                    temp = "&amp;"
                elif (i == "\""):
                    temp = "&quot;"
                elif (i == "'"):
                    temp = "&apos;"
                writingLines.append("\t<symbol> " + temp + " </symbol>\n")
            elif (i.isdigit()): # if digit
                writingLines.append("\t<integerConstant> " + i + " </integerConstant>\n")
            elif (i[0] == "\""): # if string
                writingLines.append("\t<stringConstant> " + i[1:] + " </stringConstant>\n")
            else: # otherwise, it is an identifier
                writingLines.append("\t<identifier> " + i + " </identifier>\n")
        writingLines.append("</tokens>\n") # Ending of file
        return writingLines

class mainTokenizer: # Main class
    def __init__(self, fileName): # Constructor
        self.File = fileManager(fileName) # Object for FileManager
        self.Tokenizer = tokenManager(fileName) # Object for TokenManager
    
    def Main(self):
        # Fetching Lines and removing Comments (Single line and Inline)
        lines = self.File.readLines() # Fetching lines
        lines = self.File.removeComments(lines) # Removing comments 
        # Converting lines to tokens and adding XML tags
        tokens = self.Tokenizer.tokenise(lines) # Converting lines to tokens
        tokens = self.Tokenizer.tagConverter(tokens) # Adding XML tags
        # Writing tokens to file
        self.File.writeLines(tokens) # Writing tokens to file