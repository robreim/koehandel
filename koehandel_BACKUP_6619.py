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
import pandas as pd
import numpy as np
import multiprocessing as mp
    
### Classes en functies
class Card:
    """
    A Card has two attributes: animal, and value. One function: to show which animal and value it entails
    """
    
    def __init__(self,animal, val):
            self.animal = animal
            self.value = val
            
    def show(self):
        print("{}: {}" .format(self.animal, self.value))       
    
class Deck:
    """ 
    The Deck class entails 40  Cards. When initalised, it will generate a deck of 40 cards, and shuffles the Deck randomly.
    The drawCard function show the card on top
    """

    def __init__(self):
        self.cards = [Card(key,animals.get(key)) for v in range(1,5) for key in animals]
        random.shuffle(self.cards)

            
    def show(self):
        for c in self.cards:
            c.show()
            

    def drawCard(self):
        return self.cards.pop()
    
    
class Player:
    """ 
    Player-Class entail five attributes: name, budget, number and, derived from number, an algorithm (or you could say, a list of actions)
    and also the cards the player has on hand. When initalised, it holds zero.
    """
    def __init__(self,name, number):
         self.name = name
         self.budget = 90
         self.hand =  {"Haan"  :0, 
            "Gans"  :0, 
            "Kat"   :0,
            "Hond"  :0,
            "Schaap":0,
            "Bok"   :0,
            "Ezel"  :0,
            "Varken":0,
            "Koe"   :0,
            "Paard" :0
            }
         self.strategy = strategies[number]
         self.number = number
         
<<<<<<< HEAD
    def bid(self,card_drawn,current_bid,money_supply):
        # create vector of bools
        condition = situations[(situations.Animals == card_drawn) & (situations.CurrentBid == current_bid) &
                     (situations.MoneySupply == money_supply) & (situations.BankAccount == self.budget) & 
                     (situations.CardsInHand == self.hand.get(card_drawn)) ]
        self.offer = min(self.budget,current_bid + self.strategy[condition.index.item()])

        print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,card_drawn))
=======
    def bid(self):
        """ 
        The bid function takes the minimum of the budget of the player, and of the current_bid plus an own bid. It is the bid function where the appropiate action
        is derived based upon the situation. 
        """
    
        # create vector of bools
        self.offer = min(self.budget,current_bid + self.strategy.
                         loc[auction_card.value,self.budget,self.hand.get(auction_card.animal),ezelteller
                                                                     ,current_bid])
        print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,auction_card.animal))
>>>>>>> dev
        return self.offer
    
    def calculateScore(self):
        """ This function first checks how many cards the player won of the same animal. Then the appropiate score is calculated 
        (**1 for only one card, **2 for two cards, **3 for three cards, **4 for four cards)
        """
        self.score = 0
        for score in range (1,5):
            kwartet = [k for k,v in self.hand.items() if v == score]
            self.score += sum(map(lambda x: x ** score, list(map(animals.get, kwartet))))
        print("{} heeft {} punten" .format(self.name, self.score))  
        return self.score
        
    def addtoHand(self,card): 
        """
        This function simply adds the card to the hand of the player
        """
        self.hand[card.animal] += 1

# om een iterable te maken (die ook een vorige kan verwijderen, cycle van itertools kan dit niet)
class ModifiableCycle(object):
    """To make an iterable like cycle for the bidding round, which can also delete the last popped card, 
    I made this function. Cycle of itertools cannot delete an element from an iterable.
    
    Erasing an element is necessary when a player refuses to bid more than the currend bid, because this player
    then should exit the bidding round.
    """
    def __init__(self, items=()):
        self.deque = deque(items)
    def __iter__(self):
        return self
    def __next__(self):
        if not self.deque:
            raise StopIteration
        item = self.deque.popleft()
        self.deque.append(item)
        return item
    next = __next__
    def delete_next(self):
        self.deque.popleft()
    def delete_prev(self):
        # Deletes the item just returned.
        self.deque.pop()

        
def evolution(algorithms,procs,scores,lower):
   """
    This is the selection/evolution function.
    
    It first samples two algorithms, bases on probability weights (which in turn are based on the scores of the respective algorithms)
    It then generates a rnadom number of where to cut off the list of actions. Until that point, the first child gets actions from the mother,
    after this point gets actions from the father. the second child (suffix _2) vice versa.
    
    Then mutations take place: 2 percent of actions are replaced, zeroes by tens, tens by zeroes.
    Selection/Evolution is then finished, and the two new algorithms are added to the dataframe. 
    Parameters
    
    Important: this function is built to support multiprocessing. When for example four cores will process this function, it will each start on particular lower bound 
    (0, 50, 100, 150)
    ----------
    lower :INT
    The lower bound. This to ensure that the separate cores do not name the algorithm the same name.
    Returns
    -------
    Two pd Series, which each a new child-algorithm.

   """
   ## Ik ga nu uit van drie processoren; moet evt nog geupdate worden
   new_strategies = pd.DataFrame(dtype='int8')
   for k in range(lower,lower+int((198/workers)),2):
         print(k)
         sample = algorithms.sample(n=2, weights=scores, replace=False, axis = 1)
         random_number = np.random.randint(0,len(algorithms))
         # Make two children from the two parents
         new_strategy_1 = pd.Series(sample.iloc[:random_number,0].append(sample.iloc[random_number:,1]),dtype='int8', name=k)
         new_strategy_2 = pd.Series(sample.iloc[:random_number,1].append(sample.iloc[random_number:,0]),dtype='int8', name=k+1)
         # make random mutations in the children
         mutations_1 =  new_strategy_1.sample(frac=0.02).replace(to_replace = [0,10], value = [10,0]).astype('int8')
         mutations_2 =  new_strategy_2.sample(frac=0.02).replace(to_replace = [0,10], value = [10,0]).astype('int8')
         new_strategy_1.update(mutations_1)
         new_strategy_2.update(mutations_2)
         ## add the children to the new dataframe
         new_strategies = pd.concat([new_strategies,new_strategy_1,new_strategy_2], axis =1)
   return new_strategies.astype('int8') 

