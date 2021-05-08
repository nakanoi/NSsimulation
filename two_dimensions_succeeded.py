import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as anime
from decimal import Decimal, ROUND_HALF_UP


'''
-------variables-----------------------------------------------------
Lx        :THE LENGTH of IMAGINARY ROOM [m]
Ly        :THE HEIGHT of IMAGINARY ROOM [m]
delt      :THE MICRO TIME
dell      :THE MICRO LENGTH == THE LENGTH of THE MICRO VOLUME
divLx     :DIVIDED NUMBER in x DIRECTION
divLy     :DIVIDED NUMBER in y DIRECTION 
ux        :FLUID VELOCITY in x DIRECTION AT POINT (x, y)[numpy array]
uy        :FLUID VELOCITY in y DIRECTION AT POINT (x, y)[numpy array]
vx        :TEMPORARY VELOCITY in x DIRECTION
vy        :TEMPORARY VELOCITY in y DIRECTION
ux_calced :CALCULATED VELOCITY in x DIRECTION at POINT (x, y)[numpy array]
uy_calced :CALCULATED VELOCITY in y DIRECTION at POINT (x, y)[numpy array]
div       :CALCULATED DIVERGENCE at POINT (x, y)[numpy array](THIS MUST BE ZERO)
p_rho     :DENSITY(UNIFORM)
mu        :THE DYNAMIC VISCOSITY COEFFICIENT
H         :FAN HEIGHT
v0        :THE FIRST VELOCITY CONDITION
eps       :TINY ERROR CONSTANCE THAT NEEDS in SOR
w         :ACCELATION CONSTANCE
count_max :THE NUMBER THAT YOU WANNA REPEAT
P         :THE PRESURE AT POINT (x, y)
fx        :THE FORCE in x DIRECTION AT POINT (x, y)[numpy array]
fy        :THE FORCE in y DIRECTION AT POINT (x, y)[numpy array]
---------------------------------------------------------------------
'''


def force_and_first(ux, uy, H, v0, delt):
    #GRAVITY
    #uy += 9.8 * delt

    #BOUNDARY CONDITION (v = 0 ON THE WALL)
    #x = 0 and LAST x (LEFT and RIGHT WALL)
    for y in range(ux.shape[1]):
        ux[0][y] = 0
        ux[1][y] = 0
        ux[ux.shape[0] - 2][y] = 0
        ux[ux.shape[0] - 1][y] = 0
    
    for y in range(uy.shape[1]):
        uy[0][y] = 0
        uy[1][y] = 0
        uy[uy.shape[0] - 2][y] = 0
        uy[uy.shape[0] - 1][y] = 0
        
    #y = 0 and LAST y (FLOOR and CEILING)
    for x in range(ux.shape[0]):
        ux[x][0] = 0
        ux[x][1] = 0
        ux[x][ux.shape[1] - 2] = 0
        ux[x][ux.shape[1] - 1] = 0
    
    for x in range(uy.shape[0]):
        uy[x][0] = 0
        uy[x][1] = 0
        uy[x][uy.shape[1] - 2] = 0
        uy[x][uy.shape[1] - 1] = 0

    #FAN
    for h in H:
        ux[h[0]][h[1]] = v0

    return ux, uy


def advectionX(ux, uy, delt, delx, dely):
    ux_calced = np.zeros_like(ux)
    for x in range(1, ux.shape[0] - 1):
        for y in range(1, ux.shape[1] - 1):            
            vx = ux[x][y]
            vy = (uy[x][y] + uy[x - 1][y] + uy[x][y + 1] + uy[x - 1][y + 1]) / 4

            if vx >= 0 and vy >= 0:
                ux_calced[x][y] = ux[x][y] - delt * (
                        vx * (ux[x][y] - ux[x - 1][y]) / delx + 
                        vy * (ux[x][y] - ux[x][y - 1]) / dely
                    )

            elif vx >= 0 and vy < 0:
                ux_calced[x][y] = ux[x][y] - delt * (
                        vx * (ux[x][y] - ux[x - 1][y]) / delx + 
                        vy * (ux[x][y + 1] - ux[x][y]) / dely
                    )

            elif vx < 0 and vy >= 0:
                ux_calced[x][y] = ux[x][y] - delt * (
                        vx * (ux[x + 1][y] - ux[x][y]) / delx + 
                        vy * (ux[x][y] - ux[x][y - 1]) / dely
                    )

            else:
                ux_calced[x][y] = ux[x][y] - delt * (
                        vx * (ux[x + 1][y] - ux[x][y]) / delx + 
                        vy * (ux[x][y + 1] - ux[x][y]) / dely
                    )

    return ux_calced


