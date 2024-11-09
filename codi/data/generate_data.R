library(tidyverse)
library(dplyr)
library(readr)

path <- "C:/Users/garci/Desktop/UNIVERSITAT/QUART DE CARRERA/REALITAT AUGMENTADA/ABP/Sistema-Solar/codi/data"
setwd(path)


satellites <- read.csv("satellites.csv")
view(satellites)

# Distancias de los satélites en millones de km (10^6 km)

distancias <- c(
  0.384, 0.0094, 0.0235, 0.4217, 0.671, 1.070, 1.883, 0.1814, 11.46, 11.70,
  24.18, 23.20, 11.66, 22.79, 21.30, 11.70, 0.223, 0.129, 0.128, 24.06, 17.26,
  24.96, 23.74, 21.30, 22.07, 22.69, 22.03, 22.56, 23.46, 24.53, 26.03, 26.45,
  28.34, 28.17, 28.30, 28.86, 29.22, 29.96, 31.85, 34.88, 39.24, 43.96, 44.76,
  45.91, 48.74, 48.23, 48.79, 49.50, 49.70, 50.01, 29.95, 29.68, 29.93, 30.10,
  29.70, 29.60, 29.50, 29.40, 29.30, 29.20, 29.10, 28.90, 28.80, 28.60, 28.50,
  28.40, 27.90, 27.80, 27.60, 27.50, 0.185, 0.238, 0.294, 0.377, 0.527, 1.222,
  0.585, 3.560, 12.88, 0.151, 0.151, 0.018, 0.025, 0.030, 0.137, 0.138, 0.141,
  0.134, 0.071, 0.121, 0.092, 0.042, 0.066, 0.015, 23.57, 22.82, 22.96, 22.30,
  23.10, 22.50, 23.10, 23.80, 23.50, 24.00, 24.60, 24.80, 24.90, 24.50, 25.00,
  25.20, 25.30, 25.60, 25.80, 26.00, 26.10, 26.50, 26.60, 26.90, 27.20, 27.40,
  27.60, 27.80, 28.10, 28.20, 28.30, 28.50, 28.70, 29.00, 29.20, 29.40, 29.60,
  0.191, 0.271, 0.436, 0.583, 0.129, 0.048, 0.057, 0.061, 0.060, 0.060, 0.062,
  0.070, 0.072, 0.074, 0.057, 0.118, 0.179, 0.225, 0.238, 0.254, 0.285, 0.290,
  0.308, 0.337, 0.371, 0.076, 0.090, 0.354, 5.513, 0.030, 0.050, 0.060, 0.070,
  0.085, 0.118, 5.331, 5.828, 23.54, 23.56, 48.17, 0.105)

satellites['Distance (10^6km)'] = distancias
satellites['Distance (m)'] = satellites['Distance (10^6km)'] * 10^6 * 10^3 

gm_numeric <- as.numeric(gsub("±.*", "", satellites[['gm']]))
radius_numeric <- as.numeric(gsub("±.*", "", satellites[['radius']]))

satellites['radius'] = radius_numeric
satellites['Velocity (m/s)'] = sqrt(gm_numeric / satellites['Distance (m)'])
satellites['Velocity (km/s)'] = satellites['Velocity (m/s)'] / 1000

write.csv(satellites, "satellites_modified.csv", row.names = FALSE)

# Imprimir las distancias
view(satellites)
