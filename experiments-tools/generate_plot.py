import csv
import matplotlib.pyplot as plt
import statistics

def leggi_elapsed_da_csv(file_csv):
    elapsed = []
    with open(file_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                elapsed.append(float(row['elapsed']))
            except (ValueError, KeyError):
                continue
    return elapsed

def genera_grafici(elapsed_complete, elapsed_less_primary):
    # Statistiche
    # media = statistics.mean(elapsed)
    # massimo = max(elapsed)
    # minimo = min(elapsed)
    # print(f"Media: {media:.6f}, Max: {massimo:.6f}, Min: {minimo:.6f}")
    
    # Grafico a linee
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    elapsed = elapsed_less_primary
    # plt.plot(elapsed_complete, marker='o', linestyle='-', color='red')
    # plt.plot(elapsed_less_primary, marker='o', linestyle='-', color='blue')
    # plt.title('Tempi di esecuzione (elapsed)')
    # plt.xlabel('Indice campione')
    # plt.ylabel('Tempo (secondi)')
    #plt.ylim(0.01, 0.1) # Set x-axis
    plt.plot(elapsed, marker='o', linestyle='-', color='blue')
    plt.title('Tempi di esecuzione (elapsed)')
    plt.xlabel('Indice campione')
    plt.ylabel('Tempo (secondi)')
    #plt.ylim(0.01, 0.1) # Set x-axis

    plt.grid(True)

    # Istogramma
    plt.subplot(1, 2, 2)
    plt.hist(elapsed, bins=20, color='green', edgecolor='black')
    plt.title('Distribuzione dei tempi')
    plt.xlabel('Tempo (secondi)')
    plt.ylabel('Frequenza')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("./plots/grafico_tempi.png")
    #plt.show()

def main():
    #/home/mariachiara/raidd-app/docker/samothrace-pseudonymization/docker/src/experiments_MT/L0n4t2m1_L1n3t2m0/test/split-manual.csv
    PATH_TEST = "../docker/src/experiments_MT/L0n5t3m1_L1n4t2m1_L2n3t2m0/test/"
    file_input_complete = "split-manual_complete.csv" 
    file_input_less_primary = "split-manual.csv" 
    file_input = "retrive-manual.csv"
    elapsed_complete = leggi_elapsed_da_csv(PATH_TEST + file_input_complete)
    elapsed_less_primary = leggi_elapsed_da_csv(PATH_TEST + file_input_less_primary)
    #elapsed = leggi_elapsed_da_csv(PATH_TEST + file_input)
    
    # if not elapsed:
    #     print("Nessun dato valido trovato.")
    #     return

    genera_grafici(elapsed_complete, elapsed_less_primary)

if __name__ == '__main__':
    main()
