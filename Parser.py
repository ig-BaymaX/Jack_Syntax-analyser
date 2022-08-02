class tokens: # Object class for tokens
    def __init__(self, token, openTag, closeTag): # Constructor
        self.token = token
        self.openTag = openTag
        self.closeTag = closeTag

class seperator: # Class that seperates the token from their opening tag and closing tag
    def getTokens(fileName): # returns a list of tokens
        newLines = [] # new list to store all the token objects
        with open(fileName, "r") as file: # opens the file
            lines = file.readlines()
            lines.pop() # removes the last line </tokens>
            lines.pop(0) # removes the first line <tokens>
            for line in lines:
                line = line.strip() # removes the preceding and trailing whitespace
                start = line.find(">") # Finding the starting of the token
                end = line.find("</", start) # finding the ending of the token
                newLines.append(tokens(line[start + 2 : end - 1], line[0 : start + 1], line[end : len(line)]))
        return newLines # returning the list of token objects

class parser:
    def __init__(self, fileName): # Constructor
        self.expressionEvaluator = [] # list to check if the expressions are valid
        self.scopeFinder = 0 # used to keep track of the scope
        self.indentation = "  " # used to indent the code
        self.fileName = fileName.replace(".jack", "T.xml")
        self.final = [] # list that stores the final values
        self.tokens = seperator.getTokens(self.fileName) # getting the token objects from the seperator class
        self.tokenIndex = 0; # Index of the current token

    def toString(self, tokenObject):
        """
        Parameter(s) : Object (Token)
        Action(s)    : Returns the token as a string with its corresponding tags
                     : Handles the expressions by pushing and poping brackets in the expressionEvaluator list
        Return(s)    : String -> "<tag> <token> </tag>"
        """
        if tokenObject.token in ("{", "(", "[", "<"):
            self.expressionEvaluator.append(tokenObject.token)
        elif tokenObject.token in ("}", ")", "]", ">"):
            if tokenObject.token == "}" and self.expressionEvaluator[-1] == "{":
                self.expressionEvaluator.pop()
            elif tokenObject.token == ")" and self.expressionEvaluator[-1] == "(":
                self.expressionEvaluator.pop()
            elif tokenObject.token == "]" and self.expressionEvaluator[-1] == "[":
                self.expressionEvaluator.pop()
            elif tokenObject.token == ">" and self.expressionEvaluator[-1] == "<":
                self.expressionEvaluator.pop()
            else:
                print("Error: Invalid expression")
                exit()
        return self.scopeFinder * self.indentation + (tokenObject.openTag + " " + tokenObject.token + " " + tokenObject.closeTag)
    
    def curToken(self): # returns the current token object
        """
        Parameter(s) : None
        Action(s)    : None
        Return(s)    : Object -> Current token object
        """
        return self.tokens[self.tokenIndex]
    
    def advToken(self): # returns the current token and advances the index
        """
        Parameter(s) : None
        Action(s)    : Advances the index by 1
        Return(s)    : Object -> Current token object
        """
        self.tokenIndex += 1
        return self.tokens[self.tokenIndex - 1]

    def compileClass(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <class>
                               -> class className { class variable declerations* subroutine declerations* }
                               -> </class>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<class>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # class
        self.final.append(self.toString(self.advToken())) # class name
        self.final.append(self.toString(self.advToken())) # {
        while(self.curToken().token in ("static", "field")): # for the class variables declearations
            self.compileClassVarDec()
        while(self.curToken().token in ("constructor", "function", "method")): # for the subroutines
            self.compileSubroutineDec()
        self.final.append(self.toString(self.advToken())) # }
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</class>")

    def compileClassVarDec(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <classVarDec>
                               -> (static | field) type varName (, varName)* ;
                               -> </classVarDec>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<classVarDec>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # static or field
        self.final.append(self.toString(self.advToken())) # type ("int", "char", "boolean", "void", "className")
        while(self.curToken().token != ";"):
            self.final.append(self.toString(self.advToken())) # , (multiple variables)
        self.final.append(self.toString(self.advToken())) # ; (end of variable declaration)
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</classVarDec>")
    
    def compileSubroutineDec(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <subroutineDec>
                               -> (constructor | function | method) (void | type) subroutineName (parameterList) subroutineBody
                               -> </subroutineDec>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<subroutineDec>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # constructor, function, or method
        self.final.append(self.toString(self.advToken())) # type ("int", "char", "boolean", "void", "className")
        self.final.append(self.toString(self.advToken())) # subroutineName
        self.final.append(self.toString(self.advToken())) # opening '(' bracket
        self.compileParameterList() # Parameter List
        self.final.append(self.toString(self.advToken())) # closing ')' bracket
        self.compileSubroutineBody() # subroutine body
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</subroutineDec>")
        
    def compileParameterList(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <parameterList>
                               -> ((type varName) (, type varName)*)?
                               -> </parameterList>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<parameterList>")  
        self.scopeFinder += 1
        while self.curToken().token != ")":
            self.final.append(self.toString(self.advToken())) # parameters
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</parameterList>")

    def compileSubroutineBody(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <subroutineBody>
                               -> { varDec* statements }
                               -> </subroutineBody>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<subroutineBody>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # '{' opening bracket
        if self.curToken().token == "var":
            while self.curToken().token == "var":
                self.compileVarDec()
        self.compileStatements() # Handles statements
        self.final.append(self.toString(self.advToken())) # '}' closing bracket
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</subroutineBody>")
        
    def compileVarDec(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <varDec>
                               -> var type varName (, varName)* ;
                               -> </varDec>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<varDec>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # var
        self.final.append(self.toString(self.advToken())) # type ("int", "char", "boolean", "void", "className")
        while(self.curToken().token != ";"):
            self.final.append(self.toString(self.advToken())) # , (multiple variables)
        self.final.append(self.toString(self.advToken())) # ; (end of variable declaration)
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</varDec>")

    def compileStatements(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <statements>
                               -> statement*
                               -> statement : letStatement | ifStatement | whileStatement | doStatement | returnStatement
                               -> </statements>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<statements>")
        self.scopeFinder += 1
        while self.curToken().token in ("let", "if", "while", "do", "return"):
            if self.curToken().token == "let":
                self.compileLet()
            elif self.curToken().token == "if":
                self.compileIf()
            elif self.curToken().token == "while":
                self.compileWhile()
            elif self.curToken().token == "do":
                self.compileDo()
            elif self.curToken().token == "return":
                self.compileReturn()
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</statements>")
    
    def compileLet(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <letStatement>
                               -> let varName ([expression])? = expression ;
                               -> </letStatement>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<letStatement>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # let
        self.final.append(self.toString(self.advToken())) # varName
        if self.curToken().token == '[':
            self.final.append(self.toString(self.advToken()))
            self.compileExpression() # Handles expression
            self.final.append(self.toString(self.advToken())) # closing bracket ']'
        self.final.append(self.toString(self.advToken())) # =
        self.compileExpression() # Handles expression
        self.final.append(self.toString(self.advToken())) # ;
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</letStatement>")
    
    def compileDo(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <doStatement>
                               -> do subroutineCall;
                               -> </doStatement>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<doStatement>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # do
        self.final.append(self.toString(self.advToken())) # subroutineName
        if self.curToken().token == "(":
            self.final.append(self.toString(self.advToken())) # opening '(' bracket
        elif self.curToken().token == ".":
            self.final.append(self.toString(self.advToken())) # .
            self.final.append(self.toString(self.advToken())) # className or varName
            self.final.append(self.toString(self.advToken())) # opening '(' bracket
        self.compileExpressionList() # Handles expression list
        self.final.append(self.toString(self.advToken())) # closing ')' bracket
        self.final.append(self.toString(self.advToken())) # ;
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</doStatement>")

    def compileIf(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <ifStatement>
                               -> if (expression) { statements } (else { statements })?
                               -> </ifStatement>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<ifStatement>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken())) # if 
        self.final.append(self.toString(self.advToken())) # (
        self.compileExpression() # Handles expression
        self.final.append(self.toString(self.advToken())) # )
        self.final.append(self.toString(self.advToken())) # {
        self.compileStatements() # Handles statements
        self.final.append(self.toString(self.advToken())) # }
        if self.curToken().token == "else":
            self.final.append(self.toString(self.advToken())) # else
            self.final.append(self.toString(self.advToken())) # {
            self.compileStatements() # Handles statements
            self.final.append(self.toString(self.advToken())) # }
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</ifStatement>")
    
    def compileWhile(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <whileStatement>
                               -> while (expression) { statements }
                               -> </whileStatement>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<whileStatement>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken()))
        self.final.append(self.toString(self.advToken())) # (
        self.compileExpression() # Handles expression
        self.final.append(self.toString(self.advToken())) # )
        self.final.append(self.toString(self.advToken())) # {
        self.compileStatements() # Handles statements
        self.final.append(self.toString(self.advToken())) # }
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</whileStatement>")
    
    def compileReturn(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <returnStatement>
                               -> return expression? ;
                               -> </returnStatement>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<returnStatement>")
        self.scopeFinder += 1
        self.final.append(self.toString(self.advToken()))
        if self.curToken().token != ";":
            self.compileExpression()
        self.final.append(self.toString(self.advToken())) # ;
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</returnStatement>")

    def compileExpression(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <expression>
                               -> term (op term)*
                               -> </expression>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<expression>")
        self.scopeFinder += 1
        self.compileTerm()
        while self.curToken().token in ("+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="):
            self.final.append(self.toString(self.advToken()))
            self.compileTerm()
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</expression>")
    
    def compileTerm(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <term>
                               -> integerConstant | stringConstant | keywordConstant | varName | varName[expression] | subroutineCall | (expression) | unaryOp term
                               -> </term>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<term>")
        self.scopeFinder += 1
        if self.curToken().openTag in ("<integerConstant>", "<stringConstant>", "<keyword>"):
            self.final.append(self.toString(self.advToken()))
        elif self.curToken().openTag == "<identifier>":
            self.final.append(self.toString(self.advToken()))
            if self.curToken().token == "[":
                self.final.append(self.toString(self.advToken())) # [
                self.compileExpression()
                self.final.append(self.toString(self.advToken())) # ]
            elif self.curToken().token in (".", "("):
                if self.curToken().token == "(":
                    self.final.append(self.toString(self.advToken())) # (
                elif self.curToken().token == ".":
                    self.final.append(self.toString(self.advToken())) # .
                    self.final.append(self.toString(self.advToken())) # subroutineName
                    self.final.append(self.toString(self.advToken())) # (
                self.compileExpressionList()
                if self.curToken().token == ")":
                    self.final.append(self.toString(self.advToken())) # )
        elif self.curToken().token == "(":
            self.final.append(self.toString(self.advToken()))
            self.compileExpression()
            if self.curToken().token == ")":
                self.final.append(self.toString(self.advToken()))
        elif self.curToken().token in ("-", "~"):
            self.final.append(self.toString(self.advToken()))
            self.compileTerm()
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</term>")
    
    def compileExpressionList(self):
        """
        Parameter(s) : None
        Action(s)    : Handles -> <expressionList>
                               -> (expression (, expression)*)?
                               -> </expressionList>
        Return(s)    : None
        """
        self.final.append(self.scopeFinder * self.indentation + "<expressionList>")
        self.scopeFinder += 1
        if self.curToken().token != ")":
            self.compileExpression()
            while self.curToken().token == ",":
                self.final.append(self.toString(self.advToken()))
                self.compileExpression()
        self.scopeFinder -= 1
        self.final.append(self.scopeFinder * self.indentation + "</expressionList>")
        
    def parse(self):
        """
        Parameter(s) : None
        Action(s)    : Initate the compilation process and store the compiled code in a list and return it
        Return(s)    : String List
        """
        self.compileClass()
        return self.final

class mainParser: # Main Class
    def __init__(self, fileName): # Constructor
        self.fileName = fileName
        self.parser = parser(fileName)
    
    def Main(self):
        """
        Parameter(s) : None
        Action(s)    : Invokes the parse function and writes the compiled code into a file
        Return(s)    : None
        """
        writingLines = self.parser.parse() # Initates the compilation process and returns the compiled code in a list
        if len(self.parser.expressionEvaluator) == 0: # If the list is empty, the expression in the jack file is valid
            with open(self.parser.fileName.replace("T.xml", ".xml"), "w") as file:
                for i in writingLines:
                    file.write(i + "\n")
        else: # If the list is not empty, the expression in the jack file is invalid
            print("Error: Invalid expression")
            exit()

        # Help for all methods in the parser class
        # print("\n\n")
        # print(help(self.parser.toString))
        # print(help(self.parser.curToken)) 
        # print(help(self.parser.advToken)) 
        # print(help(self.parser.compileClass)) 
        # print(help(self.parser.compileClassVarDec)) 
        # print(help(self.parser.compileSubroutineDec)) 
        # print(help(self.parser.compileParameterList))  
        # print(help(self.parser.compileSubroutineBody)) 
        # print(help(self.parser.compileVarDec)) 
        # print(help(self.parser.compileStatements))  
        # print(help(self.parser.compileLet)) 
        # print(help(self.parser.compileDo)) 
        # print(help(self.parser.compileIf))  
        # print(help(self.parser.compileWhile)) 
        # print(help(self.parser.compileReturn)) 
        # print(help(self.parser.compileExpression))  
        # print(help(self.parser.compileTerm)) 
        # print(help(self.parser.compileExpressionList)) 
        # print(help(self.parser.parse)) 
        # print("\n\n")