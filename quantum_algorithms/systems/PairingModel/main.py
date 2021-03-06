import numpy as np


import sys
sys.path.append('../..')
sys.path.append('../../../../QuantumCircuitOptimizer')
from quantum_circuit import QuantumCircuit,SecondQuantizedHamiltonian

from vqe import VQE
#from Qoperator import *
from ucc import UnitaryCoupledCluster
from spsa import SPSA


l = 4     # number of spin orbitals / number of qubits
n = 2     # Number of occupied spin orbitals
delta = 1 # Level spacing
g = 1     # Interaction strength
#g /= 4

# Matrix elements
h_pq = np.identity(l)
for p in range(l):
	h_pq[p,p] *= delta*(p - (p%2))/2
	
h_pqrs = np.zeros((l,l,l,l))
for p in range(0,l-1,2):
	for r in range(0,l-1,2):
		h_pqrs[p,p+1,r,r+1] = -0.5*g

UCCD = UnitaryCoupledCluster(n,l,'D',1)
theta = UCCD.new_parameters()

Pairing = SecondQuantizedHamiltonian(n,l,h_pq,h_pqrs)

options = {'shots':10000}

methods = ['Powell','Cobyla','Nelder-Mead']
for method in methods:
    new_theta = theta
    print('VQE with optimization method:',method)
    model = VQE(Pairing,
            ansatz = 'UCCD',
            options=options)
    model.optimize_classical(method=method)
    np.save('data/'+method+'10k.npy', model.energies)

theta = Pairing.theta
model = VQE(Pairing,
        ansatz = 'UCCD',
        options=options)
opt_options = {'feedback':1,'grad_avg':5}
optimization = SPSA(model.expval,
                    theta,
                    min_change=0.1,
                    noise_var = 0.01,
                    options=opt_options)
optimization.run()
method = 'SPSA'
np.save('data/'+method+'10k.npy', model.energies)



