#!/usr/bin/env python
import ROOT,os
from math import sqrt
from MyRootTools.plotter.Plotter import Plotter
import Analysis.Tools.syncer


# Create some example plots
hist1 = ROOT.TH1F("hist1", "hist1", 5, 0, 500)
hist1.SetBinContent(1, 50)
hist1.SetBinContent(2, 40)
hist1.SetBinContent(3, 30)
hist1.SetBinContent(4, 20)
hist1.SetBinContent(5, 10)

hist2 = ROOT.TH1F("hist2", "hist2", 5, 0, 500)
hist2.SetBinContent(1, 10)
hist2.SetBinContent(2, 10)
hist2.SetBinContent(3, 10)
hist2.SetBinContent(4, 10)
hist2.SetBinContent(5, 10)

signal1 = ROOT.TH1F("signal1", "signal1", 5, 0, 500)
signal1.SetBinContent(1, 70)
signal1.SetBinContent(2, 40)
signal1.SetBinContent(3, 20)
signal1.SetBinContent(4, 20)
signal1.SetBinContent(5, 10)

signal2 = ROOT.TH1F("signal2", "signal2", 5, 0, 500)
signal2.SetBinContent(1, 20)
signal2.SetBinContent(2, 60)
signal2.SetBinContent(3, 40)
signal2.SetBinContent(4, 20)
signal2.SetBinContent(5, 30)

up1 = ROOT.TH1F("up1", "up1", 5, 0, 500)
up1.SetBinContent(1, 45)
up1.SetBinContent(2, 35)
up1.SetBinContent(3, 35)
up1.SetBinContent(4, 25)
up1.SetBinContent(5, 15)

down1 = ROOT.TH1F("down1", "down1", 5, 0, 500)
down1.SetBinContent(1, 45)
down1.SetBinContent(2, 35)
down1.SetBinContent(3, 25)
down1.SetBinContent(4, 15)
down1.SetBinContent(5, 5)

data = ROOT.TH1F("data", "data", 5, 0, 500)
data.SetBinContent(1, 50)
data.SetBinContent(2, 60)
data.SetBinContent(3, 40)
data.SetBinContent(4, 40)
data.SetBinContent(5, 20)
for i in range(data.GetSize()-2):
    data.SetBinError(i+1, sqrt(data.GetBinContent(i+1)))

################################################################################
# This is how you steer the plotter
p=Plotter("TESTPLOT")
p.drawRatio = True
p.xtitle = "p_{T}"
p.addBackground(hist1, "Background 1", ROOT.kAzure+7)
p.addBackground(hist2, "Background 2", 15)
p.addSystematic(up1, down1, "SYS1", "Background 1")
p.addSignal(signal1, "Signal 1", ROOT.kBlue-2)
p.addSignal(signal2, "Signal 2", ROOT.kGreen-2)
p.addData(data)
p.draw()
