# Python STL
from abc import ABC, abstractmethod

# Packages
import pyomo.environ as pyo  # not used for the implementor adversary

# Modules
from .implementor import Implementor
from .adversary import Adversary
from .task import Task
from .predictive_model import PredictiveModel



class Optimizer(ABC):
    
    def __init__(self, task, description = ""):
        self._task = task
        self._description = description

        #self.schedule = None

    # Getters and setters
    def get_task(self):
        return self._task
    
    def set_task(self, new:float):
        self._task = new
    
    task = property(get_task, set_task)

    def get_description(self):
        return self._description
    
    def set_description(self, new:float):
        self._description = new
    
    description = property(get_description, set_description)

    # Abstract methods
    @abstractmethod
    def run():
        pass
    


class ImplementorAdversary(Optimizer):

    def __init__(self, task:Task, implementor: Implementor, adversary: Adversary, description = ""):

        super().__init__(task, description)
        
        self._implementor = implementor
        self._adversary = adversary

        self._instance_data = None

    # Getters and setters

    def set_adversary_predictor(self, predictor:PredictiveModel):
        self._adversary.predictor = predictor
        return True

    # Abstract methods implementation
    def run(self, max_loops:int):
        
        self._implementor.run()

        # Main implementor adversary loop
        for loop in range(max_loops):
            flag = False

            # call implementor


            # call adversary

            if flag == True:
                break

            # update instance data

        
        #return schedule

    # Specific methods
    def create_instance(self):
        
        master_schedule = self._task.get_master_schedule()
        
        # Parameters for sets
        n_days = self._task.num_of_weeks * master_schedule.get_week_length()
        
        #n_week_days = master_schedule.get_week_length
        n_rooms = master_schedule.get_num_of_rooms()
        

        
            
        c_exclusion = 1  #TODO
        c_delay = 1  #TODO
        
        
        # Get patients
        patients = self._task.get_patients()
        n_pats = self._task.num_of_patients
        
        # Get master blocks
        master_blocks = master_schedule.get_blocks()
        n_master_blocks = master_schedule.get_num_of_blocks()
        n_schedule_blocks = master_schedule.get_num_of_blocks() * self._task.num_of_weeks 
        

        # Instance data structure initialization
        instance = {}

        # Parameter g (gamma - capacity)
        update_dictionary = {}

        for b in range(n_schedule_blocks):
            
            master_block_index = b % n_master_blocks

            update_dictionary.update \
                    ({(b + 1): master_blocks[master_block_index].duration })
                
        instance.update({'g': update_dictionary})
        

        # Parameter a (compatibility)

        update_dictionary = {}
        
        for b in range(n_schedule_blocks):
            
            master_block_index = b % n_master_blocks
            
            for i, patient in enumerate(patients):

                patient_equipe = patient.equipe
                block_equipes = master_blocks[master_block_index].equipes
                
                if patient_equipe in block_equipes:
                    update_dictionary.update({(b+1,i+1) : 1})
                else:
                    update_dictionary.update({(b+1,i+1) : 0})

        instance.update({'a': update_dictionary})
        
        
        # TODO il ciclo sui pazieti potrebbe diventare unico...

        # Parameter t (estimated surgery duration time)

        update_dictionary = {}

        for i, patient in enumerate(patients):
            update_dictionary.update({i + 1: patient.uncertainty_profile.nominal_value})

        instance.update({'t': update_dictionary})

        # Parameter u (Urgency)

        update_dictionary = {}

        for i, patient in enumerate(patients):
            update_dictionary.update({i + 1: patient.urgency})

        instance.update({'u': update_dictionary})

        # Parameter w (Waiting days already spent)

        update_dictionary = {}

        for i, patient in enumerate(patients):
            update_dictionary.update({i + 1: patient.days_waiting})

        instance.update({'w': update_dictionary})

        # Parameter l (maximum waiting days allowed)

        update_dictionary = {}

        for i in range(n_pats):
            update_dictionary.update({i + 1: patient.max_waiting_days})

        instance.update({'l': update_dictionary})


        instance.update({
            'n_days': {None: n_days},
            'n_blocks': {None: n_schedule_blocks},
            'n_rooms': {None: n_rooms},
            'n_pats': {None: n_pats},

            # Objective functions coefficients
            'c_exclusion': {None: c_exclusion},
            'c_delay': {None: c_delay},
            
            # TODO controllare se ha senso tenerla
            'n_realizations': {None : 0}

            # Covers variables # ANDREBBE RIMOSSA TODO
            # 'covers_excluded': {None: len(covers)},
            # 'different_block_duration': {None: different_block_duration},
        })

        # Pyomo structure requirement - saving among the class members
        self._instance = {None: instance}
        
        self._implementor.instance_data = self._instance


    def run_implementor(self, instance_data):
        return self._implementor.run(instance_data)
        

    def run_adversary(self, schedule):
        # return self.adversary.run(schedule)
        pass

    def update_instance(self, adversary_fragilities):
        # update self.instance_data
        pass



