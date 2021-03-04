#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:44:15 2021

@author: reimert
"""

from collections import deque
import random
import time
import pandas as pd
import numpy as np
# to do:
    #v portemonnee wordt minder bij elke aankoop 
    #v bij het trekken van de ezel stijgt de geldhoeveelheid
    # sequentieel bieden
    # diegene die veilt krijgt het geld 
    # nog een biedingsronde als gelijk hoog bod
    # als eerste bod nul is, vliegt die persoon er ook uit
    # winnende bod moet minstens 10 zijn
    # slimmer biedsysteem inbouwen (basis algorithme), waarbij relatieve waarde centraal staat.
    #GA inbouwen
# voor versie 3:
    # veilingmeester kan besluiten de kaart voor het hoogste bod te nemen
    # ook twee ronde (ruilronde) inbouwen
    
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
#startkapitaal
portemonnee = 4*10 + 1*50 

##animals.update((x, (y/10 *10 + y/1000*90)/2) for x, y in animals.items())

class Card:
    def __init__(self,animal, val):
            self.animal = animal
            self.value = val
            
    def show(self):
        print("{}: {}" .format(self.animal, self.value))       
    
class Deck:
    def __init__(self):
        self.cards = [Card(key,animals.get(key)) for v in range(1,5) for key in animals]
        random.shuffle(self.cards)

            
    def show(self):
        for c in self.cards:
            c.show()
            

    def drawCard(self):
        return self.cards.pop()
    
    
class Player:
    def __init__(self,name, budget, number):
         self.name = name
         self.budget = portemonnee
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
         
    def bid(self):
        # create vector of bools
        self.offer = min(self.budget,current_bid + self.strategy.
                         loc[auction_card.value,self.budget,self.hand.get(auction_card.animal),ezelteller
                                                                     ,current_bid])
        print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,auction_card.animal))
        return self.offer
    
    def calculateScore(self):
        self.score = 0
        for score in range (1,5):
            kwartet = [k for k,v in self.hand.items() if v == score]
            self.score += sum(map(lambda x: x ** score, list(map(animals.get, kwartet))))
        print("{} heeft {} punten" .format(self.name, self.score))  
        return self.score
        
    def addtoHand(self,card): 
        self.hand[card.animal] += 1

# om een iterable te maken (die ook een vorige kan verwijderen, cycle van itertools kan dit niet)
class ModifiableCycle(object):
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
        


################### Situaties generen voor het evolutionair algoritme #####################
animals_deck = pd.DataFrame(list(animals.values()), columns =['Animals'])
bank_account = pd.DataFrame(list(range(0,1500,10)), columns=['BankAccount'])
cards_in_hand = pd.DataFrame(list(range(0,4)),columns=['CardsInHand'])
no_donkeys_drawn= pd.DataFrame(list(range(0,5,1)), columns=['MoneySupply'])
current_bid = pd.DataFrame(list(range(0,1010,10)), columns= ['CurrentBid'])

## voeg samen tot een dataframe
situations = pd.merge(animals_deck,bank_account, how='cross')
for column in [cards_in_hand,no_donkeys_drawn,current_bid]:
    situations = pd.merge(situations,column,how='cross')

del animals_deck, bank_account, cards_in_hand, no_donkeys_drawn, current_bid, column

# creeer een index aan de hand van alle kolommen
situations = situations.set_index(['Animals', 'BankAccount','CardsInHand','MoneySupply','CurrentBid'])


# creeer een dataframe met 200 kolommen (elke kolom staat voor 1 lijst met acties (algoritme), met
# met de index van situations als index)
strategies = pd.DataFrame(data=np.random.choice([0,10],len(situations)*200).reshape(-1, 200), index = situations.index)
                          
# nu kan de situations tabel weg
del situations
####################### Spel opzetten ##################################
algorithm_scores = dict.fromkeys(range(0,200),0)


starttijd = time.time()
for i in range(0,10):
    print("Tijd voor ronde {}!".format(i))
    teller = 0
    total_time = 0
    for z in range(0,200):
        print("Algorithme {} van 200".format(z))
        
        # Zorg voor een willekeurige opponent (niet tegen zichzelf)
        random_opponents = [x for x in range(0, 200) if x != z]
        random_sample = random.sample(random_opponents,3)
        
        ## Spelers opzetten
        mohsine = Player("Mohsine", portemonnee,z)
        charlotte  = Player("Charlotte", portemonnee,random_sample[0])
        joost = Player("Joost", portemonnee,random_sample[1])
        annemarie = Player("Annemarie", portemonnee,random_sample[2])
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
        # Check of ezel of niet
            if auction_card.animal == 'Ezel':
                for person in names:
                    person.budget += [50,100,200,500][ezelteller]
                ezelteller += 1
            auction_card.show()
            print(" ")
            current_bid = 0
        
            # Het eerste bod wordt gedaan door de eerste persoon na de veilingmeester. Het volgende bod moet minimaal 10
            # munten hoger zijn. De veilingmeester mag niet bieden.
            #Creeer iterable puur voor de biedingsronde        
            iter_names = ModifiableCycle(bidders)
            ## eerste bod
            next_player = next(iter_names)
            next_bid = next_player.bid()
            ## Tijd voor de biedingsronde:
            while len(bidders)>1:
                current_bid = next_bid
                previous_player = next_player
                next_player = next(iter_names)
                #update situatie en bied opnieuw           
                start = time.time()  
                next_bid = next_player.bid()
                end = time.time()
                teller += 1
                total_time += end - start
                ## als speler weigert hoger te bieden, verwijder uit de iterable
                if next_bid <= current_bid:
                    bidders.remove(next_player),iter_names.delete_prev() 
                else: 
                    pass
        
            ## Er is een winnende bieder! Voer de kasstromen uit, voeg kaart toe aan hand 
            # en maak de iteratie van de veilingmeester rond
            print("{}'s bod van {} munten is het winnende bod".format(bidders[0].name,
                                                                      bidders[0].offer))
            veilingmeester.budget += next_bid
            previous_player.budget -= next_bid
            previous_player.addtoHand(auction_card)            
            print(" ")
            
        ## Sla de beste algorithmes / actielijst op
        for person in names:
            algorithm_scores[person.number] += person.calculateScore() 
        print(person.name + " heeft  " + f"{person.score:,} punten.")
        print("Gemiddele berekentijd: {}".format(total_time/teller))
        
high_score = max(algorithm_scores.values())
eindtijd = time.time()
print("Starttijd: {}, Eindtijd: {}, Duur: {}".format(starttijd, eindtijd, eindtijd-starttijd))
algorithm_scores.keys()
for key in algorithm_scores:
    algorithm_scores[key] = algorithm_scores[key] / high_score

parents = random.choices(list(algorithm_scores.keys()), weights = algorithm_scores.values(), k=100)
size = int(len(strategies)/(2))
strategies.iloc[:size,68]