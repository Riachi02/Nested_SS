import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import re
from collections import defaultdict

class SecretSharingAnalyzer:
    def __init__(self, base_directory):
        """
        Inizializza l'analizzatore per esperimenti di secret sharing
        
        Args:
            base_directory: Directory principale contenente gli esperimenti
        """
        self.base_directory = Path(base_directory)
        self.data = defaultdict(lambda: defaultdict(dict))
        
    def load_data(self):
        """Carica tutti i dati dai file CSV nella struttura annidata"""
        print("Caricamento dati in corso...")
        
        for exp_dir in self.base_directory.iterdir():
            if not exp_dir.is_dir():
                continue
                
            experiment_name = exp_dir.name
            print(f"Processando esperimento: {experiment_name}")
            
            for size_dir in exp_dir.iterdir():
                if not size_dir.is_dir():
                    continue
                    
                file_size = size_dir.name
                
                # Carica split-manual.csv
                split_file = size_dir / "split-manual.csv"
                if split_file.exists():
                    df_split = pd.read_csv(split_file)
                    self.data[experiment_name][file_size]['split'] = df_split['elapsed'].values
                
                # Carica retrieve-manual.csv
                retrieve_file = size_dir / "retrieve-manual.csv"
                if retrieve_file.exists():
                    df_retrieve = pd.read_csv(retrieve_file)
                    self.data[experiment_name][file_size]['retrieve'] = df_retrieve['elapsed'].values
        
        print(f"Dati caricati per {len(self.data)} esperimenti")
        
    def parse_experiment_name(self, exp_name):
        """Estrae parametri dal nome dell'esperimento (shares, livelli)"""
        # Cerca pattern come "shares_X_levels_Y" o simili
        shares_match = re.search(r'shares?[_-]?(\d+)', exp_name, re.IGNORECASE)
        levels_match = re.search(r'levels?[_-]?(\d+)', exp_name, re.IGNORECASE)
        
        shares = int(shares_match.group(1)) if shares_match else None
        levels = int(levels_match.group(1)) if levels_match else None
        
        return shares, levels
    
    def parse_file_size(self, size_str):
        """Converte la stringa della dimensione file in numero"""
        # Gestisce formati come "1MB", "500KB", "2GB", ecc.
        size_str = size_str.upper()
        multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'B': 1}
        
        for unit, mult in multipliers.items():
            if unit in size_str:
                number = re.search(r'(\d+(?:\.\d+)?)', size_str)
                if number:
                    return float(number.group(1)) * mult
        
        # Se non trova unità, assume siano bytes
        number = re.search(r'(\d+)', size_str)
        return int(number.group(1)) if number else 0
    
    def plot_time_by_file_size(self):
        """Grafico dei tempi medi in funzione della dimensione del file"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        for exp_name in self.data:
            sizes = []
            split_times = []
            retrieve_times = []
            
            for size_name in sorted(self.data[exp_name].keys(), 
                                  key=lambda x: self.parse_file_size(x)):
                size_bytes = self.parse_file_size(size_name)
                sizes.append(size_bytes / (1024**2))  # Converti in MB
                
                if 'split' in self.data[exp_name][size_name]:
                    split_times.append(np.mean(self.data[exp_name][size_name]['split']))
                else:
                    split_times.append(0)
                    
                if 'retrieve' in self.data[exp_name][size_name]:
                    retrieve_times.append(np.mean(self.data[exp_name][size_name]['retrieve']))
                else:
                    retrieve_times.append(0)
            
            ax1.plot(sizes, split_times, 'o-', label=exp_name, linewidth=2, markersize=6)
            ax2.plot(sizes, retrieve_times, 's-', label=exp_name, linewidth=2, markersize=6)
        
        ax1.set_xlabel('Dimensione File (MB)')
        ax1.set_ylabel('Tempo Split (s)')
        ax1.set_title('Tempo di Split vs Dimensione File')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.set_xlabel('Dimensione File (MB)')
        ax2.set_ylabel('Tempo Retrieve (s)')
        ax2.set_title('Tempo di Retrieve vs Dimensione File')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_distribution_comparison(self):
        """Box plot per confrontare le distribuzioni dei tempi"""
        # Prepara i dati per il box plot
        split_data = []
        retrieve_data = []
        labels = []
        
        for exp_name in sorted(self.data.keys()):
            for size_name in sorted(self.data[exp_name].keys(),
                                  key=lambda x: self.parse_file_size(x)):
                label = f"{exp_name}\n{size_name}"
                
                if 'split' in self.data[exp_name][size_name]:
                    split_data.extend([(label, t) for t in self.data[exp_name][size_name]['split']])
                
                if 'retrieve' in self.data[exp_name][size_name]:
                    retrieve_data.extend([(label, t) for t in self.data[exp_name][size_name]['retrieve']])
        
        # Crea DataFrame per seaborn
        split_df = pd.DataFrame(split_data, columns=['Config', 'Time'])
        retrieve_df = pd.DataFrame(retrieve_data, columns=['Config', 'Time'])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        if not split_df.empty:
            sns.boxplot(data=split_df, x='Config', y='Time', ax=ax1)
            ax1.set_title('Distribuzione Tempi di Split')
            ax1.set_ylabel('Tempo (s)')
            ax1.tick_params(axis='x', rotation=45)
        
        if not retrieve_df.empty:
            sns.boxplot(data=retrieve_df, x='Config', y='Time', ax=ax2)
            ax2.set_title('Distribuzione Tempi di Retrieve')
            ax2.set_ylabel('Tempo (s)')
            ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_performance_heatmap(self):
        """Heatmap delle performance per diverse configurazioni"""
        # Crea matrice per heatmap
        configs = list(self.data.keys())
        sizes = set()
        for exp_data in self.data.values():
            sizes.update(exp_data.keys())
        sizes = sorted(sizes, key=lambda x: self.parse_file_size(x))
        
        split_matrix = np.zeros((len(configs), len(sizes)))
        retrieve_matrix = np.zeros((len(configs), len(sizes)))
        
        for i, config in enumerate(configs):
            for j, size in enumerate(sizes):
                if size in self.data[config]:
                    if 'split' in self.data[config][size]:
                        split_matrix[i, j] = np.mean(self.data[config][size]['split'])
                    if 'retrieve' in self.data[config][size]:
                        retrieve_matrix[i, j] = np.mean(self.data[config][size]['retrieve'])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        sns.heatmap(split_matrix, annot=True, fmt='.3f', 
                   xticklabels=sizes, yticklabels=configs,
                   cmap='YlOrRd', ax=ax1)
        ax1.set_title('Tempi Medi di Split (s)')
        ax1.set_xlabel('Dimensione File')
        ax1.set_ylabel('Configurazione')
        
        sns.heatmap(retrieve_matrix, annot=True, fmt='.3f',
                   xticklabels=sizes, yticklabels=configs,
                   cmap='YlOrRd', ax=ax2)
        ax2.set_title('Tempi Medi di Retrieve (s)')
        ax2.set_xlabel('Dimensione File')
        ax2.set_ylabel('Configurazione')
        
        plt.tight_layout()
        plt.show()
    
    def plot_scalability_analysis(self):
        """Analisi della scalabilità con diverse metriche"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        for exp_name in self.data:
            sizes_mb = []
            split_means = []
            split_stds = []
            retrieve_means = []
            retrieve_stds = []
            
            for size_name in sorted(self.data[exp_name].keys(),
                                  key=lambda x: self.parse_file_size(x)):
                size_mb = self.parse_file_size(size_name) / (1024**2)
                sizes_mb.append(size_mb)
                
                if 'split' in self.data[exp_name][size_name]:
                    split_times = self.data[exp_name][size_name]['split']
                    split_means.append(np.mean(split_times))
                    split_stds.append(np.std(split_times))
                else:
                    split_means.append(0)
                    split_stds.append(0)
                
                if 'retrieve' in self.data[exp_name][size_name]:
                    retrieve_times = self.data[exp_name][size_name]['retrieve']
                    retrieve_means.append(np.mean(retrieve_times))
                    retrieve_stds.append(np.std(retrieve_times))
                else:
                    retrieve_means.append(0)
                    retrieve_stds.append(0)
            
            # Grafico con barre di errore
            ax1.errorbar(sizes_mb, split_means, yerr=split_stds, 
                        label=exp_name, capsize=5, capthick=2, linewidth=2)
            ax2.errorbar(sizes_mb, retrieve_means, yerr=retrieve_stds,
                        label=exp_name, capsize=5, capthick=2, linewidth=2)
            
            # Throughput (MB/s)
            split_throughput = [s/t if t > 0 else 0 for s, t in zip(sizes_mb, split_means)]
            retrieve_throughput = [s/t if t > 0 else 0 for s, t in zip(sizes_mb, retrieve_means)]
            
            ax3.plot(sizes_mb, split_throughput, 'o-', label=exp_name, linewidth=2)
            ax4.plot(sizes_mb, retrieve_throughput, 's-', label=exp_name, linewidth=2)
        
        ax1.set_xlabel('Dimensione File (MB)')
        ax1.set_ylabel('Tempo Split (s)')
        ax1.set_title('Tempo di Split (con deviazione standard)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.set_xlabel('Dimensione File (MB)')
        ax2.set_ylabel('Tempo Retrieve (s)')
        ax2.set_title('Tempo di Retrieve (con deviazione standard)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        ax3.set_xlabel('Dimensione File (MB)')
        ax3.set_ylabel('Throughput (MB/s)')
        ax3.set_title('Throughput Split')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        ax4.set_xlabel('Dimensione File (MB)')
        ax4.set_ylabel('Throughput (MB/s)')
        ax4.set_title('Throughput Retrieve')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def generate_summary_stats(self):
        """Genera statistiche riassuntive"""
        print("\n" + "="*50)
        print("STATISTICHE RIASSUNTIVE")
        print("="*50)
        
        for exp_name in sorted(self.data.keys()):
            print(f"\nEsperimento: {exp_name}")
            print("-" * (len(exp_name) + 13))
            
            for size_name in sorted(self.data[exp_name].keys(),
                                  key=lambda x: self.parse_file_size(x)):
                print(f"\n  Dimensione: {size_name}")
                
                if 'split' in self.data[exp_name][size_name]:
                    split_times = self.data[exp_name][size_name]['split']
                    print(f"    Split   - Media: {np.mean(split_times):.4f}s, "
                          f"Std: {np.std(split_times):.4f}s, "
                          f"Min: {np.min(split_times):.4f}s, "
                          f"Max: {np.max(split_times):.4f}s")
                
                if 'retrieve' in self.data[exp_name][size_name]:
                    retrieve_times = self.data[exp_name][size_name]['retrieve']
                    print(f"    Retrieve- Media: {np.mean(retrieve_times):.4f}s, "
                          f"Std: {np.std(retrieve_times):.4f}s, "
                          f"Min: {np.min(retrieve_times):.4f}s, "
                          f"Max: {np.max(retrieve_times):.4f}s")
    
    def run_complete_analysis(self):
        """Esegue l'analisi completa con tutti i grafici"""
        self.load_data()
        
        if not self.data:
            print("Nessun dato trovato. Verifica il percorso della directory.")
            return
        
        print("\nGenerazione grafici...")
        
        # Imposta stile matplotlib
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        # Genera tutti i grafici
        self.plot_time_by_file_size()
        self.plot_scalability_analysis()
        self.plot_performance_heatmap()
        self.plot_distribution_comparison()
        
        # Stampa statistiche
        self.generate_summary_stats()
        
        print("\nAnalisi completata!")

# Esempio di utilizzo
if __name__ == "__main__":
    # Sostituisci con il percorso della tua directory principale
    base_dir = "path/to/your/experiments"
    
    analyzer = SecretSharingAnalyzer(base_dir)
    analyzer.run_complete_analysis()
    
    # Oppure esegui analisi specifiche:
    # analyzer.load_data()
    # analyzer.plot_time_by_file_size()
    # analyzer.generate_summary_stats()
