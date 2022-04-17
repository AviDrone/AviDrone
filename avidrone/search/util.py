#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import math
import time

import numpy as np
from dronekit import (Command, LocationGlobal, LocationGlobalRelative,
                      VehicleMode, connect)

IS_VERBOSE = False  # for verbose command-line interface output
IS_TEST = False  # for running simulations

# DEFAULT PARAMETERS
MAGNITUDE = 1  # Distance the vehicle goes
ALTITUDE = 4  # Altitude of the flight path
DEGREES = 10  # Amount to rotate in yaw
DEGREE_ERROR = 2  # Number of degrees error for rotation
DISTANCE_ERROR = 0.35  # Error in distance before target reached
LAND_THRESHOLD = 2  # Error in distance before target reached
WINDOW_SIZE = 5  # Size of the gps window original: 5
FLIGHT_MODE = "GUIDED"  # for autonomous missions


class GpsData:
    def __init__(self, window_size):
        self.window_size = window_size
        self.gps_points = []
        self.distance = []

    def add_point(self, new_gps_point, new_distance):
        self.gps_points.insert(0, new_gps_point)
        del self.gps_points[self.window_size :]
        self.distance.insert(0, new_distance)
        del self.distance[self.window_size :]

    def get_minimum_index(self):
        minimum_dist_index = 0

        for i in range(0, len(self.distance)):
            if self.distance[i] < self.distance[minimum_dist_index]:
                minimum_dist_index = i
        return minimum_dist_index

    def purge_gps_window(self):
        self.gps_points.clear()
        self.distance.clear()


class Search:
    def __init__(self):
        global_frame = self.vehicle.location.global_frame
        global_location = LocationGlobal(new_lat, new_lon, original_location.alt)
        distance = (
            2
            * math.asin(
                math.sqrt(
                    (math.sin((lat_a - lat_b) / 2)) ** 2
                    + math.cos(lat_a)
                    * math.cos(lat_b)
                    * (math.sin((lon_a - lon_b) / 2)) ** 2
                )
            )
            * 1.113195e5
        )

    @staticmethod
    def get_location(original_location, d_north, d_east, d_alt=0):

        earth_radius = 6378137.0  # Radius of "spherical" earth
        # Coordinate offsets in radians
        d_lat = d_north / earth_radius
        d_lon = d_east / (
            earth_radius * math.cos(math.pi * original_location.lat / 180)
        )

        # New position in decimal degrees
        new_lat = original_location.lat + (d_lat * 180 / math.pi)
        new_lon = original_location.lon + (d_lon * 180 / math.pi)

        if original_location.alt:
            return LocationGlobal(new_lat, new_lon, original_location.alt)
        else:
            return LocationGlobal(new_lat, new_lon, d_alt)

    @staticmethod
    def get_distance(location_a, location_b):
        lat_a, lat_b = location_a.lat, location_b.lat
        lon_a, lon_b = location_a.lat, location_b.lat

        d_lat = lat_b - lat_a
        d_lon = lon_b - lon_a

        return math.sqrt(d_lat**2 + d_lon**2) * 1.113195e5

    def get_global_pos(self):
        return self.global_frame

    @staticmethod
    def read_transceiver():
        uav_pos = [2, 2, 2]  # TODO replace this with actual positions
        beacon_pos = [1, 1, 1]  # TODO replace this with actual positions
        return util.mock_beacon(uav_pos, beacon_pos)


class Mission:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Demonstrates basic mission operations."
        )
        parser.add_argument(
            "--connect",
            help="vehicle connection target string. If not specified, SITL automatically started and used.",
        )
        args = parser.parse_args()

        connection_string = args.connect

        # Start SITL if no connection string specified
        if not connection_string:
            sitl = dronekit_sitl.start_default()
            connection_string = sitl.connection_string()

        print("Connecting to vehicle on: %s", connection_string)
        self.vehicle = connect(connection_string, wait_ready=True)  # Connect to UAV
        self.original_yaw = self.vehicle.attitude.yaw
        self.heading = -1  # TODO get correct value
        self.relative = False

    def takeoff_to(self, altitude):
        print("-- Taking off to altitude (m): ", altitude)
        self.vehicle.simple_takeoff(altitude)

        while True:
            current_alt = self.vehicle.location.global_relative_frame.alt
            if current_alt >= altitude * 0.95:
                print("-- Reached ", altitude, "m")
                break
            time.sleep(1)

    def go_to_location(self, distance, angle):
        current_location = self.vehicle.location.global_frame
        target_location = Search.get_location(current_location, distance, angle)
        self.vehicle.simple_goto(target_location)

        loop_count = 0
        while self.vehicle.mode.name == "GUIDED":
            remaining_distance = Search.get_distance(
                self.vehicle.location.global_frame, target_location
            )
            print("Distance to target: ", remaining_distance)
            loop_count += 1
            if remaining_distance <= 0.35:
                print("Reached target")
                break
            elif loop_count >= 10:  # TODO experiment with this variable.
                print("Stuck, skipping target")
                break
            time.sleep(2)

    def simple_goto_wait(self, go_to_checkpoint):
        self.vehicle.simple_goto(go_to_checkpoint)
        distance = get_distance_metres(self.get_global_pos(), go_to_checkpoint)

        while distance >= DISTANCE_ERROR and self.vehicle.mode.name == "GUIDED":
            print(distance)
            distance = get_distance_metres(self.get_global_pos(), go_to_checkpoint)
            time.sleep(1)

        if self.vehicle.mode.name != "GUIDED":
            self.vehicle.simple_goto(self.vehicle.location.global_frame)
            print("Halting simple_go_to")

        print("Checkpoint reached")

    def wobble_wait(self):
        # make vehicle wait until the wobbling settles down before moving forward.
        heading_rad = self.heading * math.pi / 180

        target_yaw = self.original_yaw + cw * heading_rad

        while abs(target_yaw - self.vehicle.attitude.yaw) % math.pi > 0.01745 * DEGREE_ERROR:
            error_degree = abs(target_yaw - vehicle.attitude.yaw) % math.pi
            print("Turn error: ", error_degree)  # 1 degree
            time.sleep(0.25)

    def condition_yaw(self):
        heading = self.heading
        original_yaw = self.vehicle.attitude.yaw
        if relative:
            is_relative = 1  # yaw relative to direction of travel
        else:
            is_relative = 0  # yaw is an absolute angle

        if self.heading < 0:
            heading = abs(heading)
            cw = -1
        else:
            cw = 1

        msg = self.vehicle.message_factory.command_long_encode(
            0,  # target system
            0,  # target component
            self.mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
            0,  # confirmation
            heading,  # param 1, yaw in degrees
            0,  # param 2, yaw speed deg/s
            cw,  # param 3, direction -1 ccw, 1 cw
            is_relative,  # param 4, relative offset 1, absolute angle 0
            0,
            0,
            0,
        )  # param 5 ~ 7 not used
        self.vehicle.send_mavlink(msg)  # send command to vehicle
        Mission.wobble_wait(self)  # TODO apply condition to see if it needs to wait


