import pyparsing as pp
# start the query program
# make a query and revieve a response
# make additional queries, if desired, and receive responses
# exit the program




# query class
# instance created when user makes a query
class Query:

    def __init__(self, column, operator, specification):
        self.column = column
        self.operator = operator
        self.specification = specification

    def get_column(self):
        return self.column

    def get_operator(self):
        return self.operator
    
    def get_specification(self):
        return self.specification

# some function for input validation using pyparsing
# returns input in the form of a query
# TODO add and/or
def validate_input(input):


    try:
        category = pp.Word(pp.alphas)
        operator = pp.one_of("= < >")
        specification = pp.Word(pp.alphas)

        query_parse = category + operator + specification
        # created parsed query
        parsed = query_parse.parse_string(input)
        newQuery = Query(parsed[0], parsed[1], parsed[2])

        print(parsed)
        return newQuery
    except pp.exceptions.ParseException:
        print("invalid")



# main goes here

programOn = True # boolean value for turning on the query program
while programOn == True:

    # while input is not valid, ask for query
    print("Make a query, or input HELP for instructions")
    queryText = input("make a query: ")

    # if exit 
    if queryText == "EXIT":
        programOn = False

    if queryText == "HELP":
        print("Query structure: \n")
        print("Initial command: category")
        print("Ex. Genre, Year of Release, Category")
        print("Initial command: operator")
        print("Ex. =, <, >")
        print("Initial command: specification")
        print("Example query: Genre = Drama")
        print("input EXIT to end the program")

    # if input is validated, make a query object
    if programOn == True:
        newQuery = validate_input(queryText)
    




