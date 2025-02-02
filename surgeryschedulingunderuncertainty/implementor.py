

# Python STL
from abc import ABC, abstractmethod

# Packages
import pyomo.environ as pyo

# Modules
from .task import Task
from ._models_components import (
    ObjRule_standard,
    ObjRule_count,
    delayDetectorRule,
    capacityRule,
    capacityOvertimeRule,
    compatibilityRule,
    oneSurgeryRule,
    YVarDefRule,
    fractionSumOneRule,
    assignmentExistRule,
    chanceConstraintRule,
    dualCapacityRule,
    dualDefinitionRule
    
)





class Implementor(ABC):
    
    def __init__(self, description = "", task:Task = None):
        self._description = description
        self._task = task
        
        #self._instance_data = None

        self._model = pyo.AbstractModel() # pyomo abstract model

    # Getters and setters
    def get_description(self):
        return self._description
    def set_description(self, new):
        self._description = new
    description = property(get_description, set_description)

    # Abstract methods

    # General methods
    def run(self):
        # Instance creation
        self._instance = self._model.create_instance(self.instance_data)

        # Solver configuration
        self._solver = pyo.SolverFactory('appsi_highs')

        # Solver launching
        solver_result = self._solver.solve(self._instance, tee=False)
        
        # Saving data of the solution
        self._instance.solutions.store_to(solver_result)
        
        return self._instance 



class StandardImplementor(Implementor):

    def __init__(self, description="", task:Task = None):
        super().__init__(description, task)

        # Sets
        self._model.n_days = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_rooms = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_blocks = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_pats = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_realizations = pyo.Param(within=pyo.NonNegativeIntegers)

        self._model.B = pyo.RangeSet(1, self._model.n_blocks)
        self._model.I = pyo.RangeSet(1, self._model.n_pats)
        self._model.K = pyo.RangeSet(1, self._model.n_realizations)

        # Parameters
        self._model.t = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.w = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.l = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.u = pyo.Param(self._model.I, within=pyo.NonNegativeReals)

        self._model.eps = pyo.Param(self._model.I, self._model.K, within=pyo.NonNegativeReals)

        self._model.g = pyo.Param(self._model.B, within=pyo.NonNegativeIntegers)
        self._model.a = pyo.Param(self._model.B, self._model.I, within=pyo.Binary)

        self._model.c_exclusion = pyo.Param(within=pyo.NonNegativeReals)
        self._model.c_delay = pyo.Param(within=pyo.NonNegativeReals)

        # Variables
        self._model.x = pyo.Var(self._model.B, self._model.I, within=pyo.Binary)
        self._model.y = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        self._model.z = pyo.Var(self._model.I, within=pyo.NonNegativeReals)

        # Objective function
        self._model.obj = pyo.Objective(rule=ObjRule_standard, sense=pyo.minimize)
        
        # Constraints
        self._model.delayDetector = pyo.Constraint(self._model.I, rule=delayDetectorRule)
        self._model.oneSurgery = pyo.Constraint(self._model.I, rule=oneSurgeryRule)
        self._model.YVarDef = pyo.Constraint(self._model.I, rule=YVarDefRule)
        
        self._model.capacity = pyo.Constraint(self._model.B, rule=capacityRule)
        self._model.capacityOvertime = pyo.Constraint(self._model.B, self._model.K, rule=capacityOvertimeRule)
        self._model.compatibility = pyo.Constraint(self._model.B, self._model.I, rule=compatibilityRule)
        
    
     
        
class ChanceConstraintsImplementor(Implementor):

    def __init__(self, task:Task, description = "", ): # TODO robustness_overtime non può essere None...
        super().__init__(description, task)

        # Sets
        self._model.n_days = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_rooms = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_blocks = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_pats = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_realizations = pyo.Param(within=pyo.NonNegativeIntegers)

        self._model.B = pyo.RangeSet(1, self._model.n_blocks)
        self._model.I = pyo.RangeSet(1, self._model.n_pats)
        self._model.K = pyo.RangeSet(1, self._model.n_realizations)

        # Parameters
        self._model.t = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.w = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.l = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.u = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        
        self._model.f = pyo.Param(self._model.I, within=pyo.NonNegativeReals)


        self._model.eps = pyo.Param(self._model.I, self._model.K, within=pyo.NonNegativeReals)

        self._model.g = pyo.Param(self._model.B, within=pyo.NonNegativeIntegers)
        self._model.a = pyo.Param(self._model.B, self._model.I, within=pyo.Binary)

        self._model.c_exclusion = pyo.Param(within=pyo.NonNegativeReals)
        self._model.c_delay = pyo.Param(within=pyo.NonNegativeReals)

        # Variables
        self._model.x = pyo.Var(self._model.B, self._model.I, within=pyo.Binary)
        self._model.q = pyo.Var(self._model.B, self._model.I, within=pyo.NonNegativeReals)
        self._model.y = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        self._model.z = pyo.Var(self._model.I, within=pyo.NonNegativeReals)

        # Objective function
        self._model.obj = pyo.Objective(rule=ObjRule_standard, sense=pyo.minimize)
        
        # Constraints
        self._model.delayDetector = pyo.Constraint(self._model.I, rule=delayDetectorRule)
        self._model.oneSurgery = pyo.Constraint(self._model.I, rule=oneSurgeryRule)
        self._model.YVarDef = pyo.Constraint(self._model.I, rule=YVarDefRule)
        
        self._model.capacity = pyo.Constraint(self._model.B, rule=capacityRule)
        self._model.capacityOvertime = pyo.Constraint(self._model.B, self._model.K, rule=capacityOvertimeRule)
        self._model.compatibility = pyo.Constraint(self._model.B, self._model.I, rule=compatibilityRule)
        
        self._model.fractionSumOne = pyo.Constraint(self._model.B, rule=fractionSumOneRule)
        self._model.assignmentExist = pyo.Constraint(self._model.B, self._model.I, rule=assignmentExistRule)
        self._model.chanceConstraint = pyo.Constraint(self._model.B, self._model.I, rule=chanceConstraintRule(self._task.robustness_overtime))
 