def advectionY(ux, uy, delt, delx, dely):
    uy_calced = np.zeros_like(uy)
    for x in range(1, uy.shape[0] - 1):
        for y in range(1, uy.shape[1] - 1):
            vx = (ux[x][y] + ux[x][y - 1] + ux[x + 1][y] + ux[x + 1][y - 1]) / 4
            vy = uy[x][y]

            if vx >= 0 and vy >= 0:
                uy_calced[x][y] = uy[x][y] - delt * (
                        vx * (uy[x][y] - uy[x - 1][y]) / delx + 
                        vy * (uy[x][y] - uy[x][y - 1]) / dely
                    )

            elif vx >= 0 and vy < 0:
                uy_calced[x][y] = uy[x][y] - delt * (
                        vx * (uy[x][y] - uy[x - 1][y]) / delx + 
                        vy * (uy[x][y + 1] - uy[x][y]) / dely
                    )

            elif vx < 0 and vy >= 0:
                uy_calced[x][y] = uy[x][y] - delt * (
                        vx * (uy[x + 1][y] - uy[x][y]) / delx + 
                        vy * (uy[x][y] - uy[x][y - 1]) / dely
                    )

            else:
                uy_calced[x][y] = uy[x][y] - delt * (
                        vx * (uy[x + 1][y] - uy[x][y]) / delx + 
                        vy * (uy[x][y + 1] - uy[x][y]) / dely
                    )

    return uy_calced


def viscosity(ux, uy, mu, delt, delx, dely, p_rho):
    ux_calced = np.zeros_like(ux)
    uy_calced = np.zeros_like(uy)
    for x in range(1, ux.shape[0] - 1):
        for y in range(1, ux.shape[1] - 1):
            ux_calced[x][y] = ux[x][y] + (
                               (
                                ux[x + 1][y] - 2 * ux[x][y] + ux[x - 1][y]
                               ) / np.power(delx, 2) + 
                               (
                                ux[x][y + 1] - 2 * ux[x][y] + ux[x][y - 1]
                               ) / np.power(dely, 2)
                           ) * delt * mu / p_rho

    for x in range(1, uy.shape[0] - 1):
        for y in range(1, uy.shape[1] - 1):
            uy_calced[x][y] = uy[x][y] + (
                               (
                                uy[x + 1][y] - 2 * uy[x][y] + uy[x - 1][y]
                               ) / np.power(delx, 2) + 
                               (
                                uy[x][y + 1] - 2 * uy[x][y] + uy[x][y - 1]
                               ) / np.power(dely, 2)
                           ) * delt * mu / p_rho

    return ux_calced, uy_calced


def divergence(ux, uy, div, delt, delx, dely):
    for x in range(div.shape[0]):
        for y in range(div.shape[1]):
            div[x][y] = ((ux[x + 2][y + 1] - ux[x + 1][y + 1]) / delx +
                         (uy[x + 1][y + 2] - uy[x + 1][y + 1]) / dely
                         ) / delt

    return div


