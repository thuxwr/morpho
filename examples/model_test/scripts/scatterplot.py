# Example for drawing scatter plot of shrinkage vs Z-score.
#
# Sampler: A set of parameters is selected randomly according to the prior.
# Generator: Data is generated with input parameters from the sampler.
# Analyzer: Analyze data and provide posterior distribution of parameters.
# Tester: Test scatter plot.
#
# Authors: W. Xu

from morpho import *

sampler_config = {
    "model_code": "model_test/models/model_fit.stan",
    "input_data": {
        "N": 0,
        "x": [],
        "y": []
    },
    "interestParams": ["slope", "intercept", "sigma"],
    "iter": 400,
    "warmup": 300
}

generator_config = {
    "model_code": "model_test/models/model_generator.stan",
    "input_data": {
        "xmin": 1,
        "xmax": 10
    },
    "interestParams": ["x", "y"],
    "iter": 1000,
    "warmup": 500
}

tester_config = {
    "variables": ["slope", "intercept", "sigma"],
    "output_path": "model_test/plots"
}

# Input for tester: a list containing results from sampler and analyzer. 
SamplingResult = []
samplerProcessor = PyStanSamplingProcessor("sampler")
samplerProcessor.Configure(sampler_config)
samplerProcessor.Run()
SamplingResult.append(samplerProcessor.results)

for i in range(len(samplerProcessor.results["is_sample"])):
    # Throw away warmup samples.
    if not samplerProcessor.results["is_sample"][i]:
        continue

    # Pass parameters to generator.
    generatorProcessor = PyStanSamplingProcessor("generator%d"%i)
    for parname in sampler_config["interestParams"]:
        generator_config["input_data"][parname] = samplerProcessor.results[parname][i]
    generatorProcessor.Configure(generator_config)
    generatorProcessor.Run()

    # Pass data from generator to analyzer.
    analyzerProcessor = PyStanSamplingProcessor("analyzer%d"%i)
    sampler_config["input_data"]["x"] = []
    sampler_config["input_data"]["y"] = []
    for j in range(len(generatorProcessor.results["is_sample"])):
        if generatorProcessor.results["is_sample"][j]==0:
            continue
        sampler_config["input_data"]["x"].append(generatorProcessor.results["x"][j])
        sampler_config["input_data"]["y"].append(generatorProcessor.results["y"][j])
    sampler_config["input_data"]["N"] = len(sampler_config["input_data"]["x"])
    sampler_config["iter"] = 2000
    sampler_config["warmup"] = 1000
    analyzerProcessor.Configure(sampler_config)
    analyzerProcessor.Run()
    SamplingResult.append(analyzerProcessor.results)

# Run tester.
testerProcessor = ScatterPlot("scatter")
testerProcessor.data = SamplingResult
testerProcessor.Configure(tester_config)
testerProcessor.Run()