class Vector:
    def __init__(self, V1, V2):
        self.V1 = np.asarray(V1)
        self.V2 = np.asarray(V2)

    @staticmethod
    def rotate_cloud(Points, V1, V2):
        # V1 is the current vector which the coordinate system is aligned to
        # V2 is the vector we want the system aligned to
        # Points is an (n,3) array of n points (x,y,z)
        V1 = np.asarray(V1)
        V2 = np.asarray(V2)

        # Normalize V1 and V2 in case they aren't already
        V1Len = (V1[0] ** 2 + V1[1] ** 2 + V1[2] ** 2) ** 0.5
        V2Len = (V2[0] ** 2 + V2[1] ** 2 + V2[2] ** 2) ** 0.5
        V1 = V1 / V1Len
        V2 = V2 / V2Len

        # Calculate the vector cross product
        V1V2Cross = np.cross(V1, V2)
        V1V2CrossNorm = (
            V1V2Cross[0] ** 2 + V1V2Cross[1] ** 2 + V1V2Cross[2] ** 2
        ) ** 0.5
        V1V2CrossNormalized = V1V2Cross / V1V2CrossNorm

        # Dot product
        V1V2Dot = np.dot(V1, V2)
        V1Norm = (V1[0] ** 2 + V1[1] ** 2 + V1[2] ** 2) ** 0.5
        V2Norm = (V2[0] ** 2 + V2[1] ** 2 + V2[2] ** 2) ** 0.5

        # angle between the vectors
        Theta = np.arccos(V1V2Dot / (V1Norm * V2Norm))
        print(Theta)

        # Using Rodriguez's rotation formula (wikipedia):
        e = V1V2CrossNormalized
        pts_rotated = np.empty((len(Points), 3))
        if np.size(Points) == 3:
            p = Points
            p_rotated = (
                np.cos(Theta) * p
                + np.sin(Theta) * (np.cross(e, p))
                + (1 - np.cos(Theta)) * np.dot(e, p) * e
            )
            pts_rotated[i] = p_rotated

        return pts_rotated

    @staticmethod
    def rotate_vector(vector, angle):
        # vector is the vector being rotated
        # angle is used to rotate vector and is given in degrees

        # Convert angle to radians
        Angle_Rad = np.radians(angle)

        # rotation matrix
        # See https://en.wikipedia.org/wiki/Rotation_matrix for more information
        r = np.array(
            (
                (np.cos(Angle_Rad), -np.sin(Angle_Rad)),
                (np.sin(Angle_Rad), np.cos(Angle_Rad)),
            )
        )

        # we only care about x and y, not z
        a_vector = (vector[0], vector[1])
        a_vector = np.asarray(a_vector)

        # vector after rotation
        rotated = r.dot(a_vector)
        # print(rotated)

        # return 3D vector
        NewVector = (rotated[0], rotated[1], vector[2])

        return NewVector

    @staticmethod
    def get_range(totalLength, dLength):
        return (totalLength / dLength) * 2


def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    new_lat = original_location.lat + (dLat * 180 / math.pi)
    new_lon = original_location.lon + (dLon * 180 / math.pi)
    return LocationGlobal(new_lat, new_lon, original_location.alt)


def get_location_metres_with_alt(original_location, dNorth, dEast, newAlt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)

    return LocationGlobal(newlat, newlon, newAlt)


def get_distance_metres(a_location1, a_location2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = a_location2.lat - a_location1.lat
    dlong = a_location2.lon - a_location1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5


def get_range(totalLength, dLength):
    return (totalLength / dLength) * 2
