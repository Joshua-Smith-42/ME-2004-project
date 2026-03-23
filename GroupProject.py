from __future__ import annotations

from typing import List, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt

import numpy as np

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
        return max(self.downforces)
    
race_track = Track([
    Segment(defined_on=(0,   300),  curvature=80),
    Segment(defined_on=(300, 600),  curvature=16),
    Segment(defined_on=(600, 1000), curvature=50),
])

positions = np.arange(1,999,10)

racecar = Car(
    mass_kg=700,
    friction_coeffecient=0.6,
    track=race_track,
    positions=positions,
)

downforce = racecar.calculate_downforce()
plt.plot(positions, racecar.velocities)
plt.plot(positions, racecar.accelerations)
plt.plot(positions, racecar.downforces)
print(f"Peak downforce required: {downforce:.1f} N")