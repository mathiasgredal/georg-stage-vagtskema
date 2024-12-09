from typing import List
import pulp as P

from georgstage.model import GeorgStage, Opgave, Vagt, get_skifte_for_gast
from georgstage.autofill import (
    N_GASTS,
    VAGT_TIDER,
    VAGT_TIDER_OG_DAG,
    FillResult,
    get_counts,
)


def autofill(model: GeorgStage, skifter=[1, 2, 3, 1, 2, 3]) -> FillResult:
    """
    Limitation: vagthavende elev must be filled manually to ensure same gast
    morning and evening.
    """
    datestr = str(model.get_current_dato())
    day_vagter: List[Vagt] = model[datestr]
    other_vagter: List[Vagt] = list(model.get_vagter(before=datestr))
    lookup = get_counts(day_vagter + other_vagter)

    # Problem
    prob = P.LpProblem("udfyld_vagter", P.LpMinimize)

    # Ude gaster
    ude_gaster = [v.gast for v in day_vagter if v.opgave == Opgave.UDE]

    # Alle gaster
    gaster = [gast for gast in range(1, N_GASTS + 1)]

    # All opgaver
    opgaver = [o.value for o in Opgave]

    # Special opgaver
    opgaver_spec = [
        Opgave.UDE.value,
        Opgave.HU.value,
        Opgave.DAEKSELEV_I_KABYS.value,
        Opgave.PEJLEGAST_A.value,
        Opgave.PEJLEGAST_B.value,
    ]
    # Normal opgaver
    opgaver_norm = [o.value for o in Opgave if o.value not in opgaver_spec]

    # Decision variables
    #   X_ijt: gast i, opgave j, hour t
    X = P.LpVariable.dicts("X", (gaster, opgaver, VAGT_TIDER_OG_DAG), 0, 1, P.LpBinary)

    lookup = get_counts(day_vagter + other_vagter)

    # Coefficients (number of times gast performed task)
    coef = {}
    for i in gaster:
        for j in opgaver:
            coef.setdefault(i, {})[j] = lookup(i, Opgave(j))

    # Objective function
    prob += P.lpSum(
        [coef[i][j] * X[i][j][t] for i in gaster for j in opgaver for t in VAGT_TIDER]
    )

    # Constraints

    # Ude gaster cannot perform other tasks
    prob += (
        P.lpSum(
            [
                X[i][j][t]
                for i in ude_gaster
                for j in [o for o in opgaver if o != Opgave.UDE]
                for t in VAGT_TIDER
            ]
        )
        == 0
    )

    # preassigned day vagter must be assigned
    for vagt in day_vagter:
        prob += X[vagt.gast][vagt.opgave.value][vagt.vagt_tid] == 1

    # all normal tasks must be assigned exactly once per vagt_tid
    #  except: UDE, HU, PEJLEGAST_A, PEJLEGAST_B, DAEKSELEV_I_KABYS
    for j in opgaver_norm:
        for t in VAGT_TIDER:
            prob += P.lpSum([X[i][j][t] for i in gaster]) == 1

    # Pejlegaster only 16-20 vagt
    for t in VAGT_TIDER:
        # Set RHS to 1 if vagt_tid is 16, else 0
        rhs = 1 if t == 16 else 0
        prob += P.lpSum([X[i][Opgave.PEJLEGAST_A.value][t] for i in gaster]) == rhs
        prob += P.lpSum([X[i][Opgave.PEJLEGAST_B.value][t] for i in gaster]) == rhs

    # Dæks elev i kabys. Only 4, 8, 12, 16
    for t in VAGT_TIDER:
        # Set RHS to 1 if vagt_tid is 16, else 0
        rhs = 1 if t in [4, 8, 12, 16] else 0
        prob += (
            P.lpSum([X[i][Opgave.DAEKSELEV_I_KABYS.value][t] for i in gaster]) == rhs
        )

    # gasts can have at most one task per shift
    for i in gaster:
        for t in VAGT_TIDER:
            prob += P.lpSum([X[i][j][t] for j in opgaver]) <= 1

    # gasts can take zero tasks outside their own shift
    for idx, skifte in enumerate(skifter):
        gaster_inactive = [i for i in gaster if get_skifte_for_gast(i) != skifte]
        t = VAGT_TIDER[idx]
        prob += P.lpSum([X[i][j][t] for i in gaster_inactive for j in opgaver]) == 0

    # gasts can not be assigned two times to same task
    # Note: does not apply to manually assigned gasts
    manual_gaster = {vagt.gast for vagt in day_vagter}
    not_manual_gaster = {gast for gast in gaster if gast not in manual_gaster}
    for i in not_manual_gaster:
        for j in opgaver:
            prob += P.lpSum([X[i][j][t] for t in VAGT_TIDER]) <= 1

    # Solve
    status = prob.solve()
    vagter = []
    for gast in gaster:
        for opgave in opgaver:
            for vagt_tid in VAGT_TIDER_OG_DAG:
                x = X[gast][opgave][vagt_tid]
                if x.varValue == 1:
                    vagter.append(Vagt(datestr, vagt_tid, gast, Opgave(opgave)))

    return FillResult(status=status, vagter=vagter)
