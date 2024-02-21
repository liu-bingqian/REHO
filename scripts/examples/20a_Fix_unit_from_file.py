import sys
import os

parent_dir = (os.
              path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(parent_dir)
os.environ["AMPL_PATH"] =r'C:\AMPL'

from reho.model.reho import *
from reho.model.preprocessing.QBuildings import QBuildingsReader

import time
import pandas as pd

if __name__ == '__main__':
    #
    # Set model type
    FixUnit = True
    nb_buildings = 22

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'

    # Set building parameters
    reader = QBuildingsReader()
    #reader.establish_connection('Suisse')
    #qbuildings_data = reader.read_db(3658, nb_buildings=2)
    reader = QBuildingsReader()
    qbuildings_data = reader.read_csv(buildings_filename='aigle_neighborhood.csv', nb_buildings=nb_buildings)
    # Set specific parameters
    parameters = {}

    # Select clustering file
    cluster = {'Location': 'Aigle', 'Attributes': ['I', 'T', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    # Choose energy system structure options
    scenario['exclude_units'] = ['Battery', 'NG_Cogeneration', 'DataHeat_DHW', 'OIL_Boiler', 'DHN_hex', 'HeatPump_DHN']
    scenario['enforce_units'] = []

    method = {}

    # Initialize available units and grids
    grids = infrastructure.initialize_grids()
    units = infrastructure.initialize_units(scenario, grids=grids)

    # Run optimization
    reho = reho(qbuildings_data=qbuildings_data, units=units, grids=grids, parameters=parameters, cluster=cluster,
                scenario=scenario, method=method, solver="cplex")

    reho.method['building-scale'] = True
    reho.method['district-scale'] = False
    #reho.method['parallel_computation'] = True


    #reho.single_optimization()
    #   SR.save_results(reho, save=['xlsx', 'pickle_all'], filename='3c')
    if FixUnit:
        # Run new optimization with the capacity of PV and electrical heater being fixed by the sizes of the first optimization
        df_results_file = pd.read_excel('aigle_neighborhood_pareto_pareto6.xlsx', sheet_name=["df_Unit"])
        #reho.df_fix_Units = reho.results['totex'][0]["df_Unit"]  # load data on the capacity of units
        reho.df_fix_Units = df_results_file["df_Unit"].set_index('Unit')
        reho.fix_units_list = ['PV', 'ElectricalHeater_DHW', 'ElectricalHeater_SH',
                               'HeatPump_Air', 'Air_Conditioner_Air', 'Battery', 'HeatPump_Geothermal', 'ThermalSolar', 'WaterTankDHW', 'WaterTankSH']  # select the ones being fixed
        #reho.fix_units_list = ['PV', 'ElectricalHeater_DHW', 'ElectricalHeater_SH',
        #                   'HeatPump_Air']
        reho.method['fix_units'] = True  # select the method fixing the unit sizes
    reho.scenario['Objective'] = 'TOTEX'
    reho.scenario['name'] = 'fixed'
    Start_Time = time.time()
    reho.single_optimization()
    End_Time = time.time()
    print(reho.infrastructure.House)
    # Save results
    SR.save_results(reho, save=['xlsx', 'pickle'], filename='20a_'+'Fix_Unit_'+str(FixUnit))
    print('Calculation time of the optimization problem: {}'.format(End_Time - Start_Time))
    '''
    district-size results None fixed 0 {'Objective': 'TOTEX', 'name': 'fixed', 'exclude_units': ['Battery', 'NG_Cogeneration', 'DataHeat_DHW', 'OIL_Boiler', 'DHN_hex', 'HeatPump_DHN'], 'enforce_units': [], 'specific': [], 'EMOO': {'EMOO_grid': 0.0}}
['Building1' 'Building2']
    '''