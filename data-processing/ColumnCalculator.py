class ColumnCalculator:
    def __init__(self, total_length, well_radius, col_size, MF):
        self.total_length = total_length
        self.well_radius = well_radius
        self.col_size = col_size
        self.MF = MF

    def calculate_columns(self):
        # Initialize variables
        ncol = 1  # Start with one column
        delr = [self.well_radius]  # Initialize with the well radius
        col_size = self.col_size

        # Calculate the column widths based on the multiplier
        current_length = self.well_radius
        while current_length < self.total_length:
            current_length += col_size * self.MF
            if current_length < self.total_length:
                ncol += 1
                delr.append(col_size)
                col_size = col_size * self.MF
            else:
                remaining_length = self.total_length - sum(delr)
                if remaining_length > 0:
                    delr[-1] += remaining_length
                break
        

        # Calculate the distance from the well
        cumulative_distances = [0]  # Initialize with zero for the first column
        for i in range(ncol):
            cumulative_distances.append(cumulative_distances[-1] + delr[i])

        # Initialize the list for centroids
        col_centroids = []

        # Calculate centroids by averaging consecutive distances
        for i in range(ncol):
            col_centroid = (cumulative_distances[i] + cumulative_distances[i + 1]) / 2
            col_centroids.append(col_centroid)

        return delr, cumulative_distances, col_centroids, ncol

