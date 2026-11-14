# TerraTwin: Planetary Analogue Discovery System

**Aether Labs | NASA Space Apps Challenge 2026**

**Live app: https://terratwin-aether.streamlit.app/** (no sign-in needed; if it has been idle, click the wake-up
button and wait about 30 seconds)

TerraTwin searches the whole Earth for places that can help us prepare to explore the Moon and Mars. It compares
Earth with five real landing sites and candidate base regions, using open NASA and partner-agency data. For every
comparison, it reports how similar the places are in each dimension, how confident that score is, where the
analogy holds, where it breaks down, and what Earth cannot reproduce at all.

## Challenge fit

| The challenge asks... | TerraTwin |
|---|---|
| Use open Earth, Moon and Mars data from NASA and other agencies | Copernicus DEM (ESA), Terrain Tiles (SRTM/NASA, GMTED/USGS, ETOPO/NOAA), MOLA/HRSC (NASA, ESA/DLR, USGS), LRO LOLA (NASA), NASA POWER, Macrostrat |
| Search globally and systematically, beyond well-known sites | Stage 1 scores every ~78 km land cell on Earth; candidates near known analogue sites are excluded from the shortlist |
| Think beyond visual similarity | Four dimensions: terrain, landing and mobility, geology, climate |
| Say what is similar, how similar, and what is different | Per-variable similarity, uncertainty band, "holds" and "breaks down" lists for every pair |
| Remember Earth's limits | Gravity, atmosphere/vacuum and radiation are listed with every result |
| Consider scale | Two scales: ~1.2 km screening, then 200 m characterisation in 50 km windows |
| Connect to exploration | Each target lists the instruments, operations and tests an analogue could support |
| Present as a map, visualisation or tool | Interactive Streamlit app with global maps, side-by-side relief, rankings and downloadable reports |

## Targets

| Target | Body | Why it matters |
|---|---|---|
| Elysium Planitia, InSight landing site | Mars | Smooth lava plain chosen for a safe landing |
| Jezero Crater, Perseverance landing site | Mars | Ancient lake and delta; search for past life |
| Mare Imbrium, Chang'e 3 landing site | Moon | Young mare basalt plain |
| Marius Hills, lava-tube skylight region | Moon | Volcanic domes and a probable lava tube, a candidate shelter |
| Lunar south pole, Shackleton region | Moon | Candidate Artemis base: sunlit rims, ice in shadowed craters |

## Results

24,548 land cells screened; 53 Earth sites characterised (2 team sites, 11 known analogues, 30 discovered
candidates, 10 ice-sheet lookalikes). Scores are 0-100 with equal weights; the band is the 5th-95th percentile
from the uncertainty analysis. All values come from `data/processed/` and can be regenerated with the pipeline.

**Validation: known analogue sites rank where they should.**
- Lunar south pole: McMurdo Dry Valleys ranks #1 of 53 (77, band 62-87).
- Jezero Crater: the Mars Desert Research Station area ranks #1 (81, band 65-91); Rio Tinto ranks #4.
- Marius Hills: the four volcanic analogue sites (Holuhraun, SP Crater, Craters of the Moon, Mauna Kea) take
  ranks #1 to #4.

