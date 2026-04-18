"""
=======================================================
  PROBLEMA DE TRANSPORT - Rezolvitor Complet
=======================================================
  Implementează (conform cursului CM):
    PAS 1 - Metoda Colțului N-V (soluție inițială de bază)
    PAS 2 - Algoritmul MODI + Stepping-Stone (optimizare)
    Tehnica Perturbării ε (pentru soluții degenerate)
=======================================================
"""

import copy
from fractions import Fraction

EPS_SYM = "ε"   # simbol afișat pentru epsilon


# ──────────────────────────────────────────────────────
#  UTILITARE AFIȘARE
# ──────────────────────────────────────────────────────

def print_header(title):
    print("\n" + "═" * 56)
    print(f"  {title}")
    print("═" * 56)

def print_table(X, supply, demand, label="Tabel"):
    m, n = len(supply), len(demand)
    col_w = 10
    print(f"\n  [{label}]")
    # header coloane
    header = " " * 6 + "".join(f"B{j+1}".center(col_w) for j in range(n)) + "  D"
    print(header)
    print("  " + "-" * (6 + col_w * n + 4))
    for i in range(m):
        row = f"  A{i+1} |"
        for j in range(n):
            val = X[i][j]
            if val is None:
                cell = "·"
            elif isinstance(val, str):
                cell = val
            elif val == 0:
                cell = "0"
            else:
                cell = str(val)
            row += cell.center(col_w)
        row += f"  {supply[i]}"
        print(row)
    print("  " + "-" * (6 + col_w * n + 4))
    foot = "  N  |" + "".join(str(demand[j]).center(col_w) for j in range(n))
    print(foot)

def print_delta_table(delta, m, n, label="Δ"):
    col_w = 7
    print(f"\n  [{label}]  δij = cij - c̃ij")
    header = " " * 6 + "".join(f"B{j+1}".center(col_w) for j in range(n))
    print(header)
    print("  " + "-" * (6 + col_w * n))
    for i in range(m):
        row = f"  A{i+1} |"
        for j in range(n):
            v = delta[i][j]
            cell = "·" if v is None else str(v)
            row += cell.center(col_w)
        print(row)


# ──────────────────────────────────────────────────────
#  INPUT
# ──────────────────────────────────────────────────────

def read_input():
    print_header("DATE PROBLEMĂ DE TRANSPORT")
    m = int(input("\n  Număr furnizori (m): "))
    n = int(input("  Număr beneficiari (n): "))

    print(f"\n  Matricea costurilor C ({m}x{n}):")
    C = []
    for i in range(m):
        while True:
            try:
                row = list(map(int, input(f"    Linia A{i+1} ({n} valori): ").split()))
                if len(row) == n:
                    C.append(row)
                    break
                print(f"    ⚠ Introduceți exact {n} valori!")
            except ValueError:
                print("    ⚠ Numai numere întregi!")

    print(f"\n  Disponibilele furnizorilor a_i ({m} valori):")
    while True:
        try:
            supply = list(map(int, input("    ").split()))
            if len(supply) == m:
                break
            print(f"    ⚠ Introduceți exact {m} valori!")
        except ValueError:
            print("    ⚠ Numai numere întregi!")

    print(f"\n  Necesarul beneficiarilor b_j ({n} valori):")
    while True:
        try:
            demand = list(map(int, input("    ").split()))
            if len(demand) == n:
                break
            print(f"    ⚠ Introduceți exact {n} valori!")
        except ValueError:
            print("    ⚠ Numai numere întregi!")

    return m, n, C, supply, demand


# ──────────────────────────────────────────────────────
#  ECHILIBRARE
# ──────────────────────────────────────────────────────

