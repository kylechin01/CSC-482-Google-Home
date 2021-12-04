# Rapid testing setup

# import sys
# sys.path.append('../')

from mainHelpers import initMain, handleQuery

def main():
    p, wikiRet, schP = initMain()

    mainLoop(p, schP, wikiRet)

def mainLoop(p, schP, wikiRet):
    while True:
        query = getQuery()
        resp = handleQuery(query, p, schP, wikiRet)
        answerQuery(resp)

def getQuery():
    # temp just for testing purposes.
    query = input("Enter your query: ")
    return query

def answerQuery(resp):
    # temp just for testing purposes.
    print(resp)

if __name__ == '__main__':
    main()