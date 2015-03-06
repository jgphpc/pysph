"""A trivial example to demonstrate the inlet and outlet feature in 2D.

We first create three particle arrays, an "inlet", "fluid" and "outlet" in the
`create_particle` function. Initially there are no fluid and outlet particles.
A single row of inlet particles are created between (0.0, 0.0) to (0.0, 1.0),
i.e. along the y-axis with a u velocity = 0.25.

The inlet and outlet are created in the `create_inlet_outlet` function.  This
function is passed a dictionary of `{array_name:particle_array}`. An inlet
between (-0.4, 0.0) and (0.0, 1.0) is created by instantiating a
`SimpleInlet`.  The inlet first makes 4 copies of the inlet particle array
data and stacks them along the negative x-axis.  The `InletOutletStep` is used
to step all particles and simply moves the particles.  As particles leave
the inlet they are converted to fluid particles.

An outlet is also created in the region (0.5, 0.0), (1.0, 1.0) and as fluid
particles enter the outlet region, they are converted to outlet particles.  As
outlet particles leave the outlet they are removed from the simulation.

The following figure should make this clear.

               inlet       fluid       outlet
              ---------    --------    --------
             | * * * x |  |        |  |        |
     u       | * * * x |  |        |  |        |
    --->     | * * * x |  |        |  |        |
             | * * * x |  |        |  |        |
              --------     --------    --------

In the figure above, the 'x' are the initial inlet particles.  The '*' are the
copies of these.  The particles are moving to the right and as they do, new
fluid particles are added and as the fluid particles flow into the outlet they
are converted to the outlet particle array and at last as the particles leave
the outlet they are removed from the simulation.

This example can be run in parallel.

"""

import numpy as np

from pysph.base.kernels import CubicSpline
from pysph.base.utils import get_particle_array
from pysph.solver.application import Application
from pysph.solver.solver import Solver
from pysph.sph.integrator import PECIntegrator
from pysph.sph.simple_inlet_outlet import SimpleInlet, SimpleOutlet
from pysph.sph.integrator_step import InletOutletStep

def create_particles():
    # Note that you need to create the inlet and outlet arrays in this method.

    # Initially fluid has no particles -- these are generated by the inlet.
    fluid = get_particle_array(name='fluid')

    outlet = get_particle_array(name='outlet')

    # Setup the inlet particle array with just the particles we need at the
    # exit plane which is replicated by the inlet.
    dx = 0.1
    y = np.linspace(0, 1, 11)
    x = np.zeros_like(y)
    m = np.ones_like(x)*dx
    h = np.ones_like(x)*dx*1.5
    rho = np.ones_like(x)
    # Remember to set u otherwise the inlet particles won't move.
    u = np.ones_like(x)*0.25

    inlet = get_particle_array(name='inlet', x=x, y=y, m=m, h=h, u=u, rho=rho)

    return [inlet, fluid, outlet]

def create_inlet_outlet(particle_arrays):
    # particle_arrays is a dict {name: particle_array}
    fluid_pa = particle_arrays['fluid']
    inlet_pa = particle_arrays['inlet']
    outlet_pa = particle_arrays['outlet']

    # Create the inlet and outlets as described in the documentation.
    inlet = SimpleInlet(
        inlet_pa, fluid_pa, spacing=0.1, n=5, axis='x', xmin=-0.4, xmax=0.0,
        ymin=0.0, ymax=1.0
    )
    outlet = SimpleOutlet(
        outlet_pa, fluid_pa, xmin=0.5, xmax=1.0, ymin=0.0, ymax=1.0
    )
    return [inlet, outlet]


app = Application()
kernel = CubicSpline(dim=2)
integrator = PECIntegrator(
    fluid=InletOutletStep(), inlet=InletOutletStep(), outlet=InletOutletStep()
)

dt = 1e-2
tf = 6

solver = Solver(
    kernel=kernel, dim=2, integrator=integrator, dt=dt, tf=tf,
    adaptive_timestep=False
)

app.setup(
    solver=solver, equations=[], particle_factory=create_particles,
    inlet_outlet_factory=create_inlet_outlet
)

app.run()