def echilibrare(m, n, C, supply, demand):
    S = sum(supply)
    D = sum(demand)
    print(f"\n  ΣD = {S},  ΣN = {D}")

    if S == D:
        print("  ✔ Problema este ECHILIBRATĂ (PTE).")
        return m, n, C, list(supply), list(demand), False, False

    fictiv = False
    if S > D:
        # furnizor excedentar → beneficiar fictiv B_{n+1}
        diff = S - D
        print(f"  ΣD > ΣN  →  introducem beneficiar fictiv B{n+1} cu b = {diff}")
        demand_new = list(demand) + [diff]
        C_new = [row + [0] for row in C]
        n_new = n + 1
        fictiv = True
        return m, n_new, C_new, list(supply), demand_new, "beneficiar", fictiv
    else:
        # beneficiar excedentar → furnizor fictiv A_{m+1}
        diff = D - S
        print(f"  ΣN > ΣD  →  introducem furnizor fictiv A{m+1} cu a = {diff}")
        supply_new = list(supply) + [diff]
        C_new = copy.deepcopy(C) + [[0] * n]
        m_new = m + 1
        fictiv = True
        return m_new, n, C_new, supply_new, list(demand), "furnizor", fictiv


# ──────────────────────────────────────────────────────
#  PAS 1 – METODA COLȚULUI N-V
# ──────────────────────────────────────────────────────

def northwest_corner(m, n, supply, demand):
    """
    Returnează:
      X      - matricea alocărilor (None = nebazică)
      basis  - lista de (i,j) componente bazice
    """
    a = list(supply)
    b = list(demand)
    X = [[None] * n for _ in range(m)]
    basis = []

    i, j = 0, 0
    while i < m and j < n:
        val = min(a[i], b[j])
        X[i][j] = val
        basis.append((i, j))
        a[i] -= val
        b[j] -= val
        if a[i] == 0 and b[j] == 0:
            # ── DEGENERARE ──────────────────────────────────────────
            # Ambele se epuizează simultan → avansăm pe AMBELE axe
            # (sărim atât linia cât și coloana).
            # Astfel NU se va pune o celulă cu val=0 în bază pe
            # iterația următoare → NC < V → soluție degenerată (corect).
            i += 1
            j += 1
        elif a[i] == 0:
            i += 1
        else:
            j += 1

    return X, basis


# ──────────────────────────────────────────────────────
#  TEHNICA PERTURBĂRII ε
# ──────────────────────────────────────────────────────

def apply_epsilon(m, n, supply_orig, demand_orig):
    """
    Perturbă disponibilele și necesarul cu ε (simbolic).
    Returnează supply_eps, demand_eps ca strings.
    """
    supply_eps = [f"{a}+{EPS_SYM}" for a in supply_orig]
    demand_eps = list(demand_orig[:-1]) + [f"{demand_orig[-1]}+{m}·{EPS_SYM}"]
    return supply_eps, demand_eps

def nw_corner_numeric(m, n, supply_num, demand_num):
    """
    Versiunea numerică (cu epsilon ca număr mic > 0) pentru calcule.
    Folosim Fraction pentru precizie exactă.
    """
    EPS = Fraction(1, 10**9)   # ε numeric mic
    a = [Fraction(x) + EPS for x in supply_num]
    b = [Fraction(x) for x in demand_num]
    b[-1] += m * EPS

    X = [[None] * n for _ in range(m)]
    basis = []

    i, j = 0, 0
    while i < m and j < n:
        val = min(a[i], b[j])
        X[i][j] = val
        basis.append((i, j))
        a[i] -= val
        b[j] -= val
        if a[i] == 0 and b[j] == 0:
            if i + 1 < m:
                i += 1
            else:
                j += 1
        elif a[i] == 0:
            i += 1
        else:
            j += 1

    return X, basis


# ──────────────────────────────────────────────────────
#  VERIFICARE DEGENERARE
# ──────────────────────────────────────────────────────

def check_degeneracy(basis, m, n, supply, demand, iteration_label="T₀"):
    NC = len(basis)
    V = m + n - 1
    if NC == V:
        print(f"  NC = {NC} = V = {V}  →  Soluție NEDEGENERATĂ ✔")
        return False
    else:
        print(f"  NC = {NC} < V = {V}  →  Soluție DEGENERATĂ ⚠")
        print(f"  Se aplică Tehnica Perturbării ε ...")
        return True


# ──────────────────────────────────────────────────────
#  CALCULUL FUNCȚIEI OBIECTIV
# ──────────────────────────────────────────────────────

