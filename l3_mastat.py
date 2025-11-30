import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd

print("Лабораторная работа №3")
print("«Однофакторный дисперсионный анализ»")
print("Студента Лазарева Я.О. группы Б23-514")
print("Вариант №12\n")

# Параметры варианта 12
np.random.seed(42)

# Генерация данных согласно варианту 12
n1, n2, n3, n4 = 200, 250, 200, 200

X1 = np.random.normal(loc=5, scale=3, size=n1)
X2 = np.random.normal(loc=5, scale=1, size=n2)
X3 = np.random.normal(loc=5, scale=5, size=n3)
X4 = np.random.normal(loc=5, scale=5, size=n4)

print("1. Исходные данные")
print("Характеристики наблюдаемых случайных величин:")
print("СВ     Распределение   Параметры   Математическое   Дисперсия   Объем")
print("                                 ожидание, m_i              выборки, n_i")
print("X1     N(5, 3)         m=5,σ=3          5              9         200")
print("X2     N(5, 1)         m=5,σ=1          5              1         250") 
print("X3     N(5, 5)         m=5,σ=5          5             25         200")
print("X4     N(5, 5)         m=5,σ=5          5             25         200")
print("Количество случайных величин k = 4\n")

# Выборочные характеристики
def calculate_sample_stats(data, name):
    n = len(data)
    mean = np.mean(data)
    var = np.var(data, ddof=1)
    std = np.std(data, ddof=1)
    return n, mean, var, std

n1, mean1, var1, std1 = calculate_sample_stats(X1, "X1")
n2, mean2, var2, std2 = calculate_sample_stats(X2, "X2") 
n3, mean3, var3, std3 = calculate_sample_stats(X3, "X3")
n4, mean4, var4, std4 = calculate_sample_stats(X4, "X4")

all_data = np.concatenate([X1, X2, X3, X4])
n_total, mean_pooled, var_pooled, std_pooled = calculate_sample_stats(all_data, "Pooled")

print("Выборочные характеристики:")
print("СВ     Среднее     Оценка дисперсии   Оценка с.к.о.")
print(f"X1     {mean1:.3f}        {var1:.3f}             {std1:.3f}")
print(f"X2     {mean2:.3f}        {var2:.3f}             {std2:.3f}")
print(f"X3     {mean3:.3f}        {var3:.3f}             {std3:.3f}")
print(f"X4     {mean4:.3f}        {var4:.3f}             {std4:.3f}")
print(f"Pooled {mean_pooled:.3f}        {var_pooled:.3f}             {std_pooled:.3f}\n")

# Визуальное представление выборок
plt.figure(figsize=(10, 6))
data_to_plot = [X1, X2, X3, X4]
plt.boxplot(data_to_plot, labels=['X1', 'X2', 'X3', 'X4'])
plt.title('Диаграммы Box-and-Whisker')
plt.ylabel('Значения')
plt.grid(True, alpha=0.3)
plt.show()

# Проверка условия применимости дисперсионного анализа
print("3. Проверка условия применимости дисперсионного анализа")
print("Статистическая гипотеза: H₀: σ₁² = σ₂² = σ₃² = σ₄²")

bartlett_stat, bartlett_p = stats.bartlett(X1, X2, X3, X4)
alpha = 0.05

if bartlett_p < alpha:
    decision = "H₀ отвергается"
    error_type = "1 рода"
else:
    decision = "H₀ принимается" 
    error_type = "2 рода"

print("Критерий Бартлетта:")
print("Выборочное значение   p-value   Статистическое   Ошибка стат.")
print("статистики критерия             решение при α=0.05   решения")
print(f"{bartlett_stat:.3f}              {bartlett_p:.3f}    {decision:15}  {error_type}\n")

# Однофакторный дисперсионный анализ
print("4. Однофакторный дисперсионный анализ")

groups = []
groups.extend(['X1'] * n1)
groups.extend(['X2'] * n2) 
groups.extend(['X3'] * n3)
groups.extend(['X4'] * n4)

f_stat, p_value = stats.f_oneway(X1, X2, X3, X4)

k = 4
n_total = n1 + n2 + n3 + n4
grand_mean = np.mean(all_data)

SS_between = (n1 * (mean1 - grand_mean)**2 + 
              n2 * (mean2 - grand_mean)**2 +
              n3 * (mean3 - grand_mean)**2 + 
              n4 * (mean4 - grand_mean)**2)

SS_within = ((n1 - 1) * var1 + (n2 - 1) * var2 + (n3 - 1) * var3 + (n4 - 1) * var4)
SS_total = SS_between + SS_within

MS_between = SS_between / (k - 1)
MS_within = SS_within / (n_total - k)

eta_squared = SS_between / SS_total
eta = np.sqrt(eta_squared)

print("Таблица дисперсионного анализа:")
print("Источник вариации    Показатель вариации   Число степеней   Несмещённая оценка")
print("                                       свободы")
print(f"Группировочный      D_b* = {SS_between/n_total:.3f}        K-1 = {k-1}        n/(K-1)*D_b* = {MS_between:.3f}")
print(f"признак")
print(f"Остаточные          D_w* = {SS_within/n_total:.3f}       n-K = {n_total-k}       n/(n-K)*D_w* = {MS_within:.3f}")  
print(f"признаки")
print(f"Все признаки        D_X* = {SS_total/n_total:.3f}       n-1 = {n_total-1}       n/(n-1)*D_X* = {var_pooled:.3f}")
print()

