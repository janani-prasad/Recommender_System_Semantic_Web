import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import geopy.distance
from SPARQLWrapper import SPARQLWrapper, TSV,  N3, POST
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from ortools.linear_solver import pywraplp
import math
import datetime


startlocLong = 0
startlocLat = 0
endlocLong = 0
endlocLat = 0
preference = ''
startPt = ''
endPt = ''
startTime = ''
graphDumpList = []
init = 0
idx = []
duration = 13
#Get user input values from txt file and store it in a variable
lines = [line.rstrip('\n') for line in open('userinput')]

for val in range(len(lines)):
    if (lines[val]).find("Start Location Latitude") != -1:
        startlocLat = lines[val].split(':')[-1]
    elif (lines[val]).find("Start Location Longitude") != -1:
        startlocLong = lines[val].split(':')[-1]
    elif (lines[val]).find("End Location Latitude") != -1:
        endlocLat = lines[val].split(':')[-1]
    elif (lines[val]).find("End Location Longitude") != -1:
        endlocLong = lines[val].split(':')[-1]
    elif (lines[val]).find("Preference") != -1:
        preference = lines[val].split(':')[-1]
    elif (lines[val]).find("Start Point") != -1:
        startPt = lines[val].split(':')[-1]
    elif (lines[val]).find("End Point") != -1:
        endPt = lines[val].split(':')[-1]
    elif (lines[val]).find("Start Time") != -1:
        startTime = lines[val].split(':')[-1]
    elif (lines[val]).find("Duration") != -1:
        duration = lines[val].split(':')[-1]

preferences = preference.split(' ')
print preference
print preferences


# Query to get list of categories available in the subgraph
sparqldbq = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/New_Pred_London_DBP_LGD_Fed")

sparqldbq.setQuery("""
   select DISTINCT ?cat 
    where 
    {
        
        ?sws <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?pois .
         {
         select distinct ?poi ?cat 
         WHERE
         {
         ?poi <http://dbpedia.org/ontology/wikiPageWikiLink> ?cati .
         bind(str(?cati) as ?cat)

         }
        } FILTER(str(?poi) = str(?pois))

    }
""")

sparqldbq.setReturnFormat(TSV)
resultsdbq = sparqldbq.query().convert()

catList = resultsdbq.split('\n')

catList = catList[1:-1]

#Fetch pois with their subjects, lat long values
sparqldb = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/New_Pred_London_DBP_LGD_Fed")

sparqldb.setQuery("""
  Prefix lgdo: <http://linkedgeodata.org/ontology/>
Prefix geom: <http://geovocab.org/geometry#>
Prefix ogc:<http://www.opengis.net/ont/geosparql#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX restaurant:<http://newprefix/category/restaurant/>
select distinct ?pois (GROUP_CONCAT(DISTINCT ?allSubj; separator =" ") as ?subj) ?lat ?long (GROUP_CONCAT(DISTINCT ?resname; separator =", ") as ?restaurants)
WHERE
{
    
    ?sws <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?pois .
    ?sws <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
    ?sws <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
    ?pois restaurant:close_to ?resname .
	{
        select distinct ?poi ?cat ?allSubj WHERE{
     ?poi <http://dbpedia.org/ontology/wikiPageWikiLink> ?cat .
      ?poi <http://purl.org/dc/terms/subject> ?allSubj . }
    }FILTER(str(?poi) = str(?pois)) 

} GROUP BY ?pois ?lat ?long

""")

sparqldb.setReturnFormat(TSV)
sparqldb.setMethod(POST)
resultsdb = sparqldb.query().convert()

graphDumpList = resultsdb.split('\n')


# Delete first and last element (heading and empty element)
graphDumpList = graphDumpList[1:-1]

dumpVectArray = np.empty(shape=[len(graphDumpList), 5], dtype='object')

vectorList = []
userPref = []

#Full array with poi repeated for each subject it is mapped to
for row in range(len(graphDumpList)):
    rowitemDump = graphDumpList[row].split("\t")
    for rowColVal in range(len(rowitemDump)):
        dumpVectArray[row][rowColVal] = rowitemDump[rowColVal]
    rowitemVals = graphDumpList[row].split(">	")[1]
    rowitemVals = rowitemVals.split('"')[0]
    if(rowitemVals.find("http://dbpedia.org/resource/Category:")) !=-1:
        rowitemVals = rowitemVals.replace("http://dbpedia.org/resource/Category:", "")
        rowitemVals = re.sub(",", "", rowitemVals)
        rowitemVals = re.sub("-", "", rowitemVals)


    vectorList.append(rowitemVals)


for row in vectorList:
    print row

vectorizer = TfidfVectorizer(lowercase=True)
dumpVect = vectorizer.fit_transform(vectorList)


userPref = [preference]

userVect = vectorizer.transform(userPref)

poiFilterIdxArray = np.empty(shape= [len(dumpVect.A), 2], dtype='object')
for row in range(len(dumpVect.A)):
      cosine_similarities = cosine_similarity(userVect, dumpVect[row]).flatten()
      poiFilterIdxArray[row][0] = cosine_similarities
      poiFilterIdxArray[row][1] = row

