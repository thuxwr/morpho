'''
Test correlation matrix by generating correlated multidimensional gaussian random variables.
Authors: W. Xu
Date: 11/27/18
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

class CorrelationTest(unittest.TestCase):

    def test(self):
        logger.info("Sampling random variables.")
        from morpho.processors.sampling import PyStanSamplingProcessor

        pystan_config = {
                "model_code": "model.stan",
                "iter": 50000, 
                "input_data": {
                    "rho12": 0.8,
                    "rho13": 0.5,
                    "rho23": 0.2
                },
                "interestParams": ["x", "y", "z"],
        }
        pystanProcessor = PyStanSamplingProcessor("samplingProcessor")
        pystanProcessor.Configure(pystan_config)

        pystanProcessor.Run()

        from morpho.processors.analysis import correlation

        correlation_config = {
                "interestParams": ["x", "y", "z"]
        }
        correlationAnalyzer = correlation("Analyzer")
        correlationAnalyzer.Configure(correlation_config)
        correlationAnalyzer.data = pystanProcessor.results
        correlationAnalyzer.Run()
        return True

if __name__ == '__main__':
    unittest.main()


