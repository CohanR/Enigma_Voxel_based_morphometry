# Install the enigmatoolbox and visualisation libraries
# git clone https://github.com/MICA-MNI/ENIGMA.git
# cd ENIGMA
# python setup.py install
# you need to have "git" installed before doing this
# Written by Remy Cohan
#------------------------------------------------

# Modules
import matplotlib.pyplot as plt
import seaborn as sns
from enigmatoolbox.datasets import load_example_data
from enigmatoolbox.utils.useful import reorder_sctx, zscore_matrix
from PIL import Image

# I am adding filenames here because later I want to save a mosaic image(s)
Enigma_heatmap_SV = "Enigma_heatmap_SV.png"
Enigma_heatmap_CT = "Enigma_heatmap_CT.png"
Enigma_heatmap_SA = "Enigma_heatmap_SA.png"
Enigma_mean_zscores_SV = "Enigma_mean_zscores_SV.png"
Enigma_mean_zscores_CT = "Enigma_mean_zscores_CT.png"
Enigma_mean_zscores_SA = "Enigma_mean_zscores_SA.png"
Enigma_boxplot = "Enigma_boxplot.png"

# Enhanced visualisations

def plot_mean_zscores(data, title, filename):
    plt.figure(figsize=(15, 6))
    sns.barplot(x=data.index, y=data.values)
    plt.xticks(rotation=90)
    plt.ylabel('Mean Z-Score')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

def plot_boxplot(data, covariate, structure, title, filename, x_labels=None):
    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(x=covariate, y=structure, data=data)
    plt.title(title)
    if x_labels:
        ax.set_xticklabels(x_labels)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

def plot_heatmap(data, title, filename):
    plt.figure(figsize=(10, 10))
    sns.heatmap(data, cmap='coolwarm', center=0, linewidths=0.5, linecolor='white')
    plt.title(title)
    plt.ylabel('Subjects')
    plt.xlabel('Regions')
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

# Function to create mosaic
def create_mosaic(filenames, output_filename):
    images = [Image.open(filename) for filename in filenames]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    mosaic = Image.new('RGB', (total_width, max_height), (255, 255, 255))
    x_offset = 0
    for img in images:
        mosaic.paste(img, (x_offset,0))
        x_offset += img.width
    mosaic.save(output_filename, quality=95)

# Load the example dataset
cov, metr1_SubVol, metr2_CortThick, metr3_CortSurf = load_example_data()

# Re-order the subcortical data
metr1_SubVol_r = reorder_sctx(metr1_SubVol)

# Z-score the data
group = cov['Dx'].to_list()
controlCode = 0
SV_z = zscore_matrix(metr1_SubVol_r.iloc[:, 1:-1], group, controlCode)
CT_z = zscore_matrix(metr2_CortThick.iloc[:, 1:-5], group, controlCode)
SA_z = zscore_matrix(metr3_CortSurf.iloc[:, 1:-5], group, controlCode)

# Visualise the z-scored data with different plots
plot_heatmap(SV_z, "Z-Scored Subcortical Volumes", Enigma_heatmap_SV)
plot_heatmap(CT_z, "Z-Scored Cortical Thickness", Enigma_heatmap_CT)
plot_heatmap(SA_z, "Z-Scored Cortical Surface Area", Enigma_heatmap_SA)


# Compute mean z-score values for a specific group (e.g., left (Temporal lobe epilepsy (TLE), which is SDx == 3)
SV_z_mean = SV_z.iloc[cov[cov['SDx'] == 3].index, :].mean(axis=0)
CT_z_mean = CT_z.iloc[cov[cov['SDx'] == 3].index, :].mean(axis=0)
SA_z_mean = SA_z.iloc[cov[cov['SDx'] == 3].index, :].mean(axis=0)

# Visualise mean z-scores
plot_mean_zscores(SV_z_mean, 'Mean Z-Scores for Subcortical Volumes (Left TLE vs Controls)', Enigma_mean_zscores_SV)
plot_mean_zscores(CT_z_mean, 'Mean Z-Scores for Cortical Thickness (Left TLE vs Controls)', Enigma_mean_zscores_CT)
plot_mean_zscores(SA_z_mean, 'Mean Z-Scores for Cortical Surface Area (Left TLE vs Controls)', Enigma_mean_zscores_SA)

# Add the 'Dx' column to metr1_SubVol_r
metr1_SubVol_r = metr1_SubVol_r.merge(cov[['SubjID', 'Dx']], on='SubjID', how='left')

# Example boxplot for 'Hippocampus_Left' from subcortical volume data
plot_boxplot(metr1_SubVol_r, 'Dx', 'Lhippo', 'Comparison of Left Hippocampus Volume (Patients vs Controls)', Enigma_boxplot, x_labels=['Control', 'Patient'])

# Create mosaic from generated plots
create_mosaic([
    Enigma_heatmap_SV, 
    Enigma_heatmap_CT, 
    Enigma_heatmap_SA, 
    Enigma_mean_zscores_SV, 
    Enigma_mean_zscores_CT, 
    Enigma_mean_zscores_SA, 
    Enigma_boxplot
], "mosaic.png")

# Save the datasets to CSV files
cov.to_csv('cov.csv', index=False)
metr1_SubVol.to_csv('metr1_SubVol.csv', index=False)
metr2_CortThick.to_csv('metr2_CortThick.csv', index=False)
metr3_CortSurf.to_csv('metr3_CortSurf.csv', index=False)
SV_z_mean.to_csv('SV_z_mean.csv', index=False)
CT_z_mean.to_csv('CT_z_mean.csv', index=False)
SA_z_mean.to_csv('SA_z_mean.csv', index=False)

print("Data processing and visualization complete. Data and images saved. Remy Cohan")