class ChanceConstraintsImplementor(Implementor):

    def __init__(self, task:Task, description = "", ): # TODO robustness_overtime non può essere None...
        super().__init__(description, task)

        # Sets
        self._model.n_days = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_rooms = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_blocks = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_pats = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_realizations = pyo.Param(within=pyo.NonNegativeIntegers)

        self._model.B = pyo.RangeSet(1, self._model.n_blocks)
        self._model.I = pyo.RangeSet(1, self._model.n_pats)
        self._model.K = pyo.RangeSet(1, self._model.n_realizations)

        # Parameters
        self._model.t = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.w = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.l = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.u = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        
        self._model.f = pyo.Param(self._model.I, within=pyo.NonNegativeReals)

        # TODO questo si potrebbe togliere
        #self._model.eps = pyo.Param(self._model.I, self._model.K, within=pyo.NonNegativeReals)

        self._model.g = pyo.Param(self._model.B, within=pyo.NonNegativeIntegers)
        self._model.a = pyo.Param(self._model.B, self._model.I, within=pyo.Binary)

        self._model.c_exclusion = pyo.Param(within=pyo.NonNegativeReals)
        self._model.c_delay = pyo.Param(within=pyo.NonNegativeReals)

        # Variables
        self._model.x = pyo.Var(self._model.B, self._model.I, within=pyo.Binary)
        self._model.q = pyo.Var(self._model.B, self._model.I, within=pyo.NonNegativeReals)
        self._model.y = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        self._model.z = pyo.Var(self._model.I, within=pyo.NonNegativeReals)

        # Objective function
        self._model.obj = pyo.Objective(rule=ObjRule_standard, sense=pyo.minimize)
        
        # Constraints
        self._model.delayDetector = pyo.Constraint(self._model.I, rule=delayDetectorRule)
        self._model.oneSurgery = pyo.Constraint(self._model.I, rule=oneSurgeryRule)
        self._model.YVarDef = pyo.Constraint(self._model.I, rule=YVarDefRule)
        
        self._model.capacity = pyo.Constraint(self._model.B, rule=capacityRule)
        self._model.capacityOvertime = pyo.Constraint(self._model.B, self._model.K, rule=capacityOvertimeRule)
        self._model.compatibility = pyo.Constraint(self._model.B, self._model.I, rule=compatibilityRule)
        
        self._model.fractionSumOne = pyo.Constraint(self._model.B, rule=fractionSumOneRule)
        self._model.assignmentExist = pyo.Constraint(self._model.B, self._model.I, rule=assignmentExistRule)
        
        self._model.chanceConstraint = pyo.Constraint(self._model.B, self._model.I, rule=chanceConstraintRule(self._task.robustness_overtime))
 


class BSImplementor(Implementor): # Budget Set

    def __init__(self, task:Task, description = "", ): # TODO robustness_overtime non può essere None...
        super().__init__(description, task)

        # Sets
        self._model.n_days = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_rooms = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_blocks = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_pats = pyo.Param(within=pyo.NonNegativeIntegers)
        self._model.n_realizations = pyo.Param(within=pyo.NonNegativeIntegers)

        self._model.B = pyo.RangeSet(1, self._model.n_blocks)
        self._model.I = pyo.RangeSet(1, self._model.n_pats)

        # Parameters
        self._model.t = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.w = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.l = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        self._model.u = pyo.Param(self._model.I, within=pyo.NonNegativeReals)
        
        self._model.g = pyo.Param(self._model.B, within=pyo.NonNegativeIntegers)
        self._model.a = pyo.Param(self._model.B, self._model.I, within=pyo.Binary)
        
        self._model.gamma = pyo.Param(self._model.B, within=pyo.NonNegativeReals)
        self._model.time_increment = pyo.Param(self._model.B, within=pyo.NonNegativeReals)
        
        self._model.c_exclusion = pyo.Param(within=pyo.NonNegativeReals)
        self._model.c_delay = pyo.Param(within=pyo.NonNegativeReals)

        # Variables
        self._model.x = pyo.Var(self._model.B, self._model.I, within=pyo.Binary)
        self._model.q = pyo.Var(self._model.B, self._model.I, within=pyo.NonNegativeReals)
        self._model.y = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        self._model.z = pyo.Var(self._model.I, within=pyo.NonNegativeReals)
        
        # Variabili duali per vincolo duale
        self._model.xi = pyo.Var(self._model.B, within=pyo.NonNegativeReals)
        self._model.pi = pyo.Var(self._model.B, self._model.I, within=pyo.NonNegativeReals)

        # Objective function
        self._model.obj = pyo.Objective(rule=ObjRule_standard, sense=pyo.minimize)
        
        # Constraints
        self._model.delayDetector = pyo.Constraint(self._model.I, rule=delayDetectorRule)
        self._model.oneSurgery = pyo.Constraint(self._model.I, rule=oneSurgeryRule)
        self._model.YVarDef = pyo.Constraint(self._model.I, rule=YVarDefRule)
        
        self._model.capacity = pyo.Constraint(self._model.B, rule=capacityRule)
        self._model.compatibility = pyo.Constraint(self._model.B, self._model.I, rule=compatibilityRule)

        self._model.dualCapacity = pyo.Constraint(self._model.B, rule=dualCapacityRule)
        self._model.dualDefinition = pyo.Constraint(self._model.B, self._model.I, rule=dualDefinitionRule)  
