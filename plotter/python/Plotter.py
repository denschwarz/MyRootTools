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
from itertools                           import count
from tWZ.Tools.user                      import plot_directory


class Plotter:
    _ids = count(0)
    def __init__(self, name):
        # Keep track of instances of this class to have unique canvas names
        self.id = next(self._ids)
        
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
        self.lumi = None                            # lumi value in label
        self.log = False                            # log scale?
        self.yfactor = 1.7                          # scale y-axis
        self.rebin = 1                              # rebin hist?
        self.ratiorange = 0.5,1.5                   # y-range of ratio plot
        self.legshift = (0., 0., 0., 0.)            # shift the Legend coordinates (x1, y1, x2, y2)

        # Internal parameters that are set automatically
        self.__bkgtotal = ROOT.TH1F()                 # Hist for sum of backgrounds
        self.__errorhist = ROOT.TGraphAsymmErrors()   # Hist for sys uncert
        self.__hasData = False                        # Keep track if date have been added
        self.__hasSignal = False                      # Keep track if signals have been added
        self.__hasBackground = False                  # Keep track if backgrounds have been added
        self.__doSystematics = False                  # Keep track if systematics have been added
        self.__backgrounds = []                       # Hists and infos of all backgrounds
        self.__sysDeltas = []                         # List of systematic shifts
        self.__sysnames = []                          # List of systematic names
        self.__signals = []                           # Hists and infos of all signals
        self.__data = {}                              # Hist and info of data
        self.__stack = ROOT.THStack()                 # Stack for backgrounds
        self.__ymin = 0                               # minimum of any histogram
        self.__ymax = 0                               # maximum of any histogram
        self.__xmin = -1                              # min of x-axis
        self.__xmax = -1                              # max of x-axis
        self.__NlegEntries = 0                        # number of entries in legend

    ############################################################################
    # Add backgrounds that are merged to a stack and displayed as filled areas
    def addBackground(self, hist, legendtext, color):
        if self.rebin > 1:
            hist.Rebin(self.rebin)
        self.__hasBackground = True
        self.__NlegEntries += 1
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
        if self.rebin > 1:
            hist.Rebin(self.rebin)        
        self.__hasSignal = True
        self.__NlegEntries += 1
        sig = {}
        sig["name"] = legendtext
        sig["hist"] = hist
        sig["hist"].SetFillColorAlpha(ROOT.kWhite, 0.0)
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
        if self.rebin > 1:
            hist.Rebin(self.rebin)
        self.__NlegEntries += 1
        if self.__hasData:
            print "[Error]: Cannot add Data more than once."
            sys.exit(1)
        self.__hasData = True
        self.__data["name"] = legendtext
        self.__data["hist"] = hist
        self.__data["hist"].SetLineColor(ROOT.kBlack)
        self.__data["hist"].SetMarkerColor(ROOT.kBlack)
        self.__data["hist"].SetMarkerStyle(8)
        self.__data["hist"].SetMarkerSize(1)
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
        if self.rebin > 1:
            up.Rebin(self.rebin)
            down.Rebin(self.rebin)            
        self.__doSystematics = True
        foundBackground = False
        for bkg in self.__backgrounds:
            if bkg["name"] == bkgname:
                foundBackground = True
                deltaUp = up.Clone()
                deltaUp.Add(bkg["hist"], -1)
                deltaDown = down.Clone()
                deltaDown.Add(bkg["hist"], -1)
                
                self.__sysDeltas.append( (sysname, bkgname, deltaUp, deltaDown) )
                self.__sysnames.append(sysname)       
        if not foundBackground:
            print "[Error]: Trying to add %s systematic to %s, but could not find a background with name %s" %(sysname, bkgname, bkgname)
            sys.exit(1)

    ############################################################################
    # Add a normalization uncertainty 
    def addNormSystematic(self, bkgname, size):
        self.__doSystematics = True
        foundBackground = False
        for bkg in self.__backgrounds:
            if bkg["name"] == bkgname:
                foundBackground = True    
                up   = bkg["hist"].Clone()
                down = bkg["hist"].Clone()
                up.Scale(1.0+size)
                down.Scale(1.0-size)
                self.addSystematic(up, down, bkgname+"_norm", bkgname)
        if not foundBackground:
            print "[Error]: Trying to add normalization systematic to %s, but could not find a background with name %s" %(sysname, bkgname, bkgname)
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
    # Private, add up all sys variations and MC stat
    # Use central for up/down if no Systematics are set
    def __getTotalUncertainty(self):
        Nbins = self.__bkgtotal.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            bincenter = self.__bkgtotal.GetXaxis().GetBinCenter(bin)
            bincontent = self.__bkgtotal.GetBinContent(bin)
            self.__errorhist.SetPoint(bin, bincenter, bincontent)
            staterr = self.__bkgtotal.GetBinError(bin)
            totalErrSquared_up   = pow(staterr, 2)
            totalErrSquared_down = pow(staterr, 2)
            # Go through all uncertainties and add up shifts connected to the
            # same sys but different backgrounds 
            for sys in self.__sysnames:
                shift_up = 0
                shift_down = 0
                for (sysname, bkgname, deltaUp, deltaDown) in self.__sysDeltas:
                    if sys == sysname:
                        shift_up += deltaUp.GetBinContent(bin)
                        shift_down += deltaDown.GetBinContent(bin)
                totalErrSquared_up += pow(shift_up, 2)
                totalErrSquared_down += pow(shift_down, 2)
            # if the total error is 0.0, the plotter does weird stuff, so
            # set to super small value > 0
            if totalErrSquared_up < pow(10, -20):
                totalErrSquared_up = pow(10, -20)
            if totalErrSquared_down < pow(10, -20):
                totalErrSquared_down = pow(10, -20)
            # Get X errors:
            ex_low = self.__bkgtotal.GetXaxis().GetBinCenter(bin) - self.__bkgtotal.GetXaxis().GetBinLowEdge(bin)
            ex_up =  self.__bkgtotal.GetXaxis().GetBinUpEdge(bin) - self.__bkgtotal.GetXaxis().GetBinCenter(bin)
            self.__errorhist.SetPointError(bin, ex_low, ex_up, sqrt(totalErrSquared_down), sqrt(totalErrSquared_up))
    ############################################################################
    # Private, create the ratio plot
    def __getRatio(self, h1, h2):
        ratio = h1.Clone()
        Nbins = ratio.GetSize()-2
        for i in range(Nbins):
            bin=i+1
            if h2.GetBinContent(bin)==0:
                r=-1
                e=0
            else:
                r = h1.GetBinContent(bin)/h2.GetBinContent(bin)
                e = h1.GetBinError(bin)/h2.GetBinContent(bin)
            ratio.SetBinContent(bin,r)
            ratio.SetBinError(bin,e)
        return ratio
    ############################################################################
    # Private, create the ratio uncertainty plot
    def __getRatioUncert(self, errorgraph):
        ratio = errorgraph.Clone()
        Npoints = errorgraph.GetN()
        for i in range(Npoints):
            point=i+1
            d1, d2 = ROOT.Double(0.), ROOT.Double(0.)
            errorgraph.GetPoint(point, d1, d2)
            Xval = float(d1)
            Yval = float(d2)
            eX_hi = errorgraph.GetErrorXhigh(point)
            eX_lo = errorgraph.GetErrorXlow(point)
                        
            if Yval==0:
                eY_hi = 0
                eY_lo = 0    
            else:
                eY_hi = errorgraph.GetErrorYhigh(point)/Yval
                eY_lo = errorgraph.GetErrorYlow(point)/Yval
                
            ratio.SetPoint(point, Xval, 1.0)
            ratio.SetPointError(point, eX_lo, eX_hi, eY_lo, eY_hi)

        return ratio
    ############################################################################
    # Private, create the ratio plot
    def __getRatioLine(self, h1):
        line = h1.Clone()
        Nbins = line.GetSize()-2
        for i in range(Nbins):
            bin=i+1
            line.SetBinContent(bin,1.0)
            line.SetBinError(bin,0.0)
        return line
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
        lumitext.SetX(0.94)
        if self.drawRatio:
            lumitext.SetTextSize(0.055)
            lumitext.SetY(0.971)
        else:
            lumitext.SetTextSize(0.0367)
            lumitext.SetY(0.951)
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
        if not self.log:
            hist.GetYaxis().SetNdivisions(505)
        else:
            hist.GetYaxis().SetNdivisions(510)
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
    # Private, set draw options for the ratio
    def __setRatioDrawOptions(self, ratio):
        (ymin, ymax) = self.ratiorange
        ratio.SetTitle('')
        ratio.GetYaxis().SetTitle(self.ratiotitle)
        ratio.GetYaxis().SetRangeUser(ymin, ymax)
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
    # Private, set draw options for the ratio that contains outside values        
    def __setRatioOutsideDrawOptions(self, ratio):
        # first apply usual cosmetics
        self.__setRatioDrawOptions(ratio) 
        # Now change marker 
        ratio.SetMarkerSize(0)
        
    ############################################################################
    # Private, get a ratio histogram that contains values outside the y range        
    def __getRatioOutside(self, ratio):        
        # If there are points outside the y range, the error bar is not drawn,
        # even if it would reach into the plot-
        # To solve this, an additional histogram is drawn
        (ymin, ymax) = self.ratiorange
        ratio_outside = ratio.Clone()
        ratio_outside.Reset()
        Nbins = ratio.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            central = ratio.GetBinContent(bin)
            error = ratio.GetBinError(bin)
            min = ratio.GetBinContent(bin)-error
            max = ratio.GetBinContent(bin)+error
            if central > ymax and min < ymax:
                # if point is above y range:
                # 1. move central value down to the edge of y range
                # 2. make error smaller to make the error bar end at the same value as before
                offset = central - ymax
                central_new = central-offset
                error_new   = error-offset
                
            elif central < ymin and max > ymin:
                # if point is below y range:
                # 1. move central value up to the edge of y range
                # 2. make error smaller to make the error bar end at the same value as before
                offset = ymin - central
                central_new = central+offset
                error_new   = error-offset
            else:
                central_new = 0.0
                error_new   = 0.0
            ratio_outside.SetBinContent(bin, central_new)
            ratio_outside.SetBinError(bin, error_new)
        return ratio_outside                

    def getTotalSystematic(self):
        return self.__errorhist
    ############################################################################
    # This function draws and saves the final plot.
    # It takes care of which objects exist (backgrounds, signals, data) and
    # all cosmetics are steered from here
    def draw(self):
        # c = ROOT.TCanvas("c", "c", 600, 600)
        c = ROOT.TCanvas("c"+str(self.id), "c"+str(self.id), 600, 600)
        pady1 = 0.31 if self.drawRatio else 0.0
        pad1 = ROOT.TPad("pad1", "pad1", 0, pady1, 1, 1.0)
        if self.drawRatio: pad1.SetBottomMargin(0.02)
        else:              pad1.SetBottomMargin(0.12)
        pad1.SetTopMargin(0.1)
        pad1.SetLeftMargin(0.19)
        pad1.SetRightMargin(0.05)
        pad1.Draw()
        pad1.cd()
        if self.log:
            self.__ymin = 0.0011*self.__ymax
            self.yfactor *= 100
            pad1.SetLogy()
        self.legend = ROOT.TLegend(.6+self.legshift[0],.85+self.legshift[1]-self.__NlegEntries*0.075,.8+self.legshift[2],.85+self.legshift[3])
        histdrawn = False # Keep track if "SAME" option should be used
        if self.__hasData:
            self.legend.AddEntry(self.__data["hist"], self.__data["name"], "pel")
        if self.__hasBackground:
            self.__buildStack()
            self.__setDrawOptions(self.__backgrounds[0]["hist"])
            self.__backgrounds[0]["hist"].Draw("HIST")
            histdrawn = True
            self.__stack.Draw("HIST SAME")
            # Uncertainty on MC
            self.__getTotalUncertainty()
            self.__setDrawOptions(self.__errorhist)
            self.__errorhist.SetFillStyle(3245)
            self.__errorhist.SetFillColor(13)
            self.__errorhist.SetLineWidth(0)
            self.__errorhist.SetMarkerStyle(0)
            self.__errorhist.Draw("E2 HIST SAME")
            self.legend.AddEntry(self.__errorhist, "Total uncertainty","f")
        if self.__hasSignal:
            for sig in self.__signals:
                self.__setDrawOptions(sig["hist"])
                self.legend.AddEntry(sig["hist"], sig["name"], "l")
                if histdrawn: sig["hist"].Draw("HIST SAME")
                else:         sig["hist"].Draw("HIST ")
                histdrawn = True

        if self.__hasData:
            self.__setDrawOptions(self.__data["hist"])
            if histdrawn: self.__data["hist"].Draw("P SAME")
            else:         self.__data["hist"].Draw("P")
            histdrawn = True

        # Now draw the ratio pad
        if self.drawRatio:
            axis = ROOT.TGaxis( self.__xmin, self.__ymin, self.__xmin, self.yfactor*self.__ymax, self.__ymin, self.yfactor*self.__ymax, 505,"")
            if self.log:
                axis = ROOT.TGaxis( self.__xmin, self.__ymin, self.__xmin, self.yfactor*self.__ymax, self.__ymin, self.yfactor*self.__ymax, 505,"G")
            axis.SetLabelOffset(0.01)
            axis.SetLabelFont(43)
            axis.SetLabelSize(21)
            axis.SetNdivisions(505)
            if self.log:
                axis.SetNdivisions(510)

            axis.Draw()
            c.cd()
            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
            pad2.SetLeftMargin(0.19)
            pad2.SetRightMargin(0.05)
            pad2.SetTopMargin(0)
            pad2.SetBottomMargin(0.38)
            pad2.Draw()
            pad2.cd()
            ratioline = self.__getRatioLine(self.__bkgtotal)
            self.__setRatioDrawOptions(ratioline)
            ratioline.SetFillColor(0)
            ratioline.SetLineColor(15)
            ratioline.SetLineWidth(2)
            ratioline.Draw("HIST")
            ratio_uncert = self.__getRatioUncert(self.__errorhist)
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
                ratio_data_outside = self.__getRatioOutside(ratio_data)
                self.__setRatioOutsideDrawOptions(ratio_data_outside)
                ratio_data_outside.Draw("P SAME")
                
            ROOT.gPad.RedrawAxis()

        # Back to pad1 and draw labels and legend
        pad1.cd()
        CMSlabel = self.__getCMS()
        CMSlabel.Draw()
        sublabel = self.__getSubtitle()
        sublabel.Draw()
        if self.lumi is not None:
            lumilable = self.__getLumi()
            lumilable.Draw()
        self.legend.Draw()
        ROOT.gPad.RedrawAxis()

        # Save plot
        plotname = os.path.join(self.plot_dir, self.plotname+".pdf")
        c.Print(plotname)
