#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Tell Cozmo to find a cube, and then drive up to it

This is a test / example usage of the robot.go_to_object call which creates a
GoToObject action, that can be used to drive within a given distance of an
object (e.g. a LightCube).
'''

import asyncio
from random import *
import cozmo
from cozmo.util import degrees, distance_mm
import time

min_num_objects = 1
forward_speed = 50
rotation_speed = 25


def find_cubes(robot):
    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    robot.say_text('where are you my love i cant seem to find you')
    cubes = robot.world.wait_until_observe_num_objects(num=min_num_objects, object_type=cozmo.objects.LightCube,
                                                       timeout=10)
    robot.set_all_backpack_lights(cozmo.lights.red_light)
    lookaround.stop()

    return cubes


def find_love(robot):
    cubes = find_cubes(robot)
    while len(cubes) < min_num_objects:
        robot.play_anim_trigger(cozmo.anim.Triggers.MajorFail).wait_for_completed()
        cubes = find_cubes(robot)

    min_dst, targ = 100000, None
    for cube in cubes:
        translation = robot.pose - cube.pose
        dst = translation.position.x ** 2 + translation.position.y ** 2
        if dst < min_dst:
            min_dst, targ = dst, cube

    if targ:
        robot.set_all_backpack_lights(cozmo.lights.off_light)
        action = robot.go_to_object(targ, distance_mm(80.0))
        action.wait_for_completed()
        direction = 0 if randint(0, 1) == 0 else 1  # Direciton flag 0: left 1:right
        seconds = randint(5, 20)

        if direction == 0:
            robot.turn_in_place(degrees(90)).wait_for_completed()
            robot.drive_wheels(forward_speed, rotation_speed)
            robot.set_all_backpack_lights(cozmo.lights.green_light)
        else:
            robot.turn_in_place(degrees(-90)).wait_for_completed()
            robot.drive_wheels(rotation_speed, forward_speed)
            robot.set_all_backpack_lights(cozmo.lights.green_light)

        robot.say_text('yaay  I love you so much')
        # Wait until the robot spins around the cube
        time.sleep(seconds)
        robot.play_anim_trigger(cozmo.anim.Triggers.MajorWin).wait_for_completed()

        if seconds < 8:
            robot.say_text('ooh that was too short see you later')

        # Random direction
        speed = randint(30, 100)
        robot.set_all_backpack_lights(cozmo.lights.blue_light)
        robot.drive_wheels(speed, -1 * speed)
        time.sleep(randint(2, 5))  # Wait until new direction found
        robot.drive_straight(randint(50, 100), randint(50, 100)).wait_for_completed()
        robot.set_all_backpack_lights(cozmo.lights.off_light)


def cube_dance(robot: cozmo.robot.Robot):
    '''Find cubes and rotate around them'''

    # Move lift down and tilt the head up
    robot.move_lift(-3)
    robot.set_head_angle(degrees(0)).wait_for_completed()
    while True:
        find_love(robot)


cozmo.run_program(cube_dance)
