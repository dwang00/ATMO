import csv
import json
import urllib

def cache():

    BEA_KEY = ""
    with open('./keys/BEA_KEY.txt', 'r') as file:
        BEA_KEY = file.read().replace('\n', '')

    EIA_KEY = ""
    with open('./keys/EIA_KEY.txt', 'r') as file:
        EIA_KEY = file.read().replace('\n', '')

    CENSUS_KEY = ""
    with open('./keys/CENSUS_KEY.txt', 'r') as file:
        CENSUS_KEY = file.read().replace('\n', '')

    if BEA_KEY == "":
        print("!!! Please enter a valid BEA key into BEA_KEY.txt !!!")
        exit()
    if EIA_KEY == "":
        print("!!! Please enter a valid EIA key into EIA_KEY.txt !!!")
        exit()
    if CENSUS_KEY == "":
        print("!!! Please enter a valid Census key into CENSUS_KEY.txt !!!")
        exit()

    toDump = {}
    
    # Income Dicts
    incomeDump = {}
    incomeData = {}

    #gdp Dicts
    gdpDump = {}
    gdpData = {}
    
    # co2 Dicts
    co2Dump = {}
    co2Data = {}

    # Gasoline data
    coalDump = {}
    coalData = {}
    
    # -------------------- Income into toDump Dictoionary --------------------
    r = urllib.request.urlopen(
        "https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAINC1&GeoFIPS=STATE&LineCode=3&Year=2017&ResultFormat=JSON".format(BEA_KEY)  # Some API link goes here
    )
    income = json.loads(r.read())
    incomeDump['description'] = income['BEAAPI']['Results']['Statistic']
    incomeDump['units'] = income['BEAAPI']['Results']['UnitOfMeasure']

    print(" * Caching Income Data...")
    
    for member in income['BEAAPI']['Results']['Data']:
        incomeData[ member['GeoName'].replace('*', '') ] = member['DataValue']

    print(" * Done. \n ----------")
        # Deleting Regional Data Entries
    del incomeData['United States']
    del incomeData['New England']
    del incomeData['Mideast']
    del incomeData['Great Lakes']
    del incomeData['Plains']
    del incomeData['Southeast']
    del incomeData['Southwest']
    del incomeData['Rocky Mountain']
    del incomeData['Far West']

    incomeDump['data'] = incomeData
    toDump['income'] = incomeDump

    # -------------------- GDP into toDump Dictoionary --------------------
    g = urllib.request.urlopen(
        "https://apps.bea.gov/api/data/?&UserID={}&method=GetData&datasetname=Regional&TableName=SAGDP2N&GeoFIPS=STATE&LineCode=3&Year=2017&Frequency=A&ResultFormat=JSON".format(BEA_KEY)  # Some API link goes here
    )
    gdp = json.loads(g.read())
    gdpDump['description'] = gdp['BEAAPI']['Results']['Statistic']
    gdpDump['units'] = gdp['BEAAPI']['Results']['UnitOfMeasure']

    print(" * Caching GDP Data...")
    
    for member in gdp['BEAAPI']['Results']['Data']:
        gdpData[ member['GeoName'].replace('*', '') ] = member['DataValue']

    print(" * Done. \n ----------")
        # Deleting Regional Data Entries
    del gdpData['United States ']
    del gdpData['New England']
    del gdpData['Mideast']
    del gdpData['Great Lakes']
    del gdpData['Plains']
    del gdpData['Southeast']
    del gdpData['Southwest']
    del gdpData['Rocky Mountain']
    del gdpData['Far West']
    
    gdpDump['data'] = gdpData
    toDump['gdp'] = gdpDump

    # -------------------- CO2 into toDump Dictoionary --------------------
    p = urllib.request.urlopen(
        "https://api.eia.gov/series/?api_key={}&series_id=EMISS.CO2-TOTV-TT-TO-US.A".format(EIA_KEY)
    )
    co2 = json.loads(p.read())
    co2Dump['description'] = co2['series'][0]['name'][:58]
    co2Dump['units'] = co2['series'][0]['units']
    
    with open("./data/id-to-alpha.csv", "r") as infile:
        alphaCodes = {}
        reader = csv.reader(infile)
        for row in reader:
            alphaCodes[ row[0] ] = row[1]
        
        print(" * Caching CO2 data...")

        for member in alphaCodes:
            c = urllib.request.urlopen(
                "https://api.eia.gov/series/?api_key={}&series_id=EMISS.CO2-TOTV-TT-TO-{}.A".format(EIA_KEY, alphaCodes[member])
            )
            thisCo2 = json.loads(c.read())
            co2Data[thisCo2['series'][0]['name'][60:]] = thisCo2['series'][0]['data'][0][1]
            
        print(" * Done.\n ----------")
                         
    co2Dump['data'] = co2Data
    toDump['co2'] = co2Dump
        
    # -------------------- Coal stats into toDump Dictoionary --------------------
    k = urllib.request.urlopen(
        "https://api.eia.gov/series/?api_key={}&series_id=COAL.CONS_TOT.AL-98.A".format(EIA_KEY)
    )
    coal = json.loads(k.read())
    coalDump['description'] = "Total coal consumption for electric power, by state"
    coalDump['units'] = coal['series'][0]['units']
    
    with open("./data/id-to-alpha.csv", "r") as infile:
        alphaCodes = {}
        reader = csv.reader(infile)
        for row in reader:
            alphaCodes[ row[0] ] = row[1]
        del alphaCodes['9']
        del alphaCodes['12']
        del alphaCodes['13']
        del alphaCodes['40']                
        del alphaCodes['46']
        
        print(" * Caching Coal Stats...")

        for member in alphaCodes:
            l = urllib.request.urlopen(
                "https://api.eia.gov/series/?api_key={}&series_id=COAL.CONS_TOT.{}-98.A".format(EIA_KEY, alphaCodes[member])
            )
            thisCoal = json.loads(l.read())
            # print(thisCoal['series'])
            coalData[ thisCoal['series'][0]['name'][20:-34] ] = thisCoal['series'][0]['data'][0][1]

        coalData['DC'] = 0
        coalData['HI'] = 0
        coalData['ID'] = 0
        coalData['RI'] = 0
        coalData['VT'] = 0  
        print(" * Done.\n ----------")
                         
    coalDump['data'] = coalData
    toDump['coal'] = coalDump

    f = "http://flags.ox3.in/svg/us/US.svg"

    with open("./data/JSON/cache.json", 'w') as outfile:
        json.dump(toDump, outfile, indent=4)

# if __name__ == "__main__":
#     app.debug = True
#     app.run()
