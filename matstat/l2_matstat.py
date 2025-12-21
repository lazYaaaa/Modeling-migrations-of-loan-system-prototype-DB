import numpy as np
from scipy import stats

print("Задание 1\n\n")
# Задаем параметры варианта
np.random.seed(42) # Для воспроизводимости результатов

m_x, sigma_x = 5, 3
m_y, sigma_y = 5, 1
n1, n2 = 250, 250

# Генерация выборок
# Для нормального распределения используем scipy.stats.norm.rvs
X = stats.norm.rvs(loc=m_x, scale=sigma_x, size=n1)
Y = stats.norm.rvs(loc=m_y, scale=sigma_y, size=n2)

# Расчет выборочных характеристик
x_mean = np.mean(X)
x_var = np.var(X, ddof=1) # Исправленная (несмещенная) выборочная дисперсия
x_std = np.std(X, ddof=1)

y_mean = np.mean(Y)
y_var = np.var(Y, ddof=1)
y_std = np.std(Y, ddof=1)

print("Выборка X (теоретические: m=5, σ²=9):")
print(f"Выборочное среднее: {x_mean:.4f}")
print(f"Оценка дисперсии (s²): {x_var:.4f}")
print(f"Оценка с.к.о. (s): {x_std:.4f}")
print("\nВыборка Y (теоретические: m=5, σ²=1):")
print(f"Выборочное среднее: {y_mean:.4f}")
print(f"Оценка дисперсии (s²): {y_var:.4f}")
print(f"Оценка с.к.о. (s): {y_std:.4f}")

print("Задание 2\n\n")
import matplotlib.pyplot as plt

# Создаем фигуру с подграфиками
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
bins_list = [5, 10, 15, 20] # NBins = 5, 10, 15, 20

for ax, bins in zip(axes.flat, bins_list):
    # Строим гистограмму
    n, bins_edges, patches = ax.hist(X, bins=bins, density=False, alpha=0.7, color='skyblue', edgecolor='black')
    ax.set_title(f'Гистограмма для X (NBins = {bins})')
    ax.set_xlabel('Значение')
    ax.set_ylabel('Частота')
    # Добавляем теоретическую плотность для наглядности
    xmin, xmax = ax.get_xlim()
    x_plot = np.linspace(xmin, xmax, 100)
    # Для гистограммы частот теоретическую кривую не нормируем на частоту
    ax.plot(x_plot, stats.norm.pdf(x_plot, m_x, sigma_x) * n1 * (bins_edges[1] - bins_edges[0]), 'r-', linewidth=2, label='Теор. распр.')

plt.tight_layout()
plt.show()

print("Задание 3\n\n")
from scipy.stats import chisquare

def format_p_value(p_value):
    """Форматирует p-value: использует научную нотацию для маленьких значений"""
    if p_value < 0.0001:
        return f"{p_value:.2e}"
    else:
        return f"{p_value:.4f}"

def chi2_test_for_distribution(sample, dist_name, dist_params, bins_list, alpha=0.05):
    """
    Функция для проведения критерия хи-квадрат с автоматическим определением типа ошибки.
    """
    results = {}
    
    # Определяем, является ли проверяемая гипотеза ИСТИННОЙ
    is_true_hypothesis = (dist_name == 'norm' and dist_params == (m_x, sigma_x))

    for bins in bins_list:
        # Строим гистограмму, чтобы получить наблюдаемые частоты
        observed_freq, bin_edges = np.histogram(sample, bins=bins)

        # Вычисляем ожидаемые частоты для заданного распределения
        if dist_name == 'norm':
            loc, scale = dist_params
            cdf_values = stats.norm.cdf(bin_edges, loc=loc, scale=scale)
        elif dist_name == 'uniform':
            a, b = dist_params
            cdf_values = stats.uniform.cdf(bin_edges, loc=a, scale=b - a)
        elif dist_name == 'chi2':
            df = dist_params[0]
            cdf_values = stats.chi2.cdf(bin_edges, df=df)
        else:
            print(f"Неизвестное распределение: {dist_name}")
            continue

        expected_probs = np.diff(cdf_values)
        expected_freq = expected_probs * len(sample)

        # Объединяем интервалы, где ожидаемая частота < 5
        observed_combined = []
        expected_combined = []
        for i in range(len(observed_freq)):
            if expected_freq[i] < 5:
                # объединяем с соседним интервалом
                if i < len(observed_freq) - 1:
                    expected_freq[i + 1] += expected_freq[i]
                    observed_freq[i + 1] += observed_freq[i]
                else:
                    expected_combined[-1] += expected_freq[i]
                    observed_combined[-1] += observed_freq[i]
            else:
                observed_combined.append(observed_freq[i])
                expected_combined.append(expected_freq[i])

        # Проводим тест
        try:
            # нормализуем ожидаемые частоты, чтобы сумма совпадала с наблюдаемыми
            total_obs = sum(observed_combined)
            total_exp = sum(expected_combined)
            if total_exp > 0:
                expected_combined = [exp * total_obs / total_exp for exp in expected_combined]

            chi2_stat, p_value = chisquare(f_obs=observed_combined, f_exp=expected_combined, ddof=0)
            stat_decision = "H₀ отвергается" if p_value < alpha else "H₀ не отвергается"

            # ИСПРАВЛЕННАЯ ЛОГИКА ОПРЕДЕЛЕНИЯ ОШИБОК:
            if p_value < alpha:
                if is_true_hypothesis:
                    error = "Возможна ошибка I рода (ложное отклонение H₀)"
                else:
                    error = "Ошибок нет (правильно отвергли ложную H₀)"
            else:
                if is_true_hypothesis:
                    error = "Ошибок нет (правильно не отвергли верную H₀)"
                else:
                    error = "Возможна ошибка II рода (не отвергли ложную H₀)"

            # Сохраняем результат
            results[bins] = {
                'chi2_stat': chi2_stat,
                'p_value': p_value,
                'p_value_formatted': format_p_value(p_value),
                'stat_decision': stat_decision,
                'error': error
            }

        except Exception as e:
            print(f"Ошибка при расчете χ² для bins={bins}: {e}")
            continue

    return results


