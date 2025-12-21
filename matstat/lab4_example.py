import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# =============================================
# 1. ИСХОДНЫЕ ДАННЫЕ
# =============================================

# Параметры распределений для варианта 9
np.random.seed(5149)  # Для воспроизводимости

# X ~ N(10, 2) - параметры: mean=10, sigma=2
mu_x, sigma_x = 10, 2

# Y ~ N(5, 2) - параметры: mean=5, sigma=2
mu_y, sigma_y = 5, 2

# Объем выборки
n = 200

# Генерация случайных чисел (согласно примечанию)
# В примечании указано: scipy.stats: uniform.rvs, norm.rvs, chi2.rvs
X = stats.norm.rvs(loc=mu_x, scale=sigma_x, size=n)  # norm.rvs для нормального распределения
Y = stats.norm.rvs(loc=mu_y, scale=sigma_y, size=n)

print("=" * 60)
print("ЛАБОРАТОРНАЯ РАБОТА №4 - ВАРИАНТ 9")
print("=" * 60)

print("\n1. ИСХОДНЫЕ ДАННЫЕ")
print("-" * 40)

print("Характеристики наблюдаемых случайных величин:")
print("+-------+---------------+-----------------+----------------+-----------------------+----------+")
print("|  СВ   | Распределение |   Параметры     | Математическое | Дисперсия,            | Объем    |")
print("|       |               |                 | ожидание, m_i  | σ²                    | выборки, |")
print("|       |               |                 |                |                       | n        |")
print("+-------+---------------+-----------------+----------------+-----------------------+----------+")
print(f"|   X   |    N(10,2)    |   N(m,σ)        |       10       |         4             |          |")
print(f"|   Y   |    N(5,2)     |   N(m,σ)        |       5        |         4             |   200    |")
print("+-------+---------------+-----------------+----------------+-----------------------+----------+")

# Выборочные характеристики
# Среднее
mean_x = np.mean(X)
mean_y = np.mean(Y)

# Оценка дисперсии (несмещенная)
var_x = np.var(X, ddof=1)  # ddof=1 для несмещенной оценки
var_y = np.var(Y, ddof=1)

# Коэффициенты корреляции
# Пирсон
pearson_r, pearson_p = stats.pearsonr(X, Y)

# Спирмен
spearman_r, spearman_p = stats.spearmanr(X, Y)

# Кендалл
kendall_tau, kendall_p = stats.kendalltau(X, Y)

print("\nВыборочные характеристики:")
print("+-------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+")
print("|  СВ   |      Среднее,         |  Оценка дисперсии,    |   КК по Пирсону,      |   КК по Спирмену,     |   КК по Кендаллу,     |")
print("|       |       x̄               |        s²             |       r_XY            |       ρ_XY            |       τ_XY            |")
print("+-------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+")
print(f"|   X   |      {mean_x:10.4f}     |      {var_x:10.4f}     |                       |                       |                       |")
print(f"|   Y   |      {mean_y:10.4f}     |      {var_y:10.4f}     |      {pearson_r:10.4f}     |      {spearman_r:10.4f}     |      {kendall_tau:10.4f}     |")
print("+-------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+")

print("\nПроверка значимости коэффициентов корреляции:")
print("+----------------+--------------+-----------------+-------------------+")
print("| Статистическая |  p-value     | Статистическое  | Ошибка стат.      |")
print("| гипотеза, H₀   |              | решение при     | решения           |")
print("|                |              | α = 0.05        |                   |")
print("+----------------+--------------+-----------------+-------------------+")

alpha = 0.05

# Функция для форматирования p-value как в примере
def format_p_value(p):
    """Форматирует p-value: если < 0.0001, то в научной записи, иначе в десятичной дроби"""
    if p < 0.0001:
        return f"{p:.2e}"
    else:
        return f"{p:.4f}"

# Для Пирсона
pearson_decision = "H₀ отвергается" if pearson_p < alpha else "H₀ принимается"

# Определение ошибки для Пирсона (теоретически r_XY = 0, т.к. X и Y независимы)
theoretical_pearson_zero = True  # X и Y независимы, сгенерированы отдельно

