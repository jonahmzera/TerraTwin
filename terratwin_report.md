# TerraTwin preliminary report
Aether Labs | NASA Space Apps Challenge 2026
Generated: 2026-11-13

## Status
Preliminary. Topography only. This report does not show that the Chyulu Hills are an analogue of Elysium Planitia.

## Research question
Do selected topographic measurements of a 50 km area of the Chyulu Hills (Kenya) resemble those of a 50 km area of Elysium Planitia (Mars)?

## Datasets
- **Chyulu Hills (Earth)**: Copernicus DEM GLO-30 (DSM), provider ESA / Copernicus. Native resolution: 30 m, resampled by averaging to ~200 m. CRS: EPSG:4326. Window: 50 km, pixel size 200 m, valid pixels 100%.
- **Elysium Planitia (Mars)**: MOLA-HRSC blended DEM v2, provider USGS Astrogeology (MOLA: NASA, HRSC: ESA/DLR). Native resolution: 200 m (read at native resolution). CRS: ESRI:104971 (Mars 2000 geographic). Window: 50 km, pixel size 200 m, valid pixels 100%.

## Method
Both windows were read at about 200 m per pixel. Relief (highest minus lowest point), mean slope, maximum slope and terrain ruggedness (TRI: mean absolute elevation difference to the 8 neighbouring pixels) were calculated from the elevation grids. Per-variable similarity = 100 x max(0, 1 - |Earth - Mars| / R), where R is a provisional comparison range. The overall score is the weighted average of the per-variable similarities, using equal provisional weights. Missing values are never treated as zero.

## Measurements and similarity
| Variable | Chyulu Hills | Elysium Planitia | Difference | R | Similarity | Weight % |
|---|---|---|---|---|---|---|
| Local relief (m) | 1423.8 | 794 | 629.8 | 3000 | 79 | 25 |
| Mean slope (degrees) | 3.04 | 0.93 | 2.11 | 5 | 57.8 | 25 |
| Maximum slope (degrees) | 30.97 | 38.6 | 7.63 | 45 | 83 | 25 |
| Roughness, TRI (m) | 8.69 | 2.65 | 6.04 | 10 | 39.6 | 25 |

Topography similarity (provisional): **64.9 / 100**

Variables compared: 4 of 4. Categories with data: 1 of 5 (topography only).

## Limitations
- Geology, geomorphology, environment and operational relevance are not compared yet.
- Windows are 50 km boxes around approximate centre points, not surveyed boundaries.
- The Chyulu window was checked on a map: its highest pixel falls inside the Chyulu Hills, not Kilimanjaro.
- Comparison ranges and weights are provisional assumptions. Changing them or the window changes the score.
- The Earth data is natively 30 m and was averaged down to about 200 m to match Mars.
- Earth data is a surface model (DSM), so vegetation can affect roughness.
- Absolute elevation is not compared because Earth and Mars use different reference surfaces.
- Mars maximum slope (38.6 degrees) may come from a single extreme pixel and is unverified.
- Mars elevation units are not stored in the file metadata and still need confirming from USGS documentation.

## References
- Copernicus DEM GLO-30, European Space Agency / Copernicus programme.
- Fergason, R. L., Hare, T. M., & Laura, J. (2018). HRSC and MOLA Blended Digital Elevation Model at 200m v2. Astrogeology PDS Annex, U.S. Geological Survey. https://astrogeology.usgs.gov/search/map/mars_mgs_mola_mex_hrsc_blended_dem_global_200m

## AI assistance
AI assistance (Claude) was used for code and for planning the analysis. The team should edit this section to describe exactly what was AI-assisted. All numbers above come from the datasets listed, not from AI.