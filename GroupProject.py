from __future__ import annotations

from typing import List, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt

import numpy as np

plt.clf
plt.close


def scale_array(arr, min, max):
    output_range = max-min
    input_range = arr.max()-arr.min()
    scaled_array = ((arr-arr.min())/input_range)*output_range + min
    return scaled_array

@dataclass
class Segment:
    defined_on: Tuple[int, int]
    """[start, stop) for segment"""
    curvature: float = 0.0
    """curvature of the segment"""

class Track:
    GRAVITY = 9.81
    
    def __init__(self, segments: List[Segment] = []):
        self.path = segments

    def expand_track(self,segments: List[Segment]) -> Track:
        self.path += segments
        return self

    def calculate_curvature(self, position: float):
        for segment in self.path:
            (start,stop) = segment.defined_on
            if start <= position < stop:
                return segment.curvature
        raise ValueError('position not defined on curve')

class Car:
    def __init__(self, mass_kg: float, friction_coeffecient:float, track:Track, positions):
        self.downforces = []
        self.mass = mass_kg
        self.friction_coeffecient: float = friction_coeffecient
        self.track = track
        self.positions = positions
        self.velocities = np.gradient(positions)
        tangential_accels = np.array(np.gradient(self.velocities))
        normal_accels = np.array([])
        for index, position in enumerate(positions):
            curvature = track.calculate_curvature(position)
            normal_accel = self.velocities[index]**2/curvature
            normal_accels = np.append(normal_accels, normal_accel)
        self.accelerations = np.sqrt(normal_accels**2 + tangential_accels**2)

    def calculate_downforce(self) -> float:
        gravitational_friction_force = self.track.GRAVITY*self.mass*self.friction_coeffecient
        self.downforces = [accel * self.mass - gravitational_friction_force for accel in self.accelerations]
        max_downforce = max(self.downforces)
        if(max_downforce > 0):
            return max_downforce
        else:
            return 0.00
    
race_track = Track([
    Segment(defined_on=(0,   300),  curvature=80),
    Segment(defined_on=(300, 600),  curvature=16),
    Segment(defined_on=(600, 1000), curvature=50),
])

positionsConstantV = np.arange(1,999,10)

times = np.arange(1,999,10)
speedProfile = 500 - ((times-500)**2)/500  #makes a list of velocities that peaks halfway through the track
positionsVariableV = np.cumsum(speedProfile)
positionsVariableV = scale_array(positionsVariableV,0,999) #ensures posistions are within range of track

carConstantV = Car(
    mass_kg = 700,
    friction_coeffecient = 0.6,
    track = race_track,
    positions = positionsConstantV
)

carVariableV = Car(
    mass_kg = 700,
    friction_coeffecient = 0.6,
    track = race_track,
    positions = positionsVariableV
) 



downforce1 = carConstantV.calculate_downforce()
downforce2 = carVariableV.calculate_downforce()
plt.plot(positionsConstantV, carConstantV.velocities)
plt.plot(positionsConstantV, carConstantV.accelerations)
plt.plot(positionsVariableV, carVariableV.velocities)
plt.plot(positionsVariableV, carVariableV.accelerations)
print(f"Peak downforce required for constant v car: {downforce1:.1f} N")
print(f"Peak downforce required for variable v car: {downforce2:.1f} N")
plt.show()