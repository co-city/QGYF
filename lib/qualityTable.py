"""
---------------------------------------------------------------------------
qualityTable.py
Created on: 2019-03-18 13:30:53
---------------------------------------------------------------------------
"""
import os
import sys
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python')
from qgis.utils import spatialite_connect

class QualityTab:

    def init(self, path):
        """ Populate the table "gyf_quality" with values of C/O City's GYF """
        group = [
            [1, 'Biologisk mångdfald', 0.2],
            [2, 'Bullerreducering', 0.2],
            [3, 'Dagvatten- och skyfallshantering', 0.2],
            [4, 'Mikroklimatreglering', 0.2],
            [5, 'Pollination', 0.8],
            [6, 'Rekreation och hälsa', 0.3]
        ]

        q_f = [
            # Biologisk mångdfald
            ['K1',  2.0, 'Bevarad viktig livsmiljö inom landskapssamband'],
            ['K2',  0.8, 'Bevarad viktig livsmiljö utanför landskapssamband'],
            ['K3',  0.8, 'Bevarad övrig natur inom landskapssamband'],
            ['K4',  0.6, 'Bevarad övrig natur utanför landskapssamband'],
            ['K5',  3.0, 'Bevarat objekt som särskilt gynnar biologisk mångfald'],
            ['K6',  0.7, 'Nyanlagd viktig livsmiljö inom landskapssamband'],
            ['K7',  0.4, 'Nyanlagd viktig livsmiljö utanför landskapssamband'],
            ['K8',  0.4, 'Nyanlagd övrig natur inom landskapssamband'],
            ['K9',  0.2, 'Nyanlagd övrig natur utanför landskapssamband'],
            ['K10', 1.0, 'Nyskapat objekt som särskilt gynnar biologisk mångfald'],
            # Bullerreducering
            ['K11', 0.7, 'Bullervall'],
            ['K12', 0.5, 'Vegetationsklädd porös mark'],
            ['K13', 0.5, 'Trädbälte 15m<bred'],
            ['K14', 0.3, 'Trädrad bakom bullerskärm'],
            ['K15', 1.0, 'Grönska i växtsubstrat på konstruktion'],
            ['K16', 0.2, 'Grönska på konstruktion utan substrat'],
            ['K17', 0.2, 'Positiva ljud från naturen / ljudmaskering'],
            # Dagvatten- och skyfallshantering
            ['K18', 0.7, 'Vattenytor och vattenstråk som används för rening och fördröjning av dagvatten'],
            ['K19', 0.5, 'Genomsläpplig vegetationsklädd naturyta'],
            ['K20', 0.5, 'Vegetationsklädd tillfällig översvämningsyta'],
            ['K21', 0.7, 'Anlagd yta särskilt utformad för rening och fördröjning av dagvatten'],
            ['K22', 0.2, 'Dagvattenhanterade träd i hårdgjord yta'],
            ['K23', 0.2, 'Uppsamling av regnvatten för bevattning'],
            # Klimatanpassning - Mikroklimatreglering
            ['K24', 0.6, 'Flerskiktad vegetation, minst tre vegetationsskikt'],
            ['K25', 0.4, 'Halvöppen vegetation, minst två vegetationsskikt'],
            ['K26', 0.2, 'Öppen vegetation, ett vegetationsskikt'],
            ['K27', 0.5, 'Lövskugga från konstruktion med grönska'],
            ['K28', 0.5, 'Lövskugga från enstaka träd'],
            # Pollinering
            ['K29', 1.3, 'Pollinatörsnod'],
            ['K30', 0.8, 'Pollinatörsgynnande yta'],
            ['K31', 2.0, 'Pollinatörsobjekt'],
            # Rekreation och hälsa
            ['K32', 1.0, 'Artrik natur'],
            ['K33', 0.7, 'Skogskänsla'],
            ['K34', 0.5, 'Grönskande stadsmiljö'],
            ['K35', 0.8, 'Kulturhistorisk grön miljö'],
            ['K36', 3.0, 'Särskilt värdefulla träd, natur- och kulturobjekt'],
            ['K37', 0.5, 'Övriga träd och naturobjekt av värde för stadsbild m.m.'],
            ['K38', 0.5, 'Nyanlagd varierad artrik miljö'],
            ['K39', 0.3, 'Blomsterprakt'],
            ['K40', 0.3, 'Odling och/eller djurhållning'],
            ['K41', 0.4, 'Längre sammanhängande gröna promenadstråk'],
            ['K42', 0.3, 'Natur- och parkytor för aktiviteter'],
            ['K43', 0.3, 'Rofylldhet']
        ]


        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()
        cur.executemany('INSERT INTO gyf_qgroup VALUES (?,?,?)', group)
        cur.executemany('INSERT INTO gyf_quality VALUES (?,?,?)', q_f)
        cur.close()
        con.commit()

        
        con.close()
