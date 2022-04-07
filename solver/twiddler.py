from z3 import *
from datetime import datetime, timedelta
import lib
import sys

# ToDo (Ordered)
# - Implement cons that were hand written.
# - Ask Hundter to run H generator to get a G and H file.
# - Examine and modify parameter file.
# - Current file uses concept of characters per second (CPS). Is this appropreiate? Regardless the CPS constants in parameters.py will either need to be disgarded entirely or changed.
# - Modify search section at bottom of twiddler.py
# - Modify Parameters.setup(), Parameters.initial_step_up(), Parameters.after_failure_step_up()

# Twiddler BitVector Index
#   L   M   R
#   11  10  9 - Index
#   8   7   6 - Middle
#   5   4   3 - Ring
#   2   1   0 - Pinky

setupTime = datetime.now()
s = Solver()
set_option(max_args=10000000, max_lines=1000000, max_depth=10000000, max_visited=1000000)
p = lib.Parameters.setup()
n = lib.NGrams.load_G_H(p)
b = lib.problem_def(s, n, p)

# ********************************
# |   Incorporate all of these   |
# |   into problem_def() above   |
# ********************************
# lib.mcc_from_scc(s, n, b)

# These letters frequently end words, so we don't want them
#   using the index finger, so they stride with SPACE.
# s.add(Extract(11, 11, b.F[n.index['E']]) == 0) #Ends 20.1% of words
# s.add(Extract(11, 11, b.F[n.index['S']]) == 0) #Ends 12.9% of words
# s.add(Extract(11, 11, b.F[n.index['D']]) == 0) #Ends 9.98% of words
# s.add(Extract(11, 11, b.F[n.index['N']]) == 0) #Ends 9.31% of words
# s.add(Extract(11, 11, b.F[n.index['T']]) == 0) #Ends 8.97% of words
# s.add(Extract(11, 11, b.F[n.index['Y']]) == 0) #Ends 6.00% of words
# s.add(Extract(11, 11, b.F[n.index['R']]) == 0) #Ends 5.90% of words
# s.add(Extract(11, 11, b.F[n.index['F']]) == 0) #Ends 4.71% of words
# s.add(Extract(11, 11, b.F[n.index['O']]) == 0) #Ends 4.18% of words
# s.add(Extract(11, 11, b.F[n.index['L']]) == 0) #Ends 3.47% of words
# s.add(Extract(11, 11, b.F[n.index['G']]) == 0) #Ends 2.94% of words
# s.add(Extract(11, 11, b.F[n.index['A']]) == 0) #Ends 2.82% of words
# s.add(Extract(11, 11, b.F[n.index['H']]) == 0) #Ends 2.71% of words

# If E cannot use *M** can it achieve 2.6846? If not fix E here.
# s.add(Extract(7, 7, b.G[n.index['E']]) == 0)


# If cost of chords is given in seconds then cumulative_cost[len(n.G)-1] is
#   the seconds to enter all of the training corpos.
# We can use this to calculate average characters per second:
# 1 / (cumulative_cost[len(n.G)-1] / total_count) this simplifies to:
# total_count / cumulative_cost[len(n.G)-1]
total_character_count = 0
for i in range(len(n.H)):
    total_character_count += n.HF[i] * len(n.H2[i])
print(f"Total character count: {total_character_count}")
chars_per_second = Real("cps")
s.add(chars_per_second == total_character_count / b.cumulative_cost[len(n.G)-1])


# ******************************************************
# Print out quick view of what configuration looks like.
# ******************************************************

def print_config(d):
    # The default buttons and double row buttons
    f = [
        2048, 3072, 1024, 1536, 512,
        2304, 3456, 1152, 1728, 576,
        256, 384, 128, 192, 64,
        288, 432, 144, 216, 72,
        32, 48, 16, 24, 8,
        36, 54, 18, 27, 9,
        4, 6, 2, 3, 1,
    ]

    # Mask f here when adding combo display feature.

    # If a chord doesn't have an n_gram fill it with the empty string.
    for x in f:
        if x not in d:
            d[x] = ""
    # print(f[0].sort())
    print(f'\n   Left       Middle       Right')
    print(f' ________________________________')
    print(f'|              Space      BckSpc | <-- Mouseclick buttons')
    print(f'|--------------------------------|')
    print(f'| [{d[f[0]]:4}] {d[f[1]]:4} [{d[f[2]]:4}] {d[f[3]]:4} [{d[f[4]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[5]]:4}  {d[f[6]]:4}  {d[f[7]]:4}  {d[f[8]]:4}  {d[f[9]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[10]]:4}] {d[f[11]]:4} [{d[f[12]]:4}] {d[f[13]]:4} [{d[f[14]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[15]]:4}  {d[f[16]]:4}  {d[f[17]]:4}  {d[f[18]]:4}  {d[f[19]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[20]]:4}] {d[f[21]]:4} [{d[f[22]]:4}] {d[f[23]]:4} [{d[f[24]]:4}] |')
    print(f'|                                |')
    print(f'|  {d[f[25]]:4}  {d[f[26]]:4}  {d[f[27]]:4}  {d[f[28]]:4}  {d[f[29]]:4}  |')
    print(f'|                                |')
    print(f'| [{d[f[30]]:4}] {d[f[31]]:4} [{d[f[32]]:4}] {d[f[33]]:4} [{d[f[34]]:4}] |')
    print(f'|________________________________|')

