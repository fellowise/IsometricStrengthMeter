import numpy as np
import matplotlib.pyplot as plt

# Starting
time = np.arange(0, 10, 0.2)

rising = np.array([0, 122, 254, 356, 455])
decline = np.array([444, 431, 412, 401, 403, 398, 387, 380, 371, 362, 358, 341, 338, 333, 312])
fullsignal = []
samplesize = rising.size + decline.size

for i in range(samplesize):
    if i < rising.size:
        fullsignal.append(rising[i])
    else:
        fullsignal.append(decline[i - rising.size])

print(fullsignal)

# Ajuste o vetor time para ter o mesmo tamanho que fullsignal
time = time[:len(fullsignal)]

# Encontrar o índice do pico
peak_index = np.argmax(fullsignal)
peak_time = time[peak_index]
peak_value = fullsignal[peak_index]

# Calcular a derivada média do início ao pico
derivative_start_to_peak = np.mean(np.gradient(fullsignal[:peak_index], time[:peak_index]))

# Calcular a derivada média do pico ao fim do sinal
derivative_peak_to_end = np.mean(np.gradient(fullsignal[peak_index:], time[peak_index:]))

# Arredondar as derivadas para uma casa decimal
derivative_start_to_peak = round(derivative_start_to_peak, 1)
derivative_peak_to_end = round(derivative_peak_to_end, 1)

# Mostrar informações
print(f"Ponto de pico: Tempo = {peak_time}, Valor = {peak_value}")
print(f"Derivada média do início ao pico: {derivative_start_to_peak}")
print(f"Derivada média do pico ao fim do sinal: {derivative_peak_to_end}")

# Criação do gráfico
plt.plot(time, fullsignal, label='Full Signal')
plt.scatter(peak_time, peak_value, color='red', label='Pico')
# Adicionar informações sobre as derivadas
plt.text(peak_time, peak_value, f'Pico\nTempo: {peak_time}\nValor: {peak_value}', verticalalignment='bottom', horizontalalignment='right', color='red')
plt.text(time[0], fullsignal[0], f'Derivada média do início ao pico: {derivative_start_to_peak}', verticalalignment='bottom', horizontalalignment='left', color='blue')
plt.text(time[-1], fullsignal[-1], f'Derivada média do pico ao fim do sinal: {derivative_peak_to_end}', verticalalignment='bottom', horizontalalignment='right', color='green')
# Ademais informações do gráfico
plt.xlabel('Time')
plt.ylabel('Strength (N)')
plt.title('Strength Development')
plt.legend()
plt.show()