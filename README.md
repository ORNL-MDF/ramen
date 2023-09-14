# Ramen: Rapid Alloy Models for Enhanced desigN
Ramen is a Python library for inexpensive analytic and semi-analytic models for process-structure-property calculations for alloys. Ramen uses [Mist](https://code.ornl.gov/mist/mist) as the underlying data structure for inputs and outputs.

*This is unreleased software created at Oak Ridge National Laboratory. Please do not release to entities outside the laboratory without discussion with the developers.*

## Installing Ramen
```
# First install mist
$ git clone https://code.ornl.gov/mist/mist
$ cd mist
$ pip install .
# Now install ramen
$ git clone https://code.ornl.gov/ramen/ramen
$ cd ramen
$ pip install .
```

## Running the example
```
$ cd examples
$ python AlCu_eutectic_spacing.py
```