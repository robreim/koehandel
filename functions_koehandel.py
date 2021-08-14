#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 18:14:05 2021

@author: reimert
Koehandel functies
"""
import random
from collections import deque
import pandas as pd
import numpy as np
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

    def __init__(self,animals):
        self.cards = [Card(key,animals.get(key)) for v in range(1,5) for key in animals]
 #       random.shuffle(self.cards)

            
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
    def __init__(self,name,number, strategy):
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
         self.strategy = strategy
         self.number = number
         
    def bid(self,auction_card, aantal_ezels):
        """ 
        The bid function takes the minimum of the budget of the player, and of the current_bid plus an own bid. It is the bid function where the appropiate action
        is derived based upon the situation. 
        """
    
        # create vector of bools
        self.offer = min(self.budget,self.strategy[auction_card.value,self.hand.get(auction_card.animal), aantal_ezels])
                             
 #       print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,auction_card.animal))
        return self.offer
    
    def calculateScore(self,animals):
        """ This function first checks how many cards the player won of the same animal. Then the appropiate score is calculated 
        (**1 for only one card, **2 for two cards, **3 for three cards, **4 for four cards)
        """
        self.score = 0
        hand = [k for k,v in self.hand.items()]
        for animal in hand:
            self.score += animals.get(animal) * self.hand.get(animal)
        kwartetten = [k for k,v in self.hand.items() if v == 4]
        self.score = self.score * (len(kwartetten) + 1)
#        print("{}: totale aantal punten: {} met {} kwartetten".format(self.name, self.score,len(kwartetten)))
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

def evolution(algorithms,scores,index,totalrange, mutation_rate):
    """
    Two 'parent' algoritmes are chosen by weighted probability (derived from their scores), after which random length of their WTP-array
    is combined to make two 'children'. Then some WTPs of the children is randomly decreased by 40 or increased by 40
    """
    #Creeer leeg dataframe
    print("Started the evolution process")
    new_strategies = pd.DataFrame(dtype='int16', index = index)
    for i in range(0,200,2):
        # Kies een sample uit de strategieeen, gewicht naar hun prestatie
        sample = algorithms.sample(n=2, weights=scores, replace=True, axis = 1)
        # Kies een willekeurige positie waar de strategieen opgebroken worden
        random_number = np.random.randint(0,len(algorithms))
        
        # Maak twee kinderen van de twee ouders
        new_strategy_1 = pd.Series(sample.iloc[:random_number,0].append(sample.iloc[random_number:,1]), name=i)
        new_strategy_2 = pd.Series(sample.iloc[:random_number,1].append(sample.iloc[random_number:,0]),name=i+1)
        
        # Kies willeurige posities waar waardes met 40 munten toenemen of afnemen
        random_positions= random.sample(range(0,len(algorithms)),int(mutation_rate*len(algorithms)))
        for num in random_positions:
             multiplier = [-1,1][random.randrange(2)]
             new_strategy_1.iloc(axis=0)[num] +=  40*multiplier
             new_strategy_2.iloc(axis=0)[num] +=  40*multiplier
        new_strategies = pd.concat([new_strategies,new_strategy_1,new_strategy_2], axis =1).clip(lower=0)
    return new_strategies


def koehandel_simulation(algo,strategies, animals, list_of_strategies,scores= None, check_performance=False, original_strategies=None):
    
    spelers =  [174,4,66]  
    mohsine = Player("Mohsine", number = algo, strategy = strategies[algo])
    charlotte  = Player("Charlotte", number =spelers[0], strategy = original_strategies[spelers[0]])
    joost = Player("Joost", number = spelers[1], strategy = original_strategies[spelers[1]])
    annemarie = Player("Annemarie", number = spelers[2],  strategy  = original_strategies[spelers[2]])
    names = [mohsine, charlotte, joost, annemarie]
    
    ## Stapel creeren (schud automatisch)
    deck = Deck(animals)
    random.shuffle(deck.cards)
    random.shuffle(names)

    # de eerste veilingmeester wordt willekeurig gekozen
    iter_veilingmeester = ModifiableCycle(names)
    ezelteller = 0
    ################### Spel starten, willekeurige beginner ######################################

    for x in range(40,0,-1):
        # Eerst wordt een nieuwe/volgende veilingmeester en 1e/2e/3e bieder aangewezen
        veilingmeester = next(iter_veilingmeester)
        bidders = [next(iter_veilingmeester) for x in range(0,3)]
  #      print("{} is de nieuwe veilingmeester, {} is aan de beurt om te bieden".format(veilingmeester.name,bidders[0].name))
    ## Trek de bovenste kaart
        auction_card = deck.drawCard()
    # Check of ezel of niet. Zo ja, voeg geld toe aan de budgetten van de spelers
        if auction_card.animal == 'Ezel':
            for person in names:
                person.budget += [50,100,200,500][ezelteller]
            ezelteller += 1
        
        """ 
        De spelers doen allen een bod, stop in een dictionary
        """
        bids = {0:bidders[0].bid(auction_card, aantal_ezels = ezelteller),
                1:bidders[1].bid(auction_card,aantal_ezels =ezelteller),
                2:bidders[2].bid(auction_card,aantal_ezels = ezelteller)}
        
        """ 
        Als er meerdere bieder met dezelfde WTP zijn: dan wint de eerste speler die aan de beurt was om te bieden de kaart
        (immers hebben de anderen niet overboden), transactieprijs is dan gelijk aan de WTP. Mocht er maar 1 hoogste bieder zijn,
         dan wordt de transactieprijs de WTP van de een na hoogste bieder 
         """
        highest_bidder = max(bids, key=bids.get)
        # delete hoogste bieder, om het een na hoogste bod te berekenen
        del bids[highest_bidder]
        transaction_price = max(bids.values())

        """ Controleer of veilingmeester gebruik maakt van zijn kooprecht (als zijn WTP 2x oger is dan de transactieprijs)
         Deze parameter (2x hoger dan de transactieprijs bod is enigszins willekeurig gekozen. Maar realistisch: want ipv dat je geld krijgt
         als veilingmeester, moet je juist geld betalen. Dus dan wil je die kaart wel heel graag hebben) """ 
         
        if veilingmeester.bid(auction_card, aantal_ezels = ezelteller) - 2* transaction_price > 0:
            veilingmeester.budget -= transaction_price
            bidders[highest_bidder].budget += transaction_price
            veilingmeester.addtoHand(auction_card)
        else:
            veilingmeester.budget += transaction_price
            bidders[highest_bidder].budget -= transaction_price
            bidders[highest_bidder].addtoHand(auction_card)            
        
        # volgende veilingmeester
        veilingmeester = next(iter_veilingmeester)
        """
        Einde v/h potje. Bereken de score van het algoritme dat op dat moment speelt (altijd de eerste). Tel daarbij 10 punten op voor de zekerheid, 
        zodat ook slechte algoritmes nog steeds een kans hebben (ofschoon een kleine) om geselecteerd te worden
        """
    result = mohsine.calculateScore(animals) + 10
    return result
    
   
    