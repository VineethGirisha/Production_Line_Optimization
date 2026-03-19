import simpy
import random
import pandas as pd

# --- Simulation Parameters ---
RANDOM_SEED = 42
SIMULATION_TIME = 1000  # minutes
PART_INTERARRIVAL_TIME = 5  # A new part arrives every 5 minutes
MACHINE_PROCESS_TIMES = {
    'Machine_1': 4,
    'Machine_2': 6,  # This machine is the bottleneck
    'Machine_3': 3
}
data = {
    'Part': [],
    'Machine': [],
    'Time': []
}

def part_source(env, interarrival_time, machine1, machine2):
    """Generates parts at a fixed rate."""
    part_id = 0
    while True:
        yield env.timeout(interarrival_time)
        part_id += 1
        # print(f"{env.now:.2f}: Part {part_id} created.")
        env.process(machine_process(env, f"Part {part_id}", machine1, 'Machine_1'))
        env.process(machine_process(env, f"Part {part_id}", machine2, 'Machine_2'))



def machine_process(env, part_name, machine, machine_name):
    """Simulates a part going through a machine."""
    with machine.request() as req:
        # print(f"{env.now:.2f}: {part_name} arrives at {machine_name}.")
        yield req
        # print(f"{env.now:.2f}: {part_name} starts processing at {machine_name}.")
        yield env.timeout(MACHINE_PROCESS_TIMES[machine_name])
        # print(f"{env.now:.2f}: {part_name} finishes processing at {machine_name}.")
        data['Part'].append(part_name)
        data['Machine'].append(machine_name)
        data['Time'].append(env.now)


# --- Simulation Setup ---
print("--- Production Line Simulation ---")
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Create the machines (resources)
machine1 = simpy.Resource(env, capacity=1)
machine2 = simpy.Resource(env, capacity=1)
machine3 = simpy.Resource(env, capacity=1)

# Start the part source process
env.process(part_source(env, PART_INTERARRIVAL_TIME, machine1, machine2))

# --- Run the Simulation ---
env.run(until=SIMULATION_TIME)
print("--- Simulation Finished ---")


df = pd.DataFrame(data)
# print(df) 


# Analyze the results
print("\n--- Analysis ---")
# Calculate average processing time for each machine
for machine in MACHINE_PROCESS_TIMES.keys():
    machine_data = df[df['Machine'] == machine]
    if not machine_data.empty:
        avg_time = machine_data['Time'].mean()
        print(f"Average processing time at {machine}: {avg_time:.2f} minutes")
    else:
        print(f"No data for {machine}")

#Calculate total parts processed
total_parts = df['Part'].nunique()
print(f"Total parts processed: {total_parts}")

#Calculate total time
total_time = df['Time'].max()
print(f"Total time taken: {total_time:.2f} minutes")

# Calculate bottleneck machine
bottleneck_machine = max(MACHINE_PROCESS_TIMES, key=MACHINE_PROCESS_TIMES.get)
print(f"Bottleneck machine: {bottleneck_machine} with processing time of {MACHINE_PROCESS_TIMES[bottleneck_machine]} minutes")

