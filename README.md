# pydashsim - HAS simulation

Simulates a HTTP Adaptive Streaming (HAS) session based on a throughput pattern and video segment sizes.
The simulation is part of the supplemental material to the HASBRAIN scientific paper: https://github.com/csieber/hasbrain

## QUICKSTART 

You need a traffic pattern and a video to run the simulation:

    python3 pydashsim.py -t samples/traffictrace.csv -s samples/segments.csv

Select a specific adaptation logic with *-l*:

    python3 pydashsim.py -l TRDA -t samples/traffictrace.csv -s samples/segments.csv

The simulation output files are placed in the **out/** folder by default. Existing files are overwritten!

## Adaptation Logics

| Logic                       | Abbreviation | Description                         |
|-----------------------------|--------------|-------------------------------------|
| NoAdaptationLogic (default) | NO           | Always select lowest quality level. |
| KLUDCPLogic                 | KLUDCP       | [1] by C. Müller et al.             |
| TRDALogic                   | TRDA         | [2] by K. Miller et al.             |
| NeuralNetworkLogic          | NN           | [3] by C. Sieber et al.             |

## Usage

```
usage: pydashsim.py [-h] [-o OPT_DIR] -t TRACE -s SEGMENTS [-l LOGIC] [-v]

Execute the simulation.

optional arguments:
  -h, --help            show this help message and exit
  -o OPT_DIR, --opt_dir OPT_DIR
                        Output folder
  -t TRACE, --trace TRACE
                        Goodput trace to use.
  -s SEGMENTS, --segments SEGMENTS
                        Video to use.
  -l LOGIC, --logic LOGIC
                        Adaptation logic (NO, KLUDCP, TRDA)
  -v, --verbose         Enable debug log.
```

## Requirements

  - scipy
  - simpy
  - keras (tested with 1.2)
  - tensorflow

## Citation

If you use the provided material, please cite the following paper:

*Towards Machine Learning-Based Optimal HAS*, Christian Christian, Korbinian Hagn, Christian Moldovan, Tobias Hoßfeld, Wolfgang Kellerer, August, 2018, Url: https://arxiv.org/abs/1808.08065

## References

  * [1] C. Müller, S. Lederer, and C. Timmerer, "An evaluation of dynamic adaptive streaming over http in vehicular environments,” in Proceedings of the 4th Workshop on Mobile Video. ACM, 2012.
  * [2] K. Miller,  E. Quacchio, G. Gennari, and A. Wolisz, “Adaptation algorithm for adaptive streaming over http,” in 19th  International  Packet Video Workshop (PV).  IEEE, 2012.
  * [3] C. Sieber, K. Hagn, C. Moldovan, T. Hoßfeld, W. Kellerer, *Towards Machine Learning-Based Optimal HAS*, August, 2018

