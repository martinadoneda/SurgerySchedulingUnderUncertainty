# Python STL

# Packages
import numpy as np

# Modules
from .uncertainty_profile import UncertaintyProfile

class Patient():

    def __init__(self, 
                 id: int, 
                 equipe: str, 
                 urgency: int,
                 days_waiting: int,
                 max_waiting_days: int = None,
                 features: np.ndarray = None, 
                 target: float = None, 
                 uncertainty_profile: UncertaintyProfile = None):
        
        self._id = id
        self._features = features
        self._target = target
        self._uncertainty_profile = uncertainty_profile
        self._equipe = equipe
        self._urgency = urgency
        self._days_waiting = days_waiting
        self._max_waiting_days = max_waiting_days

    def __str__(self):
        return f'Patient id: {self.id} \n equipe: {self.equipe} \n urgency: {self.urgency}'

    # Getters and setters
    def get_id(self):
        return self._id
    
    def set_id(self, new:int):
        self._id = new
    
    id = property(get_id, set_id)
    
    def get_equipe(self):
        return self._equipe
    
    def set_equipe(self, new:str):
        self._equipe = new
    
    equipe = property(get_equipe, set_equipe)

    def get_urgency(self):
        return self._urgency
    
    def set_urgency(self, new:int):
        self._urgency = new
    
    urgency = property(get_urgency, set_urgency)
    

    def get_features(self):
        return self._features
    
    def set_features(self, new:np.ndarray):
        self._features = new
    
    features = property(get_features, set_features)
        
    def get_target(self):
        return self._target
    
    def set_target(self, new:float):
        self._target = new
    
    target = property(get_target, set_target)

    def get_uncertainty_profile(self):
        return self._uncertainty_profile
    
    def set_uncertainty_profile(self, new:UncertaintyProfile):
        self._uncertainty_profile = new
    
    uncertainty_profile = property(get_uncertainty_profile, set_uncertainty_profile)
    
    
    def get_days_waiting(self):
        return self._days_waiting
    
    def set_days_waiting(self, new:float):
        self._days_waiting = new
    
    days_waiting = property(get_days_waiting, set_days_waiting)
    
    
    def get_days_waiting(self):
        return self._days_waiting
    
    def set_days_waiting(self, new:float):
        self._days_waiting = new
    
    days_waiting = property(get_days_waiting, set_days_waiting)


    def get_max_waiting_days(self):
        return self._max_waiting_days
    
    def set_max_waiting_days(self, new:float):
        self._max_waiting_days = new
    
    max_waiting_days = property(get_max_waiting_days, set_max_waiting_days)


