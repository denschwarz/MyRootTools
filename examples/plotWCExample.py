import ROOT
from MyRootTools.plotter.PlotWCDependence import PlotWCDependence
import Analysis.Tools.syncer
from tWZ.Tools.user                      import plot_directory

filename = "/mnt/hephy/cms/dennis.schwarz/www/tWZ/plots/analysisPlots/EFT_SYS_v1_noData/Run2018/all/trilepT-minDLmass12-onZ1-deepjet0-met60/Results.root"
WCname = "cHq1Re11"
processes = ["ttZ", "WZ", "ZZ"]
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen]
legends = ["t#bar{t}Z", "WZ", "ZZ"]

histname = "Z1_pt"
bin = 2


p = PlotWCDependence(filename, histname, bin, WCname)
p.plot_dir = plot_directory+"/WCdependence"
p.setDescription("Z p_{T}")
for i,pname in enumerate(processes):
    p.addProcess(pname, colors[i], legends[i])
p.draw()