def compute_cost(X, C, basis):
    total = Fraction(0)
    for (i, j) in basis:
        if X[i][j] is not None:
            total += Fraction(C[i][j]) * X[i][j]
    return total


# ──────────────────────────────────────────────────────
#  SISTEMUL S: ui + vj = cij  (multiplicatori duali)
# ──────────────────────────────────────────────────────

def compute_multipliers(basis, C, m, n):
    """
    Rezolvă sistemul ui + vj = c_ij pentru (i,j) ∈ basis.
    Alegem u1 = 0 (sau variabila care apare cel mai des).
    """
    u = [None] * m
    v = [None] * n

    # Alegem variabila cu cele mai multe apariții = 0
    from collections import Counter
    cnt = Counter()
    for (i, j) in basis:
        cnt[('u', i)] += 1
        cnt[('v', j)] += 1
    most_common = cnt.most_common(1)[0][0]
    if most_common[0] == 'u':
        u[most_common[1]] = Fraction(0)
    else:
        v[most_common[1]] = Fraction(0)

    # Propagare iterativă
    changed = True
    while changed:
        changed = False
        for (i, j) in basis:
            if u[i] is not None and v[j] is None:
                v[j] = Fraction(C[i][j]) - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = Fraction(C[i][j]) - v[j]
                changed = True

    return u, v


# ──────────────────────────────────────────────────────
#  COSTURILE MODIFICATE c̃ij  și  DIFERENȚELE δij
# ──────────────────────────────────────────────────────

