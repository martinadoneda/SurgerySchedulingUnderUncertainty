# Python STL
from abc import ABC, abstractmethod
import random

# Packages
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# Modules
from .patient import Patient
from .task import Task


class PatientsProvider(ABC):
    """
    Abstract class for patients providers. Patients providers are object which
    generates patient. They can process dataset and extract a patient for each line
    or they can generate patients with random process. These different ways are
    implemented in different concrete classes. Generation can be driven by asking 
    for specific kind of patients, in particular specifing the equipe or the 
    urgency. Patients providers also can generate patients for the training of 
    predictive models.

    Attributes
    ----------
    _task : Task
        Task contains the problem specifications.
    _description : str
        To keep a text description of the provider created.

    Methods
    -------
    provide_patient(self, requested_equipe:str = None, requested_urgency:int = None) -> Patient:
        Provide a single patient, can specify equpe and urgency
    """

    
    def __init__(self, task:Task, description = ""):
        self._description = description
        self._task = task

    # Getters and setters
    def get_description(self):
        return self._description
    
    def set_description(self, new:str):
        self._description = new
    
    description = property(get_description, set_description)

    def get_task(self):
        return self._task
    
    def set_task(self, new:Task):
        self._task = new
    
    task = property(get_task, set_task)

    # Abstract methods
    @abstractmethod
    def provide_patient(self, requested_equipe:str = None, requested_urgency:int = None) -> Patient:
        pass


    @abstractmethod
    def provide_patient_set(self, patient_model, num):
        pass

    @abstractmethod
    def provide_patient_training(self, patient_model, num):
        pass

    # General methods
    def provide_sets(self, patient_model, num_patients, num_training):
        return (self.provide_patient_set(patient_model=patient_model, num=num_patients), 
                self.provide_patient_training(patient_model=patient_model, num = num_training))
    


class PatientsFromHistoricalDataProvider(PatientsProvider):
    """
    Inherit from abstract class PatientsProvider
    Class for a patients provider that extract patients from a dataset of already
    processed patients. In general this kind of patients can be used for test purposes
    or to train the predictive models. The Dataset must contain some columns with the 
    following names:
     - target (float): the true surgery time.
     - equipe (str): which equipe have processed the patient.
     - urgency (int): urgency grade required. Urgency grades are converted as 
       specified in the task object.
     - other columns: will be treated as "features" for predicting the surgery time.
       Numerical columns are preserved, categorical are encoded through one-hot-encoding.
    
    Attributes
    ----------
    _task: Task
        Task contains the problem specifications.
    _description: str
        To keep a text description of the provider created.
    _historical_data: pd.DataFrame
        Is the pandas' dataframe which provide patients' data.
    _sampled_indexes: set
        Keep track of rows already used from the dataset.
    _patient_id_start_number: int
        When all rows are used, the function restart sampling including already used rows.
        This variable allow to generate patients with different ids. 

    Methods
    -------
    provide_patient(self, requested_equipe:str = None, requested_urgency:int = None) -> Patient:
        Provide a single patient, can specify equpe and urgency
    """

    def __init__(self, 
                 task:Task, 
                 historical_data: pd.DataFrame, 
                 description = ""):
        """
        Constructor.

        Parameters
        ----------
        _task : Task
            Task contains the problem specifications.
        _description : str, optional
            To keep a text description of the provider created.
        _historical_data: pd.DataFrame
            Is the pandas' dataframe which provide patients' data.
        """
        super().__init__(task, description)
        
        self._historical_data = historical_data
        
        self._sampled_indexes = set()
        self._patient_id_start_number = 0

        ## One hot encoding of categorical features

        # Select columns containing categorical data  (object type)
        categorical_columns = self._historical_data.select_dtypes(include=['object']).columns
        # Instantiate one - hot- tencoder
        encoder = OneHotEncoder( drop='first')
        # Run the one - hot - encoder
        one_hot_encoded = encoder.fit_transform(self._historical_data[categorical_columns])
        # New dataframe
        one_hot_encoded_df = pd.DataFrame(one_hot_encoded.toarray(), columns=encoder.get_feature_names_out(categorical_columns))
        # Concatenatign with original dataframe
        df = pd.concat([self._historical_data, one_hot_encoded_df], axis=1)
        # Exclude equipe columns
        categorical_columns = categorical_columns.difference(['equipe'])
        # Removing encoded columns
        self._historical_data = df.drop(columns=categorical_columns)


    # Getters and setters
    def get_historical_data(self):
        return self._historical_data
    
    def set_historical_data(self, new:pd.DataFrame):
        self._historical_data = new
    
    historical_data = property(get_historical_data, set_historical_data)


    # Abstract methods implementation

    def provide_patient(self, requested_equipe:str = None, requested_urgency:int = None) -> Patient:

        """
        Provide a single patient. Can request an equipe and/or an urgency.

        Parameters
        ----------
        requested_equipe: str, optional
            The equipe which will process the patient provided.

        requested_urgency: int, optional
            The urgency grade assigned to the patient.

        Returns
        -------
        Patient
            A patient object filled with information in the dataset.
        """


        if (requested_equipe != None) & (requested_equipe != None):
            filtered_data = self._historical_data.loc[
                (self._historical_data['equipe'] == requested_equipe) &
                (self._historical_data['urgency'] == requested_urgency)
            ]
        elif requested_equipe != None:
            filtered_data = self._historical_data.loc[
                (self._historical_data['equipe'] == requested_equipe)
            ]
        elif requested_urgency != None:
            filtered_data = self._historical_data.loc[
                (self._historical_data['urgency'] == requested_urgency)
            ]

        available_indexes = [ x for x in list(filtered_data.index) if x not in self._sampled_indexes]
        patient_index = random.choice(available_indexes)
        self._sampled_indexes.add(patient_index)

        id = patient_index + self._patient_id_start_number
        features = np.array(self._historical_data.loc[patient_index, ~self._historical_data.columns.isin(['equipe', 'target', 'urgency'])])
        
        target = self._historical_data.loc[patient_index, ~self._historical_data.columns.isin(['target'])]
        equipe = self._historical_data.loc[patient_index, ~self._historical_data.columns.isin(['equipe'])]
        urgency = self._historical_data.loc[patient_index, ~self._historical_data.columns.isin(['urgency'])]

        return Patient(id=id,equipe=equipe, urgency=urgency, features=features, target=target, uncertainty_profile=None)


    def provide_patient_set(self, patient_model, num):
        pass

    def provide_patient_training(self, patient_model, num):
        pass

    # Specific methods

    def reset_sampled_indexes(self, enforce = False):
        """_summary_
        Quando chiamata, se forzata o se tutti i pazienti sono stati estratti, si resetta il contenitore
        degli indici già estratti.
        Args:
            enforce (bool, optional): _description_. Defaults to False.
        """
        if enforce | (len(self._historical_data.index) == self._sampled_indexes):
            print("Warning: from now on patients can be resampled.")
            self._sampled_indexes = set()
            self._patient_id_start_number += len(self._historical_data) # aggiungo righe su id



class PatientsGeneratedProvider(PatientsProvider):

    # Abstract methods implementation

    def provide_patient(self, patient_model):
        pass

    def provide_patient_set(self, patient_model, num):
        pass

    def provide_patient_training(self, patient_model, num):
        pass