# Networking and LLM, enhanced with system instructions

This repo is part of a blog post found here: <insert link>.  

## Getting Started

Clone this repo and then create a `.env` file with the following fields and fill in with your own information.

```commandline
OPENAI_API_KEY=<INSERT OPENAI API KEY>
APIC=<INSERT APIC IP>
APIC_USERNAME=<INSERT USERNAME>
APIC_PASSWORD=<INSERT PASSWORD>
APIC_PORT=<INSERT PORT NUMBER>
```

* Run `pip install -r requirements.txt`
* Modify instructions in [instructions](instructions) directory as needed
* Example command `python eval.py --tuned --iteration 1`, 
  * `--tuned` implies that we want to run against [tuned.md](instructions/tuned.md) file. Other options are `few-shot` and `zero-shot`
  * `--iteration` suggests how many times to run the test

### Example Output
```
(.venv) ➜  networking_llm_instruction git:(main) ✗ python eval.py --tuned --iteration 1
Number of iterations: 1
sending request to openAI
using gpt-4-1106-preview, this run cost: 0.13 with 12714 tokens
Initializing SSH Session...
Question: Q1. how to get a list of Tenants
correct answer cmd: moquery -c fvTenant
gpt answer cmd: moquery -c fvTenant
Question: Q2. how to get a list of EPGs
correct answer cmd: moquery -c fvAEPg
gpt answer cmd: moquery -c fvAEPg
Question: Q3. how to get a list of path bindings
correct answer cmd: moquery -c fvRsPathAtt
gpt answer cmd: moquery -c fvRsPathAtt
Question: Q4. how to get a list of filters
correct answer cmd: moquery -c vzFilter
gpt answer cmd: moquery -c vzFilter
Question: Q5. how to find a list of VPC paired devices
correct answer cmd: moquery -c fabricExplicitGEp
```

## Results
Results will be stored in [results](results) directory in a CSV format
Each result has a score of `-1`(invalid syntax), `0`(incorrect, but syntax is OK) and `1`(correct)


## Plot Results
* We use plotly library to show the end results
* There are a few examples in the `utils/plot.py` main sections
* Run `python utils/plot.py` will plot all the charts as shown from the blog post.
* You can make adjustments as needed from the main section of `plot.py`.