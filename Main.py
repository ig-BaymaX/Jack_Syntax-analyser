import Tokenizer, Parser

class syntaxAnalyzer:
    def __init__(self, fileName):
        self.fileName = fileName

    def analyze(self):
        # Tokenizing the file
        t = Tokenizer.mainTokenizer(self.fileName)
        t.Main() # Creating the tokenized xml output file
        # Parsing the file
        p = Parser.mainParser(self.fileName)
        p.Main() # Creating the parsed xml output file
        # showing success message
        print("Successfully tokenized and parsed the file")

 # Main
fileName = input("Enter the file name: ")
syntaxAnalyzer = syntaxAnalyzer(fileName)
syntaxAnalyzer.analyze()