print(f"Эмпирический коэффициент детерминации η² = {eta_squared:.3f}")
print(f"Эмпирическое корреляционное отношение η = {eta:.3f}")

print("\nСтатистическая гипотеза: H₀: m₁ = m₂ = m₃ = m₄")

if p_value < alpha:
    anova_decision = "H₀ отвергается"
    anova_error_type = "1 рода" 
else:
    anova_decision = "H₀ принимается"
    anova_error_type = "2 рода"

print("Однофакторный дисперсионный анализ:")
print("Выборочное значение   p-value   Статистическое   Ошибка стат.")
print("статистики критерия             решение при α=0.05   решения")
print(f"{f_stat:.3f}               {p_value:.3f}    {anova_decision:15}  {anova_error_type}\n")

# Метод линейных контрастов
print("5. Метод линейных контрастов")

def confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    h = sem * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - h, mean + h

ci1 = confidence_interval(X1)
ci2 = confidence_interval(X2)
ci3 = confidence_interval(X3) 
ci4 = confidence_interval(X4)

print("Доверительные интервалы для m₁,..., mₖ (95%):")
print("СВ     Среднее     Нижняя граница   Верхняя граница")
print(f"X1     {ci1[0]:.3f}        {ci1[1]:.3f}            {ci1[2]:.3f}")
print(f"X2     {ci2[0]:.3f}        {ci2[1]:.3f}            {ci2[2]:.3f}")
print(f"X3     {ci3[0]:.3f}        {ci3[1]:.3f}            {ci3[2]:.3f}")
print(f"X4     {ci4[0]:.3f}        {ci4[1]:.3f}            {ci4[2]:.3f}")

# Визуализация доверительных интервалов
plt.figure(figsize=(10, 6))
means = [ci1[0], ci2[0], ci3[0], ci4[0]]
lower_bounds = [ci1[1], ci2[1], ci3[1], ci4[1]]
upper_bounds = [ci1[2], ci2[2], ci3[2], ci4[2]]
x_pos = np.arange(len(means))

plt.errorbar(x_pos, means, yerr=[np.array(means) - np.array(lower_bounds), 
                                np.array(upper_bounds) - np.array(means)], 
             fmt='o', capsize=5, capthick=2)
plt.xticks(x_pos, ['X1', 'X2', 'X3', 'X4'])
plt.ylabel('Значения')
plt.title('Доверительные интервалы для средних')
plt.grid(True, alpha=0.3)
plt.show()

# Попарные сравнения методом Тьюки - ИСПРАВЛЕННАЯ ЧАСТЬ
print("\nПопарные сравнения mᵢ и mⱼ:")

# Подготовка данных для метода Тьюки
tukey_data = pd.DataFrame({
    'values': all_data,
    'groups': groups
})

# Выполнение попарных сравнений
tukey_result = pairwise_tukeyhsd(tukey_data['values'], tukey_data['groups'], alpha=0.05)

# Альтернативный способ получения результатов Тьюки
print("Гипотеза           Разность      p-value   Статистическое   Ошибка стат.")
print("                   средних                 решение при       решения")
print("                                  α=0.05")

# Получаем результаты в виде DataFrame для более надежного доступа
tukey_df = tukey_result.summary().as_csv()
tukey_lines = tukey_df.split('\n')[2:]  # Пропускаем заголовки

comparisons = [
    ('X1', 'X2'),
    ('X1', 'X3'), 
    ('X1', 'X4'),
    ('X2', 'X3'),
    ('X2', 'X4'),
    ('X3', 'X4')
]

# Простой способ - используем t-тест для попарных сравнений
from scipy.stats import ttest_ind

print("\nПопарные сравнения (t-тест с поправкой Бонферрони):")
print("Гипотеза           t-статистика   p-value   Статистическое   Ошибка стат.")
print("                                                   решение при       решения")
print("                                                   α=0.05")

alpha_bonferroni = 0.05 / 6  # Поправка Бонферрони для 6 сравнений

for i, (group1, group2) in enumerate(comparisons):
    if group1 == 'X1': data1 = X1
    elif group1 == 'X2': data1 = X2
    elif group1 == 'X3': data1 = X3
    else: data1 = X4
        
    if group2 == 'X1': data2 = X1
    elif group2 == 'X2': data2 = X2
    elif group2 == 'X3': data2 = X3
    else: data2 = X4
    
    t_stat, p_val = ttest_ind(data1, data2, equal_var=False)
    mean_diff = np.mean(data1) - np.mean(data2)
    
    if p_val < alpha_bonferroni:
        decision = "H₀ отвергается"
        error_type = "1 рода"
    else:
        decision = "H₀ принимается" 
        error_type = "2 рода"
        
    print(f"H₀: m{group1[-1]}=m{group2[-1]}   {t_stat:10.4f}    {p_val:8.4f}    {decision:15}  {error_type}")

# Также выведем результаты Тьюки в их исходном формате
print("\nРезультаты теста Тьюки (HSD):")
print(tukey_result)

print("\nАнализ завершен!")