# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:08:35 2019

@author: vince
"""

from __future__ import print_function

from ortools.sat.python import cp_model
import pandas as pd
import datetime as dt
import numpy as np

class AllSolutionCollector(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__collect = []

    def on_solution_callback(self):
        """Collect a new combination."""
        # https://github.com/google/or-tools/blob/stable/examples/python/appointments.py
        self.__solution_count += 1
        combination = [self.Value(v) for v in self.__variables]
        #print("hoi")
        self.__collect.append(combination)

    def solution_count(self):
        return self.__solution_count

    def combinations(self):
        """Returns all collected combinations."""
        return self.__collect


def solve_loans(df, df_act_cf):
    """Solves the loan problem with the CP-SAT solver."""
    # Create the model.
    model = cp_model.CpModel()

    # create the sets
    loans = list(set(df['loan']))
    subloans = list(set(df['subloan']))
    steps = list(set(df['step']))

    df.set_index(['loan','subloan','step'],inplace=True)
    df_act_cf.set_index(['step'],inplace=True)

    act_cf = df_act_cf['act_cf'].tolist()

    # parameters
    sum_act_cf = sum(act_cf)

    # create the sub loan variabels
    sub_loan_b = [[model.NewBoolVar('x[%i][%i]' % (l, s)) for s in subloans] for l in loans]

    # create cf sum variable
    max_act_cf = int(max(df_act_cf['act_cf'])*1.1)
    cf_sum = [model.NewIntVar(0, max_act_cf, 'cf_sum[%i]' % t) for t in steps]

    # for each loan only 1 subloan
    print("Setting up constraints")
    print("constraint: choose 1 subloan")
    for l in loans:
        model.Add(sum(sub_loan_b[l][s] for s in subloans) == 1)

    print("constraint: cashflows should match actual cashflow as close as possible")
    for t in steps:
        model.Add(sum(sum(sub_loan_b[l][s] * df.loc[l,s,t]['exp_cf'] for s in subloans) for l in loans) == cf_sum[t])

    # total predicted cf can not deviate more than 5% from actual cf
    model.Add(sum(cf_sum[t] for t in steps) - int(round(sum_act_cf,0)) <= int(round(0.05*sum_act_cf,0)))
    model.Add(sum(cf_sum[t] for t in steps) - int(round(sum_act_cf,0)) >= int(round(0.05*sum_act_cf * -1,0)))

    # for each timestep the predicted cf can not deviate too much from the actual cf 
    for t in steps:
        model.Add(cf_sum[t] - act_cf[t] <= int(round(0.25 * act_cf[t],0)))
        model.Add(cf_sum[t] - act_cf[t] >= int(round(0.25 * act_cf[t]*-1,0)))
    

    solver = cp_model.CpSolver()

    # Sets a time limit of 10 seconds.
    solver.parameters.max_time_in_seconds = 60.0

    print("make a for solution printer")
    a = []
    for l in loans:
        for s in subloans:
            a.append(sub_loan_b[l][s])

    solution_collector  = AllSolutionCollector(a)
    print("Search for all possible solutions")
    status = solver.SearchForAllSolutions(model, solution_collector)

    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_collector.solution_count())

    return solution_collector.combinations()


def calc_abs_error(a, b):
    abs_error = sum(abs(a - b))
    return abs_error


# import data
df_wide = pd.read_csv('loan_data_wide.csv')
df_long = pd.melt(df_wide,id_vars=['step'],var_name='loan_id',value_name='exp_cf')

df_long['loan'] = df_long['loan_id'].apply(lambda x: int(x.split('_')[0]))
df_long['subloan'] = df_long['loan_id'].apply(lambda x: int(x.split('_')[1]))

df_wide.set_index('step',inplace=True)
df_act_cf = pd.read_csv('act_cf.csv')

start_time = dt.datetime.now()
combinations = solve_loans(df_long, df_act_cf)

print("calc time was {}".format(dt.datetime.now() - start_time))

# calculate the abs error of each solution
abs_err_solutions = []
for i in combinations:
    b_mask = np.array(i) == 1
    pred_cf = df_wide.iloc[:,b_mask].sum(axis=1)
    abs_error = calc_abs_error(pred_cf,df_act_cf['act_cf'])
    abs_err_solutions.append(abs_error)

min_abs_error = min(abs_err_solutions)
idx = abs_err_solutions.index(min_abs_error)

print("the best solution has an abserror of {}".format(min(abs_err_solutions)))
print("the best solution has an mean abserror of {}".format(min(abs_err_solutions)/len(df_act_cf)))

idx2 = np.array(combinations[idx]) == 1.0
print("the selected loan ID's are {}".format(list(df_wide.columns[idx2])))

df_wide.iloc[:,idx2].sum(axis=1).to_csv('inspect.csv',header=['pred_cf'])

#print(np.argmax(abs_error_solutions))

"""
info on callback
https://developers.google.com/optimization/cp/cp_solver

sudoku
https://github.com/google/or-tools/blob/stable/examples/python/sudoku_sat.py

task allocation
https://github.com/google/or-tools/blob/stable/examples/python/task_allocation_sat.py

"""
