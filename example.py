from georgstage.app import App
from georgstage.solver import *

if __name__ == '__main__':

    app = App()
    app.load()

    task_counts = get_task_counts(app.df)
    vagthavende = [1,21,41]
    hu = [7,8,9]

    prob, X = get_instance(task_counts, vagthavende, hu=hu)
    status = prob.solve()
    if status == 1:
        print_sol(task_counts, X)
    else:
        print('Not optimized...')