if pearson_p < alpha:
    if not theoretical_pearson_zero:
        pearson_error = "Нет ошибки"
    else:
        pearson_error = "Ошибка I рода"
else:
    if theoretical_pearson_zero:
        pearson_error = "Нет ошибки"
    else:
        pearson_error = "Ошибка II рода"

pearson_p_formatted = format_p_value(pearson_p)
print(f"| H₀: r_XY = 0     | {pearson_p_formatted:>12} | {pearson_decision:15} | {pearson_error:17} |")

# Для Спирмена
spearman_decision = "H₀ отвергается" if spearman_p < alpha else "H₀ принимается"

# Определение ошибки для Спирмена (теоретически ρ_XY = 0)
if spearman_p < alpha:
    if not theoretical_pearson_zero:
        spearman_error = "Нет ошибки"
    else:
        spearman_error = "Ошибка I рода"
else:
    if theoretical_pearson_zero:
        spearman_error = "Нет ошибки"
    else:
        spearman_error = "Ошибка II рода"

spearman_p_formatted = format_p_value(spearman_p)
print(f"| H₀: ρ_XY = 0     | {spearman_p_formatted:>12} | {spearman_decision:15} | {spearman_error:17} |")

# Для Кендалла
kendall_decision = "H₀ отвергается" if kendall_p < alpha else "H₀ принимается"

# Определение ошибки для Кендалла (теоретически τ_XY = 0)
if kendall_p < alpha:
    if not theoretical_pearson_zero:
        kendall_error = "Нет ошибки"
    else:
        kendall_error = "Ошибка I рода"
else:
    if theoretical_pearson_zero:
        kendall_error = "Нет ошибки"
    else:
        kendall_error = "Ошибка II рода"

kendall_p_formatted = format_p_value(kendall_p)
print(f"| H₀: τ_XY = 0     | {kendall_p_formatted:>12} | {kendall_decision:15} | {kendall_error:17} |")
print("+----------------+--------------+-----------------+-------------------+")

print("\n2. ВИЗУАЛЬНОЕ ПРЕДСТАВЛЕНИЕ ДВУМЕРНОЙ ВЫБОРКИ")
print("-" * 40)

print("Диаграмма рассеяния случайных величин X и Y:")

# Создаем график
plt.figure(figsize=(8, 6))

# Используем scatter согласно примечанию - только точки
plt.scatter(X, Y, alpha=0.6, color='blue', edgecolor='black', s=30)

# Только подписи осей X и Y
plt.xlabel('X')
plt.ylabel('Y')

# Устанавливаем оси от 0
plt.xlim(0, max(X) * 1.1)  # От 0 до максимума X + 10%
plt.ylim(0, max(Y) * 1.1)  # От 0 до максимума Y + 10%

plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("Статистическая гипотеза: H₀: X и Y независимы")

# Разбиваем на 5 интервалов для X и Y (как в таблице отчета)
num_bins = 5

# Определяем границы интервалов для X и Y
x_min, x_max = X.min(), X.max()
y_min, y_max = Y.min(), Y.max()

# Создаем границы интервалов
x_bins = np.linspace(x_min, x_max, num_bins + 1)
y_bins = np.linspace(y_min, y_max, num_bins + 1)

# Округляем границы для читаемости
x_bins = np.round(x_bins, 2)
y_bins = np.round(y_bins, 2)

print(f"\nГраницы интервалов для X:")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"Δ{i + 1} = [{x_bins[i]:.2f}; {x_bins[i + 1]:.2f})")
    else:
        print(f"Δ{i + 1} = [{x_bins[i]:.2f}; {x_bins[i + 1]:.2f}]")

print(f"\nГраницы интервалов для Y:")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"[{y_bins[i]:.2f}; {y_bins[i + 1]:.2f})")
    else:
        print(f"[{y_bins[i]:.2f}; {y_bins[i + 1]:.2f}]")

# Используем hist2d для группировки согласно примечанию
hist, x_edges, y_edges = np.histogram2d(X, Y, bins=[x_bins, y_bins])

