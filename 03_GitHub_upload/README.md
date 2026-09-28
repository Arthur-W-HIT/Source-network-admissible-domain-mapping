# Source-network admissible-domain mapping: supporting research data

Supporting numerical data for “A source–network admissible domain mapping method for flexible heating in coupled combined heat and power–district heating systems”, Energy revision R1.

Repository: https://github.com/Arthur-W-HIT/Source-network-admissible-domain-mapping

## Contents and scope

- `data/`: numerical results from the adopted R1 calculation, including all 1728 scenarios, the 12 reference conditions, restoration and capacity-matching results.
- `parameters/`: heating coefficients, non-heating reference outputs and complete numerical local-response matrices. Matrix units and vector order are given in Appendix E and heating_parameters.json.
- `settings/`: network-boundary settings and source-check case settings. These are configuration records, not model source files.
- `validation/`: principal and extended source checks, all retained residuals, error ranges and finite perturbation outputs. `results.csv` contains the 15 extended extraction cases.
- `figure_data/`: source plotting samples, network intersections, set metrics and corrected weighted-violation diagnostics.
- `reference_figures/`: the 19 active figures in the clean manuscript; filenames match the LaTeX source. Obsolete marked-up figures are excluded.
- `scripts/reproduce.py`: verifies packaged hashes and the main reported coverage statistics, exports grouped tables, and regenerates representative numerical plots. Plot styling is independent of the archived publication layout.

The package supports numerical verification and plotting from saved results. It does not contain the turbine or district-heating physical models, Modelica files, licensed libraries, raw simulator binaries or internal project logs. Physical simulations require the original model implementation and applicable software licenses.

## Run

Use Python 3 with numpy, pandas and matplotlib, from this directory:

```
python scripts/reproduce.py
```

Outputs are written to `reproduced/`. No physical simulation or parameter fitting is performed. `manifest.json` contains SHA-256 hashes for the distributed files.

## Data conventions

The stored interface identifiers `S1`, `S2a`, `S2b` correspond to manuscript C1, C2, C3. Fractions such as coupled_coverage and add31 are multiplied by 100 for percentages. `main_reference`, `narrow_sensitivity` and `historical_extension` distinguish the 12, 420 and 1296 disjoint scenario groups. The historical_extension label is retained as a data identifier; these scenarios form the extended group in the manuscript. All 1728 conditions are used in Figure 8 with equal design weights; the weights are not operating probabilities.

The 12-reference-group coverage is 90.32%, 92.29%, 99.36%; mean additional C3 coverage is 9.04%. High-extraction errors and changed loss rankings remain in the data. Figure references, input tables and regeneration coverage are listed in FIGURE_DATA_MAP.md.

The numerical matrices retain their parameterization load nodes. No extrapolation beyond 50–100% load is intended. Old fixed electrical-loss coefficients are not included; electrical-loss parameters use the section-work formulation.

Please cite the associated manuscript when using these materials. Contact the corresponding authors for questions about the data or permissions beyond research verification.
