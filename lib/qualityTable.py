"""
---------------------------------------------------------------------------
qualityTable.py
Created on: 2019-03-18 13:30:53
---------------------------------------------------------------------------
"""
import os
import sys
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
            [1, 'K1',  2.0, 'Bevarad viktig livsmiljö inom landskapssamband'],
            [1, 'K2',  0.8, 'Bevarad viktig livsmiljö utanför landskapssamband'],
            [1, 'K3',  0.8, 'Bevarad övrig natur inom landskapssamband'],
            [1, 'K4',  0.6, 'Bevarad övrig natur utanför landskapssamband'],
            [1, 'K5',  3.0, 'Bevarat objekt som särskilt gynnar biologisk mångfald'],
            [1, 'K6',  0.7, 'Nyanlagd viktig livsmiljö inom landskapssamband'],
            [1, 'K7',  0.4, 'Nyanlagd viktig livsmiljö utanför landskapssamband'],
            [1, 'K8',  0.4, 'Nyanlagd övrig natur inom landskapssamband'],
            [1, 'K9',  0.2, 'Nyanlagd övrig natur utanför landskapssamband'],
            [1, 'K10', 1.0, 'Nyskapat objekt som särskilt gynnar biologisk mångfald'],
            # Bullerreducering
            [2, 'K11', 0.7, 'Bullervall'],
            [2, 'K12', 0.5, 'Vegetationsklädd porös mark'],
            [2, 'K13', 0.5, 'Trädbälte 15m<bred'],
            [2, 'K14', 0.3, 'Trädrad bakom bullerskärm'],
            [2, 'K15', 1.0, 'Grönska i växtsubstrat på konstruktion'],
            [2, 'K16', 0.2, 'Grönska på konstruktion utan substrat'],
            [2, 'K17', 0.2, 'Positiva ljud från naturen / ljudmaskering'],
            # Dagvatten- och skyfallshantering
            [3, 'K18', 0.7, 'Vattenytor och vattenstråk som används för rening och fördröjning av dagvatten'],
            [3, 'K19', 0.5, 'Genomsläpplig vegetationsklädd naturyta'],
            [3, 'K20', 0.5, 'Vegetationsklädd tillfällig översvämningsyta'],
            [3, 'K21', 0.7, 'Anlagd yta särskilt utformad för rening och fördröjning av dagvatten'],
            [3, 'K22', 0.2, 'Dagvattenhanterade träd i hårdgjord yta'],
            [3, 'K23', 0.2, 'Uppsamling av regnvatten för bevattning'],
            # Klimatanpassning - Mikroklimatreglering
            [4, 'K24', 0.6, 'Flerskiktad vegetation, minst tre vegetationsskikt'],
            [4, 'K25', 0.4, 'Halvöppen vegetation, minst två vegetationsskikt'],
            [4, 'K26', 0.2, 'Öppen vegetation, ett vegetationsskikt'],
            [4, 'K27', 0.5, 'Lövskugga från konstruktion med grönska'],
            [4, 'K28', 0.5, 'Lövskugga från enstaka träd'],
            # Pollinering
            [5, 'K29', 1.3, 'Pollinatörsnod'],
            [5, 'K30', 0.8, 'Pollinatörsgynnande yta'],
            [5, 'K31', 2.0, 'Pollinatörsobjekt'],
            # Rekreation och hälsa
            [6, 'K32', 1.0, 'Artrik natur'],
            [6, 'K33', 0.7, 'Skogskänsla'],
            [6, 'K34', 0.5, 'Grönskande stadsmiljö'],
            [6, 'K35', 0.8, 'Kulturhistorisk grön miljö'],
            [6, 'K36', 3.0, 'Särskilt värdefulla träd, natur- och kulturobjekt'],
            [6, 'K37', 0.5, 'Övriga träd och naturobjekt av värde för stadsbild m.m.'],
            [6, 'K38', 0.5, 'Nyanlagd varierad artrik miljö'],
            [6, 'K39', 0.3, 'Blomsterprakt'],
            [6, 'K40', 0.3, 'Odling och/eller djurhållning'],
            [6, 'K41', 0.4, 'Längre sammanhängande gröna promenadstråk'],
            [6, 'K42', 0.3, 'Natur- och parkytor för aktiviteter'],
            [6, 'K43', 0.3, 'Rofylldhet']
        ]


        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()
        cur.executemany('INSERT OR IGNORE INTO gyf_qgroup VALUES (?,?,?)', group)
        cur.executemany('INSERT OR IGNORE INTO gyf_quality VALUES (?,?,?,?)', q_f)
        cur.close()
        con.commit()
        con.close()