# Параметры
alpha = 0.05
bins_list = [5, 10, 15, 20]  # Добавлен NBins = 20

# Тест для H₀: X ~ N(5, 3)
results_3a = chi2_test_for_distribution(X, 'norm', (m_x, sigma_x), bins_list, alpha)

print("Задание 3а: H₀: X ~ N(5, 3)")
for bins, res in results_3a.items():
    print(f"NBins={bins}: χ² = {res['chi2_stat']:.4f}, p-value = {res['p_value_formatted']}, "
          f"Решение: {res['stat_decision']}, {res['error']}")

a_unif = m_x - 3*sigma_x
b_unif = m_x + 3*sigma_x

results_3b = chi2_test_for_distribution(X, 'uniform', (a_unif, b_unif), bins_list, alpha)

print("\nЗадание 3б: H₀: X ~ R(-4, 14)")
for bins, res in results_3b.items():
    print(f"NBins={bins}: χ² = {res['chi2_stat']:.4f}, p-value = {res['p_value_formatted']}, "
          f"Решение: {res['stat_decision']}, {res['error']}")

# --- Задание 3в ---
df_chi2 = 5
results_3c = chi2_test_for_distribution(X, 'chi2', (df_chi2,), bins_list, alpha)

print("\nЗадание 3в: H₀: X ~ χ²(5)")
for bins, res in results_3c.items():
    print(f"NBins={bins}: χ² = {res['chi2_stat']:.4f}, p-value = {res['p_value_formatted']}, "
          f"Решение: {res['stat_decision']}, {res['error']}")

print("Задание 4\n\n")
from scipy.stats import kstest

alpha = 0.05
results_4 = {}

# а) H₀: X ~ N(5, 3)
stat_ks_norm, pvalue_ks_norm = kstest(X, 'norm', args=(m_x, sigma_x))
results_4['X ~ N(5,3)'] = (stat_ks_norm, pvalue_ks_norm)

# б) H₀: X ~ R(a, b)
stat_ks_unif, pvalue_ks_unif = kstest(X, 'uniform', args=(a_unif, b_unif - a_unif))
results_4['X ~ R(-4,14)'] = (stat_ks_unif, pvalue_ks_unif)

# в) H₀: X ~ χ²(5)
df_chi2 = 5
stat_ks_chi2, pvalue_ks_chi2 = kstest(X, 'chi2', args=(df_chi2,))
results_4['X ~ χ²(5)'] = (stat_ks_chi2, pvalue_ks_chi2)

print("Задание 4: Критерий Колмогорова")
for dist_name, (stat, pval) in results_4.items():
    decision = "H₀ отвергается" if pval < alpha else "H₀ не отвергается"
    # Исправленная логика определения ошибок для KS-теста
    if pval < alpha:
        if dist_name == 'X ~ N(5,3)':
            error = "Возможна ошибка I рода"
        else:
            error = "Ошибок нет"
    else:
        if dist_name == 'X ~ N(5,3)':
            error = "Ошибок нет"
        else:
            error = "Возможна ошибка II рода"
    print(f"H₀: {dist_name}: D = {stat:.4f}, p-value = {format_p_value(pval)}, Решение: {decision}, {error}")
from statsmodels.distributions.empirical_distribution import ECDF

plt.figure(figsize=(10, 6))

