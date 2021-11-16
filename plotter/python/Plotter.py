"""
This is a plotter class. It can be used to draw CMS publication-ready plots.
You can add three types of histograms to a plot: backgrounds, signals and data.
Backgrounds have a name (that appears in the legend), a color, are stacked and
appear as colored areas.
Signals have a name (that appears in the legend) and a color and appear as
lines in the plot.
Data can be added only once and appears as black markers.
Systematic uncertainties are plugged in as variaitons of single backgrounds and
treated internally in the plotter.

Some parameters can be changed in order to customize the plot.
"""


import ROOT,os,sys
from math                                import sqrt
from tWZ.Tools.user                      import plot_directory


class Plotter:
    def __init__(self, name):
        # A few global drawing options
        ROOT.gStyle.SetLegendBorderSize(0)
        ROOT.gStyle.SetPadTickX(1)
        ROOT.gStyle.SetPadTickY(1)
        ROOT.gStyle.SetOptStat(0)

        # Some parameters that can be changed
        self.plotname = name                        # Name of the pdf file
        self.plot_dir = plot_directory              # Directory to save in
        self.legend = ROOT.TLegend(.6,.5,.8,.85)    # Legend
        self.ytitle = "Events"                      # Title Y-axis
        self.xtitle = ""                            # Title X-axis
        self.ratiotitle = "#frac{Data}{SM}"         # Title of ratio
        self.drawRatio = False                      # Draw ratio?
        self.subtext = "Work in progress"           # Subtext of CMS label
        self.lumi = "137"                           # lumi value in label
        self.yfactor = 1.7                          # scale y-axis

        # Internal parameters that are set automatically
        self.__bkgtotal = ROOT.TH1F()                 # Hist for sum of backgrounds
        self.__errorhist = ROOT.TH1F()                # Hist for sys uncert
        self.__hasData = False                        # Keep track if date have been added
        self.__hasSignal = False                      # Keep track if signals have been added
        self.__hasBackground = False                  # Keep track if backgrounds have been added
        self.__doSystematics = False                  # Keep track if systematics have been added
        self.__backgrounds = []                       # Hists and infos of all backgrounds
        self.__signals = []                           # Hists and infos of all signals
        self.__data = {}                              # Hist and info of data
        self.__sysnames = []                          # Names of uncertainties
        self.__stack = ROOT.THStack()                 # Stack for backgrounds
        self.__ymin = 0                               # minimum of any histogram
        self.__ymax = 0                               # maximum of any histogram
        self.__xmin = -1                              # min of x-axis
        self.__xmax = -1                              # max of x-axis

    ############################################################################
    # Add backgrounds that are merged to a stack and displayed as filled areas
    def addBackground(self, hist, legendtext, color):
        self.__hasBackground = True
        bkg = {}
        bkg["name"] = legendtext
        bkg["hist"] = hist
        bkg["hist"].SetFillColor(color)
        bkg["hist"].SetLineColor(color)
        self.__backgrounds.append(bkg)
        if hist.GetMaximum() > self.__ymax:
            self.__ymax = hist.GetMaximum()
        # Check if min and max bounds of x-axis fit other histograms
        if self.__xmin == -1:
            self.__xmin = hist.GetXaxis().GetBinLowEdge(1)
        else:
            if hist.GetXaxis().GetBinLowEdge(1) != self.__xmin:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)
        if self.__xmax == -1:
            self.__xmax = hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2)
        else:
            if hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2) != self.__xmax:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)
    ############################################################################
    # Add signals that are displayed as lines
    def addSignal(self, hist, legendtext, color):
        self.__hasSignal = True
        sig = {}
        sig["name"] = legendtext
        sig["hist"] = hist
        sig["hist"].SetLineColor(color)
        sig["hist"].SetLineWidth(2)
        self.__signals.append(sig)
        if hist.GetMaximum() > self.__ymax:
            self.__ymax = hist.GetMaximum()
        # Check if min and max bounds of x-axis fit other histograms
        if self.__xmin == -1:
            self.__xmin = hist.GetXaxis().GetBinLowEdge(1)
        else:
            if hist.GetXaxis().GetBinLowEdge(1) != self.__xmin:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)
        if self.__xmax == -1:
            self.__xmax = hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2)
        else:
            if hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2) != self.__xmax:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)

    ############################################################################
    # Add data that are displayed with markers,
    # only one data histogram is allowed
    def addData(self, hist, legendtext="Data"):
        if self.__hasData:
            print "[Error]: Cannot add Data more than once."
            sys.exit(1)
        self.__hasData = True
        self.__data["name"] = legendtext
        self.__data["hist"] = hist
        self.__data["hist"].SetLineColor(ROOT.kBlack);
        self.__data["hist"].SetMarkerColor(ROOT.kBlack);
        self.__data["hist"].SetMarkerStyle(8);
        self.__data["hist"].SetMarkerSize(1);
        if hist.GetMaximum() > self.__ymax:
            self.__ymax = hist.GetMaximum()
        # Check if min and max bounds of x-axis fit other histograms
        if self.__xmin == -1:
            self.__xmin = hist.GetXaxis().GetBinLowEdge(1)
        else:
            if hist.GetXaxis().GetBinLowEdge(1) != self.__xmin:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)
        if self.__xmax == -1:
            self.__xmax = hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2)
        else:
            if hist.GetXaxis().GetBinUpEdge(hist.GetSize()-2) != self.__xmax:
                print "[Error]: Histogram hast not the same lower bound as those already added."
                sys.exit(1)

    ############################################################################
    # Add systematic
    def addSystematic(self, up, down, sysname, bkgname):
        self.__doSystematics = True
        foundBackground = False
        for bkg in self.__backgrounds:
            if bkg["name"] == bkgname:
                foundBackground = True
                self.__sysnames.append(sysname)
                bkg[sysname+"__up"] = up
                bkg[sysname+"__down"] = down
        if not foundBackground:
            print "[Error]: Trying to add %s systematic to %s, but could not find a background with name %s" %(sysname, bkgname, bkgname)
            sys.exit(1)

    ############################################################################
    # Customize min/max of y axis
    def setCustomYRange(self, min, max):
        self.__ymin = min
        self.__ymax = max

    ############################################################################
    # Private function to sort backgrounds by their integral, put them in a stack,
    # and fill legend with the names (in the correct order).
    # Also create a histogram with all backgrounds added.
    def __buildStack(self):
        bkg_list = []
        # First go through backgrounds and store the integral
        isFirst = True
        for bkg in self.__backgrounds:
            integral = bkg["hist"].Integral()
            bkg_list.append( (bkg["hist"], integral, bkg["name"]) )
            if isFirst:
                self.__bkgtotal = bkg["hist"].Clone()
                isFirst = False
            else:
                self.__bkgtotal.Add(bkg["hist"])
        # Sort by integral
        def takeSecond(elem):
            return elem[1]
        bkg_list.sort(key=takeSecond)
        # Now fill stack
        for hist, integral, bkgname in bkg_list:
            self.__stack.Add(hist)
        # Legend has to be filled in reverse order
        for hist, integral, bkgname in reversed(bkg_list):
            self.legend.AddEntry(hist, bkgname, "f")
        # Also set a new ymax
        if self.__stack.GetMaximum() > self.__ymax:
            self.__ymax = self.__stack.GetMaximum()

    ############################################################################
    # Private, add up all sys variations
    # Use central for up/down if no Systematics are set
    def __getTotalSystematic(self):
        uphists = []
        downhists = []
        for sys in self.__sysnames:
            h_up = ROOT.TH1F()
            h_down = ROOT.TH1F()
            for i,bkg in enumerate(self.__backgrounds):
                if sys+"__up" in bkg.keys():
                    if i==0:
                        h_up = bkg[sys+"__up"].Clone()
                        h_down = bkg[sys+"__down"].Clone()
                    else:
                        h_up.Add(bkg[sys+"__up"])
                        h_down.Add(bkg[sys+"__down"])
                else:
                    if i==0:
                        h_up = bkg["hist"].Clone()
                        h_down = bkg["hist"].Clone()
                    else:
                        h_up.Add(bkg["hist"])
                        h_down.Add(bkg["hist"])
            uphists.append(h_up)
            downhists.append(h_down)
        self.__calculateTotalUncert(uphists, downhists)

    ############################################################################
    # Private, return a histogram with all backgrounds added and errors from the
    # systematic variations
    def __calculateTotalUncert(self, uphists, downhists):
        errorhist = self.__bkgtotal.Clone()
        Nbins = self.__bkgtotal.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            sum2 = 0
            for j, hist in enumerate(uphists):
                diff_up = abs(hist.GetBinContent(bin) - self.__bkgtotal.GetBinContent(bin))
                diff_down = abs(downhists[j].GetBinContent(bin) - self.__bkgtotal.GetBinContent(bin))
                sum2 += 0.5*(diff_up + diff_down)
            err = errorhist.GetBinError(bin)
            errorhist.SetBinError(bin, sqrt(sum2+err))
        self.__errorhist = errorhist
    ############################################################################
    # Private, create the ratio plot
    def __getRatio(self, h1, h2):
        ratio = h1.Clone()
        Nbins = ratio.GetSize()-2
        for i in range(Nbins):
            bin=i+1
            if h2.GetBinContent(bin)==0:
                r=0
                e=0
            else:
                r = h1.GetBinContent(bin)/h2.GetBinContent(bin)
                e = h1.GetBinError(bin)/h2.GetBinContent(bin)
            ratio.SetBinContent(bin,r)
            ratio.SetBinError(bin,e)
        return ratio

    ############################################################################
    # Private, set options for the CMS label
    def __getCMS(self):
        cmstext = ROOT.TLatex(3.5, 24, "CMS")
        cmstext.SetNDC()
        cmstext.SetTextAlign(13)
        cmstext.SetTextFont(62)
        if self.drawRatio: cmstext.SetTextSize(0.08)
        else:              cmstext.SetTextSize(0.06)
        cmstext.SetX(0.24)
        cmstext.SetY(0.84)
        return cmstext

    ############################################################################
    # Private, set options for the subtext of the CMS label
    def __getSubtitle(self):
        subtext = ROOT.TLatex(3.5, 24, self.subtext)
        subtext.SetNDC()
        subtext.SetTextAlign(13)
        subtext.SetX(0.24)
        subtext.SetTextFont(52)
        if self.drawRatio: subtext.SetTextSize(0.06)
        else:              subtext.SetTextSize(0.04)
        subtext.SetY(0.77)
        return subtext

    ############################################################################
    # Private, set options for the lumi label
    def __getLumi(self):
        infotext = "%s fb^{-1} (13 TeV)" %(self.lumi)
        lumitext = ROOT.TLatex(3.5, 24, infotext)
        lumitext.SetNDC()
        lumitext.SetTextAlign(33)
        lumitext.SetTextFont(42)
        lumitext.SetX(0.9)
        if self.drawRatio:
            lumitext.SetTextSize(0.055)
            lumitext.SetY(0.961)
        else:
            lumitext.SetTextSize(0.0367)
            lumitext.SetY(0.941)
        lumitext.Draw()
        return lumitext

    ############################################################################
    # Private, set draw options for the histograms
    def __setDrawOptions(self, hist):
        hist.SetTitle("")
        hist.GetXaxis().SetTitle(self.xtitle)
        hist.GetYaxis().SetTitle(self.ytitle)
        hist.GetYaxis().SetTitleOffset(1.3)
        hist.GetYaxis().SetTitleSize(0.06)
        hist.GetYaxis().SetNdivisions(505)
        hist.GetYaxis().SetRangeUser(self.__ymin, self.yfactor*self.__ymax)
        hist.GetXaxis().SetTickLength(0.07)
        hist.GetXaxis().SetNdivisions(505)
        if not self.drawRatio:
            hist.GetXaxis().SetTitleSize(25)
            hist.GetXaxis().SetTitleFont(43)
            hist.GetXaxis().SetTitleOffset(1.2)
            hist.GetXaxis().SetLabelFont(43)
            hist.GetXaxis().SetLabelSize(21)
        else:
            hist.GetXaxis().SetLabelSize(0.)
            hist.GetYaxis().SetLabelSize(0.)

    ############################################################################
    # Private, set draw options for the histograms
    def __setRatioDrawOptions(self, ratio):
        ratio.SetTitle('')
        ratio.GetYaxis().SetTitle(self.ratiotitle)
        ratio.GetYaxis().SetRangeUser(0.5, 1.5)
        ratio.GetYaxis().SetNdivisions(505)
        ratio.GetYaxis().CenterTitle()
        ratio.GetYaxis().SetTitleSize(22)
        ratio.GetYaxis().SetTitleFont(43)
        ratio.GetYaxis().SetTitleOffset(2.2)
        ratio.GetYaxis().SetLabelFont(43)
        ratio.GetYaxis().SetLabelSize(19)
        ratio.GetYaxis().SetLabelOffset(0.009)
        ratio.GetXaxis().SetTitle(self.xtitle)
        ratio.GetXaxis().SetTickLength(0.07)
        ratio.GetXaxis().SetTitleSize(25)
        ratio.GetXaxis().SetTitleFont(43)
        ratio.GetXaxis().SetTitleOffset(4.0)
        ratio.GetXaxis().SetLabelFont(43)
        ratio.GetXaxis().SetLabelSize(21)
        ratio.GetXaxis().SetLabelOffset(0.035)
        ratio.GetXaxis().SetNdivisions(505)

    ############################################################################
    # This function draws and saves the final plot.
    # It takes care of which objects exist (backgrounds, signals, data) and
    # all cosmetics are steered from here
    def draw(self):
        c = ROOT.TCanvas("c", "c", 600, 600)
        pady1 = 0.31 if self.drawRatio else 0.0
        pad1 = ROOT.TPad("pad1", "pad1", 0, pady1, 1, 1.0)
        if self.drawRatio: pad1.SetBottomMargin(0.02)
        else:              pad1.SetBottomMargin(0.12)
        pad1.SetLeftMargin(0.19)
        pad1.Draw()
        pad1.cd()

        histdrawn = False # Keep track if "SAME" option should be used
        if self.__hasData:
            self.legend.AddEntry(self.__data["hist"], self.__data["name"], "pel")
        if self.__hasBackground:
            self.__buildStack()
            self.__setDrawOptions(self.__backgrounds[0]["hist"])
            self.__backgrounds[0]["hist"].Draw("HIST")
            histdrawn = True
            self.__stack.Draw("HIST SAME")
            if self.__doSystematics:
                self.__getTotalSystematic()
                self.__errorhist.SetFillStyle(3245)
                self.__errorhist.SetFillColor(13)
                self.__errorhist.SetLineWidth(0)
                self.__errorhist.SetMarkerStyle(0)
                self.__errorhist.Draw("E2 SAME")
                self.legend.AddEntry(self.__errorhist, "Total uncertainty","f")
        if self.__hasSignal:
            for sig in self.__signals:
                self.__setDrawOptions(sig["hist"])
                self.legend.AddEntry(sig["hist"], sig["name"], "l")
                if histdrawn: sig["hist"].Draw("SAME")
                else:         sig["hist"].Draw("")
                histdrawn = True

        if self.__hasData:
            self.__setDrawOptions(self.__data["hist"])
            if histdrawn: self.__data["hist"].Draw("P SAME")
            else:         self.__data["hist"].Draw("P")
            histdrawn = True


        # Now draw the ratio pad
        if self.drawRatio:
            axis = ROOT.TGaxis( self.__xmin, self.__ymin, self.__xmin, self.yfactor*self.__ymax, self.__ymin, self.yfactor*self.__ymax, 505,"")
            axis.SetLabelOffset(0.01)
            axis.SetLabelFont(43)
            axis.SetLabelSize(21)
            axis.SetNdivisions(505)
            axis.Draw()
            c.cd();
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
            pad2.SetLeftMargin(0.19)
            pad2.SetTopMargin(0)
            pad2.SetBottomMargin(0.38);
            pad2.Draw()
            pad2.cd()
            ratio = self.__getRatio(self.__bkgtotal, self.__bkgtotal)
            self.__setRatioDrawOptions(ratio)
            ratio.SetFillColor(0)
            ratio.SetLineColor(15)
            ratio.SetLineWidth(2)
            ratio.Draw("HIST")
            if self.__doSystematics:
                ratio_uncert = self.__getRatio(self.__errorhist, self.__bkgtotal)
                ratio_uncert.Draw("E2 SAME")
            if self.__hasSignal:
                ratios_sig = []
                for sig in self.__signals:
                    ratios_sig.append(self.__getRatio(sig["hist"], self.__bkgtotal))
                for r in ratios_sig:
                    self.__setRatioDrawOptions(r)
                    r.Draw("HIST SAME")
            if self.__hasData:
                ratio_data = self.__getRatio(self.__data["hist"], self.__bkgtotal)
                self.__setRatioDrawOptions(ratio_data)
                ratio_data.Draw("P SAME")
            ROOT.gPad.RedrawAxis()

        # Back to pad1 and draw labels and legend
        pad1.cd()
        CMSlabel = self.__getCMS()
        CMSlabel.Draw()
        sublabel = self.__getSubtitle()
        sublabel.Draw()
        lumilable = self.__getLumi()
        lumilable.Draw()
        self.legend.Draw()
        ROOT.gPad.RedrawAxis()

        # Save plot
        plotname = os.path.join(self.plot_dir, self.plotname+".pdf")
        c.Print(plotname)
