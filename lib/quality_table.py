"""
---------------------------------------------------------------------------
qualityTable.py
Created on: 2019-03-18 13:30:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.utils import spatialite_connect
from PyQt5.QtCore import QSettings

class QualityTable:

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

        text = [
            # Biologisk mångdfald
            "Grön- eller blåyta av hög ekologisk kvalitet som ingår i utpekat landskapssamband.<br><br>Ytan är både viktig för djur och växters spridning samt utgörs antingen av viktig livsmiljö för skyddsvärda arter eller av kärnområden/värdekärnor som är viktiga för en mångfald av arter.<br><br>Ytans kvalitet ska upprätthållas över tid. Det ska säkerställas att storleken är tillräcklig och att slitage och störningar inte påverkar kvaliteten negativt. Detta kan göras i exempelvis skötselplan.",
            "Grön- eller blåyta utpekad för området som exempelvis viktig livsmiljö eller värdekärna men som är fragmenterad, dvs. är isolerad från landskapssamband.",
            "Grön- eller blåyta av ensartad karaktär som ligger inom ett landskapssamband men inte uppfyller kraven enligt K1/K2.<br><br>Viktiga för växter och djurs spridning.<br><br>Även dessa områden kännetecknas av naturliga och självreglerande processer och kan ofta utvecklas mot högre biodiversitet.",
            "Isolerade grön eller blåytor av ensartad karaktär som inte uppfyller kraven i K1/K2.<br><br>Även dessa områden kännetecknas av naturliga och självreglerande processer och kan ofta utvecklas mot högre biodiversitet.",
            "Gäller endast bevarade objekt som bevarats i sitt ursprungliga läge.<br><br><i>50 kvm/st:</i> Stora gamla träd (>80 cm diameter)<br><i>25 kvm/st:</i> hålträd, bärande träd<br><i>15 kvm/st:</i> högstubbar, buskar, tätt buskage/fågelsnår, död ved (större träd, lågor eller stammar)",
            "Här krävs att grön- eller blåytan både kompletterar befintlig viktig livsmiljö i området och stärker ett svagt samband som även gör den till ny spridningsväg mellan två befintliga biotoper av samma/liknande slag.<br><br>Ta reda på vilka viktiga livsmiljöer, som finns i närområdet. Svaga samband kan till exempel ses i ekologiska kartläggningar. Fråga din kommunekolog om hjälp.",
            "Anlagd grön- eller blåyta med tillskapta höga naturvärden som utgör viktig livsmiljö, men som ligger isolerat från landskapssamband.<br><br>Nyskapad biotop, viktig för det lokala djur- och växtlivet, exempelvis skogsbiotop, gröna tak, parker med höga ekologiska kvaliteter men som är avskärmade från sitt samband, ex fickparker omgiven av hög och stängd bebyggelse.",
            "Anlagd grön- eller blåyta av ensartad karraktär som kompletterar befintlig viktig livsmiljö, kärnområde eller värdekärna i eller fyller ut ett befintligt ”hålrum” som även gör den till ny spridningsväg mellan två befintliga biotoper av samma/liknande slag.",
            "Isolerade grön- eller blåytor som inte uppfyller kraven i K6/K7.<br><br>Även dessa områden kännetecknas av naturliga och självreglerande processer och kan ofta utvecklas mot högre biodiversitet.",
            "Gäller endast nyskapade eller tillförda objekt som särskilt gynnar biologisk mångfald.<br><br>Åtgärder behöver förankras hos ekolog för att säkersälla att de kommer ha positiv effekt på den biologiska mångfalden. Om befintliga träd tas ned men lämnas som död ved eller högstubbar får även detta räknas.<br><br>15/25/50 kvm/st",
            # Bullerreducering
            "Upphöjd mark med vegetation, i första hand placerad nära bullerkällan. Ska bestå av poröst material med potential att dämpa buller, exempelvis jord.<br><br>Bullervallens yta räknas.",
            "Vegetationsklädd mark placerad i markplan mellan bullerkällan och mottagaren. Marken måste vara porös för att få tillgodoräknas.<br><br>Vid armerad vegetation räknas hälften av ytan (vegetation i fogar räknas ej).",
            "Grönyta med flera trädrader som placeras mellan bullerkällan och mottagaren på sådan höjd att siktlinjen skärmas.<br><br>Det ska ej vara möjligt att se igenom vägridån, den ska dölja bullerkällan.",
            "Träden ska placeras utan stora glipor mellan trädens kronor. Om träden placeras i hårdgjord mark bör de planteras i skelettjord eller motsvarande. Om träden får bra förutsättningar ökar storleken på trädens kronor.<br><br>Ibland kan dubbla trädrader vara en lösning för att få till en bra krontäckning. Om detta görs, räknas bara en rad.",
            "Substratytan där växtligheten i vertikala ytor kan växa får räknas. Substratet skall vara tjockt och poröst. Kan vara gröna tak, väggar eller fristående skärmar.<br><br>För att få tillgodoräkna poängen måste följande kriterier uppfyllas för respektive kategori:<br><br><i>Gröna tak</i> - 10 cm substrat. Bullret hos mottagaren ska vara dominerat av bidrag som kommit över de gröna taken.<br><br><i>Gröna väggar</i> - 20 cm substrat / 10 cm substrat + 10 cm luftspalt mot fasad. Kassetter med substrat kan monteras med avstånd till fasad, utan förändrad akustisk effekt. För klängväxter som inte behöver substrat, kan i stället en akustisk absorbent användas (tillexempel mineralull).<br><br><i>Fristående bullerskärmar</i> - 20 cm bred. Det är även viktigt att skärmen har en hård kärna så att ljud inte passerar igenom skärmen.",
            "Den yta som täcks av vegetation direkt eller senast inom loppet av 5 år räknas.<br><br>Klätterväxter på bullerplank, fasad, pergola mm",
            "Objekt och föremål som maskerar oönskat ljud, bidrar till rofylldhet och bättre ljudmiljö. Får endast räknas där det positiva ljudet har potential att överrösta det negativa bullret. I mycket bullriga miljöer bidrar inte positiva ljud till rofyllda miljöer.<br><br>Var gränsen går för när det är för bullrigt varierar.  50 dBA är en nivå som rapporterats för stadsparker. Men även vid högre nivåer kan positiva ljud ibland ha önskad effekt.<br><br>25 kvm/st",
            # Dagvatten- och skyfallshantering
            "Vattenytor och vattenstråk som renar och fördröjer dagvatten. Träd som ingår i ytorna räknas in här (räknas ej separat). Hårdgjorda ytor räknas ej.<br><br>Vattnet ska vara så pass rent att det inte påverkar det akvatiska ekosystemet negativt.",
            "Naturytor med låg avrinning men hög genomsläpplighet (avrinningskofficient max 0,1).<br><br>Exempelvis ett skogsområde som minskar avrinning mot ett bostadsområde. Den samlar inte upp dagvatten men tar hand om merparten av det regn som faller på den.",
            "Ytor och stråk i lågpunkter som fungerar som tillfälliga översvämningsytor vid kraftiga regn.<br><br>Träd som ingår i ytorna räknas in här (räknas ej separat). Hårdgjorda ytor räknas ej.",
            "Anlagda ytor så som regnbäddar, växtbäddar, växtbäddar på bjälklag, gröna tak, m.m. som är särskilt utformade för dagvattenhantering med flera olika vegetationsskikt räknas.<br><br>Avrinningsytan som anläggningen tar hand om räknas. Hårdgjorda ytor räknas ej.",
            "Enstaka träd i skelettjord särskilt anlagda för dagvattenhantering.<br><br>Avrinningsytan som anläggningen tar hand om räknas. Skelettjordar med relativt stor porvolym har en magasinerande förmåga, medan träd har en förmåga att ta upp och transpirera vatten och fördröja dagvatten i lövverket.<br><br>Omkringliggande ytor planeras så att dagvatten ifrån dessa tillrinner ytan på ett för trädet optimalt sätt (hänsyn till vattenkrav och tålighet).",
            "Dagvatten som samlats upp i magasin eller tunna för bevattning av omgivande grönska.<br><br>Gäller endast särskilt utformade bevattningssystem.<br><br>25 kvm/st",
            # Mikroklimatreglering
            "Vegetationsytor av såväl torrare eller fuktigare karaktär med minst tre vegetationsskikt (fältskikt, buskskikt och trädskikt). Flerskiktad vegetation ger upphov till både evapotranspiration och skuggning , vilket ger god temperaturreglerande förmåga.<br><br>Ger stor kyleffekt dagtid och kan vara 4–5 grader svalare än omgivande bebyggelse.",
            "Vegetationsytor av halvöppen karktär (fältskikt och antingen buskskikt eller trädskikt).<br><br>Ger upphov till evapotranspiration och skuggning men är mindre effektiv än K22.",
            "Öppna grönytor med en låg andel eller avsaknad av träd.",
            "Grönska placerad på så sätt att den har potential att skugga soliga lägen.<br><br>Räkna den yta som beräknas vara täckt av växtlighet inom loppet av 5 år. Grönska på konstruktioner ger skugga och minskar strålningstemperaturen från hårdgjorda ytor. Grönska på byggnader som ingår i kvartersmark ska inte räknas eftersom de räknas i GYF Kvarter.",
            "Träd med potential att skugga soliga lägen räknas. Skuggande träd på hårdgjorda ytor till exempel gatuträd har stor inverkan på minskandet av strålningstemperaturen.<br><br>Den upplevda temperaturen kan vara upp till 14 grader svalare under ett träd. Gaturummet bör utformas på ett sätt som tillåter grönska att ta plats utan att riskera ansamling av luftföroreningar pga. förhindrad vertikal luftomblandning.<br><br>25 kvm/st.",
            # Pollination
            "Yta som innehåller alla resurser som pollinatörer behöver för hela sin livscykel, det vill säga både boplatser, parningshabitat, värdväxter, övervintringsplatser och födoresurser över hela säsongen (april–oktober för bin).<br><br>En pollinatörsnod kan även utgöra flera, utspridda ytor inom det avgränsade området vilka tillsammans bidrar med de tre olika resurstyperna, men ytorna behöver då vara sammanlänkade.<br><br>En pollinatörsnod måste totalt vara minst 100 kvm för att få räknas.<br><br>Rätt typ av förvaltning krävs för att säkerställa resurserna.",
            "Isolerade eller mindre ytor som innehåller födoresurser eller boplatser för pollinatörer men som endast delvis uppfyller kraven i K29.",
            "Enstaka, särskilt viktiga element för pollinatörer i form av föda eller bon för bin, som inte ingår i K 27-K28.<br><br>Träd och buskar som uppfyller 3/3 på nektar- och pollenlistan samt boplatser får räknas här.<br><br>25 kvm/st",
            # Rekreation och hälsa
            "Bevarade naturmiljöer med höga biologiska värden med många växter och djur att upptäcka och studera.<br><br>Då värdet ligger i områdets rika natur och upplevelsen av denna måste nyttjandet planeras och styras så att områdets värden bevaras på lång sikt.<br><br>Ytan ska innehålla både lättillgängliga, mer ordnade delar och vilda, orörda partier.",
            "Skogsdungar och skogsområden, minst 200x200 meter, men helst större, gärna uppemot 5 ha.<br><br>De kan utgöras av både artrik natur eller mer ordinär skogsmiljö, så kallad vardagsnatur.<br><br>Ytan kan innehålla både lättillgängliga mer ordnade delar och mer orörda delar.",
            "Stadsrum som kännetecknas av grönska och som visuellt ger intryck av en grön stadsbild.<br><br>Både befintliga och nyanlagda ytor får räknas.<br><br>Ska vara tillgängliga för människor men vara tillräckligt stora i relation till antal nyttjare så att slitage och trängsel undviks och ytans värde bibehålls.",
            "Gröna miljöer utpekade i kulturmiljöprogram eller liknande.<br><br>De ska vara av kulturhistoriskt värde, ha betydelse för att förstå områdets historia och/eller av stor betydelse för områdets identitet.<br><br>Ska vara tillgängliga för människor men på så sätt att slitage undviks och ytans värde bibehålls.",
            "Här räknas enskilda bevarade natur- och kulturobjekt som utpekats som särskilt värdefulla i natur- och kulturutredningar, landskapsanalyser eller liknande och som inte står inom yta annan kulturell-yta.<br><br>Väcker fantasi och mystik, värdefulla för lärande m.m. 25 kvm/st",
            "Grönska och naturobjekt av betydelse för stadsbild och upplevelsen av stadsmiljön.<br><br>Träd som tillför viktiga visuella stadsbildskvalitéer, upplevelser och årstidsväxlingar. Hit räknas även exotiska blommande träd in.<br><br>25 kvm/st",
            "Varierad nyanlagd artrik park eller naturmark. Motsvarar ofta K6/K7.<br><br>För att få räknas krävs att området kan nyttjas för rekreation (promenader och lugn vistelse), lärande m.m.<br><br>Ska vara tillgängliga för människor men vara tillräckligt stora i relation till antal nyttjare så att slitage och trängsel undviks.",
            "Avser ytor med rik blomning. Avser både befintliga och nyanlagda ytor förutsatt att de är blomrika och sköts på ändamålsenligt sätt.<br><br>Endast den faktisk blommande yta räknas. Vertikala ytor får räknas. Träd räknas i kvalitet K36 eller K37.<br><br>Ska vara tillgängliga för människor men vara tillräckligt stora i relation till antal nyttjare så att slitage och trängsel undviks.",
            "Områden avsatta för odling eller djurhållning i det offentliga rummet som uppmuntrar till delaktighet.<br><br>Odlingsområden ska vara iordningställda med tillgång till vatten, kompostplatser m.m.<br><br>Områden för pallkragar får räknas om de är större än 100 kvm och iordningställda för ändamålet.",
            "Sammanhängande natur- och parkstruktur som möjliggöra längre promenader (mer än 20 min) i gröna miljöer.<br><br>Stråken kan utgöras av omväxlande större grönområden och gröna stråk. Gröna promenadstråk kan innehålla både natur och park och kan bestå av både befintlig och anlagd grönska.<br><br>En väg genom park/naturområde räknas (alltså räknas ej alla stigar med möjliga vägar)",
            "Natur- och parkytor iordningställda för skilda aktiviteter.<br><br>Natur- och parkytorna ska vara tillräckligt stora i relation till antal nyttjare så att  slitage och trängsel undviks. Ryms ﬂera aktiviteter inom en yta får dessa räknas förutsatt att aktiviteterna inte stör eller motverkar varandra.<br><br>Ytor med konstgräs och gummiytor får inte räknas.",
            "Natur- och parkområden som har särskilt god ljudmiljö, &#60; 45 dBA men helst &#60; 40 dBA och som är utformade så att de upplevs lugna och rofyllda, utan störningar från trafik, verksamheter, högljudda aktiviteter eller andra störande element."
        ]

        q_f = [
            # Biologisk mångdfald
            [1, 'K1',  2.0, 'Bevarad viktig livsmiljö inom landskapssamband', 'Bevarad livsmiljö inom landskapssamband', text[0]],
            [1, 'K2',  0.8, 'Bevarad viktig livsmiljö utanför landskapssamband', 'Bevarad livsmiljö utanför landskapssamband', text[1]],
            [1, 'K3',  0.8, 'Bevarad övrig natur inom landskapssamband', 'Bevarad övrig natur inom landskapssamband', text[2]],
            [1, 'K4',  0.6, 'Bevarad övrig natur utanför landskapssamband', 'Bevarad övrig natur utanför landskapssamband', text[3]],
            [1, 'K5',  3.0, 'Bevarat objekt som särskilt gynnar biologisk mångfald', 'Bevarat objekt för ökad biologisk mångfald', text[4]],
            [1, 'K6',  0.7, 'Nyanlagd viktig livsmiljö inom landskapssamband', 'Nyanlagd livsmiljö inom landskapssamband', text[5]],
            [1, 'K7',  0.4, 'Nyanlagd viktig livsmiljö utanför landskapssamband', 'Nyanlagd livsmiljö utanför landskapssamband', text[6]],
            [1, 'K8',  0.4, 'Nyanlagd övrig natur inom landskapssamband', 'Nyanlagd övrig natur inom landskapssamband', text[7]],
            [1, 'K9',  0.2, 'Nyanlagd övrig natur utanför landskapssamband', 'Nyanlagd övrig natur utanför landskapssamband', text[8]],
            [1, 'K10', 1.0, 'Nyskapat objekt som särskilt gynnar biologisk mångfald', 'Nyskapat objekt för ökad biologisk mångfald', text[9]],
            # Bullerreducering
            [2, 'K11', 0.7, 'Bullervall', 'Bullervall', text[10]],
            [2, 'K12', 0.5, 'Vegetationsklädd porös mark', 'Vegetationsklädd porös mark', text[11]],
            [2, 'K13', 0.5, 'Trädbälte 15m&#60;bred', 'Trädbälte 15m<bred', text[12]],
            [2, 'K14', 0.3, 'Trädrad bakom bullerskärm', 'Trädrad bakom bullerskärm', text[13]],
            [2, 'K15', 1.0, 'Grönska i växtsubstrat på konstruktion', 'Grönska i växtsubstrat på konstruktion', text[14]],
            [2, 'K16', 0.2, 'Grönska på konstruktion utan substrat', 'Grönska på  konstruktion utan substrat', text[15]],
            [2, 'K17', 0.2, 'Positiva ljud från naturen / ljudmaskering', 'Positiva naturljud', text[16]],
            # Dagvatten- och skyfallshantering
            [3, 'K18', 0.7, 'Vattenytor och vattenstråk som används för rening och fördröjning av dagvatten', 'Vattenytor och stråk som renar och fördröjer dagvatten', text[17]],
            [3, 'K19', 0.5, 'Genomsläpplig vegetationsklädd naturyta', 'Genomsläpplig vegetationsklädd naturyta', text[18]],
            [3, 'K20', 0.5, 'Vegetationsklädd tillfällig översvämningsyta', 'Vegetationsklädd tillfällig översvämningsyta', text[19]],
            [3, 'K21', 0.7, 'Anlagd yta särskilt utformad för rening och fördröjning av dagvatten', 'Anlagd naturyta som renar och fördröjer dagvatten', text[20]],
            [3, 'K22', 0.2, 'Dagvattenhanterade träd i hårdgjord yta', 'Dagvattenhanterande träd i hårdgjord miljö', text[21]],
            [3, 'K23', 0.2, 'Uppsamling av regnvatten för bevattning', 'Uppsamling av regnvatten för bevattning', text[22]],
            # Klimatanpassning - Mikroklimatreglering
            [4, 'K24', 0.6, 'Flerskiktad vegetation, minst tre vegetationsskikt', 'Flerskiktad vegetation, tre vegetationsskikt', text[23]],
            [4, 'K25', 0.4, 'Halvöppen vegetation, minst två vegetationsskikt', 'Halvöppen vegetation, två vegetationsskikt', text[24]],
            [4, 'K26', 0.2, 'Öppen vegetation, ett vegetationsskikt', 'Öppen vegetetation, ett vegetationsskikt', text[25]],
            [4, 'K27', 0.5, 'Lövskugga från konstruktion med grönska', 'Lövskugga från konstruktion med grönska', text[26]],
            [4, 'K28', 0.5, 'Lövskugga från enstaka träd', 'Lövskugga från enstaka träd', text[27]],
            # Pollinering
            [5, 'K29', 1.3, 'Pollinatörsnod', 'Pollinatörsnod', text[28]],
            [5, 'K30', 0.8, 'Pollinatörsgynnande yta', 'Pollinatörsgynnande yta', text[29]],
            [5, 'K31', 2.0, 'Pollinatörsobjekt', 'Pollinatörsobjekt', text[30]],
            # Rekreation och hälsa
            [6, 'K32', 1.0, 'Artrik natur', 'Artrik natur', text[31]],
            [6, 'K33', 0.7, 'Skogskänsla', 'Skogskänsla', text[32]],
            [6, 'K34', 0.5, 'Grönskande stadsmiljö', 'Grönskande stadsmiljö', text[33]],
            [6, 'K35', 0.8, 'Kulturhistorisk grön miljö', 'Kulturhistorisk grön miljö', text[34]],
            [6, 'K36', 3.0, 'Särskilt värdefulla träd, natur- och kulturobjekt', 'Värdefulla träd, natur- och gröna kulturobjekt', text[35]],
            [6, 'K37', 0.5, 'Övriga träd och naturobjekt av värde för stadsbild m.m.', 'Övriga träd och naturobjekt av värde för stadsbild', text[36]],
            [6, 'K38', 0.5, 'Nyanlagd varierad artrik miljö', 'Nyanlagd varierad artrik miljö', text[37]],
            [6, 'K39', 0.3, 'Blomsterprakt', 'Blomsterprakt', text[38]],
            [6, 'K40', 0.3, 'Odling och/eller djurhållning', 'Odling och djurhållning', text[39]],
            [6, 'K41', 0.4, 'Längre sammanhängande gröna promenadstråk', 'Sammanhängande gröna promenadstråk', text[40]],
            [6, 'K42', 0.3, 'Natur- och parkytor för aktiviteter', 'Natur- och parkytor för aktiviteter', text[41]],
            [6, 'K43', 0.3, 'Rofylldhet','Rofylldhet', text[42]]
        ]

        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
        cur = con.cursor()
        cur.execute("SELECT id FROM gyf_qgroup")
        if not cur.fetchall():
            cur.executemany('INSERT OR IGNORE INTO gyf_qgroup VALUES (?,?,?)', group)
            cur.executemany('INSERT OR IGNORE INTO gyf_quality VALUES (?,?,?,?,?,?)', q_f)
            con.commit()
        cur.close()
        con.close()