# Эмпирическая функция распределения (ECDF) для X
ecdf_x = ECDF(X)
x_vals = np.linspace(min(X), max(X), 200)
plt.step(x_vals, ecdf_x(x_vals), where='post', label='ECDF X', color='blue')

# Теоретические CDF
plt.plot(x_vals, stats.norm.cdf(x_vals, m_x, sigma_x), label='CDF N(5,3)', color='red', linestyle='--')
plt.plot(x_vals, stats.uniform.cdf(x_vals, loc=a_unif, scale=b_unif - a_unif), label='CDF R(-4,14)', color='green', linestyle=':')
plt.plot(x_vals, stats.chi2.cdf(x_vals, df_chi2), label='CDF χ²(5)', color='orange', linestyle='-.')

plt.title('Сравнение ECDF выборки X с теоретическими CDF')
plt.xlabel('x')
plt.ylabel('F(x)')
plt.legend()
plt.grid(True)
plt.show()

print("Задание 5\n\n")
# Гистограммы
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.hist(X, bins=15, alpha=0.7, color='skyblue', edgecolor='black', density=True, label='X')
ax1.hist(Y, bins=15, alpha=0.7, color='lightcoral', edgecolor='black', density=True, label='Y')
ax1.set_title('Гистограммы X и Y')
ax1.set_xlabel('Значение')
ax1.set_ylabel('Плотность')
ax1.legend()

# ECDF
ax2.step(np.sort(X), np.arange(n1) / n1, where='post', label='ECDF X', color='blue')
ax2.step(np.sort(Y), np.arange(n2) / n2, where='post', label='ECDF Y', color='red')
ax2.set_title('ECDF X и Y')
ax2.set_xlabel('x')
ax2.set_ylabel('F(x)')
ax2.legend()

plt.tight_layout()
plt.show()
from scipy.stats import ks_2samp, ranksums
from statsmodels.stats.descriptivestats import sign_test

alpha = 0.05
results_5 = {}

# 1. Двухвыборочный критерий хи-квадрат (проверка однородности)
# Для этого нужно создать таблицу сопряженности. Сгруппируем данные по общим интервалам.
def two_sample_chi2(x, y, bins=10):
    # Определяем общие интервалы по обеим выборкам
    all_data = np.concatenate([x, y])
    bin_edges = np.histogram_bin_edges(all_data, bins=bins)
    
    # Частоты для X и Y в этих интервалах
    freq_x, _ = np.histogram(x, bins=bin_edges)
    freq_y, _ = np.histogram(y, bins=bin_edges)
    
    # Создаем таблицу сопряженности
    cont_table = np.array([freq_x, freq_y])
    
    # Применяем тест хи-квадрат для таблиц сопряженности
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(cont_table, correction=False)
    return chi2_stat, p_value

chi2_stat_2samp, p_value_chi2_2samp = two_sample_chi2(X, Y, bins=10)
results_5['Chi-squared'] = ('X и Y однородны', chi2_stat_2samp, p_value_chi2_2samp)

# 2. Двухвыборочный критерий Колмогорова-Смирнова
ks_stat_2samp, p_value_ks_2samp = ks_2samp(X, Y)
results_5['KS-test'] = ('F_X(t) = F_Y(t)', ks_stat_2samp, p_value_ks_2samp)

# 3. Знаковый критерий (Sign test)
# Проверяем гипотезу о равенстве медиан.
# Объединяем выборки и смотрим, из какой выборки элемент больше.
# H₀: Медианы равны.
sign_stat, p_value_sign = sign_test(X, Y)
results_5['Sign test'] = ('Медианы равны', sign_stat, p_value_sign)

# 4. U-критерий Манна-Уитни-Уилкоксона (ранговый критерий)
# H₀: Распределения X и Y одинаковы.
u_stat, p_value_u = ranksums(X, Y)
results_5['U-test'] = ('P(X > Y) = P(Y > X)', u_stat, p_value_u)

print("Задание 5: Двухвыборочные критерии")
print(f"Уровень значимости α = {alpha}")
print("+" + "-"*90 + "+")
for test_name, (h0, stat, pval) in results_5.items():
    decision = "H₀ отвергается" if pval < alpha else "H₀ не отвергается"
    # Для двухвыборочных тестов H₀ всегда ложна (распределения разные), поэтому:
    if pval < alpha:
        error = "Ошибок нет"  # Правильно отвергли ложную H₀
    else:
        error = "Возможна ошибка II рода"  # Не отвергли ложную H₀
    print(f"| {test_name:<12} | H₀: {h0:<25} | Стат.: {stat:7.4f} | p-value: {format_p_value(pval):<8} | Решение: {decision:<15} | {error}")
print("+" + "-"*90 + "+")