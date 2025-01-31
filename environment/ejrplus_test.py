from main import *

data = find_data('./environment', False)

ejr_violations = []
counter = 0
for path in data:
    instance, profile = parse(path, 1)
    
    instance, profile = to_1d(instance, profile,0)
    counter += 1
    print("-----------------------------------")
    print(path)
    print(f"Projects {len(instance)}")
    print(f"Votes: {len(profile)}")
    print(f"Instance {counter} of {len(data)}")
    print("-----------------------------------")
    
    greedy_output = pbr.greedy_utilitarian_welfare(instance, profile, Cost_Sat)
    
    violations, _ = strong_ejr_plus_violations(instance, profile, greedy_output, Cost_Sat, True)
    
    ejr_violations.append(violations)
    

print(np.mean(ejr_violations))
    
    