##########################################################################################################################

<<<<<<< HEAD

# genereer strategieen/actielijst voor evolutionair algorithme
list_of_strategies = []
for algorithm in range(0,200):
    strategy = random.choices([0,50],k=len(situations))
    list_of_strategies.append(strategy)

del strategy, algorithm

####################### Spel opzetten ##################################
list_best_strategies = []

for z in range(0,200,4):
    print("Algorithme {} tot {}".format(z,z+3))      
    ## Spelers opzetten
    mohsine = Player("Mohsine", portemonnee,list_of_strategies[z])
    charlotte = Player("Charlotte", portemonnee,list_of_strategies[z+1])
    joost = Player("Joost", portemonnee,list_of_strategies[z+2])
    annemarie = Player("Annemarie", portemonnee,list_of_strategies[z+3])
    names = [mohsine, charlotte, joost, annemarie]
    # Waardes initialiseren
    for i in range(1,11):     
        for player in names:
            player.budget = portemonnee
            player.hand = {"Haan"  :0, 
                "Gans"  :0, 
                "Kat"   :0,
                "Hond"  :0,
                "Schaap":0,
                "Bok"   :0,
                "Ezel"  :0,
                "Varken":0,
                "Koe"   :0,
                "Paard" :0
                }
        ## Stapel schudden
        deck = Deck()
        deck.shuffle()
        deck.show()
        
        
        ################### Spel starten, willekeurige beginner ######################################
    
 
        # de eerste veilingmeester wordt willekeurig gekozen
        ##veilingmeester = names[random.choice([0,1,2,3])]
        random.shuffle(names)
        iter_veilingmeester = ModifiableCycle(names)
        iter_first_bidder = ModifiableCycle(names)
=======
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
## Creer Index met alle mogelijke situaties
a = [list(animals.values()), list(range(0,1500,10)), list(range(0,4)), list(range(0,5,1)),list(range(0,1010,10))]
index = pd.MultiIndex.from_product(a)

del a
# creeer een dataframe met 198 kolommen (elke kolom staat voor 1 lijst met acties (algoritme), met
# met de index van situations als index)
strategies = pd.DataFrame(data=np.random.choice([0,10],size = len(index)*198).reshape(-1, 198), index = index, dtype = 'int8')
print(strategies)

####################### Spel opzetten ##################################
algorithm_scores = dict.fromkeys(range(0,198),0)
>>>>>>> dev

# Aantal generaties 
for g in range(0,2):
    # Aantal potjes
    for i in range(0,5):
        print("Tijd voor ronde {}!".format(i))
        # Loop over de algoritmes
        for z in range(0,198):
            print("Algorithme {} van 198".format(z))
            
<<<<<<< HEAD
            # Het eerste bod wordt gedaan door de eerste persoon na de veilingmeester. Het volgende bod moet minimaal 10
            # munten hoger zijn. De veilingmeester mag niet bieden.
            situation ={'card_drawn':auction_card.animal,'current_bid':current_bid,'money_supply':ezelteller}
=======
            # Zorg voor een willekeurige opponent (niet tegen zichzelf)
            random_opponents = [x for x in range(0, 198) if x != z]
            random_sample = random.sample(random_opponents,3)
>>>>>>> dev
            
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
            
<<<<<<< HEAD
            ## eerste bod
            next_player = next(iter_names)
            next_bid = next_player.bid(**situation)
            ## Tijd voor de biedingsronde:
            while len(bidder_names)>1:
                current_bid = next_bid
                previous_player = next_player
                next_player = next(iter_names)
                #update situatie en bied opnieuw
                situation ={'card_drawn':auction_card.animal,'current_bid':current_bid,'money_supply':ezelteller}
                next_bid = next_player.bid(**situation)
                ## als speler weigert hoger te bieden, verwijder uit de iterable
                if next_bid <= current_bid:
                    bidder_names.remove(next_player),iter_names.delete_prev() 
                else: 
                    pass
        
            ## Er is een winnende bieder! Voer de kasstromen uit, voeg kaart toe aan hand 
            # en maak de iteratie van de veilingmeester rond
            print("{}'s bod van {} munten is het winnende bod".format(bidder_names[0].name,
                                                                      bidder_names[0].offer))
            veilingmeester.budget += next_bid
            previous_player.budget -= next_bid
            previous_player.addtoHand(auction_card)
            veilingmeester = next(iter_veilingmeester)
            print(" ")
            
        ### scores evalueren
        for person in names:
            person.calculateScore()
    
    ## Sla de beste algorithmes / actielijst op
    highscore = {mohsine:mohsine.total_score
                 ,charlotte:charlotte.total_score
                 ,joost:joost.total_score
                 ,annemarie:annemarie.total_score}
    
    list_best_strategies.append(max(highscore,key=highscore.get).strategy)
    for person in names:
        print(person.name + " " + f"{sum(person.total_score)/len(person.total_score):,} punten gemiddeld")
 
=======
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
>>>>>>> dev
