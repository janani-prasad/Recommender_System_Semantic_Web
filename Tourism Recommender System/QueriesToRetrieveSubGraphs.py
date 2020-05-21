# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, N3, TSV, POST
import numpy as np

#Query to retrieve pois from dbpedia
sparqldb = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/dbpedia")

sparqldb.setQuery("""
SELECT distinct ?poi
WHERE
{
 ?category <http://www.w3.org/2004/02/skos/core#broader>  <http://dbpedia.org/resource/Category:Visitor_attractions_in_London> .
 ?poi <http://dbpedia.org/ontology/wikiPageWikiLink> ?category .
 ?category <http://www.w3.org/2004/02/skos/core#prefLabel> ?caten .
 ?poi <http://purl.org/dc/terms/subject> ?allSubj .

 FILTER(lang(?caten)="en") .
 FILTER(?caten IN("Annual events in London"@en,"Canals in London"@en,"Castles in London"@en,"Gardens in London"@en,"Monasteries in London"@en,"Monuments and memorials in London"@en,"Towers in London"@en,"Churches in London"@en,"Entertainment in London"@en,"Music venues in London"@en,"Retail buildings in London"@en,"Theatre in London"@en,"Nature reserves in London"@en,"Archaeological sites in London"@en,"Retail markets in London"@en,"English Heritage sites in London"@en,"Public art in London"@en,"Palaces in London"@en,"River Thames"@en,"Royal buildings in London"@en,"World Heritage Sites in London"@en,"Heritage railways in London"@en,"Conservation areas in London"@en,"London Zoo"@en,"Caves of London"@en,"Museums in London"@en,"Parks and open spaces in London"@en,"Ruins in London"@en,"Windmills in London"@en,"Protected areas of London"@en,"Piers in London"@en)) .
}
""")

sparqldb.setReturnFormat(TSV)
resultsdb = sparqldb.query().convert()
#
print(resultsdb)

attractionsList = resultsdb.split('\n')
indexes = []

for row in range(len(attractionsList)):
    if (attractionsList[row]).find("\u0027") != -1:
        attractionsList[row]=attractionsList[row].replace("\u0027", "\'")
    if (attractionsList[row]).find("\u00E9") != -1:
        attractionsList[row]=attractionsList[row].replace("\u00E9", "e")
    if (attractionsList[row]).find("\u00ED") != -1:
        attractionsList[row]=attractionsList[row].replace("\u00ED", "i")
    if (attractionsList[row]).find("\u00E1") != -1:
        attractionsList[row]=attractionsList[row].replace("\u00E1", "a")
    if (attractionsList[row]).find("\u2013") != -1:
        attractionsList[row]=attractionsList[row].replace("\u2013", "-")
    if (attractionsList[row]).find("\t") != -1:
        attractionsList[row]=attractionsList[row].replace("\t", "  ")
    if (attractionsList[row]).find("\'") != -1:
        attractionsList[row] = attractionsList[row].replace("\'", "")
    if (attractionsList[row]).find(".jpg") != -1:
        indexes.append(row)
    if (attractionsList[row]).find("List_of_") != -1:
        indexes.append(row)
    if (attractionsList[row]).find("/United_Kingdom>") != -1:
        indexes.append(row)
    if (attractionsList[row]).find("/London>") != -1:
        indexes.append(row)
    if (attractionsList[row]).find("Tourism_in") != -1:
        indexes.append(row)
    # # if (attractionsList[row]).find(" .") != -1:
    #     attractionsList[row] = attractionsList[row].replace(" .", "")


attractionsList = np.delete(attractionsList, indexes, axis=0)
#
# # filePOI = open('London_DBP_Data.n3','w')
# # for row in range(len(attractionsList)):
# #     filePOI.write(attractionsList[row])
# #     filePOI.write('\n')
# #
# # filePOI.close()
#
print attractionsList

poiList = []
for row in xrange(1, len(attractionsList)):
    if(attractionsList[row]):
        poiList.append(attractionsList[row])

poiFilterString = ', '.join(map(str, poiList))


#Query to retrieve pois and their subjects from dbpedia and save them as a dump
sparqleg = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/dbpedia")

