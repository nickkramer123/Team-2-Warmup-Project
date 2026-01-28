import pyparsing as pp
from google.cloud.firestore_v1.base_query import FieldFilter, Or # TODO do we need more than this?

# start the query program
# make a query and revieve a response
# make additional queries, if desired, and receive responses
# exit the program


# movie class
class Movie:
    def __init__(self, index: int, movie_name: str, year_of_release: int, category: str, run_time: int, genre: list[str], imdb_rating: float, votes: int, gross_total: float, seen: str):
        self.index = index
        self.movie_name = movie_name
        self.year_of_release = year_of_release
        self.category = category
        self.run_time = run_time
        self.genre = genre
        self.imdb_rating = imdb_rating
        self.votes = votes
        self.gross_total = gross_total
        self.seen = seen

    # returns a dictionary containing all of the information of the movie
    def to_dict(self):
        return {"index": self.index, 
                "movie_name": self.movie_name,
                "year_of_release": self.year_of_release,
                "category": self.category,
                "run_time": self.run_time,
                "genre": self.genre,
                "imdb_rating": self.imdb_rating,
                "votes": self.votes,
                "gross_total": self.gross_total,
                "seen": self.seen}
    
    # takes in a dictionary and returns a movie object
    @staticmethod
    def from_dict(source):
        return Movie(source['index'], source['movie_name'], source['year_of_release'], source['category'], source['run_time'], source['genre'], source['imdb_rating'], source['votes'], source['gross_total'], source['seen'])

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
    if query.logical_op == "AND":

        finishedQuery = movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification)).where(
        filter=FieldFilter(query.column2, query.operator2, query.specification2)
    )
    # or 
    if query.logical_op == "OR":
        finishedQuery = movies_ref.where(
            filter=Or(
                [
                    FieldFilter(query.column, query.operator, query.specification),
                    FieldFilter(query.column2, query.operator2, query.specification2),
                ]
            )
        )
    # simple queries
    else:
        finishedQuery = movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification))
    return finishedQuery
    



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
        print("Ex. =, <, >, in")
        print("Initial command: specification")
        print("Example query: Genre = Drama")
        print("input EXIT to end the program")

    # if input is validated, make a query object
    elif programOn == True:
        # validate the input
        newQuery = validate_input(queryText)
        # if query is valid, run it
        if newQuery.valid == True:
            finalQuery = make_query(newQuery)
