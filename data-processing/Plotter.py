import matplotlib.pyplot as plt
import flopy.utils
import pandas as pd
import numpy as np
from Units import UnitConverter
converter = UnitConverter()

class ObservedVsSimulatedPlotter:
    def __init__(self, head_file_path, screen_layer_indices, obs_id, str_hd, obs_path, col_centroids, analysis_period, pumping_end_time, col_length,workspace):
        self.head_file_path = head_file_path
        self.screen_layer_indices = screen_layer_indices
        self.obs_id = obs_id
        self.obs_path = obs_path
        self.obs_DD = []  # Initialize as empty lists
        self.observed_DD = []
        self.observed_time = []
        self.distance = col_centroids
        self.avg_head = []  # List to store average head values
        self.analysis_period = analysis_period
        self.pumping_end_time=pumping_end_time
        self.workspace = workspace
        # Load the heads data from the head file
        head_file = flopy.utils.HeadFile(self.head_file_path)
        self.times = head_file.get_times()
    
        # Initialize a list to store drawdown data for each layer
        self.drawdown_curves = [[] for _ in range(len(self.screen_layer_indices))]
        self.col_length=col_length
        
        # Adjust for dynamic starting heads
        self.starting_heads = str_hd  # This assumes str_hd is a numeric value representing the starting head.
           
        for time_step in self.times:
            head_data = head_file.get_data(totim=time_step)
            
            # Extract the head values for the specified observation point and all selected layers
            head_at_obs = [head_data[lay, 0, self.obs_id] for lay in self.screen_layer_indices]
            
            # Calculate drawdown for each layer and store it in the corresponding list
            for i, head_value in enumerate(head_at_obs):
                if isinstance(self.starting_heads, np.ndarray):
                    # Dynamic starting head for "Recovery Only" scenario
                    starting_head_for_layer = self.starting_heads  # Adjust indexing based on your data structure
                    drawdown = starting_head_for_layer - head_value
                else:
                    # Static starting head for other scenarios
                    drawdown = self.starting_heads - head_value
                self.drawdown_curves[i].append(drawdown)

                
            # Calculate and store the average drawdown for all layers
            average_drawdown = sum(self.drawdown_curves[i][-1] for i in range(len(self.screen_layer_indices))) / len(self.screen_layer_indices)
            self.avg_head.append(average_drawdown)
            
            # Read real observed data
            # Read the CSV file into a DataFrame
            df = pd.read_csv(self.obs_path)
        
            # Extract the time and drawdown (DD) columns
            obs_time_series = df[["Time", "DD"]].values.tolist()
            self.observed_time = [converter.minutes_to_sec(row[0]) for row in obs_time_series]
            self.observed_DD = [row[1] for row in obs_time_series]
        
    
    def plot_obs_simulated(self):
        if self.analysis_period == "Pumping + Recovery":
            # Plot Observed Curve
            plt.plot(self.observed_time, self.observed_DD, label="Observed Data", linestyle='--', color='k')
            
            # Plot Average simulated drawdown
            plt.plot(self.times, self.avg_head, label="Simulated Data", linestyle='-', color='r')
            
            plt.xlabel("Time (seconds)")
            plt.ylabel("Drawdown (meters)")
            plt.title("Drawdown of Obsrved VS Simulated")
            plt.legend()
            plt.grid(True)
            plt.show()
        elif self.analysis_period == "Pumping Only":
            # Filter or truncate time and drawdown data to the pumping period only
            # Pseudo-code for filtering:
            # Assume self.pumping_end_time marks the end of the pumping period
            observed_time_pumping = [t for t in self.observed_time if t <= self.pumping_end_time]
            observed_DD_pumping = [dd for t, dd in zip(self.observed_time, self.observed_DD) if t <= self.pumping_end_time]
            simulated_time_pumping = [t for t in self.times if t <= self.pumping_end_time]
            avg_head_pumping = [head for t, head in zip(self.times, self.avg_head) if t <= self.pumping_end_time]
            
            # Plotting logic similar to above but using the filtered/truncated data
            plt.plot(observed_time_pumping, observed_DD_pumping, label="Observed Data", linestyle='--', color='k')
            plt.plot(simulated_time_pumping, avg_head_pumping, label="Simulated Data", linestyle='-', color='r')
            plt.xlabel("Time (seconds)")
            plt.ylabel("Drawdown (meters)")
            plt.title("Drawdown of Observed VS Simulated (Pumping Only)")
            plt.legend()
            plt.grid(True)
            plt.show()
            
        elif self.analysis_period == "Recovery Only":
            # Filter or truncate time and drawdown data to the recovery period only
            # Similar logic to "Pumping Only" but adjust for the recovery period
            recovery_time=[]
            for t in self.times:
                recovery_time.append(t+self.pumping_end_time)
            observed_time_recovery = [t for t in self.observed_time if t > self.pumping_end_time]
            observed_DD_recovery = [dd for t, dd in zip(self.observed_time, self.observed_DD) if t > self.pumping_end_time]
            simulated_time_recovery = recovery_time
            avg_head_recovery = [head for t, head in zip(recovery_time, self.avg_head) if t > self.pumping_end_time]
            
            # Plotting logic for recovery period
            plt.plot(observed_time_recovery, observed_DD_recovery, label="Observed Data", linestyle='--', color='k')
            plt.plot(simulated_time_recovery, avg_head_recovery, label="Simulated Data", linestyle='-', color='r')
            plt.xlabel("Time (seconds)")
            plt.ylabel("Drawdown (meters)")
            plt.title("Drawdown of Observed VS Simulated (Recovery Only)")
            plt.legend()
            plt.grid(True)
            plt.show()
    
    def get_obs_DD(self):
        return self.avg_head, self.observed_DD, self.observed_time

    def plot_avg_head_vs_distance(self):
        # Load the heads data from the head file
        head_file = flopy.utils.HeadFile(self.head_file_path)

        last_time_step = min(head_file.get_times(), key= lambda x:abs(self.pumping_end_time-x))
    
        # Initialize a list to store head data for all columns
        #head_at_depth = [[] for _ in self.screen_layer_indices]
        head_at_depth=[]
        for lay in self.screen_layer_indices:
            # Extract the flows at the last time step for the specified layer
            head_data = head_file.get_data(totim=last_time_step)
            head_values = head_data[lay, 0, :]  # Get head values for all cells in the layer
    
            # Store the head values for the layer in the list
            for i in range(len(head_values)):
                if i >= len(head_at_depth):
                    head_at_depth.append([head_values[i]])
                else:
                    head_at_depth[i].append(head_values[i])
    
        # Calculate the average head vertically for each column
        self.avg_head_at_depth = [sum(column) / len(column) for column in head_at_depth]

        # Create a time series plot of average head versus distance from the well (column 0)
        plt.figure(figsize=(8, 6))
        plt.semilogx(self.distance, self.avg_head_at_depth, label="Average Head vs. Distance", linestyle='-', color='b')
    
        plt.xlabel("Distance from Well")
        plt.ylabel("Average Head (meters)")
        plt.title("Average Head vs. Distance")
        plt.grid(True)
        plt.show()
        
        return self.avg_head_at_depth
    
    def save_avg_head_vs_distance_to_excel(self, filepath):
        # Prepare the data as a dictionary
        data = {
            "Distance from Well (m)": self.distance,
            "Average Head (m)": self.avg_head_at_depth
        }
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(data)
        # Save the DataFrame to an Excel file
        df.to_excel(filepath, index=False)
        print(f"Average Head vs. Distance data saved to {filepath}")

    def radius_influence(self, threshold=0.2):
        distance_at_starting_head = None  # Initialize with a default value, such as None or an appropriate number
        for i, head in enumerate(self.avg_head_at_depth):
            if abs(self.starting_heads - head) < threshold:
                distance_at_starting_head = self.distance[i]
                break
        if distance_at_starting_head is None:
            distance_at_starting_head = self.col_length
        return distance_at_starting_head

        

