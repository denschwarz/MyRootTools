import ROOT
import array
from tWZ.Tools.user                      import plot_directory

class PlotWCDependence:
    def __init__(self, filename, histname, bin, WCname, suffix):
        # A few global drawing options
        ROOT.gStyle.SetLegendBorderSize(0)
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        ROOT.gStyle.SetOptStat(0)

        self.__filename = filename
        self.__histname = histname
        self.__bin = bin
        self.__WCname = WCname
        self.__processes = []
        self.__colors = []
        self.__legendtexts = []
        self.plot_dir = plot_directory
        self.__descriptionExists = False
        self.__description = ""
        self.__suffix = suffix
        self.__rebin = 1

    def addProcess(self, pname, color, legendtext):
        self.__processes.append(pname)
        self.__colors.append(color)
        self.__legendtexts.append(legendtext)

    def setDescription(self, text):
        self.__description = text
        self.__descriptionExists = True

    def doRebin(self, rebin):
        self.__rebin = rebin

    def __setDrawOptions(self, hist):
        hist.SetTitle("")
        hist.GetXaxis().SetTitle(self.__WCname)
        hist.GetYaxis().SetTitle("Events")
        hist.GetYaxis().SetTitleOffset(1.3)
        hist.GetYaxis().SetTitleSize(0.06)
        hist.GetYaxis().SetNdivisions(505)
        hist.GetXaxis().SetTickLength(0.07)
        hist.GetXaxis().SetNdivisions(505)
        hist.GetXaxis().SetTitleSize(25)
        hist.GetXaxis().SetTitleFont(43)
        hist.GetXaxis().SetTitleOffset(1.2)
        hist.GetXaxis().SetLabelFont(43)
        hist.GetXaxis().SetLabelSize(21)
        hist.SetLineWidth(2)

    def draw(self):
        file = ROOT.TFile(self.__filename)
        graphs = []
        graphs_norm = []
        ymax = 0
        keys = file.GetListOfKeys()
        bounds = ["-inf", "inf"]
        for pname in self.__processes:
            sm_content = 0
            template = self.__histname+"__"+pname+"__"+self.__WCname+"="
            xvals = []
            yvals = []
            for key in keys:
                keyname = key.GetName()
                if template in keyname:
                    WCvalue = float(keyname.replace(template, ""))
                    hist = file.Get(keyname)
                    hist.Rebin( int(self.__rebin) ) 
                    content = hist.Integral()
                    if self.__bin > 0:
                        content = hist.GetBinContent( int(self.__bin) )
                        bounds[0] = str(hist.GetXaxis().GetBinLowEdge(int(self.__bin)))
                        bounds[1] = str(hist.GetXaxis().GetBinUpEdge(int(self.__bin)))
                    xvals.append(WCvalue)
                    if abs(WCvalue)<0.0000001:
                        sm_content = content
                    yvals.append(content)
                    if content > ymax:
                        ymax = content
            yvals_norm = []
            for y in yvals:
                if sm_content<0.0000001: yvals_norm.append(0)
                else:                    yvals_norm.append(y/sm_content)
            graphs.append(ROOT.TGraph(len(xvals), array.array('f',xvals), array.array('f',yvals)))
            graphs_norm.append(ROOT.TGraph(len(xvals), array.array('f',xvals), array.array('f',yvals_norm)))



        c = ROOT.TCanvas("c", "c", 600, 600)
        ROOT.gPad.SetBottomMargin(0.12)
        ROOT.gPad.SetLeftMargin(0.19)
        leg = ROOT.TLegend(.2, .65, .45, .85)
        for i, graph in enumerate(graphs):
            self.__setDrawOptions(graph)
            graph.SetLineColor(self.__colors[i])
            graph.SetMarkerColor(self.__colors[i])
            if i==0:
                graph.GetHistogram().SetMinimum(0.)
                graph.GetHistogram().SetMaximum(ymax*1.5)
                graph.Draw("AL")
            else:
                graph.Draw("L SAME")
            leg.AddEntry(graph, self.__legendtexts[i], "l")
        leg.Draw()

        if self.__descriptionExists:
            description = ROOT.TLatex(3.5, 24, bounds[0]+" < "+self.__description+" < "+bounds[1])
            description.SetNDC()
            description.SetTextAlign(13)
            description.SetTextFont(52)
            description.SetTextSize(0.04)
            description.SetX(0.5)
            description.SetY(0.8)
            description.Draw()
        c.Print(self.plot_dir+"/"+self.__suffix+"__"+self.__WCname+"__"+self.__histname+"__"+str(self.__bin)+".pdf")

        d = ROOT.TCanvas("d", "d", 600, 600)
        ROOT.gPad.SetBottomMargin(0.12)
        ROOT.gPad.SetLeftMargin(0.19)
        leg_norm = ROOT.TLegend(.2, .65, .45, .85)
        for i, graph in enumerate(graphs_norm):
            self.__setDrawOptions(graph)
            graph.SetLineColor(self.__colors[i])
            graph.SetMarkerColor(self.__colors[i])
            graph.GetYaxis().SetTitle("#frac{EFT}{SM}")
            if i==0:
                graph.GetHistogram().SetMinimum(0.)
                graph.GetHistogram().SetMaximum(5.)
                graph.Draw("AL")
            else:
                graph.Draw("L SAME")
            leg_norm.AddEntry(graph, self.__legendtexts[i], "l")
        leg_norm.Draw()

        if self.__descriptionExists:
            description_norm = ROOT.TLatex(3.5, 24, bounds[0]+" < "+self.__description+" < "+bounds[1])
            description_norm.SetNDC()
            description_norm.SetTextAlign(13)
            description_norm.SetTextFont(52)
            description_norm.SetTextSize(0.04)
            description_norm.SetX(0.5)
            description_norm.SetY(0.8)
            description_norm.Draw()
        d.Print(self.plot_dir+"/NORM__"+self.__suffix+"__"+self.__WCname+"__"+self.__histname+"__"+str(self.__bin)+".pdf")
