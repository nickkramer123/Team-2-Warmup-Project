import pyparsing as pp
from google.cloud.firestore_v1.base_query import FieldFilter, Or
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from tabulate import tabulate

# setup for firebase
cred = credentials.Certificate("movie-collection-fd2b8-firebase-adminsdk-fbsvc-0d2c29ef17.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
movies_ref = db.collection("movies")

# movie class
# holds all of the movie information and allows for ease of data transformation from firebase to a dictionary
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
    
# helper function to handle genre array_contains
def genre_check(column, operator):
    if column == "genre":
        #handles if the user is looking for not what they specified
        if operator == "!=" or operator == ">" or operator == "<":
            operator = "array_contains_not"
        else:
            # handles if the user wants ==, >=, or <=
            operator = "array_contains"
    return operator

#helper function to handle array_contains_not
def array_contains_not(query, movies_ref):
    finishedQuery1 = []
    finishedQuery2 = []
    # If the first operator is a not operator
    if query.operator == "array_contains_not":
        notQuery = movies_ref.where(filter=FieldFilter(query.column, "array_contains", query.specification)).get()
        allQuery = movies_ref.get()
        for doc in allQuery:
            if doc not in notQuery:
                finishedQuery1.append(doc)
    else:
        finishedQuery1 = movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification)).get()
    # If the second operator exists and is a not operator
    if query.operator2 and query.operator2 == "array_contains_not":
        notQuery = movies_ref.where(filter=FieldFilter(query.column2, "array_contains", query.specification2)).get()
        allQuery = movies_ref.get()
        for doc in allQuery:
            if doc not in notQuery:
                finishedQuery2.append(doc)
    elif query.operator2:
        finishedQuery2 = movies_ref.where(filter=FieldFilter(query.column2, query.operator2, query.specification2)).get()
    #return finishedQuery1 and finishedQuery2
    return finishedQuery1, finishedQuery2

# validate_input function for input validation using pyparsing
# takes in the user input and returns it in the form of a Query or None is Query is not valid
def validate_input(input):
    #setup pyparsing
    category = pp.Word(pp.alphas + "_")
    operator = pp.one_of("== < > <= >= !=")
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

# make_query function takes in a Query and returns the ou
def make_query(query):
    # check for integers
    query.specification = if_numeric(query.column, query.specification)
    # handle case for list type of genre
    query.operator = genre_check(query.column, query.operator)

    # and queries
    if query.logical_op == "AND":
        query.specification2 = if_numeric(query.column2, query.specification2)
        query.operator2 = genre_check(query.column2, query.operator2)
        #Seperated AND queries because only one "array-contains" can be used in one query at a time to firebase
        if query.operator == "array_contains_not" or query.operator2 == "array_contains_not":
            finishedQuery1, finishedQuery2 = array_contains_not(query, movies_ref)
        else:
            finishedQuery1 = movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification)).get()
            finishedQuery2 = movies_ref.where(filter=FieldFilter(query.column2, query.operator2, query.specification2)).get()
        finishedQuery = []
        for doc in finishedQuery1:
            if doc in finishedQuery2:
                finishedQuery.append(doc)

    # or 
    elif query.logical_op == "OR":
        query.specification2 = if_numeric(query.column2, query.specification2)
        query.operator2 = genre_check(query.column2, query.operator2)
        if query.operator == "array_contains_not" or query.operator2 == "array_contains_not":
            finishedQuery1, finishedQuery2 = array_contains_not(query, movies_ref)
            finishedQuery = []
            for doc in finishedQuery1:
                finishedQuery.append(doc)
            for doc in finishedQuery2:
                if doc not in finishedQuery:
                    finishedQuery.append(doc)
        else:
            finishedQuery = movies_ref.where(
                filter=Or(
                    [
                        FieldFilter(query.column, query.operator, query.specification),
                        FieldFilter(query.column2, query.operator2, query.specification2),
                    ]
                )
            ).stream()
        
    # simple queries
    else:
        # handle special case of not included in an array
        if query.operator == "array_contains_not":
            finishedQuery, _ = array_contains_not(query, movies_ref)
        else:
            finishedQuery = movies_ref.where(filter=FieldFilter(query.column, query.operator, query.specification)).stream()
    return finishedQuery

# main function handles the user input from the command line
# it asks for user input and then calls validate_input and make_query functions to interact with firebase db
# main then prints the information the user requested from the db
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
            print('category operator "specification"')
            print("categories:")
            print("genre, year_of_release, category, movie_name, runtime, imdb_rating, gross_total, seen")
            print("operators:")
            print("==, <, >, <=, >=, !=")
            print("Example query: genre == \"Drama\"")
            print("Combine two queries with AND or OR")
            print("Example query: year_of_release > \"1990\" AND category == \"R\"")
            print("input EXIT to end the program")

        # if input is validated, make a query object
        elif programOn == True:
            # validate the input
            newQuery = validate_input(queryText)
            # if query is valid, run it
            if newQuery is not None:
                finalQuery = make_query(newQuery)
                # format data returned from query to be ready to print
                data = []
                for doc in finalQuery:
                    movie = Movie.from_dict(doc.to_dict())
                    data.append(movie.to_dict())
                print(tabulate(data, headers="keys", tablefmt="grid"))

            else:
                print("invalid query. Try again")
            
if __name__ == "__main__":
    main()