def compute_delta(C, u, v, basis, m, n):
    basis_set = set(basis)
    delta = [[None] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if (i, j) not in basis_set:
                c_tilde = u[i] + v[j]
                delta[i][j] = Fraction(C[i][j]) - c_tilde
    return delta


# ──────────────────────────────────────────────────────
#  DETERMINAREA CIRCUITULUI (CICLULUI) STEPPING-STONE
# ──────────────────────────────────────────────────────

def find_cycle(start, basis_set, m, n):
    """
    Găsește ciclul pornind din celula 'start' (nebazică),
    exact ca în caiet/seminar.

    Ordinea de preferință pentru prima mișcare (sens orar față de start):
        1. coloană SUS   (i descrescător)
        2. linie DREAPTA (j crescător)
        3. coloană JOS   (i crescător)
        4. linie STÂNGA  (j descrescător)

    La fiecare pas ulterior se alternează coloană/linie, cu aceeași
    preferință de direcție (sus/dreapta > jos/stânga).
    DFS cu backtracking garantează găsirea circuitului corect.
    """
    def col_candidates(r, c):
        up   = sorted([(ii, c) for ii in range(0, r)
                       if (ii, c) in basis_set], key=lambda x: -x[0])
        down = sorted([(ii, c) for ii in range(r+1, m)
                       if (ii, c) in basis_set], key=lambda x:  x[0])
        return up + down

    def row_candidates(r, c):
        right = sorted([(r, jj) for jj in range(c+1, n)
                        if (r, jj) in basis_set], key=lambda x:  x[1])
        left  = sorted([(r, jj) for jj in range(0, c)
                        if (r, jj) in basis_set], key=lambda x: -x[1])
        return right + left

    def dfs(path, use_col):
        cur = path[-1]
        candidates = col_candidates(cur[0], cur[1]) if use_col                      else row_candidates(cur[0], cur[1])
        for nxt in candidates:
            if len(path) >= 3:
                if use_col and nxt[0] == path[0][0]:
                    return path + [nxt]
                if not use_col and nxt[1] == path[0][1]:
                    return path + [nxt]
            if nxt not in path:
                result = dfs(path + [nxt], not use_col)
                if result:
                    return result
        return None

    r0, c0 = start
    # Ordinea de încercare a primei mișcări: col_up, row_right, col_down, row_left
    first_moves = (
        sorted([(ii, c0) for ii in range(0, r0)
                if (ii, c0) in basis_set], key=lambda x: -x[0]),   # col sus
        sorted([(r0, jj) for jj in range(c0+1, n)
                if (r0, jj) in basis_set], key=lambda x:  x[1]),   # linie dr
        sorted([(ii, c0) for ii in range(r0+1, m)
                if (ii, c0) in basis_set], key=lambda x:  x[0]),   # col jos
        sorted([(r0, jj) for jj in range(0, c0)
                if (r0, jj) in basis_set], key=lambda x: -x[1]),   # linie st
    )
    # use_col pentru pasul 2 (după prima mișcare): True dacă prima e pe linie
    use_col_next = (False, True, False, True)

    for moves, ucn in zip(first_moves, use_col_next):
        for first in moves:
            if first == start:
                continue
            result = dfs([start, first], ucn)
            if result:
                return result
    return None


# ──────────────────────────────────────────────────────
#  O ITERAȚIE DE OPTIMIZARE
# ──────────────────────────────────────────────────────

def optimize_step(X, C, basis, m, n, iteration):
    """
    Returnează:
      (X_new, basis_new, f_new, stop)
    """
    basis_set = set(basis)
    u, v = compute_multipliers(basis, C, m, n)
    delta = compute_delta(C, u, v, basis, m, n)

    # Afișare multiplicatori
    print(f"\n  Multiplicatori duali (u, v):")
    u_str = "  u: " + "  ".join(
        f"u{i+1}={float(u[i]):.4g}" if u[i] is not None else f"u{i+1}=?" for i in range(m))
    v_str = "  v: " + "  ".join(
        f"v{j+1}={float(v[j]):.4g}" if v[j] is not None else f"v{j+1}=?" for j in range(n))
    print(u_str)
    print(v_str)

    # Afișare Δ
    print()
    delta_disp = [[None]*n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if (i,j) not in basis_set:
                delta_disp[i][j] = round(float(delta[i][j]), 6) \
                    if delta[i][j] is not None else None
    print_delta_table(delta_disp, m, n)

    # Test optimalitate
    neg_deltas = [(i, j) for i in range(m) for j in range(n)
                  if delta[i][j] is not None and delta[i][j] < 0]

    if not neg_deltas:
        print("\n  ✔ Toate δij ≥ 0  →  SOLUȚIE OPTIMĂ (STOP)")
        return X, basis, compute_cost(X, C, basis), True

    # Alegem celula cu δij minim
    pq = min(neg_deltas, key=lambda ij: delta[ij[0]][ij[1]])
    p, q = pq
    print(f"\n  min{{δij < 0}} = δ{p+1}{q+1} = {float(delta[p][q]):.4g}")
    print(f"  → Circuit pornind din celula ({p+1},{q+1})")

    cycle = find_cycle((p, q), basis_set, m, n)
    if cycle is None:
        print("  ⚠ Nu s-a găsit ciclu valid! (caz degenerat avansat)")
        return X, basis, compute_cost(X, C, basis), True

    # Marcăm celulele ciclului +θ / -θ alternativ
    signs = []
    for idx, cell in enumerate(cycle):
        signs.append('+' if idx % 2 == 0 else '-')

    cycle_str = " → ".join(f"({r+1},{c+1}){s}" for (r,c),s in zip(cycle, signs))
    print(f"  Circuit: {cycle_str}")

    # ── Tabelul Ti cu circuitul marcat (ca în caiet) ─────────────────
    col_w = 9
    cycle_set = {cell: ('+' if signs[k] == '+' else '-')
                 for k, cell in enumerate(cycle)}
    print(f"\n  [Tabel T{iteration} cu circuitul]")
    hdr = " " * 6 + "".join(f"B{j+1}".center(col_w) for j in range(n))
    print(hdr)
    print("  " + "-" * (6 + col_w * n + 4))
    for i in range(m):
        row_str = f"  A{i+1} |"
        for j in range(n):
            cell = (i, j)
            xval = X[i][j]
            if cell == (p, q):
                # celula nebazică de start: afișăm 0 (θ inițial)
                cell_str = "0"
            elif cell in cycle_set:
                sign = cycle_set[cell]
                v = int(round(float(xval))) if xval is not None else 0
                cell_str = f"{v}{sign}θ"
            elif xval is not None:
                cell_str = str(int(round(float(xval))))
            else:
                cell_str = "·"
            row_str += cell_str.center(col_w)
        print(row_str)
    print("  " + "-" * (6 + col_w * n + 4))

    # θ = min al celulelor cu semn - (prima valoare minimă)
    minus_cells = [(cycle[k], X[cycle[k][0]][cycle[k][1]])
                   for k in range(1, len(cycle), 2)]
    theta = min(v for _, v in minus_cells)
    vals_str = ", ".join(str(int(round(float(v)))) for _, v in minus_cells)
    print(f"\n  θ = min{{{vals_str}}} = {int(round(float(theta)))}")

    # Construim noul X
    X_new = copy.deepcopy(X)
    for idx, (r, c) in enumerate(cycle):
        if signs[idx] == '+':
            if X_new[r][c] is None:
                X_new[r][c] = theta
            else:
                X_new[r][c] += theta
        else:
            X_new[r][c] -= theta

    # Actualizăm baza: eliminăm celula cu θ (care devine 0)
    leave = None
    for k in range(1, len(cycle), 2):
        r, c = cycle[k]
        if X_new[r][c] == 0:
            if leave is None:
                leave = (r, c)
            X_new[r][c] = None

    basis_new = [cell for cell in basis if cell != leave]
    if (p, q) not in basis_new:
        basis_new.append((p, q))

    f_new = compute_cost(X_new, C, basis_new)
    f_old = compute_cost(X, C, basis)
    delta_val = int(round(float(delta[p][q])))
    theta_val = int(round(float(theta)))
    fold_val  = int(round(float(f_old)))
    fnew_val  = int(round(float(f_new)))
    print(f"\n  f_nou = {fold_val} + ({delta_val}) · {theta_val} = {fnew_val}")

    return X_new, basis_new, f_new, False


# ──────────────────────────────────────────────────────
#  ALGORITM PRINCIPAL
# ──────────────────────────────────────────────────────

def solve(m_orig, n_orig, C_orig, supply_orig, demand_orig):

    # ── Echilibrare ──
    print_header("PAS 1 – ECHILIBRARE & SOLUȚIE INIȚIALĂ (N-V)")
    m, n, C, supply, demand, fictiv_type, was_fictiv = echilibrare(
        m_orig, n_orig, C_orig, supply_orig, demand_orig)

    # ── Metoda N-V (verificăm degenerare) ──
    X_nv, basis_nv = northwest_corner(m, n, supply, demand)
    print("\n  Tabelul N-V (soluție inițială):")
    print_table(X_nv, supply, demand, "N-V")

    NC = len(basis_nv)
    V = m + n - 1
    print(f"\n  NC = {NC},  V = m+n-1 = {m}+{n}-1 = {V}")
    degenerate = check_degeneracy(basis_nv, m, n, supply, demand)

    if degenerate:
        # ── Tehnica ε ──
        print_header("TEHNICA PERTURBĂRII ε (soluție degenerată)")
        print(f"\n  Modificăm disponibilele: ai → ai + ε  (i=1..{m})")
        print(f"  Modificăm necesarul:     b{n} → b{n} + {m}·ε")
        print(f"  unde 0 < ε << 1\n")

        # Obținem soluție nedegenerată cu ε numeric
        X_eps, basis_eps = nw_corner_numeric(m, n, supply, demand)

        # Afișăm tabelul cu simboluri ε
        supply_sym = [f"{a}+{EPS_SYM}" for a in supply]
        demand_sym = list(demand)
        demand_sym[-1] = f"{demand[-1]}+{m}{EPS_SYM}"
        print(f"  Soluție nedegenerată după perturbație:")
        # Afișăm valorile bazice
        basis_str = {(i,j): f"{float(X_eps[i][j]):.4g}" for (i,j) in basis_eps}
        X_disp = [[None]*n for _ in range(m)]
        for (i,j) in basis_eps:
            X_disp[i][j] = basis_str[(i,j)]
        print_table(X_disp, supply_sym, demand_sym, "N-V (cu ε)")
        print(f"  NC = {len(basis_eps)} = V = {V}  ✔ soluție nedegenerată")

        X_work = X_eps
        basis_work = basis_eps
    else:
        X_work = [[Fraction(v) if v is not None else None
                   for v in row] for row in X_nv]
        basis_work = basis_nv

    C_frac = [[Fraction(c) for c in row] for row in C]

    # ── PAS 2 – Optimizare iterativă ──
    print_header("PAS 2 – ALGORITMUL DE OPTIMIZARE (MODI)")
    f_crt = compute_cost(X_work, C_frac, basis_work)
    print(f"\n  Costul soluției inițiale: f₀ = {float(f_crt):.4g}")

    iteration = 0
    MAX_ITER = 100
    while iteration < MAX_ITER:
        print(f"\n{'─'*56}")
        print(f"  ITERAȚIA I_{iteration} (T_{iteration}, X_{iteration}, f_{iteration})")
        print(f"  f_{iteration} = {float(f_crt):.4g}")

        X_new, basis_new, f_new, stop = optimize_step(
            X_work, C_frac, basis_work, m, n, iteration)

        X_work = X_new
        basis_work = basis_new
        f_crt = f_new
        iteration += 1

        if stop:
            break

    # ── PAS 3 – Soluția finală ──
    print_header("PAS 3 – SOLUȚIA OPTIMĂ")

    # Facem ε → 0: rotunjim la cel mai apropiat întreg
    X_final = [[None]*n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            v = X_work[i][j]
            if v is not None:
                int_val = round(float(v))   # ε → 0 (rotunjire corectă)
                X_final[i][j] = int_val if int_val != 0 else None

    # Reconstruim baza după ε→0
    basis_final = [(i,j) for (i,j) in basis_work
                   if X_final[i][j] is not None]

    # Costul final (pe datele originale, fără fictivi)
    m_s, n_s = m_orig, n_orig
    f_total = sum(C_orig[i][j] * (X_final[i][j] or 0)
                  for i in range(m_s) for j in range(n_s)
                  if X_final[i][j])

    supply_disp = list(supply_orig)
    demand_disp = list(demand_orig)
    if was_fictiv == "beneficiar":
        supply_disp = supply_orig
        demand_disp = demand_orig
    if was_fictiv == "furnizor":
        supply_disp = supply_orig
        demand_disp = demand_orig

    print("\n  Alocările optime xij:")
    for i in range(m_orig):
        for j in range(n_orig):
            v = X_final[i][j]
            if v:
                print(f"    x{i+1}{j+1} = {v}  "
                      f"(A{i+1} → B{j+1},  cost unitar c{i+1}{j+1} = {C_orig[i][j]})")

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │  Costul MINIM de transport: {f_total:>6}  │")
    print(f"  └─────────────────────────────────────┘")

    print_table([[X_final[i][j] for j in range(n_orig)]
                 for i in range(m_orig)],
                supply_orig, demand_orig, "Soluție Optimă")

    if was_fictiv == "beneficiar":
        print(f"\n  ⚠ B{n_orig} era beneficiar fictiv → surplusul rămas nedistribuit.")
    if was_fictiv == "furnizor":
        print(f"\n  ⚠ A{m_orig} era furnizor fictiv → necesarul neacoperit.")

    return f_total, X_final


# ──────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────

def main():
    print("\n" + "╔" + "═"*54 + "╗")
    print("║     REZOLVITOR – PROBLEMA DE TRANSPORT (CM)         ║")
    print("║     Metoda N-V + MODI + Tehnica ε                   ║")
    print("╚" + "═"*54 + "╝")

    m, n, C, supply, demand = read_input()

    print("\n  Matricea costurilor introdusă:")
    for i, row in enumerate(C):
        print(f"    A{i+1}: {row}")
    print(f"  Disponibile: {supply}")
    print(f"  Necesar:     {demand}")

    cont = input("\n  Date corecte? (d/n): ").strip().lower()
    if cont != 'd':
        print("  Repornește programul și introdu datele din nou.")
        return

    solve(m, n, C, supply, demand)

    print("\n" + "═"*56)
    print("  Program terminat.")
    print("═"*56 + "\n")


if __name__ == "__main__":
    main()