# Data Processing
I am not totally sure yet how we want to process and run the data through our network.

I have been using Jupyter notebooks to experiment.

```
pip install jupyter
```

Then, you can run jupyter notebook in the directory with a `.ipynb` file. And you can set up SSH tunnelling to view the notebook on your computer.

```
ssh -L 8888:localhost:8888 -J mav120@h2p.crc.pitt.edu mav120@login0
```

The port and the `mav120@login0` part depend on if you requested a GPU node or not.