# Преобразуем в целочисленный массив
contingency_table = hist.astype(int)

print("\nЭмпирическая таблица сопряженности:")
print("+" + "-" * 75 + "+")
print("| Y\\X       ", end="")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"| [{x_bins[i]:5.2f};{x_bins[i + 1]:5.2f}) ", end="")
    else:
        print(f"| [{x_bins[i]:5.2f};{x_bins[i + 1]:5.2f}] ", end="")
print("|")

print("+" + "-" * 75 + "+")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"| [{y_bins[i]:5.2f};{y_bins[i + 1]:5.2f}) ", end="")
    else:
        print(f"| [{y_bins[i]:5.2f};{y_bins[i + 1]:5.2f}] ", end="")

    for j in range(num_bins):
        print(f"|{contingency_table[i, j]:^20} ", end="")
    print("|")
    print("+" + "-" * 75 + "+")

# Проверка гипотезы о независимости с помощью критерия хи-квадрат
# Используем scipy.stats.chi2_contingency согласно примечанию
chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print("\nТеоретическая таблица сопряженности (ожидаемые частоты):")
print("+" + "-" * 75 + "+")
print("| Y\\X       ", end="")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"| [{x_bins[i]:5.2f};{x_bins[i + 1]:5.2f}) ", end="")
    else:
        print(f"| [{x_bins[i]:5.2f};{x_bins[i + 1]:5.2f}] ", end="")
print("|")

print("+" + "-" * 75 + "+")
for i in range(num_bins):
    if i < num_bins - 1:
        print(f"| [{y_bins[i]:5.2f};{y_bins[i + 1]:5.2f}) ", end="")
    else:
        print(f"| [{y_bins[i]:5.2f};{y_bins[i + 1]:5.2f}] ", end="")

    for j in range(num_bins):
        print(f"|{expected[i, j]:^20.2f} ", end="")
    print("|")
    print("+" + "-" * 75 + "+")

# Форматируем p-value
p_formatted = format_p_value(p_value)

# Статистическое решение
alpha_chi2 = 0.05  # α = 0.05
chi2_decision = "H₀ отвергается" if p_value < alpha_chi2 else "H₀ принимается"

# Определение ошибки (теоретически X и Y независимы)
theoretical_independent = True  # X и Y независимы по построению

if p_value < alpha_chi2:
    if not theoretical_independent:
        chi2_error = "Нет ошибки"
    else:
        chi2_error = "Ошибка I рода"
else:
    if theoretical_independent:
        chi2_error = "Нет ошибки"
    else:
        chi2_error = "Ошибка II рода"

print("\nПроверка гипотезы о независимости:")
print("+----------------+--------------+-----------------+-------------------+")
print("| Выборочное     | p-value      | Статистическое  | Ошибка стат.      |")
print("| значение       |              | решение при     | решения           |")
print("| статистики     |              | α = 0.05        |                   |")
print("| критерия       |              |                 |                   |")
print("+----------------+--------------+-----------------+-------------------+")
print(f"| {chi2_stat:14.4f} | {p_formatted:>12} | {chi2_decision:15} | {chi2_error:17} |")
print("+----------------+--------------+-----------------+-------------------+")

print("\n" + "=" * 60)
print("ПРИМЕЧАНИЯ:")
print("1. Для группировки использована функция numpy.histogram2d (аналог matplotlib.pyplot.hist2d)")
print("2. Для проверки гипотезы использована функция scipy.stats.chi2_contingency")
print("3. Число интервалов: 5×5 = 25 ячеек")
print("4. Степени свободы: (5-1)×(5-1) = 16")
print(f"5. Ожидаемые частоты в каждой ячейке должны быть ≥5: {'Да' if np.all(expected >= 5) else 'Нет'}")
print("=" * 60)

# =============================================
# 4. ИССЛЕДОВАНИЕ КОРРЕЛЯЦИОННОЙ СВЯЗИ
# =============================================

print("\n4. ИССЛЕДОВАНИЕ КОРРЕЛЯЦИОННОЙ СВЯЗИ")
print("-" * 40)