#Sort array in descending
poiFilterIdxArray = poiFilterIdxArray[poiFilterIdxArray[:,0].argsort()[::-1]]

poiWithTimeWindowAr = np.empty(shape= [len(poiFilterIdxArray), 6], dtype='object')
for row in range(len(poiFilterIdxArray)):
    if(poiFilterIdxArray[row][0] > 0):
        poiWithTimeWindowAr[row][0] = dumpVectArray[poiFilterIdxArray[row][1]][0].split("resource/")[1]
        poiWithTimeWindowAr[row][0] = poiWithTimeWindowAr[row][0].split(">")[0]
        print dumpVectArray[poiFilterIdxArray[row][1]][1]
        #comment the categories specifically taken from Wikipage wikilink pred. The wikipagewikilink has been taken using distinct
        # for rowL in range(len(catList)):
        #     tempList = (dumpVectArray[poiFilterIdxArray[row][1]][1]).split(" ")
        #     if(catList[rowL] in tempList):
        #         poiWithTimeWindowAr[row][1] = catList[rowL]
        #Subjects
        poiWithTimeWindowAr[row][1] = dumpVectArray[poiFilterIdxArray[row][1]][1].replace("http://dbpedia.org/resource/Category:", "")
        #lat
        tempLat = re.findall(r'"([^"]*)"', dumpVectArray[poiFilterIdxArray[row][1]][2])[0]
        poiWithTimeWindowAr[row][2] = float(tempLat)
        #long
        tempLong = re.findall(r'"([^"]*)"', dumpVectArray[poiFilterIdxArray[row][1]][3])[0]
        poiWithTimeWindowAr[row][3] = float(tempLong)
        # cosine similarity score
        poiWithTimeWindowAr[row][4] = str(poiFilterIdxArray[row][0]).split('[', 1)[1].split(']')[0]
        #Group concat Restaurants for each Poi
        poiWithTimeWindowAr[row][5] = dumpVectArray[poiFilterIdxArray[row][1]][4]

poiWithTimeWindowAr = poiWithTimeWindowAr[~np.all(poiWithTimeWindowAr == None, axis=1)]

# the starting and ending POIs do not have cosine similarity score
firstrow = [startPt,"none",startlocLat,startlocLong,1,""]
lastrow = [endPt,"none",endlocLat,endlocLong,1,""]

#Insert values in poiWith TimeWidowAr for Start nd End locations
poiWithstartEndAr = np.empty(shape= [len(poiWithTimeWindowAr)+2, 5], dtype='object')
poiWithstartEndAr = np.vstack([firstrow, poiWithTimeWindowAr])
poiWithstartEndAr = np.vstack([poiWithstartEndAr, lastrow])

# OR Tools MIP Implementation starts
score = range(len(poiWithstartEndAr))

for row in range(len(poiWithstartEndAr)):
    score[row] = poiWithstartEndAr[row][4]
    score[row] = math.ceil(float(score[row])*1000)/1000

scoreLen = len(score)

timeArray = np.empty(shape= [scoreLen, scoreLen], dtype='object')


for row in range(len(timeArray)):
    for col in range(len(timeArray)):
        if(row == col):
            timeArray[row][col] = 0
        elif (row == 0 and col != 0):
            pt1 = geopy.Point(startlocLat, startlocLong)
            pt2 = geopy.Point(poiWithstartEndAr[col][2], poiWithstartEndAr[col][3])
            dist = geopy.distance.distance(pt1, pt2).km
            tempDistance = float(dist / 5) * 100 / 100
            tempDistDeci = datetime.timedelta(hours=tempDistance)
            temps = tempDistDeci.seconds/60
            timeArray[row][col] = temps
        elif (row == len(timeArray)-1 and col != len(timeArray)-1):
            pt1 = geopy.Point(poiWithstartEndAr[col][2], poiWithstartEndAr[col][3])
            pt2 = geopy.Point(endlocLat, endlocLong)
            dist = geopy.distance.distance(pt1, pt2).km
            tempDistance = float(dist / 5) * 100 / 100
            tempDistDeci = datetime.timedelta(hours=tempDistance)
            temps = tempDistDeci.seconds / 60
            timeArray[row][col] = temps
        else:
            pt1 = geopy.Point(poiWithstartEndAr[row][2], poiWithstartEndAr[row][3])
            pt2 = geopy.Point(poiWithstartEndAr[col][2], poiWithstartEndAr[col][3])
            dist = geopy.distance.distance(pt1, pt2).km
            tempDistance = float(dist/5)*100 / 100
            tempDistDeci = datetime.timedelta(hours=tempDistance)
            temps = tempDistDeci.seconds / 60
            timeArray[row][col] = temps