sparqleg.setQuery("""
CONSTRUCT
{
 ?category <http://www.w3.org/2004/02/skos/core#broader>  <http://dbpedia.org/resource/Category:Visitor_attractions_in_London> .
 ?poi <http://dbpedia.org/ontology/wikiPageWikiLink> ?category .
 ?poi <http://dbpedia.org/ontology/abstract> ?desc  .
 ?category <http://www.w3.org/2004/02/skos/core#prefLabel> ?caten .
 ?poi <http://purl.org/dc/terms/subject> ?allSubj .
}

WHERE
{
 ?category <http://www.w3.org/2004/02/skos/core#broader>  <http://dbpedia.org/resource/Category:Visitor_attractions_in_London> .
 ?poi <http://dbpedia.org/ontology/wikiPageWikiLink> ?category .
 OPTIONAL{?poi <http://dbpedia.org/ontology/abstract> ?desc  .
 FILTER langmatches(lang(?desc),"en") .}
 ?category <http://www.w3.org/2004/02/skos/core#prefLabel> ?caten .
 ?poi <http://purl.org/dc/terms/subject> ?allSubj .


 FILTER(lang(?caten)="en") .
 FILTER(?caten IN("Annual events in London"@en,"Canals in London"@en,"Castles in London"@en,"Gardens in London"@en,"Monasteries in London"@en,"Monuments and memorials in London"@en,"Towers in London"@en,"Churches in London"@en,"Entertainment in London"@en,"Music venues in London"@en,"Retail buildings in London"@en,"Theatre in London"@en,"Nature reserves in London"@en,"Archaeological sites in London"@en,"Retail markets in London"@en,"English Heritage sites in London"@en,"Public art in London"@en,"Palaces in London"@en,"River Thames"@en,"Royal buildings in London"@en,"World Heritage Sites in London"@en,"Heritage railways in London"@en,"Conservation areas in London"@en,"London Zoo"@en,"Caves of London"@en,"Museums in London"@en,"Parks and open spaces in London"@en,"Ruins in London"@en,"Windmills in London"@en,"Protected areas of London"@en,"Piers in London"@en)) .
}

""")

sparqleg.setReturnFormat(N3)
sparqleg.setMethod(POST)
resultseg = sparqleg.query().convert()
print "N3"
print resultseg
attractionsLists = resultseg.split('\n')
print len(attractionsLists)
# print(attractionsList)
filePOI = open('New_London_DBP_Dump_Cat_AllSubj_Poi.n3','w')
filePOI.write(resultseg)
filePOI.close()




#Query to retrieve restaurants in linkedgeodata for pois retrieved from dbpedia and save them as a dump
sparqlFullFed = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/linkedgeodata")

sparqlFullFed.setQuery("""

PREFIX restaurant:<http://newprefix/category/restaurant/>
Prefix lgdo: <http://linkedgeodata.org/ontology/>
Prefix geom: <http://geovocab.org/geometry#>
Prefix ogc:<http://www.opengis.net/ont/geosparql#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
CONSTRUCT
{
    ?swsnode <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?name .
    ?swsnode <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?flat .
    ?swsnode <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?flong .
    ?name restaurant:close_to ?resname .
    ?res rdfs:label ?resname .
    ?res geom:geometry ?resgeo .

}
WHERE
{
    ?swsnode <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?name .
    FILTER(?name IN("""+ poiFilterString +""")) .
    ?swsnode <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .
  bind(xsd:float(?lat) as ?flat) .
    ?swsnode <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?long .
  bind(xsd:float(?long) as ?flong) .
   optional {
    ?res
            a lgdo:Restaurant ;
            rdfs:label ?resname ;
            geom:geometry [
            ogc:asWKT ?resgeo
            ] .
  Filter(bif:st_intersects (?resgeo, bif:st_point(?flong, ?flat), 0.50)) .}

  
}
""")

sparqlFullFed.setReturnFormat(N3)
sparqlFullFed.setMethod(POST)
resultsFed = sparqlFullFed.query().convert()
# resultslgd = sparqldb.query().convert()
print "LGD***************"
print resultsFed
fedList = resultsFed.split("\n")
print len(fedList)
filelPOI = open('London_LGD_DUMP_New_Pred_RESTAURANT.n3','w')

filelPOI.write(resultsFed)

filelPOI.close()




































# filePOI = open('London_Poi_AllPois_Fedrn.n3','w')
#
# filePOI.write(resultsFed)
# filePOI.close()

# with open('London_Poi_Fed.n3', 'a') as f:
#      f.write(resultsdb)

#
# attractionsList = resultsdb.split('\n')
# print len(attractionsList)
#
#
#
#
# indexes = []
#
# for row in range(len(attractionsList)):
#     if (attractionsList[row]).find("\u0027") != -1:
#         attractionsList[row]=attractionsList[row].replace("\u0027", "\'")
#     if (attractionsList[row]).find("\u00E9") != -1:
#         attractionsList[row]=attractionsList[row].replace("\u00E9", "e")
#     if (attractionsList[row]).find("\u00ED") != -1:
#         attractionsList[row]=attractionsList[row].replace("\u00ED", "i")
#     if (attractionsList[row]).find("\u00E1") != -1:
#         attractionsList[row]=attractionsList[row].replace("\u00E1", "a")
#     if (attractionsList[row]).find("\u2013") != -1:
#         attractionsList[row]=attractionsList[row].replace("\u2013", "-")
#     if (attractionsList[row]).find("\t") != -1:
#         attractionsList[row]=attractionsList[row].replace("\t", "  ")
#     if (attractionsList[row]).find("\'") != -1:
#         attractionsList[row] = attractionsList[row].replace("\'", "")
#     if (attractionsList[row]).find(".jpg") != -1:
#         indexes.append(row)
#     if (attractionsList[row]).find("List_of_") != -1:
#         indexes.append(row)
#     if (attractionsList[row]).find("dbr:United_Kingdom") != -1:
#         indexes.append(row)
#     if (attractionsList[row]).find("Tourism_in") != -1:
#         indexes.append(row)
#     # # if (attractionsList[row]).find(" .") != -1:
#     #     attractionsList[row] = attractionsList[row].replace(" .", "")
#
#
# attractionsList = np.delete(attractionsList, indexes, axis=0)

