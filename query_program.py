import pyparsing as pp
from google.cloud.firestore_v1.base_query import FieldFilter, Or # TODO do we need more than this?
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import firestore_async
from google.cloud.firestore import AsyncClient
from tabulate import tabulate



# setup for firebase
cred = credentials.Certificate("movie-collection-fd2b8-firebase-adminsdk-fbsvc-0d2c29ef17.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
movies_ref = db.collection("movies")

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
        genre_str = ""
        for g in range(0,len(self.genre)):
            if g != len(self.genre) - 1:
                genre_str += self.genre[g] + ", "
            else:
                genre_str += self.genre[g]

        return {"index": f"{self.index}", 
                "movie_name": f"{self.movie_name}",
                "year_of_release": self.year_of_release,
                "category": f"{self.category}",
                "run_time": f"{self.run_time}",
                "genre": f"{genre_str}",
                "imdb_rating": f"{self.imdb_rating}",
                "votes": f"{self.votes}",
                "gross_total": f"{self.gross_total}",
                "seen": f"{self.seen}"}
    
    # takes in a dictionary and returns a movie object
    @staticmethod
    def from_dict(source):
        return Movie(source['index'], source['movie_name'], source['year_of_release'], source['category'], source['run_time'], source['genre'], source['imdb_rating'], source['votes'], source['gross_total'], source['seen'])

    def __str__(self):
        return self.movie_name

# query class
# instance created when user makes a query
class Query:

    def __init__(self, column, operator, specification, logical_op=None,
                 column2 = None, operator2 = None, specification2 = None):
        self.column = column
        self.operator = operator
        self.specification = specification
        self.logical_op = logical_op
        self.column2 = column2
        self.operator2 = operator2
        self.specification2 = specification2
        self.valid = False
        
    def get_column(self):
        return self.column

    def get_operator(self):
        return self.operator
    
    def get_specification(self):
        return self.specification
    
# helper dictionary function so integers work
NUMERIC = {
    "year_of_release": int,
    "run_time": int,
    "votes": int,
    "imdb_rating": float,
    "gross_total": float,
}

def if_numeric(column, value):
    if column in NUMERIC:
        return NUMERIC[column](value)
    else:
        return value   

# some function for input validation using pyparsing
# returns input in the form of a query
def validate_input(input):

    category = pp.QuotedString('"')
    operator = pp.one_of("== < > <= >= != array_contains")
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
            return None

    # mark the query as valid
    newQuery.valid = True
    return newQuery


# TODO make sure it works once admin is up
def make_query(query):
    
    # check for integers
    specification1 = if_numeric(query.column, query.specification)

    # and queries
    if query.logical_op == "AND":

        specification2 = if_numeric(query.column, query.specification2)
        finishedQuery = movies_ref.where(filter=FieldFilter(query.column, query.operator, specification1)).where(
        filter=FieldFilter(query.column2, query.operator2, specification2)).stream()

    # or 
    elif query.logical_op == "OR":
        specification2 = if_numeric(query.column, query.specification2)
        finishedQuery = movies_ref.where(
            filter=Or(
                [
                    FieldFilter(query.column, query.operator, specification1),
                    FieldFilter(query.column2, query.operator2, specification2),
                ]
            )
        ).stream()
    # simple queries
    else:
        finishedQuery = movies_ref.where(filter=FieldFilter(query.column, query.operator, specification1)).stream()
    return finishedQuery
    

# function that runs query/validates it

# function that prints query output



# main goes here
def main():
    
    # program loop
    programOn = True # boolean value for turning on the query program
    while programOn == True:

        # while input is not valid, ask for query
        print("Make a query, input HELP for instructions, or EXIT")
        queryText = input("make a query: ")

        # if exit 
        if queryText == "EXIT":
            programOn = False

        elif queryText == "HELP":
            print("Query structure:")
            print('"category", operator, "specification"')
            print("categories:")
            print("genre, year _of_release, category, movie_name, runtime, imdb_rating, gross_total, seen")
            print("operators:")
            print("==, <, >, <=, >=, !=, array-contains (only for genre)")
            print("Example query: \"genre\" array_contains \"Drama\"")
            print("Combine two queries with AND or OR")
            print("Example query: \"year_of_release\" > \"1990\" AND \"category\" == \"R\"")
            print("input EXIT to end the program")

        # if input is validated, make a query object
        elif programOn == True:
            # validate the input
            newQuery = validate_input(queryText)
            # if query is valid, run it
            if newQuery is not None:
                finalQuery = make_query(newQuery)

                data = []
                for doc in finalQuery:
                    movie = Movie.from_dict(doc.to_dict())
                    data.append(movie.to_dict())
                print(tabulate(data, headers="keys", tablefmt="grid"))


            else:
                print("invalid query. Try again")
            
if __name__ == "__main__":
    main()