**Discoveries: less-studied places that match as well as, or better than, known analogues.**
- **Al-Jufra district, Libya** (26.75 N, 17.93 E): ranks #1 for the InSight lava plain (63, band 53-70), ahead of
  every known analogue (best known site: #8), and #1 for Mare Imbrium (65, band 56-75). Mapped as volcanic rock,
  low relief, and hyper-arid (about 18 mm of rain per year).
- **Panjgur district, Pakistan** (26.75 N, 64.34 E): ties the Mars Desert Research Station for Jezero Crater
  (81, band 66-90): sedimentary rocks, gentle terrain, about 77 mm of rain per year.
- **Tibesti, Chad** (20.96 N, 17.23 E): the best new site for the Marius Hills volcanic region (63, band 55-70):
  volcanic rock, about 44 mm of rain per year.
- **Mugu, Nepal** and **near Rosario de Lerma, Argentina**: the best new sites for the rugged lunar south pole
  terrain (67 and 66), second only to the Dry Valleys.

**A lesson from the lookalikes.** On terrain alone, the closest Earth matches to the InSight lava plain are the
Antarctic ice sheets. They also match Mars's cold better than any desert. Only the geology dimension shows that
they are ice, not basalt (rock-type score 0). They may be useful analogues for icy Martian plains, but not for
InSight's lava. This is why TerraTwin reports each dimension separately, not just one number.

**Where every analogy breaks down.** No site comes close to the Moon's or Mars's temperatures, daily temperature
swings or air pressure (the best climate score at any site is 60 out of 100, and 48 outside the polar regions),
and none reproduces their gravity or radiation.

These are screening results, not field-verified conclusions. They show where a closer look would be worthwhile.

## Run the app

Requires Python 3.13 (tested with 3.13.17 on Windows 11).

```bash
py -3.13 -m venv .venv313
.venv313\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

The app reads the CSV files in `data/processed/`, so it works offline and starts in seconds.

## Reproduce every number

```bash
pip install -r requirements-pipeline.txt
python -m scripts.run_pipeline --step all
```

Or one step at a time: `targets`, `screen`, `candidates`, `earth`. All data is read directly from public hosts
with HTTP range requests (no logins, no API keys). Downloads are cached in `data/cache/` (not in Git), so steps
can be re-run and resume after a network error. A full run downloads about 1.5 GB and takes about 30-60 minutes.

Run the tests:

```bash
python -m pytest
```

## Method

**Stage 1, global screening.** About 4,096 Terrain Tiles (zoom 6) cover the Earth. Each is cut into cells of about
78 km and block-averaged to about 1.2 km pixels (correcting the Web Mercator stretch towards the poles). Cells that
are mostly sea are skipped. Each target is averaged to the same 1.2 km pixels and measured the same way.

**Stage 2, characterisation.** For each target, the six best cells outside the Antarctic and Greenland ice sheets
(at least 500 km apart, at least 100 km from known analogue sites) are re-measured at 200 m, together with the
team's 2 sites and 11 well-known analogue sites. Smooth ice sheets top the terrain-only ranking for several
targets, so two ice-sheet cells per target are also kept as "lookalikes", to show what the other dimensions
reveal about them.
- Terrain: Copernicus GLO-30 for Earth, MOLA/HRSC 200 m for Mars, LOLA 118 m for the Moon, all resampled onto a
  local azimuthal equidistant grid at 200 m in a 50 km window.
- Climate: NASA POWER long-term means at the site centre.
- Geology: the mapped geologic unit from Macrostrat.

**Measurements.** Slope: Horn (1981). Ruggedness: TRI, mean absolute difference to the 8 neighbours (Wilson et
al., 2007). Relief, hypsometric integral (Strahler, 1952), share of area flatter than 5 degrees, and
95th-percentile slope. Edge pixels without a full neighbourhood are excluded.

**Scoring.** `similarity = 100 x max(0, 1 - |Earth - target| / R)`. R is the 5th-95th percentile spread of the
variable across the Earth sites compared, not a hand-picked number. Relief, slope and ruggedness are compared on a
log scale. Dimension score = mean of its variables; overall = weighted mean of the dimensions with data (equal
weights by default). Missing data is never counted as zero; it lowers the reported coverage.

**Uncertainty.** Each score is recomputed hundreds of times with random weights (Dirichlet around the chosen
weights) and comparison ranges (x0.67 to x1.5). The 5th-95th percentile band is shown next to every score.

**Validation.**
- Well-known analogue sites are scored exactly like new candidates; their ranks are shown in the app.
- The pipeline independently reproduces the team's first Colab measurement of the Chyulu Hills within a few percent.
- The mean elevation measured at the InSight site agrees with the published landing elevation of -2,613 m
  (Golombek et al., 2020), confirming the Mars DEM is in metres.
- Unit tests check the terrain measures on synthetic surfaces with known answers (`tests/`).

## Limitations

- Windows are fixed squares around centre points; a smaller area inside could match better or worse.
- Stage 1 uses ~1.2 km pixels and can miss small features such as single craters or lava tubes.
- Pixels at or below sea level are treated as sea in stage 1, so below-sea-level basins are under-represented.
- Copernicus is a surface model: vegetation and buildings add roughness.
- Moon and Mars climate values are rounded literature values, not measurements at the exact site.
- Geology matching uses map keywords, not mineralogy.
- Not yet scored: vegetation, dust and aerosols, ice and permafrost, caves and the subsurface.
- No Earth site reproduces lunar or Martian gravity, the lunar vacuum, the thin Martian atmosphere or their
  radiation environments.

## Project structure

```
app.py                      Overview page (entry point)
pages/                      Earth Explorer, Planetary Explorer, Comparison Lab, Global Discovery, Reports, Methods
config/settings.py          Paths, data sources and citations, processing constants
config/study_locations.py   Moon/Mars targets (with sources) and Earth sites
modules/data_collection.py  Remote reading and reprojection of Earth, Mars and Moon DEMs
modules/terrain_analysis.py Slope, ruggedness, relief and other terrain measures
modules/global_screening.py Stage 1 screening of all Earth land
modules/environmental_analysis.py  NASA POWER climate
modules/geological_analysis.py     Macrostrat geology and rock-type matching
modules/similarity_scoring.py      Multi-dimensional scoring and uncertainty
modules/report_generator.py        Downloadable Markdown reports
scripts/run_pipeline.py     Reproduces all data in data/processed
tests/                      Unit and end-to-end tests
```

## Data sources and credits

- Copernicus DEM GLO-30, European Space Agency / Copernicus programme, via AWS Open Data. https://doi.org/10.5069/G9028PQB
- Terrain Tiles, Mapzen/Tilezen via AWS Open Data (SRTM courtesy NASA/USGS, GMTED2010 courtesy USGS, ETOPO1 courtesy NOAA). https://registry.opendata.aws/terrain-tiles/
- Fergason, R. L., Hare, T. M., & Laura, J. (2018). HRSC and MOLA Blended Digital Elevation Model at 200m v2. USGS Astrogeology.
- LOLA Science Team. LRO LOLA Global LDEM 118 m (2014); Smith, D. E. et al. (2010), GRL 37, L18204.
- NASA POWER Project, NASA Langley Research Center. https://power.larc.nasa.gov/
- Peters, S. E., Husson, J. M., & Czaplewski, J. (2018). Macrostrat. G-Cubed 19, 1393-1409.
- Place names for discovered candidates: OpenStreetMap Nominatim (data (c) OpenStreetMap contributors).
- Target coordinates and environment values: Golombek et al. (2020); Banfield et al. (2020); Farley et al. (2022);
  Rodriguez-Manfredi et al. (2023); Zhang et al. (2015); Haruyama et al. (2009); Williams et al. (2017);
  Paige et al. (2010); Colaprete et al. (2010); Horvath et al. (2022). Full references in `config/study_locations.py`.

Method references: Horn (1981), Proc. IEEE 69; Wilson et al. (2007), Marine Geodesy 30; Strahler (1952), GSA Bulletin 63.

Open-source tools: Streamlit, NumPy, pandas, Plotly, Matplotlib, rasterio/GDAL, PyProj. Related projects reviewed
for methods (not copied): GlacioHack/xdem, r-barnes/richdem, bopen/elevation, alekfal/pynasapower.

## Team

TerraTwin was conceived and built by **Aether Labs** for the NASA Space Apps Challenge 2026. The team defined the
research question, chose the Earth study sites and the Moon and Mars targets, decided how analogues should be
compared and validated, ran the analysis, and reviewed every result presented here.

**Use of Super Intelligence (SI), as required by the challenge rules:** SI tools assisted with writing code and
documentation. No images, video or audio were SI-generated, and no NASA branding was generated. All data and
numbers come from the open datasets listed above through `scripts/run_pipeline.py`.
