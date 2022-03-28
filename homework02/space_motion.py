"""
Write a program that simulates the motion of objects in space. (stars/planets/satellites etc.)
Any two objects are attracted to each other by the force of gravitation which can be calculated using the following formula:
(The formula is written in TeX, you can use free online tools such as latexbase.com to view it)

$$\vec{F_{ij}} = \frac{G m_i m_j}{r_{ij}^2} \frac{\vec{r_{ij}}}{\|r_{ij}\|}.$$

The force that acts on an object $i$ can be calculated as the vector sum of all forces acting on the object.
In our case, we only need to account for the gravitational forces caused by other objects in the simulation.

$$\vec{F_i} = \sum_{j \neq i} \vec{F_{ij}}$$

You are required to write four functions:

- "calculate_force" will calculate the force acting on an object based on other objects' current state in the simulation.
- "update_space_object" will calculate new coordinates and speed for an object based on the return value of calculate_force, the timestep and the object's current state.
- "update_motion" will simulate the motion of all objects for a single timestep (the size of the timestep is passed in)
- "simulate_motion" is a generator function that yields a dictionary with object names as keys and tuples of (x,y) coordinates as values. Each iteration progresses the simulation by the defined timestep.

More precise descriptions of each function's required functionality can be found in the code below.
For examples of function calls, check the test script `test_space_motion.py`.

You also have to write a parametrized decorator "logging" that will measure how many times a function
has been called and how long it ran. The information should be printed to standard output in this form:
"function_name - number_of_calls - time units\n".
The decorator should have an optional "units" parameter for specifying the output format (default is 'ms').
The decorator should accept 'ns', 'us', 'ms', 's', 'min', 'h' and 'days' as values for the "units" parameter.
The time should be printed as a float number with exactly 3 decimal places (eg. 0.042).

A couple more things:

- Use scientific notation (SI units).
- Do not bother with optimisation; just write something that works! (That is a nice thing to hear for once, isn't it?)
- Any function that takes multiple space objects should take them as separately named tuples, not as a list of them.

    f(5, earth, moon, mars, sun) - GOOD
    f(5, (earth, moon, mars, sun)) - MUCH BAD

Good luck!
"""

import time  # measuring time
from collections import namedtuple
import math
import timeit

# Define universal gravitation constant
G = 6.67408e-11  # N-m2/kg2
SpaceObject = namedtuple('SpaceObject', 'name mass x y vx vy color')
Force = namedtuple('Force', 'fx fy')


def attraction(planet, other):
    other_x, other_y = other.x, other.y
    distance_x = other_x - planet.x
    distance_y = other_y - planet.y
    distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

    force = G * planet.mass * other.mass / distance**2
    theta = math.atan2(distance_y, distance_x)
    force_x = math.cos(theta) * force
    force_y = math.sin(theta) * force
    return force_x, force_y


def logging(unit='ms'):
    units = ['ns', 'us', 'ms', 's', 'min', 'h', 'days']
    multiples = [10**9, 10**6, 10**3, 1, 1/60, 1/3600, 1/3600/24]

    def decorator_wrapper(func):
        def wrapper(*args, **kwargs):
            wrapper.calls += 1
            time_0 = timeit.default_timer()
            ret = func(*args, **kwargs)
            time_1 = timeit.default_timer()
            func_time = (time_1 - time_0) * multiples[units.index(unit)]
            print(f"{func.__name__} - {wrapper.calls} - {format(func_time, '.3f')} {unit}")
            return ret
        wrapper.calls = 0
        return wrapper
    return decorator_wrapper


@logging(unit='ms')
def calculate_force(main_object, *others):
    # input: one of the space objects (indexed as i in below formulas),
    # other space objects (indexed as j, may be any number of them)
    # returns named tuple (see above) that represents x and y components of the gravitational force
    # calculate force (vector) for each pair (space_object, other_space_object):
    # |F_ij| = G*m_i*m_j/distance^2
    # F_x = |F_ij| * (other_object.x-space_object.x)/distance
    # analogous for F_y
    # for each coordinate (x, y) it sums force from all other space objects
    total_fx = total_fy = 0
    for planet in others:
        if main_object == planet:
            continue
        force_x, force_y = attraction(main_object, planet)
        total_fx += force_x
        total_fy += force_y
    force = Force(fx=total_fx, fy=total_fy)

    return force


@logging(unit='s')
def update_space_object(main_object, force=Force(0,0), timestep=1):
    # here we update coordinates and speed of the object based on the force that acts on it
    # input: space_object we want to update (evolve in time), force (from all other objects) that acts on it, size of timestep
    # returns: named tuple (see above) that contains updated coordinates and speed for given space_object
    # hint:
    # acceleration_x = force_x / mass
    # same for y
    # speed_change_x = acceleration_x * timestep
    # same for y
    # speed_new_x = speed_old_x + speed_change_x
    # same for y
    # x_final = x_old + speed_new_x * timestep

    total_fx = force.fx
    total_fy = force.fy
    x_vel = main_object.vx
    y_vel = main_object.vy
    x_pos = main_object.x
    y_pos = main_object.y

    x_vel += total_fx / main_object.mass * timestep
    y_vel += total_fy / main_object.mass * timestep

    x_pos += x_vel * timestep
    y_pos += y_vel * timestep

    space_object = SpaceObject(main_object.name, mass=main_object.mass, x=x_pos, y=y_pos, vx=x_vel, vy=y_vel, color=main_object.color)

    return space_object


@logging(unit='ms')
def update_motion(timestep, *planets):
    # input: timestep and space objects we want to simulate (as named tuples above)
    # returns: list or tuple with updated objects
    # hint:
    # iterate over space objects, for given space object calculate_force with function above, update

    updated_space_objects = []
    Pos = namedtuple('Pos', 'x y')
    for planet in planets:
        f = calculate_force(planet, planets)
        x = update_space_object(planet, f, timestep).x
        y = update_space_object(planet, f, timestep).y
        new_pos = Pos(x, y)
        updated_space_objects.append(new_pos)

    return updated_space_objects  # (named tuple with x and y)


@logging()
def simulate_motion(timestep, epochs, *planets):
    # generator that in every iteration yields dictionary with the name of the objects as a key and tuple of coordinates (x first, y second) as values
    # input size of the timestep, number of timesteps (integer), space objects (any number of them)"""
    pp = list(planets)
    pepe = pp
    new_dict = {}
    for planet in pp:
        new_dict[planet.name] = (0, 0)
    for i in range(epochs):
        for j, planet in enumerate(pp):
            f = calculate_force(planet, *tuple(pp))
            new_planet = update_space_object(planet, f, timestep)
            x = new_planet.x
            y = new_planet.y
            pp[j] = new_planet
            new_dict[planet.name] = (x, y)
        yield new_dict