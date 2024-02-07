# Python Minimoog  

Just a little emulation of famous Minimoog synth, using pyo library. 

This project was developed with my unique code buddy @moeni27

### A small advice

The suggestion is to create a conda environment as **pyo** does not work with any python version aside from *v3.9, v3.8, v3.7, v3.6*. Using *miniconda*, you can run the following:
```
conda create -n <env_name> python=3.8
conda activate <env_name>
pip install pyo
```
and to run the program, you just have to:
```
conda activate <env_name>
python minimoog.py
```
