#!/usr/bin/env python
import ROOT,os
from math import sqrt
from MyRootTools.plotter.Plotter import Plotter
import Analysis.Tools.syncer


# This is how you steer the plotter

# Import some example ROOT histograms
from exampleHists import *


for drawRatio in [True, False]:
    plotname = "TESTPLOT_RATIO" if drawRatio else "TESTPLOT"
    p = Plotter(plotname)
    p.drawRatio = drawRatio
    p.ratiorange = 0.2, 1.8
    p.xtitle = "p_{T}"
    # Add Backgrounds, those will be stacked
    p.addBackground(hist1, "Background 1", ROOT.kAzure+7)
    p.addBackground(hist2, "Background 2", 15)
    # Assign a shape systematic by providing up/down variations
    p.addSystematic(up1, down1, "SYS1", "Background 1")
    # Add a normalisation uncertainty
    p.addNormSystematic("Background 2", 0.3)
    # Add some signals
    p.addSignal(signal1, "Signal 1", ROOT.kBlue-2)
    p.addSignal(signal2, "Signal 2", ROOT.kRed, lineStyle=2)
    # Add data
    p.addData(data)
    # Draw
    p.draw()