def print_details(m):
    # We generate a dictionary where the chords are the keys and n_grams the values.
    num_2 = 0
    num_3 = 0
    num_4 = 0
    num_5 = 0
    press_lookup = {}
    for i in range(len(n.G)):
        if m[b.G[i]] in press_lookup:
            assert m[b.G[i]] == 0
        else:
            press_lookup[int(str(m[b.G[i]]))] = n.G[i]
            if len(n.G[i]) == 2:
                # print("i: " + str(i) + ", m[G[i]]: " + str(m[G[i]]) + ", n.G: " + n.G[i])
                num_2 += 1
            elif len(n.G[i]) == 3:
                num_3 += 1
            elif len(n.G[i]) == 4:
                num_4 += 1
            elif len(n.G[i]) == 5:
                num_5 += 1
            # elif len(n.G[i]) == 1:
            print("i: " + str(i) + ", m[G[i]]: " + str(m[b.G[i]]) + ", n_gram: " + n.G[i])
    print(f'Chorded-2_grams: {num_2}, 3_grams: {num_3}, 4_grams: {num_4}, 5_grams: {num_5}')
    
    print_config(press_lookup)

# **************************************************
# Sit back relax and let the SMT solver do the work.
# **************************************************

# Timeout is given in milliseconds
s.set("timeout", (p.timeout.days * 24 * 60 * 60 + p.timeout.seconds) * 1000)
print(f"N-Grams: {str(len(n.G))}, Setup Time: {datetime.now() - setupTime}")
print("---------------------------------------")
print(f"CharsPerSec - Result  - Time:This Run  - Time:All Runs")
# print(s)
# print("---------------------------------------")

hi_sat = 0
lo_unsat = float("inf")
lo_unknown = float("inf")
search_has_failed = False
last_print_time = datetime.min
last_sat_time = datetime.min
solver_time = datetime.now()
last_was_update = False
m = None
f = open("config.txt", "a")
# See comments above in "Guide the Search" for understanding how this works.
while min(lo_unsat, lo_unknown, p.cps_hi) - max(hi_sat, p.cps_lo) > p.cps_res:
    # print(f"lo_unsat: {lo_unsat}, lo_unknown: {lo_unknown}, p.cps_hi: {p.cps_hi}, hi_sat: {hi_sat}, p.cps_lo: {p.cps_lo}, p.cps_res: {p.cps_res}")
    solveTime = datetime.now()

    # We start from p.cps_lo initially and increment up by initial_step_up
    #   until we encounter an UNSAT or UNKNOWN problem then we begin
    #   binary search.
    if not search_has_failed:
        guess_cps = max(hi_sat, p.cps_lo - p.initial_step_up()) + p.initial_step_up()
    else:
        guess_cps = p.after_failure_step_up(min(lo_unsat, lo_unknown, p.cps_hi),
                                            max(hi_sat, p.cps_lo))

    # For some reason the solver cannot handle this constraint:
    #   s.add(chars_per_second >= cps)
    #   So we calclate max cumulative cost and set the limit that way.
    guess_max_cumulative_cost = total_count / guess_cps
    s.push() # Create new state
    s.add(b.cumulative_cost[len(n.G)-1] <= guess_max_cumulative_cost)
    
    
    result = s.check()
    guess_time = datetime.now() - solveTime
    if datetime.now() >= last_print_time + p.update_time:
        if last_was_update:
            print("") # Print newline
            last_was_update = False
        last_print_time = datetime.now()
        print(f"{guess_cps:.9f} - {str(result):7} - {guess_time} - {datetime.now() - solver_time}")
    else:
        print(f".", flush=True, end="")
        last_was_update = True

    sys.stdout = f
    if result == sat:
        hi_sat = guess_cps
        m = s.model()
        if datetime.now() >= last_sat_time + p.sat_time:
            last_sat_time = datetime.now()
            print_details(m)
    elif result == unsat:
        lo_unsat = guess_cps
        search_has_failed = True
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.
    elif result == unknown:
        lo_unknown = guess_cps
        search_has_failed = True
        s.pop() # Restore state (i.e. Remove guess constraint)
                # Only remove guess constraint when it can't be attained, not when sat.
    sys.stdout = sys.__stdout__

    # s.pop() # Restore state (i.e. Remove guess constraint)

if last_was_update:
    print("") # Print newline
print("---------------------------------------")
print(f"Sat: {hi_sat:.4f}, Unknown: {lo_unknown:.4f}, Unsat: {lo_unsat:.4f}")
print(f"Total Time: {datetime.now() - setupTime}")
print("---------------------------------------")

sys.stdout = f
print_details(m)
sys.stdout = sys.__stdout__
f.close()

print_details(m)
# ******************************************************
# TODO: Convert SMT solver output to configuration file.
# ******************************************************