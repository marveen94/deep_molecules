import math as m
from multiprocessing import Pool, cpu_count
from pathlib import Path
from datetime import datetime
import numpy as np


Nx = 50  # Number of points in x-direction
Ny = 50  # Number of points in y-direction
Nz = 50  # Number of points in z-direction

gamma = 0.36  # Angstrom

grid_space = 0.155  # Angstrom

Lx = Nx * grid_space  # Angstrom
Ly = Ny * grid_space  # Angstrom
Lz = Nz * grid_space  # Angstrom

offset = Lx / 2  # The offset for "COM" coordinates.

int_energy_data = []
int_energy_per_atom_data = []
sum_ind_atom_energies = []
difference_energy = []
id_numbers = []


def get_data(file_name):

    fin = open(file_name)
    first = fin.readline().split()
    no_atoms = int(first[0])
    frame = np.zeros((no_atoms, 4))
    info = fin.readline().split()
    internal_energy_0K = float(info[12])
    id_number = int(info[1])
    temp_dict = []
    ind_energy = 0.0

    for i in range(no_atoms):
        temp_dict = []
        temp_dict = fin.readline().split()
        # Here we check the atomic species and assign the atomic number.
        if temp_dict[0] == "H":
            frame[i, 0] = 1
            ind_energy += -0.5
        elif temp_dict[0] == "C":
            frame[i, 0] = 6
            ind_energy += -37.8450
        elif temp_dict[0] == "N":
            frame[i, 0] = 7
            ind_energy += -54.5892
        elif temp_dict[0] == "O":
            frame[i, 0] = 8
            ind_energy += -75.0673
        elif temp_dict[0] == "F":
            frame[i, 0] = 9
            ind_energy += -99.7339

        frame[i, 1] = np.single(temp_dict[1])  # Insert x coordinate
        frame[i, 2] = np.single(temp_dict[2])  # Insert y coordinate
        frame[i, 3] = np.single(temp_dict[3])  # Insert z coordinate
        diff_energy = internal_energy_0K - ind_energy

    return no_atoms, internal_energy_0K, frame, id_number, ind_energy, diff_energy


def np_gaussian_pot(atomic_info, gamma):

    x = np.linspace(0, Lx, 50, endpoint=False)
    y = np.linspace(0, Lx, 50, endpoint=False)
    z = np.linspace(0, Lx, 50, endpoint=False)
    # atom_info N x 3
    # only coordinates
    atom_info = atomic_info[:, 1:]
    # zeta N
    zeta = atomic_info[:, 0]

    xxx, yyy, zzz = np.meshgrid(x, y, z)
    xxx, yyy, zzz = xxx - x.max() / 2, yyy - y.max() / 2, zzz - z.max() / 2

    square_norm = (
        (xxx[None, ...] - atom_info[:, 0][..., None, None, None]) ** 2
        + (yyy[None, ...] - atom_info[:, 1][..., None, None, None]) ** 2
        + (zzz[None, ...] - atom_info[:, 2][..., None, None, None]) ** 2
    )
    new_potential = np.sum(
        zeta[..., None, None, None] * np.exp(-square_norm / (2 * gamma ** 2)), axis=0
    )

    return new_potential


def read_data(i):
    path = f"/Users/lucabrodoloni/Desktop/Stage/Dataset/dsgdb9nsd_{i}.xyz"
    # if Path(path).is_file():
    try:
        mol_1 = get_data(path)

        no_atoms = mol_1[0]
        internal_energy = mol_1[1]
        atomic_info = mol_1[2]
        id_number = mol_1[3]
        ind_energy = mol_1[4]
        diff_energy = mol_1[5]

        sizex = np.amax(atomic_info[:, 1]) - np.amin(atomic_info[:, 1])
        sizey = np.amax(atomic_info[:, 2]) - np.amin(atomic_info[:, 2])
        sizez = np.amax(atomic_info[:, 3]) - np.amin(atomic_info[:, 3])

        int_energy_data.append(internal_energy)
        int_energy_per_atom_data.append(internal_energy / no_atoms)
        sum_ind_atom_energies.append(ind_energy)
        difference_energy.append(diff_energy)
        id_numbers.append(id_number)

        my_pot = gaussian_pot(
            atomic_info,
            gamma,
        )
        my_pot = torch.unsqueeze(my_pot, 0).float()
        result.append((my_pot, diff_energy))
    except:
        pass
    return


if __name__ == "__main__":

    list_id = [f"{i}".zfill(6) for i in range(50000)]
    # for i in range(1, 133886):
    start_time = datetime.now()
    pool = Pool(7)
    for i in list_id:
        # read_data(i)
        pool.apply_async(read_data, args=(i,))
    pool.close()
    pool.join()
    print(f"Duration {datetime.now() - start_time}")


# np.savetxt('internal_energies_medium_atoms.txt', int_energy_data, fmt='%1.7f')
# np.savetxt('internal_energies_per_atom_medium_atoms.txt',
#            int_energy_per_atom_data, fmt='%1.7f')
# np.savetxt('individual_atoms_energy_summed.txt',
#            sum_ind_atom_energies, fmt='%1.7f')
# np.savetxt('difference_gs_summed_energies.txt', difference_energy, fmt='%1.7f')
# np.savetxt('id_numbers.txt', id_numbers, fmt='%i')
