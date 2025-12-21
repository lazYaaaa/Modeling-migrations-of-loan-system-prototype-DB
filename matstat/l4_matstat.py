import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Для отображения символов
import warnings
warnings.filterwarnings('ignore')

# =============================================
# 1. ИСХОДНЫЕ ДАННЫЕ
# =============================================

# Параметры распределений для варианта 12
np.random.seed(5149)  # Для воспроизводимости

# X ~ N(5, 3) - параметры: mean=5, sigma=sqrt(3)
mu_x, sigma_x = 5, np.sqrt(3)

# Y ~ N(5, 1) - параметры: mean=5, sigma=1
mu_y, sigma_y = 5, 1

# Объем выборки
n = 250

# Генерация случайных чисел (согласно примечанию)
# В примечании указано: scipy.stats: uniform.rvs, norm.rvs, chi2.rvs
X = stats.norm.rvs(loc=mu_x, scale=sigma_x, size=n)  # norm.rvs для нормального распределения
Y = stats.norm.rvs(loc=mu_y, scale=sigma_y, size=n)

print("=" * 60)
print("ЛАБОРАТОРНАЯ РАБОТА №4 - ВАРИАНТ 12")
print("=" * 60)

print("\n1. ИСХОДНЫЕ ДАННЫЕ")
print("-" * 40)

# Таблица исходных данных
fig, ax = plt.subplots(figsize=(12, 2))
ax.axis('tight')
ax.axis('off')

