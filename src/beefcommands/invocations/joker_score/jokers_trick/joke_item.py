from abc import ABC, abstractmethod

class JokerItem(ABC):
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
    
    @abstractmethod
    def HandleItem(self, **kwarks): # <- not sure if that the right syntax but it will be an arbitrary amount of args
        pass

class PlusTwoShield(JokerItem):
    def __init__(self, id, name, description): # <- these need to actaully come from somewhere
        super().__init__(id, name, description)
        
    def HandleItem(self, joker, victim):
        pass
        #logic for intercepting a -2 and blocking a -2