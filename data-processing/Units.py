class UnitConverter:
    def __init__(self):
        # Define conversion factors for the specific units you need
        self.ft_to_m = 0.3048  # Feet to meters
        self.inch_to_m = 0.0254  # Inches to meters
        self.day_to_sec = 86400  # Seconds to days
        self.min_to_sec = 60  # Minutes to seconds
        self.hr_to_sec = 3600  # Hours to seconds
        self.cubic_m_per_hour_to_cubic_m_per_sec_factor = 3600.0  # Convert m³/hr to m³/day
        self.m_per_day_to_m_per_sec_factor = 86400.0  # Convert m/day to m/sec

    def feet_to_meters(self, value):
        return value * self.ft_to_m

    def inches_to_meters(self, value):
        return value * self.inch_to_m

    def days_to_sec(self, value):
        return value * self.day_to_sec

    def minutes_to_sec(self, value):
        return value * self.min_to_sec

    def hours_to_sec(self, value):
        return value * self.hr_to_sec

    def cubic_m_per_hour_to_cubic_m_per_sec(self, value):
        return value / self.cubic_m_per_hour_to_cubic_m_per_sec_factor

    def meters_per_day_to_meters_per_sec(self, value):
        return value / self.m_per_day_to_m_per_sec_factor
