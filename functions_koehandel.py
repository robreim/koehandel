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
                             
        print("{} biedt {} munten voor de/het {}".format(self.name,self.offer,auction_card.animal))
        return self.offer
    
    def calculateScore(self,animals):
        """ This function first checks how many cards the player won of the same animal. Then the appropiate score is calculated 
        (**1 for only one card, **2 for two cards, **3 for three cards, **4 for four cards)
        """
        self.score = 0
        kwartetten = [k for k,v in self.hand.items() if v == 4]
        for kwartet in kwartetten:
            self.score += animals.get(kwartet) * 4
        self.score = self.score * len(kwartetten)
        print("{}: totale aantal punten: {} met {} kwartetten".format(self.name, self.score,len(kwartetten)))
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

        
def mp_evolution(algorithms,procs,scores,lower):
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
   new_strategies = pd.DataFrame(dtype='int16')
   for k in range(lower,lower+int((198/3)),2):
         random_positions= random.sample(range(0,40),2)
         print(k)
         sample = algorithms.sample(n=2, weights=scores, replace=False, axis = 1)
         random_number = np.random.randint(0,len(algorithms))
         # Make two children from the two parents
         new_strategy_1 = pd.Series(sample.iloc[:random_number,0].append(sample.iloc[random_number:,1]), name=k)
         new_strategy_2 = pd.Series(sample.iloc[:random_number,1].append(sample.iloc[random_number:,0]),name=k+1)
         # make random mutations in the children
         for num in [0,1]:
             multiplier = [-1,1][random.randrange(2)]
             new_strategy_1.iloc(axis=0)[random_positions[num]] +=  20*multiplier
             new_strategy_2.iloc(axis=0)[random_positions[num]] +=  20*multiplier
   #      mutations_1 =  new_strategy_1.sample(frac=0.02).replace(to_replace = [0,10], value = [10,0]).astype('int16')
   #      mutations_2 =  new_strategy_2.sample(frac=0.02).replace(to_replace = [0,10], value = [10,0]).astype('int16')
   #      new_strategy_1.update(mutations_1)
   #      new_strategy_2.update(mutations_2)
         ## add the children to the new dataframe
         new_strategies = pd.concat([new_strategies,new_strategy_1,new_strategy_2], axis =1)
   return new_strategies.astype('int16') 

def evolution(algorithms,scores,index,totalrange):
    """
    description
    """
    #Creeer leeg dataframe
    print("Started the evolution process")
    new_strategies = pd.DataFrame(dtype='int16', index = index)
    for i in range(0,totalrange,2):
        print("Busy with the evolution process: {} of {} ".format(i,totalrange))
        # Kies een sample uit de strategieeen, gewicht naar hun prestatie
        sample = algorithms.sample(n=2, weights=scores, replace=False, axis = 1)
        # Kies een willekeurige positie waar de strategieen opgebroken worden
        random_number = np.random.randint(0,len(algorithms))
        # Kies willeurige posities waar waardes met 20 munten toenemen of afnemen
        random_positions= random.sample(range(0,200),4)
        
        # Maak twee kinderen van de twee ouders
        new_strategy_1 = pd.Series(sample.iloc[:random_number,0].append(sample.iloc[random_number:,1]), name=i)
        new_strategy_2 = pd.Series(sample.iloc[:random_number,1].append(sample.iloc[random_number:,0]),name=i+1)
        for num in random_positions:
             multiplier = [-1,1][random.randrange(2)]
             new_strategy_1.iloc(axis=0)[num] +=  20*multiplier
             new_strategy_2.iloc(axis=0)[num] +=  20*multiplier
        new_strategies = pd.concat([new_strategies,new_strategy_1,new_strategy_2], axis =1).clip(lower=0)
    
    return new_strategies