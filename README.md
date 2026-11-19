# ECU44291 Quantitative Macroeconomics: lecture notebooks and code

Trinity College Dublin, Michaelmas Term 2026. Joseph Kopecky.

One folder per week. Before each lecture the blank notebook is posted; after it, the complete notebook and the week's code. The blank notebooks open in Google Colab with nothing to install.

| Week | Blank notebook | Open in Colab | Complete notebook and code |
|---|---|---|---|
| 1 | [lecture01_solow_blank.ipynb](week01/lecture01_solow_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week01/lecture01_solow_blank.ipynb) | [lecture01_solow.ipynb](week01/lecture01_solow.ipynb), [code](week01/code) |
| 2 | [lecture02_rootfinding_olg_blank.ipynb](week02/lecture02_rootfinding_olg_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week02/lecture02_rootfinding_olg_blank.ipynb) | [lecture02_rootfinding_olg.ipynb](week02/lecture02_rootfinding_olg.ipynb), [code](week02/code) |
| 3 | [lecture03_lifecycle_blank.ipynb](week03/lecture03_lifecycle_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week03/lecture03_lifecycle_blank.ipynb) | [lecture03_lifecycle.ipynb](week03/lecture03_lifecycle.ipynb), [code](week03/code) |
| 4 | [lecture04_vfi_blank.ipynb](week04/lecture04_vfi_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week04/lecture04_vfi_blank.ipynb) | [lecture04_vfi.ipynb](week04/lecture04_vfi.ipynb), [code](week04/code) |
| 5 | [lecture05_theory_howard_blank.ipynb](week05/lecture05_theory_howard_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week05/lecture05_theory_howard.ipynb) (complete) | [lecture05_theory_howard.ipynb](week05/lecture05_theory_howard.ipynb), [code](week05/code) |
| 6 | [lecture06_continuous_blank.ipynb](week06/lecture06_continuous_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week06/lecture06_continuous.ipynb) (complete) | [lecture06_continuous.ipynb](week06/lecture06_continuous.ipynb), [code](week06/code) |
| 7 | [lecture07_closing_blank.ipynb](week07/lecture07_closing_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week07/lecture07_closing.ipynb) (complete) | [lecture07_closing.ipynb](week07/lecture07_closing.ipynb), [code](week07/code) |
| 8 | [lecture08_calibration_blank.ipynb](week08/lecture08_calibration_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week08/lecture08_calibration.ipynb) (complete) | [lecture08_calibration.ipynb](week08/lecture08_calibration.ipynb), [code and data](week08/code) |
| 9 | [lecture09_policy_blank.ipynb](week09/lecture09_policy_blank.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week09/lecture09_policy.ipynb) (complete) | [lecture09_policy.ipynb](week09/lecture09_policy.ipynb) |

## Tutorials

| Tutorial | Exercise notebook | Worked | Open the worked version in Colab |
|---|---|---|---|
| 1 (7 Oct) | [tutorial01.ipynb](week03/tutorial01.ipynb) | [tutorial01_complete.ipynb](week03/tutorial01_complete.ipynb); Exercise 3's broken solvers in [tutorial01_debrief.ipynb](week03/tutorial01_debrief.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/week03/tutorial01_complete.ipynb) |

## Reference

- **Python cheat sheet: an attempt to demystify our code.** [python_cheatsheet.ipynb](reference/python_cheatsheet.ipynb) [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/reference/python_cheatsheet.ipynb). The symbols and lines in our code that look like magic, taken apart. The PDF is on Blackboard.
- **pandas cheat sheet: reading and using data.** [pandas_cheatsheet.ipynb](reference/pandas_cheatsheet.ipynb) [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joekopecky/ECU44291-lectures/blob/main/reference/pandas_cheatsheet.ipynb). One page: what each piece of pandas does, and the traps. The PDF is on Blackboard.

Slides, method cards, deadlines and the module's rules on generative AI are on Blackboard. Your own project code lives in your private repository, not here.

## Getting the notebooks into your project

Clone this repository once, next to your project, and pull it each week:

```
cd ~/code
git clone https://github.com/joekopecky/ECU44291-lectures.git   # once
cd ECU44291-lectures
git pull                                                        # every week
```

Then copy the week's blank notebook into your project and work there:

```
cp ~/code/ECU44291-lectures/week02/lecture02_rootfinding_olg_blank.ipynb ~/code/ECU44291-project/notebooks/
```

Never edit files inside this folder; `git pull` will refuse if you have.

### The calibration data (Week 8)

The Irish data for M3 are in [week08/code/data](week08/code/data), with a README on every source. Copy them into your project's `data/` folder once:

```
cp ~/code/ECU44291-lectures/week08/code/data/* ~/code/ECU44291-project/data/
```

The Week 8 notebook finds the data by itself: it reads `code/data/` when it sits next to it, and otherwise (in your project, or on Colab) reads the same files from this repository.