timeBudget = int(duration) * 60
solver = pywraplp.Solver('SolveOrienteeringProblemMIP',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
x = {}
u = {}
#Create variables (paper eq 6)
for i in range(scoreLen):
  for j in range(scoreLen):
      x[i, j] = solver.BoolVar('x[%i,%i]' % (i, j))

#create helper variable to eliminate sub tour
for i in range(scoreLen):
  u[i] = solver.IntVar(0.0, scoreLen, 'u'+ str(i))

# Constraints
#(C1)
# Sum of row <=1
for i in range(scoreLen):
  solver.Add(solver.Sum([x[i,j] for j in range(scoreLen)]) <= 1)

# (C2)
#If i ==j, put x[i, j] = 0
for i in range(scoreLen):
  for j in range(scoreLen):
      if (i == j):
          solver.Add(x[i,j] == 0)


#Ensure that we start at 1st node and end at Nth node (paper eq 1)
solver.Add(solver.Sum([x[0, i] for i in range(1, scoreLen)]) == 1)
solver.Add(solver.Sum([x[j, scoreLen-1] for j in range(scoreLen-1)]) == 1)
# No node goes out of last node and no node goes to 0
solver.Add(solver.Sum([x[j, 0] for j in range(1, scoreLen)]) == 0)
solver.Add(solver.Sum([x[scoreLen-1, i] for i in range(scoreLen - 1)]) == 0)
solver.Add(solver.Sum([x[0, scoreLen-1]]) == 0)

# Working (paper eq 2)
for k in range(1, scoreLen-1):
    solver.Add(
      solver.Sum([x[i, k] for i in range(scoreLen-1)]) - solver.Sum([x[k, j] for j in range(1, scoreLen)]) == 0)


# (C4)
#Ensure travel is within time budget (paper eq 3)
solver.Add(solver.Sum([(timeArray[i][j] + 60) * x[i, j] for i in range(scoreLen - 1) for j in range(1, scoreLen) ]) <= timeBudget)

# To eliminate sub tour c1 (paper eq 4)
for i in range(1, scoreLen):
 solver.Add(u[i] >=1)

# To eliminate sub tour c2 (paper eq 5)
for i in range(1, scoreLen):
    for j in range(1, scoreLen):
        solver.Add(u[i] - u[j] + 1 <= (scoreLen- 1) * (1 - x[i, j]))


# Objective (paper eq 0)
solver.Maximize(solver.Sum([score[i] * x[i, j] for i in range(1, scoreLen - 1) for j in range(1, scoreLen)]))

# Sets a time limit of 20 seconds.
solver.set_time_limit(20000)

solver.Solve()

listOfPOIs = []
tempo = 0
for i in range(scoreLen):
    for j in range(scoreLen):
        if(x[i, j].solution_value() > 0):
            listOfPOIs.append(str(i) + ":" + str(j))
            print i,  j,  x[i, j].solution_value()
            tempo = tempo + timeArray[i][j]

# The objective value of the solution.
print 'Optimal objective value = %d' % solver.Objective().Value()
# The problem has a feasible solution.
print pywraplp.Solver.FEASIBLE
print solver.VerifySolution(1e-7, True)

finalListArray = np.empty(shape= [len(listOfPOIs), 3], dtype='object')
finalListIdx = []
for i in range(len(listOfPOIs)):
    finalListArray[i][0] = int(listOfPOIs[i].split(":")[0])
    finalListArray[i][1] = int(listOfPOIs[i].split(":")[1])
    finalListArray[i][2] = timeArray[finalListArray[i][0]][finalListArray[i][1]]

temp = False
tempVal = 0
finalListIdx.append(finalListArray[0][0])
finalListIdx.append(finalListArray[0][1])

should_restart = True
while should_restart:
  should_restart = False
  for i in range(len(finalListArray)):
      if (temp == False):
          if (finalListArray[0][1] == finalListArray[i][0]):
              finalListIdx.append(finalListArray[i][1])
              temp = True
              tempVal = finalListArray[i][1]
              should_restart = True
              break
      if (temp == True):
          if (tempVal == finalListArray[i][0]):
              finalListIdx.append(finalListArray[i][1])
              temp = True
              tempVal = finalListArray[i][1]
              should_restart = True
              break

dayTime = datetime.timedelta(hours= int(startTime))

for i in range(1, len(finalListIdx)):
    dayTime = dayTime + datetime.timedelta(minutes=timeArray[finalListIdx[i - 1]][finalListIdx[i]])
    userPrefSub = ''
    tempSubList = poiWithstartEndAr[finalListIdx[i]][1].split(" ")
    if (i != len(finalListIdx) - 1):
        for prefRow in range(len(preferences)):
            if (preferences[prefRow] in tempSubList):
                userPrefSub = preferences[prefRow]
        print " Arrive in " + poiWithstartEndAr[finalListIdx[i]][0] + " at " + str(dayTime) +". Category: " + userPrefSub
    else:
        print " Arrive in " + poiWithstartEndAr[finalListIdx[i]][0] + " at " + str(dayTime)
    if (i != len(finalListIdx) - 1):
        tempRes = poiWithstartEndAr[finalListIdx[i]][5].split(",")[:3]
        threeRes = ",".join(tempRes)
        print " Suggested restaurants around are " + threeRes
    #print "\n"
    #Visiting time for each poi
    dayTime = dayTime + datetime.timedelta(minutes= 60)
    if (i != len(finalListIdx) - 1):
        print " Start from " + poiWithstartEndAr[finalListIdx[i]][0] + " at " + str(dayTime)

