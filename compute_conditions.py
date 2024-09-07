import math

def speed_of_sound_at_altitude(feet):
    # Constants
    gamma = 1.4  # Adiabatic index for air
    R = 287.05  # Specific gas constant for air in J/(kg*K)
    
    # Conversion factors
    feet_to_meters = 0.3048
    
    # Temperature in Kelvin at sea level
    T0 = 288.15  # K (15°C at sea level)
    
    # Lapse rate (rate of temperature decrease with altitude)
    lapse_rate = -0.00649  # K/m
    
    # Altitude in meters
    altitude_m = feet * feet_to_meters
    
    # Tropopause altitude (in meters) where temperature becomes constant
    tropopause_altitude_m = 11000  # 36,089 feet
    
    if altitude_m <= tropopause_altitude_m:
        # Calculate temperature at given altitude in the troposphere
        T = T0 + lapse_rate * altitude_m
    else:
        # Above the tropopause, temperature is constant at -56.5°C or 216.65K
        T = 216.65
    
    # Calculate the speed of sound (m/s)
    speed_of_sound = (gamma * R * T) ** 0.5
    
    # Return speed of sound and temperature
    return speed_of_sound, T

def air_density_at_altitude(feet, temperature):
    # Constants
    R = 287.05  # Specific gas constant for air in J/(kg*K)
    g = 9.80665  # Gravitational acceleration in m/s²
    P0 = 101325  # Sea level standard atmospheric pressure in Pa
    T0 = 288.15  # Sea level standard temperature in K
    L = -0.00649  # Temperature lapse rate in K/m
    feet_to_meters = 0.3048
    
    # Altitude in meters
    altitude_m = feet * feet_to_meters
    
    # Pressure calculation using barometric formula for the troposphere
    if altitude_m <= 11000:
        P = P0 * (1 + (L * altitude_m) / T0) ** (-g / (R * L))
    else:
        # For altitudes above 11,000 meters, a simplified approach is used.
        P = 22632.1  # Constant pressure in Pa at 11,000 meters
    
    # Calculate air density using the ideal gas law
    rho = P / (R * temperature)
    
    return rho, P

def dynamic_viscosity(temperature):
    # Sutherland's law constants
    mu_0 = 1.716e-5  # Reference viscosity at T0 = 273.15 K in Pa·s
    T0 = 273.15  # Reference temperature in K
    S = 110.4  # Sutherland constant in K
    
    # Calculate viscosity using Sutherland's law
    mu = mu_0 * ((T0 + S) / (temperature + S)) * (temperature / T0) ** (3 / 2)
    
    return mu

def flight_speed(mach_number, altitude_feet):
    # Get the speed of sound at the given altitude
    sound_speed, temperature = speed_of_sound_at_altitude(altitude_feet)
    
    # Compute flight speed using Mach number
    flight_speed = mach_number * sound_speed
    
    # Return flight speed in meters per second and temperature
    return flight_speed

def reynolds_number(mach_number, altitude_feet, length_scale):
    # Get flight speed and temperature at the altitude
    flight_speed_at_mach = flight_speed(mach_number, altitude_feet)
    sound_speed, temperature = speed_of_sound_at_altitude(altitude_feet)
    
    # Get air density and pressure at the altitude
    density, pressure = air_density_at_altitude(altitude_feet, temperature)
    
    # Get dynamic viscosity at the altitude
    viscosity = dynamic_viscosity(temperature)
    
    # Calculate Reynolds number
    reynolds = (density * flight_speed_at_mach * length_scale) / viscosity
    
    return reynolds

def atmospheric_pressure_at_altitude(feet):
    # Get temperature and pressure at the altitude
    sound_speed, temperature = speed_of_sound_at_altitude(feet)
    density, pressure = air_density_at_altitude(feet, temperature)
    
    return pressure

# Example usage
altitude_feet = 10000  # Example altitude in feet
mach_number = 0.85     # Example Mach number
length_scale = 4       # Example length scale in meters

# Calculate Reynolds number
reynolds = reynolds_number(mach_number, altitude_feet, length_scale)

# Calculate atmospheric pressure
pressure = atmospheric_pressure_at_altitude(altitude_feet)

print(f"The Reynolds number at {altitude_feet} feet, Mach {mach_number}, and a length scale of {length_scale} meters is {reynolds:.2e}.")
print(f"The atmospheric pressure at {altitude_feet} feet is {pressure:.2f} Pa.")