print("Случайная величина U = λX + (1-λ)Y, λ∈[0; 1]")
print("Случайная величина V = λX³ + (1-λ)Y³, λ∈[0; 1]")

# Создаем массив значений λ от 0 до 1
lambda_values = np.linspace(0, 1, 101)

# Массивы для хранения коэффициентов корреляции
r_XU = []  # Коэффициент Пирсона r(X, U)
rho_XU = []  # Коэффициент Спирмена ρ(X, U)
tau_XU = []  # Коэффициент Кендалла τ(X, U)

r_XV = []  # Коэффициент Пирсона r(X, V)
rho_XV = []  # Коэффициент Спирмена ρ(X, V)
tau_XV = []  # Коэффициент Кендалла τ(X, V)

# Вычисляем коэффициенты корреляции для каждого λ
for lam in lambda_values:
    # Вычисляем U и V
    U = lam * X + (1 - lam) * Y
    V = lam * (X ** 3) + (1 - lam) * (Y ** 3)

    # Коэффициенты корреляции между X и U
    r_xu, _ = stats.pearsonr(X, U)
    rho_xu, _ = stats.spearmanr(X, U)
    tau_xu, _ = stats.kendalltau(X, U)

    r_XU.append(r_xu)
    rho_XU.append(rho_xu)
    tau_XU.append(tau_xu)

    # Коэффициенты корреляции между X и V
    r_xv, _ = stats.pearsonr(X, V)
    rho_xv, _ = stats.spearmanr(X, V)
    tau_xv, _ = stats.kendalltau(X, V)

    r_XV.append(r_xv)
    rho_XV.append(rho_xv)
    tau_XV.append(tau_xv)

# График 1: Зависимости коэффициентов корреляции r(X,U), ρ(X,U), τ(X,U) от λ
plt.figure(figsize=(12, 10))

plt.subplot(2, 1, 1)
plt.plot(lambda_values, r_XU, 'b-', linewidth=2, label='$r_{XU}(λ)$ - Пирсон')
plt.plot(lambda_values, rho_XU, 'r-', linewidth=2, label='$ρ_{XU}(λ)$ - Спирмен')
plt.plot(lambda_values, tau_XU, 'g-', linewidth=2, label='$τ_{XU}(λ)$ - Кендалл')
plt.xlabel('λ')
plt.ylabel('Коэффициент корреляции')
plt.title('Зависимости коэффициентов корреляции от λ: $r_{XU}(λ)$, $ρ_{XU}(λ)$, $τ_{XU}(λ)$')
plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.ylim(-0.1, 1.1)

# График 2: Зависимости коэффициентов корреляции r(X,V), ρ(X,V), τ(X,V) от λ
plt.subplot(2, 1, 2)
plt.plot(lambda_values, r_XV, 'b-', linewidth=2, label='$r_{XV}(λ)$ - Пирсон')
plt.plot(lambda_values, rho_XV, 'r-', linewidth=2, label='$ρ_{XV}(λ)$ - Спирмен')
plt.plot(lambda_values, tau_XV, 'g-', linewidth=2, label='$τ_{XV}(λ)$ - Кендалл')
plt.xlabel('λ')
plt.ylabel('Коэффициент корреляции')
plt.title('Зависимости коэффициентов корреляции от λ: $r_{XV}(λ)$, $ρ_{XV}(λ)$, $τ_{XV}(λ)$')
plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)

plt.tight_layout()
plt.show()

# Диаграммы рассеяния для крайних значений λ
print("\nДиаграммы рассеяния для крайних значений λ:")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# λ = 0
lam_0 = 0
V_0 = lam_0 * (X ** 3) + (1 - lam_0) * (Y ** 3)

# Диаграмма рассеяния X и V при λ = 0
axes[0, 0].scatter(X, V_0, alpha=0.6, color='blue', edgecolor='black', s=30)
axes[0, 0].set_xlabel('X')
axes[0, 0].set_ylabel('V')
axes[0, 0].set_title(f'Диаграмма рассеяния X и V при λ = {lam_0}')
axes[0, 0].grid(True, alpha=0.3)

