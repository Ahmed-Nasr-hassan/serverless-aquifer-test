from scipy.interpolate import interp1d
import numpy as np
import pandas as pd

class DrawdownInterpolation:
    def __init__(self, observed_time, observed_DD, simulated_times, simulated_drawdowns,analysis_period,pumping_end_time):
        self.observed_time = observed_time
        self.observed_DD = observed_DD
        self.simulated_times = simulated_times
        self.simulated_drawdowns = simulated_drawdowns
        self.interpolated_times = None
        self.interpolated_observed_drawdown = None
        self.interpolated_simulated_drawdown = None
        self.pumping_end_time=pumping_end_time
        self.analysis_period=analysis_period

    def interpolate_to_smallest_time_step(self):
        # Determine the smallest time step in observed data for interpolation
        smallest_time_step = np.diff(self.observed_time).min()
        self.interpolated_times = np.arange(self.observed_time[0], self.observed_time[-1] + smallest_time_step, smallest_time_step)
        self.interpolated_observed_drawdown = interp1d(self.observed_time, self.observed_DD, kind='linear', bounds_error=False, fill_value='extrapolate')(self.interpolated_times)

    def interpolate_simulated_to_observed(self):
        if self.analysis_period == "Recovery Only":
            recovery_time=[]
            for t in self.simulated_times:
                recovery_time.append(t+self.pumping_end_time)
            self.interpolated_simulated_drawdown = interp1d(recovery_time, self.simulated_drawdowns, kind='linear', bounds_error=False, fill_value='extrapolate')(self.interpolated_times)
        else:
            self.interpolated_simulated_drawdown = interp1d(self.simulated_times, self.simulated_drawdowns, kind='linear', bounds_error=False, fill_value='extrapolate')(self.interpolated_times)

    def calculate_rmse(self):
        # Calculate the RMSE between interpolated observed and simulated drawdowns
        valid_indices = ~np.isnan(self.interpolated_simulated_drawdown)
        errors = self.interpolated_observed_drawdown[valid_indices] - self.interpolated_simulated_drawdown[valid_indices]
        rmse = np.sqrt(np.mean(errors ** 2))
        return rmse

    
    def calculate_total_residual_error(self):
        # Calculate the total absolute residual error between interpolated observed and simulated drawdowns
        valid_indices = ~np.isnan(self.interpolated_simulated_drawdown)
        residual_errors = np.abs(self.interpolated_observed_drawdown[valid_indices] - self.interpolated_simulated_drawdown[valid_indices])
        return np.sum(residual_errors)
    
    def save_results_to_excel(self, output_excel_path):
        if self.interpolated_times is None or self.interpolated_observed_drawdown is None or self.interpolated_simulated_drawdown is None:
            raise ValueError("Interpolation has not been performed yet. Call the interpolation methods first.")
        results_df = pd.DataFrame({
            "Time (sec)": self.interpolated_times,
            "Observed_DD (m)": self.interpolated_observed_drawdown,
            "Simulated_DD (m)": self.interpolated_simulated_drawdown
        })
        results_df.to_excel(output_excel_path, index=False)
    
