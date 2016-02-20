import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
import math


gravity = 9.8

class Tandem:
    def __init__(self, human_output, watt_hours, mass):
        self.watt_hours = watt_hours
        self.position = 50.0
        self.speed = 1
        self.human_output = human_output
        self.mass = mass

    def GetPowerOutput(self, power_requested, speed):
        prop_eff = 0.8
        if power_requested >= 0:
            self.watt_hours -= power_requested * (1.0 / prop_eff) / 3600
            return power_requested + self.human_output
        else:	# power_requested < 0
            self.watt_hours -= prop_eff * power_requested / 3600
            return power_requested + self.human_output

    def GetPowerLost(self, speed):
        windage_coef = 2.0
        friction_coef = 0.59
        aero_coef = .3
        windage_loss = windage_coef * speed
        friction_loss = friction_coef * speed
        aero_loss = aero_coef * speed * speed
        return (windage_loss + friction_loss + aero_loss) * speed

    def GetForceDelta(self, slope):
        return self.mass * gravity * np.sin(slope)

    def GetAcceleration(self, slope):
        power_requested = self.GetPowerRequested(slope)
        force_output = (self.GetPowerOutput(power_requested, self.speed) - self.GetPowerLost(self.speed)) / self.speed - self.GetForceDelta(slope)
        return force_output / (self.mass)

    def GetPowerRequested(self, slope):
        if slope < -.05 and self.speed > 8:
            return -1500
        if slope < -.03 and self.speed > 5:
            return -700
        return slope * 3000.0 + 5400 * (slope) ** 2

class Map:
    def __init__(self, distances, altitudes):
        self.distances = distances
        self.altitudes = altitudes
        self.distance = 195000


class Optimizer:
    def __init__(self, tandem):
        self.tandem = tandem


    def RunSimulation(self, map):
        time = 0
        slope = 0.0
        data_point = 0

        speeds = []
        positions = []
        slopes = []
        times = []
        powers = []
        while True:
            while tandem.position > map.distances[data_point]:
                data_point += 1
            rise = float(map.altitudes[data_point + 20] - map.altitudes[data_point])
            run = float(map.distances[data_point + 20] - map.distances[data_point])
            slope = np.arctan2(rise, run)
            if slope > .2:
                slope = .2
            if slope < -.2:
                slope = -.2
            time += 1

            if True:
                speeds.append(tandem.speed)
                positions.append(tandem.position)
                slopes.append(slope)
                times.append(time)
                powers.append(tandem.GetPowerRequested(slope))
                
            tandem.position += tandem.speed
            if tandem.position > map.distance:
                print 'slope = ', slope, '\n' 
                print 'Time = ', (time / 60) /60, ':', (time / 60) % 60 , '\n'
                print 'speed = ', tandem.speed, '\n'
                print 'position = ', tandem.position, '\n'
                print 'pos = ', map.distances[data_point], '\n'
                print 'Battery life remaining: ', tandem.watt_hours, ' watt hours\n'
                print 'acceleration = ', tandem.GetAcceleration(slope)                
                break
            tandem.speed += tandem.GetAcceleration(slope) 

        #plt.plot(times, speeds)
        #plt.plot(times, powers)
        #plt.show()
        
        
        fig = plt.figure(figsize=(15,6),dpi=80)
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2, sharex = ax1)
        
        ax1.plot(times, speeds)
        ax2.plot(times, powers) 
        plt.show()

    def CreateMap(self, path_to_file):
        with open(path_to_file) as f:
            reader = csv.reader(f, delimiter="\t")
            d = list(reader)
        meters_per_deg_lat = 111000
        meters_per_deg_long = 85000
        
        dist = 0
        dist_data = []
        alt_data = []
        for i in range(len(d)-1):
            horizontal_meters = (float(d[i+1][1]) - float(d[i][1])) * meters_per_deg_lat
            vertical_meters = (float(d[i+1][2]) - float(d[i][2])) * meters_per_deg_long
            dist += ( math.sqrt(horizontal_meters ** 2 + vertical_meters ** 2) )
            dist_data.append(dist)
            alt_data.append(float(d[i][3]) - 1845)
        self.map = Map(dist_data, alt_data)


tandem = Tandem(350.0, 1000.0, 190.0)
optimizer = Optimizer(tandem)

optimizer.CreateMap('death_ride.txt')
optimizer.RunSimulation(optimizer.map)






