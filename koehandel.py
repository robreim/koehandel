#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:44:15 2021

@author: reimert
Beknopte uitleg spel:
Bij Koehandel gaat het er om kwartetten te verzamelen. Er zijn in totaal 10 dieren (met verschillende waardes), elk komt vier keer voor. 
Er wordt een veilingmeester aangewezen die de kaart trekt en de andere spelers kunnen bieden. Diegene met het hoogste bod wint. 
Speciale vermelding voor de Ezel: als een Ezel wordt getrokken, krijgt iedere speler geld: bij de eerste getrokken Ezel 50, tweede 100, derde 200 en bij de vierde 500.
De Ezel wordt daarna zoals alle andere dieren geveild.

Op dit moment wijkt de code op de volgende punten af van het originele spel:
    - Het is voor spelers niet mogelijk 'koehandel' aan te gaan (https://nl.wikipedia.org/wiki/Koehandel_(kaartspel)#Koehandel). Dit wordt misschien later toegevoegd.
    - Omdat het hierdoor moeilijker is kwartetten te vormen, krijgen spelers ook punten voor niet-kwartetten. Als ze 1 paard hebben (1000 punten), krijgen ze 1000 punten, 
    bij twee paarden 1000^2, drie paarden 1000^3, vier paarden 1000^4. Zo worden spelers nog steeds gestimuleerd kwartetten te verzamelen.
    - De veilingmeester heeft (nog) niet het recht een dier te kopen voor het bedrag van het winnende bod.
    
Doel:
    Het doel is een genetisch (evolutionair) algoritme te vinden die het hoogste puntenaantal behaald. Dit gaat als volgt:
        - Vooraf aan het spel wordt elk mogelijke situatie geschetst die een speler kan aantreffen, in de context van:
            1. Waarde van de opgegooide kaart (40, 90, 160, 250, 350, 500, 350, 500, 650, 800, 1000)
            2. Geld in kas: 0 tot 1500, in stapjes van 10
            3. Aantal kaarten van veilingskaart al in hand: (0,1,2, of 3)
            4. Aantal getrokken Ezels (proxy voor de geldhoeveelheid), (0,1,2,3, of 4)
            5. Het huidige bod
        
        - Deze mogelijke situaties worden gekoppeld aan een even lange lijst met acties: 0 bieden ('passen'), of 10 meer bieden ('bieden')
            - Bij elke situatie hoort dus een bijbehorende acties: alleen die is voor elk algoritme weer anders. In het begin wordt deze lijst met acties willekeurig gegenereerd,
            dus zullen er ook situaties komen waarbij een Paard (1000 punten) geveild wordt, en dat een algoritme niet meer dan 10 munten biedt. 
            - Maar: er zullen altijd algoritmes zijn (we genereren er namelijk 198 (aangezien het multiprocessing gedaan wordt door drie processoren heb ik voor 198 gekozen ipv 200)), die het gemiddeld over 5 potjes net ietsje beter doen. Als alle algoritmes 5 potjes gespeeld 
            hebben, worden de scores genormaliseerd, en kan vergeleken worden welke algoritmes het beter hebben gedaan. Dan komt de selectieprocedure:
            - Basered op de genormaliseerde scores, worden er  twee 'ouders'-algoritme getrokken, maar dit keer niet willekeurig: de kans is groter om geselecteerd worden als 
            het algoritme een hoge score heeft behaald (probability weighting).
            - Er worden twee 'kind'- algoritmes gemaakt: het ene kind 'erft' de eerste helft aan acties van de 'moeder'-algoritme, en de tweede helft van het 'vader'-algoritme. 
            Het tweede kind vice versa.
            - Dan worden er nog willekeurige mutaties gemaakt: een paar '0'en worden '10'en, een paar '10'en worden '0'en.
            - Deze stappen worden herhaald totdat we weer 198 algoritmes hebben.
            - En dan spelen deze 198 algoritmes weer elk 5 potjes. Uiteindelijk worden er 1000 generaties gemaakt (iteraties). Tegen die tijd zullen de algoritmes een stuk slimmer
            zijn, maar ook slimmer dan een mens? We gaan het zien!

"""

from collections import deque
from functools import partial
import random
import time
import pandas as pd
import numpy as np
import multiprocessing as mp
from functions_koehandel import *

##########################################################################################################################

##################################Situatie-index opzetten#################################################################

animals = {"Haan"  :10, 
            "Gans"  :40, 
            "Kat"   :90,
            "Hond"  :160,
            "Schaap":250,
            "Bok"   :350,
            "Ezel"  :500,
            "Varken":650,
            "Koe"   :800,
            "Paard" :1000
            }
## Creer Index met alle mogelijke situaties (waardes dieren, WTP,)
a = [list(animals.values()),list(range(0,4)), list(range(0,5))]
index = pd.MultiIndex.from_product(a)

del a
# creeer een dataframe met 198 kolommen (elke kolom staat voor 1 lijst met acties (algoritme), met
# met de index van situations als index)
strategies = pd.DataFrame(data=np.random.([0,10],size = len(index)*198).reshape(-1, 198), index = index, dtype = 'int8')

wtp_base_strategies = pd.DataFrame(data=random.sample(range(0, 100,10),10))

for x in range(0,200):
    temp_list = random.sample(range(0, 100,10),10)
    
    
df = pd.concat([pd.DataFrame(random.sample(range(0, 100,10),10), columns=[i]) for i in range(200)], reset_index=True)

          ignore_index=True)         
print(strategies)

####################### Spel opzetten ##################################
algorithm_scores = dict.fromkeys(range(0,198),0)
#hello
# Aantal generaties 
for g in range(0,2):
    # Aantal potjes
    for i in range(0,5):
        print("Tijd voor ronde {}!".format(i))
        # Loop over de algoritmes
        for z in range(0,198):
            print("Algorithme {} van 198".format(z))
            
            # Zorg voor een willekeurige opponent (niet tegen zichzelf)
            random_opponents = [x for x in range(0, 198) if x != z]
            random_sample = random.sample(random_opponents,3)
            
            ## Spelers opzetten. Startkapitaal is 90 muntjes
            mohsine = Player("Mohsine", number = z)
            charlotte  = Player("Charlotte", number = random_sample[0])
            joost = Player("Joost", number = random_sample[1])
            annemarie = Player("Annemarie",  number =random_sample[2])
            names = [mohsine, charlotte, joost, annemarie]                           
         
            ## Stapel creeren (schud automatisch)
            deck = Deck()
            # de eerste veilingmeester wordt willekeurig gekozen
            random.shuffle(names)
            iter_veilingmeester = ModifiableCycle(names)
            ezelteller = 0
            ################### Spel starten, willekeurige beginner ######################################
    
            for x in range(40,0,-1):
                # Eerst wordt een nieuwe/volgende veilingmeester en 1e/2e/3e bieder aangewezen
                veilingmeester = next(iter_veilingmeester)
                bidders = [next(iter_veilingmeester) for x in range(0,3)]
                print("{} is de nieuwe veilingmeester, {} is aan de beurt om te bieden".format(veilingmeester.name,bidders[0].name))
            ## Trek de bovenste kaart
                auction_card = deck.drawCard()
            # Check of ezel of niet. Zo ja, voeg geld toe aan de budgetten van de spelers
                if auction_card.animal == 'Ezel':
                    for person in names:
                        person.budget += [50,100,200,500][ezelteller]
                    ezelteller += 1
                auction_card.show()
                print(" ")
                current_bid = 0
            
                # Het eerste bod wordt gedaan door de eerste persoon na de veilingmeester. Het volgende bod moet minimaal 10
                # munten hoger zijn. De veilingmeester mag niet bieden.Creeer iterable puur voor de biedingsronde        
                iter_names = ModifiableCycle(bidders)
                ## eerste bod
                next_player = next(iter_names)
                next_bid = next_player.bid()
                ## Tijd voor de biedingsronde. Als er nog maar een speler overblijft, eindigt de biedingsronde:
                while len(bidders)>1:
                    # Update status: het zojuist afgegeven bod is nu het huidige bod, de speler die bood is de vorige speler.
                    current_bid = next_bid
                    previous_player = next_player
                    next_player = next(iter_names)
                    #De volgende speler biedt
                    next_bid = next_player.bid()
                    ## als speler weigert hoger te bieden, verwijder uit de iterable
                    if next_bid <= current_bid:
                        bidders.remove(next_player),iter_names.delete_prev() 
                    else:     
                        pass
                    
                ## Er is een winnende bieder! Voer de kasstromen uit, voeg kaart toe aan hand 
   
                print("{}'s bod van {} munten is het winnende bod".format(bidders[0].name,
                                                                          bidders[0].offer))
                veilingmeester.budget += next_bid
                previous_player.budget -= next_bid
                previous_player.addtoHand(auction_card)            
                print(" ")
                
            ## Einde v/h potje. Bereken de scores
            for person in names:
                algorithm_scores[person.number] += person.calculateScore() 
                print(person.name + " heeft  " + f"{person.score:,} punten.")
            
    ## Nu hebben 198 algoritmes x aantal potjes gespeeld. Tijd om de balans op te maken! Norm de scores. 
    sum_scores = sum(algorithm_scores.values())
    algorithm_scores.keys()
    for key in algorithm_scores:
        algorithm_scores[key] = algorithm_scores[key] / sum_scores
        
    ########################################### Evolutie Mechanisme ####################################################
    ## Start het evolutie mechanisme (traag). Gebruik multiprocessing om het te versnellen (ong. 2x zo snel). ############
    #######################################################################################################################
    start = time.time()  
    ## 1 kern minder gebruiken dan de pc heeft. Nu  fix 3 processoren
    #workers = mp.cpu_count() -1
    workers = 3
    pool = mp.Pool(processes = workers)
    ## Verdeel de werklast evenredig over de processoren 
    results= pool.map(partial(evolution,strategies,workers,algorithm_scores), range(0,198,66))
    pool.close()
    pool.join()
    strategies = pd.concat(results, axis = 1).astype('int8')
    end = time.time()
    print("Evolutie compleet. Duur: {} minuten".format((end-start)/60))
    print(pool)

# to do:
    # veilingmeester kan besluiten de kaart voor het hoogste bod te nemen
    # ook twee ronde (ruilronde) inbouwen