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

from functools import partial
import random
import time
import pandas as pd
import numpy as np
import multiprocessing as mp
from functions_koehandel import *
from collections import OrderedDict
import matplotlib.pyplot as plt
import csv
##########################################################################################################################
aantal_rondes = 5
aantal_generaties = 100
mutatiegraad = 0.04
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
a = [list(animals.values()), list(range(0,4)),list(range(0,5))]
index = pd.MultiIndex.from_product(a,names=["Dier","Hand","Ezels"])
index
del a
# creeer een willekeurig dataframe met 198 kolommen (elke kolom staat voor 1 lijst met acties (algoritme), met
# met de index van situations als index)

strategies = pd.DataFrame(data=np.random.randint(1,50,size = len(index)*200).reshape(-1, 200), index = index, dtype = 'int16').mul(10)

# Behoud originele strategie om prestatie te kunnen meten
strategies_original = strategies

####################### Spel opzetten ##################################

start = time.time()
high_score = [0 for x in range(0,aantal_generaties)]
number_of_algorithms = strategies.shape[1] 
# Aantal generaties 
for g in range(0,aantal_generaties):
    print("Generatie: {}".format(g+1))
    algorithm_scores = [0 for x in range(0,200)]
    # Aantal potjes
    for i in range(0,aantal_rondes):
        print("Tijd voor ronde {}!".format(i+1))
        list_of_strategies = list(range(0,number_of_algorithms))
        # Loop over de individuen
        for t in range(0,200):
           algorithm_scores[t] += koehandel_simulation(t,strategies, animals, 
                                                       list_of_strategies = list_of_strategies, 
                                                       original_strategies = strategies_original)
           list_of_strategies.remove(t)

     ########################################### E####################################################
    ## Nog 10 potjes om te kijken hoe goed het beste algoritme van dit potje is    ############
    #################################################################################################### nog 2 extra potjes om te kijken hoe goed het winnende algoritme is vs originele strategien
    performance = 0
    
    for r in range(0,10):
        performance =+ koehandel_simulation(algorithm_scores.index(max(algorithm_scores)),strategies,  animals,
                                                    original_strategies =  strategies_original, check_performance = True,
                                                    list_of_strategies = list(range(0,200)))
                
    high_score[g] = performance / 10
    ########################################### Evolutie Mechanisme ####################################################
    ## Start het evolutie mechanisme                                                                             ############
    #######################################################################################################################
    strategies = evolution(algorithms = strategies,scores=algorithm_scores, index = index, totalrange = 100, mutation_rate = mutatiegraad)
 


end = time.time()

print("Het duurde {} minuten".format((end-start)/60))

# Print resultaten 
df = pd.DataFrame(high_score)
df['rolling_average'] =  df.rolling(window=10).mean()
df['rolling_average'].plot.line()
plt.xlabel('Aantal generaties')
plt.ylabel('Aantal punten')
plt.show()



# export resultaten
with open('/home/reimert/Documents/koehandel/scores_new', 'w') as f:
    # create the csv writer
  writer = csv.writer(f)
  for row in high_score:
      writer.writerow([row])

strategies.to_excel('/home/reimert/Documents/koehandel/strategies.xlsx')
