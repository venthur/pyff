How to use the FeedbackController
=================================

Enter the src directory and start FeedbackController:

    cd src
    python FeedbackController.py


If you made changes to the gui.ui or just checked out the tree from SVN, you
may have to rebuild the gui.py:

    cd src
    make

How to use the parallel port under linux
========================================

```bash
$ sudo modprobe -r lp
$ sudo chmod 666 /dev/parport0
```

Citing Us
=========

If you use Pyff for anything that results in a publication, We humbly ask you to
cite us:

```bibtex
@ARTICLE{venthur2010,
    author={Venthur, Bastian  and  Scholler, Simon  and  Williamson, John  and  Dähne, Sven  and  Treder, Matthias S  and  Kramarek, Maria T  and  Müller, Klaus-Robert  and  Blankertz, Benjamin},
    title={Pyff---A Pythonic Framework for Feedback Applications and Stimulus Presentation in Neuroscience},
    journal={Frontiers in Neuroinformatics},
    volume={4},
    year={2010},
    number={100},
    url={http://www.frontiersin.org/neuroinformatics/10.3389/fninf.2010.00100/abstract},
    doi={10.3389/fninf.2010.00100},
    issn={1662-5196},
}
```

