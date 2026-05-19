import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from dataset_loader import load_dataset
from feature_extraction import extract_features

os.makedirs("eval_img", exist_ok=True)

def run_comprehensive_evaluation():
    print("Running comprehensive grid evaluation...\n")
    frequencies = ["20Hz", "100Hz", "Mixed"]
    sensor_modes = ["acc_only", "gyro_only", "both"]
    feature_modes = ["mean_only", "mean_std", "all", "raw"]
    kernels = ["linear", "poly", "rbf", "sigmoid"]
    
    results = []

    for freq in frequencies:
        if freq == "Mixed":
            data_raw, labels_raw = load_dataset("data", target_freq=None)
        else:
            data_raw, labels_raw = load_dataset("data", target_freq=freq)
            
        if len(data_raw) == 0:
            continue
            
        for sensor in sensor_modes:
            for mode in feature_modes:
                X = [extract_features(frame, mode=mode, sensors=sensor) for frame in data_raw]
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X, labels_raw, test_size=0.2, random_state=42, stratify=labels_raw
                )
                
                for kernel in kernels:
                    model = make_pipeline(StandardScaler(), SVC(kernel=kernel))
                    model.fit(X_train, y_train)
                    acc = accuracy_score(y_test, model.predict(X_test))
                    
                    results.append({
                        "Frequency": freq,
                        "Sensors": sensor,
                        "Features": mode,
                        "Kernel": kernel,
                        "Accuracy": round(acc, 4)
                    })
                    print(f"Freq: {freq:5} | Sensors: {sensor:9} | Mode: {mode:9} | Kernel: {kernel:7} | Acc: {acc:.4f}")

    df = pd.DataFrame(results)
    # Plots are an ai feature generated using matplotlib 
    # Plot 1: Feature Modes vs Accuracy (grouped by Kernel) for 100Hz and both sensors
    df_plot1 = df[(df["Frequency"] == "100Hz") & (df["Sensors"] == "both")]
    if not df_plot1.empty:
        pivot_100 = df_plot1.pivot(columns="Kernel", index="Features", values="Accuracy")
        pivot_100.plot(kind="bar", figsize=(10, 6), colormap='viridis')
        plt.title("Accuracy by Feature Mode and Kernel (100Hz, Both Sensors)")
        plt.ylabel("Accuracy")
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45)
        plt.legend(title="Kernel")
        plt.tight_layout()
        plt.savefig("eval_img/comprehensive_features_kernels.png")
        print("\nSaved plot to eval_img/comprehensive_features_kernels.png")
    
    # Plot 2: Frequency vs Accuracy (comparing top 3 configurations)
    top_configs = df.groupby(["Sensors", "Features", "Kernel"])["Accuracy"].mean().nlargest(3).index
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(frequencies))
    width = 0.25
    
    for i, (sens, feat, kern) in enumerate(top_configs):
        accs = [df[(df["Frequency"]==f) & (df["Sensors"]==sens) & (df["Features"]==feat) & (df["Kernel"]==kern)]["Accuracy"].values[0] for f in frequencies]
        label = f"{sens} + \n{feat} + {kern}"
        ax.bar(x + (i-1)*width, accs, width, label=label)
        
    ax.set_xticks(x)
    ax.set_xticklabels(frequencies)
    ax.set_ylabel("Accuracy")
    ax.set_title("Frequencies vs Accuracy on Top 3 Configurations")
    ax.legend(title="Sensors+Features+Kernel", loc='lower right')
    plt.tight_layout()
    plt.savefig("eval_img/comprehensive_frequencies.png")
    print("Saved plot to eval_img/comprehensive_frequencies.png\n")
    
    # Plot 3: All vs All Comparison (Horizontal Bar Chart)
    df_sorted = df.sort_values("Accuracy", ascending=True)
    labels = df_sorted.apply(lambda row: f"{row['Frequency']} | {row['Sensors']} | {row['Features']} | {row['Kernel']}", axis=1)
    
    plt.figure(figsize=(12, 20)) # Made taller to fit all bars (108 total combinations)
    plt.barh(labels, df_sorted["Accuracy"], color='steelblue')
    plt.xlabel("Accuracy")
    plt.title("All Configurations vs All Configurations")
    plt.xlim(0, 1.0)
    plt.tight_layout()
    plt.savefig("eval_img/all_vs_all_comparison.png")
    print("Saved plot to eval_img/all_vs_all_comparison.png\n")

    # Plot 4: Accuracy Distribution by Kernel (Boxplot)
    plt.figure(figsize=(8, 6))
    df.boxplot(column="Accuracy", by="Kernel", grid=False, patch_artist=True, boxprops=dict(facecolor="lightblue"))
    plt.title("Accuracy Distribution by Kernel")
    plt.suptitle("") # Remove default pandas suptitle
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig("eval_img/distribution_by_kernel.png")
    print("Saved plot to eval_img/distribution_by_kernel.png")

    # Plot 5: Accuracy Distribution by Sensor Choice (Boxplot)
    plt.figure(figsize=(8, 6))
    df.boxplot(column="Accuracy", by="Sensors", grid=False, patch_artist=True, boxprops=dict(facecolor="lightgreen"))
    plt.title("Accuracy Distribution by Sensor Choice")
    plt.suptitle("")
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig("eval_img/distribution_by_sensor.png")
    print("Saved plot to eval_img/distribution_by_sensor.png")

    # Plot 6: Heatmap of Average Accuracy (Sensors vs Features)
    pivot_sf = df.pivot_table(index="Sensors", columns="Features", values="Accuracy", aggfunc="mean")
    plt.figure(figsize=(8, 6))
    plt.imshow(pivot_sf, cmap='viridis', aspect='auto')
    plt.colorbar(label='Average Accuracy')
    plt.xticks(np.arange(len(pivot_sf.columns)), pivot_sf.columns)
    plt.yticks(np.arange(len(pivot_sf.index)), pivot_sf.index)
    plt.title("Heatmap: Average Accuracy by Sensors & Features")
    
    # Add text annotations safely
    for i in range(len(pivot_sf.index)):
        for j in range(len(pivot_sf.columns)):
            val = pivot_sf.iloc[i, j]
            plt.text(j, i, f"{val:.3f}", ha='center', va='center', 
                     color='white' if val < pivot_sf.values.mean() else 'black',
                     bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
            
    plt.tight_layout()
    plt.savefig("eval_img/heatmap_sensors_features.png")
    print("Saved plot to eval_img/heatmap_sensors_features.png\n")

    print("Top 5 Configurations Overall:")
    print(df.sort_values(by="Accuracy", ascending=False).head())
    
    # Save a markdown table
    with open("evaluation_table.md", "w") as f:
        f.write("### Comprehensive Evaluation Results\n\n")
        f.write(df.sort_values(by="Accuracy", ascending=False).to_markdown(index=False))
        f.write("\n")

if __name__ == "__main__":
    run_comprehensive_evaluation()