# filePOI = open('London_Poi_ThreeCat.n3','w')
# for row in range(len(attractionsList)):
#     filePOI.write(attractionsList[row])
#     filePOI.write("\n")
#
#
# filePOI.close()
# print len(attractionsList)

# print("attractions")
# print(attractionsList)


#
# with open('London_Attraction_Fed.n3', 'a') as f:
#      f.write(attractionsList)
#
# fullArray = np.empty(shape=[len(attractionsList), 3], dtype='object')
# geoArray = np.empty(shape=[len(attractionsList), 3], dtype='object')
#
#
#
# poiList = []
# initialVal = 0
# latlongList = []
# pois = []
#
# for row in xrange(initialVal+3, len(attractionsList)):
#     rowitemVals = attractionsList[row].split('  ')
#     # print("col length")
#     # print(len(rowitemVals))
#     for rowColVal in range(len(rowitemVals)):
#         fullArray[row][rowColVal] = rowitemVals[rowColVal]
#         geoArray[row][rowColVal] = rowitemVals[rowColVal]
#     # print(geoArray[row])
#
#
# for row in xrange(initialVal+3, len(geoArray)):
#     pois.append(geoArray[row][0])
#     latLong = geoArray[row][2]
#     latlongval = latLong.split('(', 1)[1].split(')')[0]
#     latlongList.append(latlongval.split(" "))
#
#
#
# latlongarray = np.array(latlongList)
# print(len(latlongarray))
# print(len(pois))
#
# restaurantArray = np.empty(shape=[len(latlongarray), 5], dtype='object')
#
# restaurantList = []
#
#
# file = open('London_Attraction_Fed.n3','w')
#
# for row in range(len(latlongarray)):
#     print(pois[row])
#     sparqllgd = SPARQLWrapper("http://linkedgeodata.org/sparql")
#
#     sparqllgd.setQuery("""
#         prefix virtrdf:  <http://www.openlinksw.com/schemas/virtrdf#>
#         prefix ns1:  <http://geovocab.org/geometry#>
#         prefix ns2:  <http://linkedgeodata.org/triplify/>
#         prefix dbr:	<http://dbpedia.org/resource/>
#         CONSTRUCT {?s <http://www.opengis.net/ont/geosparql#asWKT> "POINT("""+latlongarray[row][0]+""" """+latlongarray[row][1]+""")"^^virtrdf:Geometry .
#         }
#         WHERE
#         {?s <http://www.opengis.net/ont/geosparql#asWKT> ?o
#
#         }limit 1
#         """)
#
#     sparqllgd.setReturnFormat(N3)
#     resultslgd = sparqllgd.query().convert()
#     print("\n")
#     print("Restaurants in 0.9 metres from Palaces in London list")
#     print(resultslgd)
#     restaurantArrayList = resultslgd.split('\n')
#     for col in range(len(restaurantArrayList)):
#         if (restaurantArrayList[col]).find("\u00E9") != -1:
#             restaurantArrayList[col] = restaurantArrayList[col].replace("\u00E9", "e")
#         restaurantArray[row][col] = restaurantArrayList[col]
#
#
# for row in range(len(restaurantArray)):
#
#     for col in range((restaurantArray.shape[1])):
#         if (restaurantArray[row][col]) is None:
#             continue
#         if (restaurantArray[row][col]).find("\t") != -1:
#             restaurantArray[row][col] = restaurantArray[row][col].replace("\t", "  ")
#         if (restaurantArray[row][col]).find("\'") != -1:
#             restaurantArray[row][col] = restaurantArray[row][col].replace("\'", "")
#         if (row > 0):
#             if ((col == 0) or (col == 1)):
#                 if (restaurantArray[row][col]).find("@prefix") != -1:
#                     continue
#
#
#         file.write(restaurantArray[row][col])
#         file.write("\n")
#     file.write("\n")
#
#
# file.close()

# print("restaurants")
# print(restaurantArray)



#removing unwanted pois
#
# for row in range(len(poiarray)):
#     if(poiarray[row]).find("\u0027") != -1:
#         poiarray[row]=poiarray[row].replace("\u0027", "\'")
#     if (poiarray[row]).find(" ,") != -1:
#         poiarray[row] = poiarray[row].replace(" ,", "")
#     if (poiarray[row]).find(" .") != -1:
#         poiarray[row] = poiarray[row].replace(" .", "")
#     if (poiarray[row]).find(".jpg") != -1:
#         indexes.append(row)
#     if (poiarray[row]).find("List_of_tallest_buildings_and_structures_in_London") != -1:
#         indexes.append(row)
#     if (poiarray[row]).find("dbr:United_Kingdom") != -1:
#         indexes.append(row)
#
# poiarray = np.delete(poiarray, indexes, axis=0)
# print(poiarray)
# longarray = np.empty(shape=[len(poiarray), 3], dtype='object')