table_data = [
    ['СВ', 'Распределение', 'Параметры', 'Математическое\nожидание, m_i', 'Дисперсия, σ²', 'Объем выборки, n'],
    ['X', 'N(5,3)', 'N(m,σ)', '5', '3', ''],
    ['Y', 'N(5,1)', 'N(m,σ)', '5', '1', '250']
]

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                colWidths=[0.1, 0.15, 0.12, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Форматирование шапки таблицы
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Форматирование остальных ячеек
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        table[(i, j)].set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

plt.title('Характеристики наблюдаемых случайных величин', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

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

# Функция для форматирования p-value
def format_p_value(p):
    """Форматирует p-value: если < 0.0001, то в научной записи, иначе в десятичной дроби"""
    if p < 0.0001:
        return f"{p:.2e}"
    else:
        return f"{p:.4f}"

alpha = 0.05

# Для Пирсона
pearson_decision = "H₀ отвергается" if pearson_p < alpha else "H₀ принимается"
theoretical_pearson_zero = True
if pearson_p < alpha:
    pearson_error = "Ошибка I рода" if theoretical_pearson_zero else "Нет ошибки"
else:
    pearson_error = "Нет ошибки" if theoretical_pearson_zero else "Ошибка II рода"

# Для Спирмена
spearman_decision = "H₀ отвергается" if spearman_p < alpha else "H₀ принимается"
if spearman_p < alpha:
    spearman_error = "Ошибка I рода" if theoretical_pearson_zero else "Нет ошибки"
else:
    spearman_error = "Нет ошибки" if theoretical_pearson_zero else "Ошибка II рода"

# Для Кендалла
kendall_decision = "H₀ отвергается" if kendall_p < alpha else "H₀ принимается"
if kendall_p < alpha:
    kendall_error = "Ошибка I рода" if theoretical_pearson_zero else "Нет ошибки"
else:
    kendall_error = "Нет ошибки" if theoretical_pearson_zero else "Ошибка II рода"

# Выборочные характеристики - графическая таблица
fig, ax = plt.subplots(figsize=(14, 2))
ax.axis('tight')
ax.axis('off')

sample_data = [
    ['СВ', 'Среднее, x̄', 'Оценка дисперсии, s²', 'КК по Пирсону, r_XY', 'КК по Спирмену, ρ_XY', 'КК по Кендаллу, τ_XY'],
    ['X', f'{mean_x:.4f}', f'{var_x:.4f}', '', '', ''],
    ['Y', f'{mean_y:.4f}', f'{var_y:.4f}', f'{pearson_r:.4f}', f'{spearman_r:.4f}', f'{kendall_tau:.4f}']
]

table_sample = ax.table(cellText=sample_data, cellLoc='center', loc='center',
                       colWidths=[0.1, 0.15, 0.18, 0.18, 0.18, 0.18])
table_sample.auto_set_font_size(False)
table_sample.set_fontsize(9)
table_sample.scale(1, 2.5)

# Форматирование
for i in range(len(sample_data[0])):
    table_sample[(0, i)].set_facecolor('#2196F3')
    table_sample[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(sample_data)):
    for j in range(len(sample_data[0])):
        table_sample[(i, j)].set_facecolor('#e3f2fd' if i % 2 == 0 else 'white')

plt.title('Выборочные характеристики', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

pearson_p_formatted = format_p_value(pearson_p)
spearman_p_formatted = format_p_value(spearman_p)
kendall_p_formatted = format_p_value(kendall_p)

# Таблица проверки значимости коэффициентов корреляции - графическая
fig, ax = plt.subplots(figsize=(12, 2.5))
ax.axis('tight')
ax.axis('off')

significance_data = [
    ['Статистическая гипотеза, H₀', 'p-value', 'Статистическое решение при α = 0.05', 'Ошибка стат. решения'],
    ['H₀: r_XY = 0', pearson_p_formatted, pearson_decision, pearson_error],
    ['H₀: ρ_XY = 0', spearman_p_formatted, spearman_decision, spearman_error],
    ['H₀: τ_XY = 0', kendall_p_formatted, kendall_decision, kendall_error]
]

table_sig = ax.table(cellText=significance_data, cellLoc='center', loc='center',
                    colWidths=[0.25, 0.2, 0.27, 0.25])
table_sig.auto_set_font_size(False)
table_sig.set_fontsize(9)
table_sig.scale(1, 2.5)

# Форматирование
for i in range(len(significance_data[0])):
    table_sig[(0, i)].set_facecolor('#FF9800')
    table_sig[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(significance_data)):
    for j in range(len(significance_data[0])):
        table_sig[(i, j)].set_facecolor('#fff3e0' if i % 2 == 0 else 'white')

print("\n2. ВИЗУАЛЬНОЕ ПРЕДСТАВЛЕНИЕ ДВУМЕРНОЙ ВЫБОРКИ")
print("-" * 40)

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

plt.title('Диаграмма рассеяния случайных величин X и Y', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("Статистическая гипотеза: X и Y независимы")

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

# Создание графической таблицы эмпирической сопряженности
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('tight')
ax.axis('off')

# Подготовка данных для таблицы
x_labels = [f"[{x_bins[i]:.1f};\n{x_bins[i+1]:.1f})" if i < num_bins-1 else f"[{x_bins[i]:.1f};\n{x_bins[i+1]:.1f}]" 
            for i in range(num_bins)]
y_labels = [f"[{y_bins[i]:.1f};\n{y_bins[i+1]:.1f})" if i < num_bins-1 else f"[{y_bins[i]:.1f};\n{y_bins[i+1]:.1f}]" 
            for i in range(num_bins)]

# Формирование данных таблицы
table_data_emp = [['Y \\ X'] + x_labels]
for i in range(num_bins):
    row = [y_labels[i]]
    for j in range(num_bins):
        row.append(str(int(contingency_table[i, j])))
    table_data_emp.append(row)

table_emp = ax.table(cellText=table_data_emp, cellLoc='center', loc='center',
                    colWidths=[0.15] + [0.17]*num_bins)
table_emp.auto_set_font_size(False)
table_emp.set_fontsize(8)
table_emp.scale(1, 2)

# Форматирование
for i in range(len(x_labels) + 1):
    table_emp[(0, i)].set_facecolor('#4CAF50')
    table_emp[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(table_data_emp)):
    table_emp[(i, 0)].set_facecolor('#4CAF50')
    table_emp[(i, 0)].set_text_props(weight='bold', color='white')
    for j in range(1, len(table_data_emp[0])):
        table_emp[(i, j)].set_facecolor('#e8f5e9' if i % 2 == 0 else 'white')

plt.title('Эмпирическая таблица сопряженности', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

# Проверка гипотезы о независимости с помощью критерия хи-квадрат
# Используем scipy.stats.chi2_contingency согласно примечанию
chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)

# Графическая таблица теоретической сопряженности
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('tight')
ax.axis('off')

# Формирование данных таблицы ожидаемых частот
table_data_theo = [['Y \\ X'] + x_labels]
for i in range(num_bins):
    row = [y_labels[i]]
    for j in range(num_bins):
        row.append(f'{expected[i, j]:.2f}')
    table_data_theo.append(row)

table_theo = ax.table(cellText=table_data_theo, cellLoc='center', loc='center',
                     colWidths=[0.15] + [0.17]*num_bins)
table_theo.auto_set_font_size(False)
table_theo.set_fontsize(8)
table_theo.scale(1, 2)

# Форматирование
for i in range(len(x_labels) + 1):
    table_theo[(0, i)].set_facecolor('#2196F3')
    table_theo[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(table_data_theo)):
    table_theo[(i, 0)].set_facecolor('#2196F3')
    table_theo[(i, 0)].set_text_props(weight='bold', color='white')
    for j in range(1, len(table_data_theo[0])):
        table_theo[(i, j)].set_facecolor('#e3f2fd' if i % 2 == 0 else 'white')

plt.title('Теоретическая таблица сопряженности (ожидаемые частоты)', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

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

# Графическая таблица проверки гипотезы о независимости
fig, ax = plt.subplots(figsize=(12, 2.5))
ax.axis('tight')
ax.axis('off')

chi2_data = [
    ['Выборочное значение статистики критерия', 'p-value', 'Статистическое решение при α = 0.05', 'Ошибка стат. решения'],
    [f'{chi2_stat:.4f}', p_formatted, chi2_decision, chi2_error]
]

table_chi2 = ax.table(cellText=chi2_data, cellLoc='center', loc='center',
                     colWidths=[0.27, 0.2, 0.27, 0.25])
table_chi2.auto_set_font_size(False)
table_chi2.set_fontsize(9)
table_chi2.scale(1, 2.5)

# Форматирование
for i in range(len(chi2_data[0])):
    table_chi2[(0, i)].set_facecolor('#9C27B0')
    table_chi2[(0, i)].set_text_props(weight='bold', color='white')

for j in range(len(chi2_data[0])):
    table_chi2[(1, j)].set_facecolor('#f3e5f5')

plt.title('Проверка гипотезы о независимости', fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("ПРИМЕЧАНИЯ:")
print("1. Для группировки использована функция numpy.histogram2d")
print("2. Для проверки гипотезы использована функция scipy.stats.chi2_contingency")
print("3. Число интервалов: 5x5 = 25 ячеек")
print("4. Степени свободы: (5-1)x(5-1) = 16")
print(f"5. Ожидаемые частоты в каждой ячейке должны быть >=5: {'Да' if np.all(expected >= 5) else 'Нет'}")
print("=" * 60)

# =============================================
# 4. ИССЛЕДОВАНИЕ КОРРЕЛЯЦИОННОЙ СВЯЗИ
# =============================================

print("\n4. ИССЛЕДОВАНИЕ КОРРЕЛЯЦИОННОЙ СВЯЗИ")
print("-" * 40)
print("U = lambda*X + (1-lambda)*Y, lambda в [0; 1]")
print("V = lambda*X^3 + (1-lambda)*Y^3, lambda в [0; 1]")

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
plt.plot(lambda_values, r_XU, 'b-', linewidth=2, label='r_XU(λ) - Pearson')
plt.plot(lambda_values, rho_XU, 'r-', linewidth=2, label='rho_XU(λ) - Spearman')
plt.plot(lambda_values, tau_XU, 'g-', linewidth=2, label='tau_XU(λ) - Kendall')
plt.xlabel('λ')
plt.ylabel('Correlation coefficient')
plt.title('Dependence of correlation coefficients on λ: r_XU(λ), rho_XU(λ), tau_XU(λ)')
plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.ylim(-0.1, 1.1)

# График 2: Зависимости коэффициентов корреляции r(X,V), ρ(X,V), τ(X,V) от λ
plt.subplot(2, 1, 2)
plt.plot(lambda_values, r_XV, 'b-', linewidth=2, label='r_XV(λ) - Pearson')
plt.plot(lambda_values, rho_XV, 'r-', linewidth=2, label='rho_XV(λ) - Spearman')
plt.plot(lambda_values, tau_XV, 'g-', linewidth=2, label='tau_XV(λ) - Kendall')
plt.xlabel('λ')
plt.ylabel('Correlation coefficient')
plt.title('Dependence of correlation coefficients on λ: r_XV(λ), rho_XV(λ), tau_XV(λ)')
plt.grid(True, alpha=0.3)
plt.legend(loc='best')
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)

plt.tight_layout()
plt.show()

# Диаграммы рассеяния для крайних значений λ
print("\nScatter plots for extreme values of λ:")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# λ = 0
lam_0 = 0
V_0 = lam_0 * (X ** 3) + (1 - lam_0) * (Y ** 3)

# Диаграмма рассеяния X и V при λ = 0
axes[0, 0].scatter(X, V_0, alpha=0.6, color='blue', edgecolor='black', s=30)
axes[0, 0].set_xlabel('X')
axes[0, 0].set_ylabel('V')
axes[0, 0].set_title(f'Scatter plot X and V at λ = {lam_0}')
axes[0, 0].grid(True, alpha=0.3)

# Диаграмма рассеяния рангов X и V при λ = 0
# Используем scipy.stats.rankdata согласно примечанию
rank_X_0 = stats.rankdata(X)
rank_V_0 = stats.rankdata(V_0)
axes[0, 1].scatter(rank_X_0, rank_V_0, alpha=0.6, color='red', edgecolor='black', s=30)
axes[0, 1].set_xlabel('Rank X')
axes[0, 1].set_ylabel('Rank V')
axes[0, 1].set_title(f'Scatter plot of ranks X and V at λ = {lam_0}')
axes[0, 1].grid(True, alpha=0.3)

# λ = 1
lam_1 = 1
V_1 = lam_1 * (X ** 3) + (1 - lam_1) * (Y ** 3)

# Диаграмма рассеяния X и V при λ = 1
axes[1, 0].scatter(X, V_1, alpha=0.6, color='green', edgecolor='black', s=30)
axes[1, 0].set_xlabel('X')
axes[1, 0].set_ylabel('V')
axes[1, 0].set_title(f'Scatter plot X and V at λ = {lam_1}')
axes[1, 0].grid(True, alpha=0.3)

# Диаграмма рассеяния рангов X и V при λ = 1
rank_X_1 = stats.rankdata(X)
rank_V_1 = stats.rankdata(V_1)
axes[1, 1].scatter(rank_X_1, rank_V_1, alpha=0.6, color='purple', edgecolor='black', s=30)
axes[1, 1].set_xlabel('Rank X')
axes[1, 1].set_ylabel('Rank V')
axes[1, 1].set_title(f'Scatter plot of ranks X and V at λ = {lam_1}')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Вывод значений для крайних случаев
print("\nCorrelation coefficient values for extreme cases:")

# λ = 0
print(f"\nFor λ = 0:")
print(f"V = Y^3 (as λ=0)")
r_XV_0, _ = stats.pearsonr(X, V_0)
rho_XV_0, _ = stats.spearmanr(X, V_0)
tau_XV_0, _ = stats.kendalltau(X, V_0)
print(f"r(X,V) = {r_XV_0:.4f}")
print(f"rho(X,V) = {rho_XV_0:.4f}")
print(f"tau(X,V) = {tau_XV_0:.4f}")

# λ = 1
print(f"\nFor λ = 1:")
print(f"V = X^3 (as λ=1)")
r_XV_1, _ = stats.pearsonr(X, V_1)
rho_XV_1, _ = stats.spearmanr(X, V_1)
tau_XV_1, _ = stats.kendalltau(X, V_1)
print(f"r(X,V) = {r_XV_1:.4f}")
print(f"rho(X,V) = {rho_XV_1:.4f}")
print(f"tau(X,V) = {tau_XV_1:.4f}")

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

print(f"\nFor λ = 0.5 (middle):")
print(f"For pair (X, U):")
print(f"  r(X,U) = {r_XU_mid:.4f}")
print(f"  rho(X,U) = {rho_XU_mid:.4f}")
print(f"  tau(X,U) = {tau_XU_mid:.4f}")
print(f"For pair (X, V):")
print(f"  r(X,V) = {r_XV_mid:.4f}")
print(f"  rho(X,V) = {rho_XV_mid:.4f}")
print(f"  tau(X,V) = {tau_XV_mid:.4f}")
