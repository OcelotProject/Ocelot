Accepted differences
********************

Ocelot does not exactly reproduce the release version of ecoinvent. Here is a list of accepted differences between the two model outputs.

Roundoff errors
===============

Occasionally the ecoinvent system model will round small numbers to zero. For example, in the master data the dataset ``natural gas, burned in gas turbine, for compressor station`` releases 2.9 * 10^-17 kg of ``Dioxins, measured as 2,3,7,8-tetrachlorodibenzo-p-dioxin``. I guess that this is a standard factor for combustion which is scaled down to the energy consumption in this activity. This number is rounded to zero in the official release, but Ocelot keeps this small emission.