def SOR(ux, uy, div, delt, delx, dely, P, eps, w):
    for x in range(1, P.shape[0] - 1):
        for y in range(1, P.shape[1] - 1):
            P_calced = (
                        (P[x + 1][y] + P[x - 1][y]) / np.power(delx, 2) +
                        (P[x][y + 1] + P[x][y - 1]) / np.power(dely, 2) - 
                        div[x][y]
                        ) * np.power(delx * dely, 2) * 0.5 / (np.power(delx, 2) + np.power(dely, 2))
            error = max(abs(P[x][y] - P_calced), eps)
            P[x][y] = (1 - w) * P[x][y] + w * P_calced

    return error, P


def Poisson(ux, uy, div, delt, delx, dely, P, eps, w, count_max):
    error = 1
    count = 0
    div = divergence(ux, uy, div, delt, delx, dely)
    while error > eps or count > count_max:
        error, P = SOR(ux, uy, div, delt, delx, dely, P, eps, w)
        count += 1

    return P


def fix_u(ux, uy, P, delt, delx, dely, p_rho):
    for x in range(P.shape[0] - 1):
        for y in range(P.shape[1] - 1):
            ux[x + 2][y + 1] -= (P[x + 1][y] - P[x][y]) * delt / delx
            uy[x + 1][y + 2] -= (P[x][y + 1] - P[x][y]) * delt / dely

    return ux, uy


def plot(ux, uy, Lx, Ly, delt, delx, dely, plots, v0):
    plt.xlim(-0.1, Lx + 0.1)
    plt.ylim(-0.1, Ly + 0.1)
    for x in range(uy.shape[0]):
        for y in range(ux.shape[1]):
            abs_u = (np.sqrt(np.power(ux[x][y], 2) + 
                     np.power(uy[x][y], 2) +
                     0.01)
                     )
            img = plt.quiver(x * delx,
                      y * dely,
                      ux[x][y] * delt,
                      uy[x][y] * delt,
                      color=cm.jet(abs_u / v0),
                      )
    plt.show()
    plots.append([img])

    return plots


def main():
    #SET EACH CONSTANCE
    Lx = 4.2
    Ly = 2.4
    delt = 0.01
    dell = 0.1
    divLx = int(
                Decimal(
                    str(Lx / dell)).quantize(Decimal('0'),
                    rounding=ROUND_HALF_UP
                )
            )
    divLy = int(
                Decimal(
                    str(Ly / dell)).quantize(Decimal('0'),
                    rounding=ROUND_HALF_UP
                )
            )
    ux = np.zeros((divLx + 2, divLy + 1))
    uy = np.zeros((divLx + 1, divLy + 2))
    div = np.zeros((divLx - 1, divLy - 1))
    P = np.zeros((divLx - 1, divLy - 1))
    p_rho = 1.2
    mu = 1.82e-5
    H = [[1, 3], [1, 4]]
    v0 = 5.0
    eps = 1e-8
    w = 1.7 
    count_max = 10000
    time_range = .5
    passed_time = 0.0
    plots = []
    fig = plt.figure()

    #PLOT
    plot(ux, uy, Lx, Ly, delt, dell, dell, plots, v0)

    while passed_time < time_range:
        print(passed_time)

        #FIRST CONDITION
        ux, uy = force_and_first(ux, uy, H, v0, delt)

        #ADVECT ux, uy
        ux = advectionX(ux, uy, delt, dell, dell)
        uy = advectionY(ux, uy, delt, dell, dell)    

        #CALCULATE VISCOSITY ux, uy
        ux, uy = viscosity(ux, uy, mu, delt, dell, dell, p_rho)

        #CALCULATE EACH DIVERGENCE at EACH POINT
        P = Poisson(ux, uy, div, delt, dell, dell, P, eps, w, count_max)

        #FIX THE VELOCITY
        ux, uy = fix_u(ux, uy, P, delt, dell, dell, p_rho)
        ux, uy = force_and_first(ux, uy, H, v0, delt)

        #PLOT
        plots = plot(ux, uy, Lx, Ly, delt, dell, dell, plots, v0)

        passed_time += delt

    ani = anime.ArtistAnimation(fig, plots)
    ani.save('./plots_movie.mp4', writer="ffmpeg")


if __name__ == '__main__':
    main()
