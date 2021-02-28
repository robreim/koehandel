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
portemonnee = 5*10 + 1*50 

##animals.update((x, (y/10 *10 + y/1000*90)/2) for x, y in animals.items())

class Card:
    def __init__(self,animal, val):
            self.animal = animal
            self.value = val
            
    def show(self):
        print("{}: {}" .format(self.animal, self.value))       
    
class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        
    def build(self):
        for v in range(1,5):
            for key in animals:
                self.cards.append(Card(key,animals.get(key)))
        
    def show(self):
        for c in self.cards:
            c.show()
            
    def shuffle(self):
        for i in range(len(self.cards)-1,0,-1):
            r = random.randint(0,i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]
            
    def drawCard(self):
        return self.cards.pop()
    
    
class Player:
    def __init__(self,name, budget, strategy):
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
         self.strategy = strategy
         self.total_score = []
         
    def bid(self):
        # create vector of bools
        self.offer = min(self.budget,current_bid + self.strategy.loc[auction_card.value,
                                                                     self.budget,self.hand.get(auction_card.animal),ezelteller
                                                                     ,current_bid].item())
        print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,auction_card.animal))
        return self.offer
    
    def calculateScore(self):
        self.score = 0
        for score in range (1,5):
            kwartet = [k for k,v in self.hand.items() if v == score]
            self.score += sum(map(lambda x: x ** score, list(map(animals.get, kwartet))))
        print("{} heeft {} punten" .format(self.name, self.score))  
        self.total_score.append(self.score)
        
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
animals_deck = pd.DataFrame(list(animals.values()), columns= ['Animals'])
bank_account = pd.DataFrame(list(range(0,1500,10)), columns=['BankAccount'])
cards_in_hand = pd.DataFrame(list(range(0,4)),columns=['CardsInHand'])
no_donkeys_drawn= pd.DataFrame(list(range(0,5,1)), columns=['MoneySupply'])
current_bid = pd.DataFrame(list(range(0,1010,10)), columns= ['CurrentBid'])

## voeg samen tot een dataframe
situations = pd.merge(animals_deck,bank_account, how='cross')
for column in [cards_in_hand,no_donkeys_drawn,current_bid]:
    situations = pd.merge(situations,column,how='cross')

del animals_deck, bank_account, cards_in_hand, no_donkeys_drawn, current_bid, column

situations = situations.set_index(['Animals', 'BankAccount','CardsInHand','MoneySupply','CurrentBid'])

# genereer strategieen/actielijst voor evolutionair algorithme
list_of_strategies = []
for algorithm in range(0,200):
    situations['Action']= random.choices([0,10],k=len(situations))
    list_of_strategies.append(situations)

del algorithm
####################### Spel opzetten ##################################
list_best_strategies = []

teller = 0
total_time = 0

for z in range(0,200,4):
    print("Algorithme {} tot {}".format(z,z+3))      
    ## Spelers opzetten
    mohsine = Player("Mohsine", portemonnee,list_of_strategies[z])
    charlotte = Player("Charlotte", portemonnee,list_of_strategies[z+1])
    joost = Player("Joost", portemonnee,list_of_strategies[z+2])
    annemarie = Player("Annemarie", portemonnee,list_of_strategies[z+3])
    names = [mohsine, charlotte, joost, annemarie]
    # Waardes initialiseren
    for i in range(1,6):     
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

        ezelteller = 0
        
        print("Tijd voor ronde {}!".format(i))
        
        for x in range(40,0,-1):
            # Eerst wordt een nieuwe/volgende veilingmeester en 1e/2e/3e bieder aangewezen
            veilingmeester = next(iter_veilingmeester)
            first_bidder = next(iter_veilingmeester)
            second_bidder = next(iter_veilingmeester)
            third_bidder = next(iter_veilingmeester)
            
            print("{} is de nieuwe veilingmeester, {} is aan de beurt om te bieden".format(veilingmeester.name, first_bidder.name))
        ## Trek de bovenste kaart
            auction_card = deck.drawCard()
        # Check of ezel of niet
            if auction_card.animal == 'Ezel':
                for person in [mohsine,charlotte,joost,annemarie]:
                    person.budget += [50,100,200,500][ezelteller]
                ezelteller += 1
            auction_card.show()
            print(" ")
            current_bid = 0
            
            # Het eerste bod wordt gedaan door de eerste persoon na de veilingmeester. Het volgende bod moet minimaal 10
            # munten hoger zijn. De veilingmeester mag niet bieden.
 
            #Creeer iterable puur voor de biedingsronde (drie spelers!)
            bidder_names = [first_bidder,second_bidder,third_bidder]
            iter_names = ModifiableCycle(bidder_names)
            
            ## eerste bod
            next_player = next(iter_names)
            next_bid = next_player.bid()
            ## Tijd voor de biedingsronde:
            while len(bidder_names)>1:
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
 
print("Gemiddele berekentijd: {}".format(total_time/teller))