class ChanceConstraintsOptimizer(Optimizer):
    
    def __init__(self, task:Task, description = ""):
        
        from ._models_components import (
            ObjRule_standard,
            ObjRule_count,
            delayDetectorRule,
            capacityRule,
            capacityOvertimeRule,
            compatibilityRule,
            oneSurgeryRule,
            YVarDefRule
        )

        self._description = description
        self._instance_data = None
        
        # Model definition
        
        self._model = pyo.AbstractModel() # pyomo abstract model
        
        # Sets
        self._model.n_days = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_rooms = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_blocks = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_pats = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_realizations = pyo.Param(within=pyo.NonNegativeIntegers)

        #self._model.D = pyo.RangeSet(1, self._model.n_days)
        #self._model.J = pyo.RangeSet(1, self._model.n_rooms)
        self._model.B = pyo.RangeSet(1, self._model.n_blocks)
        self._model.I = pyo.RangeSet(1, self._model.n_pats)
        self._model.K = pyo.RangeSet(1, self._model.n_realizations)

        # Parameters
        self._model.t = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.w = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.l = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.u = pyo.Param(self._model.I, within=pyo.NonNegativeReals)

        self._model.eps = pyo.Param(self._model.I, self._model.K, within=pyo.NonNegativeReals)

        #self._model.g = pyo.Param(self._model.D, self._model.J, self._model.B, within=pyo.NonNegativeIntegers)
        #self._model.a = pyo.Param(self._model.D, self._model.J, self._model.B, self._model.I, within=pyo.Binary)
        self._model.g = pyo.Param(self._model.B, within=pyo.NonNegativeIntegers)
        self._model.a = pyo.Param(self._model.B, self._model.I, within=pyo.Binary)

        self._model.c_exclusion = pyo.Param(within=pyo.NonNegativeReals)
        self._model.c_delay = pyo.Param(within=pyo.NonNegativeReals)

        # Variables
        #self._model.x = pyo.Var(self._model.D, self._model.J, self._model.B, self._model.I, within=pyo.Binary)
        self._model.x = pyo.Var(self._model.B, self._model.I, within=pyo.Binary)
        self._model.y = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        self._model.z = pyo.Var(self._model.I, within=pyo.NonNegativeReals)

        # Objective function
        self._model.obj = pyo.Objective(rule=ObjRule_standard, sense=pyo.minimize)
        
        # Constraints
        self._model.delayDetector = pyo.Constraint(self._model.I, rule=delayDetectorRule)
        #self._model.capacity = pyo.Constraint(self._model.D, self._model.J, self._model.B, rule=capacityRule)
        #self._model.capacityOvertime = pyo.Constraint(self._model.D, self._model.J, self._model.B, self._model.K, rule=capacityOvertimeRule)
        #self._model.compatibility = pyo.Constraint(self._model.D, self._model.J, self._model.B, self._model.I, rule=compatibilityRule)
        self._model.oneSurgery = pyo.Constraint(self._model.I, rule=oneSurgeryRule)
        self._model.YVarDef = pyo.Constraint(self._model.I, rule=YVarDefRule)
        
        self._model.capacity = pyo.Constraint(self._model.B, rule=capacityRule)
        self._model.capacityOvertime = pyo.Constraint(self._model.B, self._model.K, rule=capacityOvertimeRule)
        self._model.compatibility = pyo.Constraint(self._model.B, self._model.I, rule=compatibilityRule)
        


        
        
        

    # Getters and setters
    def get_description(self):
        return self._description
    
    def set_description(self, new):
        self._description = new

    description = property(get_description, set_description)
    
    def get_instance_data(self):
        return self._instance_data
    
    def set_instance_data(self, new):
        self._instance_data = new

    instance_data = property(get_instance_data, set_instance_data)

    # Abstract methods

    # General methods
    def run(self): #!!!!!
        # Instance creation
        self._instance = self._model.create_instance(self.instance_data)

        # Solver configuration
        self._solver = pyo.SolverFactory('appsi_highs')
        #solver.options['Threads'] = config['SOLVER']['SolverThreads']
        #solver.options['TimeLimit'] = config['SOLVER']['SolverTimeLimit']
        #solver.options['MIPGap'] = config['SOLVER']['SolverMIPGap']

        # Solver launching
        solver_result = self._solver.solve(self._instance, tee=False)
        
        # Saving data of the solution
        self._instance.solutions.store_to(solver_result)

        return self._instance # questa adrebbe processata dentro una schedula prima di procedere