# Диаграмма рассеяния рангов X и V при λ = 0
# Используем scipy.stats.rankdata согласно примечанию
rank_X_0 = stats.rankdata(X)
rank_V_0 = stats.rankdata(V_0)
axes[0, 1].scatter(rank_X_0, rank_V_0, alpha=0.6, color='red', edgecolor='black', s=30)
axes[0, 1].set_xlabel('Ранг X')
axes[0, 1].set_ylabel('Ранг V')
axes[0, 1].set_title(f'Диаграмма рассеяния рангов X и V при λ = {lam_0}')
axes[0, 1].grid(True, alpha=0.3)

# λ = 1
lam_1 = 1
V_1 = lam_1 * (X ** 3) + (1 - lam_1) * (Y ** 3)

# Диаграмма рассеяния X и V при λ = 1
axes[1, 0].scatter(X, V_1, alpha=0.6, color='green', edgecolor='black', s=30)
axes[1, 0].set_xlabel('X')
axes[1, 0].set_ylabel('V')
axes[1, 0].set_title(f'Диаграмма рассеяния X и V при λ = {lam_1}')
axes[1, 0].grid(True, alpha=0.3)

# Диаграмма рассеяния рангов X и V при λ = 1
rank_X_1 = stats.rankdata(X)
rank_V_1 = stats.rankdata(V_1)
axes[1, 1].scatter(rank_X_1, rank_V_1, alpha=0.6, color='purple', edgecolor='black', s=30)
axes[1, 1].set_xlabel('Ранг X')
axes[1, 1].set_ylabel('Ранг V')
axes[1, 1].set_title(f'Диаграмма рассеяния рангов X и V при λ = {lam_1}')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Вывод значений для крайних случаев
print("\nЗначения коэффициентов корреляции для крайних случаев:")

# λ = 0
print(f"\nПри λ = 0:")
print(f"V = Y³ (т.к. λ=0)")
r_XV_0, _ = stats.pearsonr(X, V_0)
rho_XV_0, _ = stats.spearmanr(X, V_0)
tau_XV_0, _ = stats.kendalltau(X, V_0)
print(f"r(X,V) = {r_XV_0:.4f}")
print(f"ρ(X,V) = {rho_XV_0:.4f}")
print(f"τ(X,V) = {tau_XV_0:.4f}")

# λ = 1
print(f"\nПри λ = 1:")
print(f"V = X³ (т.к. λ=1)")
r_XV_1, _ = stats.pearsonr(X, V_1)
rho_XV_1, _ = stats.spearmanr(X, V_1)
tau_XV_1, _ = stats.kendalltau(X, V_1)
print(f"r(X,V) = {r_XV_1:.4f}")
print(f"ρ(X,V) = {rho_XV_1:.4f}")
print(f"τ(X,V) = {tau_XV_1:.4f}")

# λ = 0.5
lam_mid = 0.5
U_mid = lam_mid * X + (1 - lam_mid) * Y
V_mid = lam_mid * (X ** 3) + (1 - lam_mid) * (Y ** 3)

r_XU_mid, _ = stats.pearsonr(X, U_mid)
rho_XU_mid, _ = stats.spearmanr(X, U_mid)
tau_XU_mid, _ = stats.kendalltau(X, U_mid)

r_XV_mid, _ = stats.pearsonr(X, V_mid)
rho_XV_mid, _ = stats.spearmanr(X, V_mid)
tau_XV_mid, _ = stats.kendalltau(X, V_mid)

print(f"\nПри λ = 0.5 (середина):")
print(f"Для пары (X, U):")
print(f"  r(X,U) = {r_XU_mid:.4f}")
print(f"  ρ(X,U) = {rho_XU_mid:.4f}")
print(f"  τ(X,U) = {tau_XU_mid:.4f}")
print(f"Для пары (X, V):")
print(f"  r(X,V) = {r_XV_mid:.4f}")
print(f"  ρ(X,V) = {rho_XV_mid:.4f}")
print(f"  τ(X,V) = {tau_XV_mid:.4f}")