import pyparsing as pp
from google.cloud.firestore_v1.base_query import FieldFilter, Or # TODO do we need more than this?

# start the query program
# make a query and revieve a response
# make additional queries, if desired, and receive responses
# exit the program




# query class
# instance created when user makes a query
class Query:

    def __init__(self, column, operator, specification, logical_op=None,
                 column2 = None, operator2 = None, specification2 = None, valid = False):
        self.column = column
        self.operator = operator
        self.specification = specification
        self.logical_op = logical_op
        self.column2 = column2
        self.operator2 = operator2
        self.specification2 = specification2
        
    def get_column(self):
        return self.column

    def get_operator(self):
        return self.operator
    
    def get_specification(self):
        return self.specification

# some function for input validation using pyparsing
# returns input in the form of a query
def validate_input(input):

    category = pp.QuotedString('"')
    operator = pp.one_of("= < > <= >= != of")
    specification = pp.QuotedString('"')

    logical_op = pp.Keyword("AND") | pp.Keyword("OR")

    parsed_query = category + operator + specification
    comp_query = parsed_query + logical_op + parsed_query
    

    # if and/or operator exists
    try:
        # created parsed query
        parsed = comp_query.parse_string(input, parse_all=True)
        newQuery = Query(parsed[0], parsed[1], parsed[2], parsed[3], parsed[4], parsed[5], parsed[6])

    # else
    except pp.ParseException as e:
        try:
            # created parsed query
            parsed = parsed_query.parse_string(input, parse_all=True)
            newQuery = Query(parsed[0], parsed[1], parsed[2])

        except pp.exceptions.ParseException as e2:
            print("INVALID INVALID")
            return None

    print("Valid")
    # mark the query as valid
    newQuery.valid = True
    return newQuery


# TODO make sure it works once admin is up
def make_query(query):
    movies_ref = db.collection("movies")

    # and queries
    if query.logical_op == "OR":

        movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification)).where(
        filter=FieldFilter(query.column2, query.operator2, query.specification2)
    )
    # or 
    if query.logical_op == "OR":
        movies_ref.where(
            filter=Or(
                [
                    FieldFilter(query.column, query.operator, query.specification),
                    FieldFilter(query.column2, query.operator2, query.specification2),
                ]
            )
        )
    # simple queries
    else:
        movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification))
    
    



# main goes here

programOn = True # boolean value for turning on the query program
while programOn == True:

    # while input is not valid, ask for query
    print("Make a query, or input HELP for instructions")
    queryText = input("make a query: ")

    # if exit 
    if queryText == "EXIT":
        programOn = False

    elif queryText == "HELP":
        print("Query structure: \n")
        print("Initial command: category")
        print("Ex. Genre, Year of Release, Category")
        print("Initial command: operator")
        print("Ex. =, <, >")
        print("Initial command: specification")
        print("Example query: Genre = Drama")
        print("input EXIT to end the program")

    # if input is validated, make a query object
    elif programOn == True:
        # validate the input
        newQuery = validate_input(queryText)
        # if query is valid, run it
        if newQuery.valid == True:
            make_query(newQuery)

    




