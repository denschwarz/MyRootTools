import ROOT
from math import sqrt

class backgroundAlpha:
    def __init__(self):
        self.__data_CR = ROOT.TH1F()
        self.__MC_CR = ROOT.TH1F()
        self.__MC_SR = ROOT.TH1F()
        self.__alpha_hist = ROOT.TH1F()
        self.__xmin = 0
        self.__xmax = 100000
        self.__fitfunctions = []
        self.__fitformulas = []

    def setDataCR(self, hist):
        self.__data_CR = hist.Clone()

    def subtractBackgroundCR(self, hist):
        self.__data_CR.Add(hist, -1)

    def setMCCR(self, hist):
        self.__MC_CR = hist.Clone()

    def setMCSR(self, hist):
        self.__MC_SR = hist.Clone()

    def setFitFormula(self, formula):
        self.__fitformulas.append(formula)

    def setFitRange(self, xmin, xmax):
        self.__xmin = xmin
        self.__xmax = xmax

    def getAlphaHist(self):
        return self.__alpha_hist

    def getAlphaFunctions(self):
        return self.__fitfunctions

    ############################################################################
    ## Error propagation for a ratio (c1+-e1)/(c2+-e2)
    def __doErrorProgagationRatio(self, c1, e1, c2, e2):
        error = 0.
        ratio = 0.
        if c2 != 0:
            ratio = c1/c2
            error = sqrt(e1/c2 * e1/c2 + c1*e2/(c2*c2) * c1*e2/(c2*c2))
        return ratio, error

    def __calculateAlphaHist(self):
        Nbins = self.__data_CR.GetSize()-2
        self.__alpha_hist = self.__MC_CR.Clone()
        self.__alpha_hist.Reset()
        for i in range(Nbins):
            bin = i+1
            c1 = self.__MC_CR.GetBinContent(bin)
            e1 = self.__MC_CR.GetBinError(bin)
            c2 = self.__MC_SR.GetBinContent(bin)
            e2 = self.__MC_SR.GetBinError(bin)
            ratio, error = self.__doErrorProgagationRatio(c1, e1, c2, e2)
            self.__alpha_hist.SetBinContent(bin, ratio)
            self.__alpha_hist.SetBinError(bin, error)

    def __doAlphaFit(self):
        counter=1
        for formula in self.__fitformulas:
            fit = ROOT.TF1("fit"+str(counter), formula, self.__xmin, self.__xmax)
            self.__alpha_hist.Fit("fit"+str(counter),"R")
            self.__fitfunctions.append(fit)
            print formula, "has a chi2 of", fit.GetChisquare()
            counter+=1


    def getPrediction(self):
        self.__calculateAlphaHist()
        self.__doAlphaFit()
        prediction = self.__data_CR.Clone()
        Nbins = prediction.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            content = prediction.GetBinContent(bin)
            error = prediction.GetBinError(bin)
            bincenter = prediction.GetBinCenter(bin)
            centralfactor = self.__fitfunctions[0].Eval(bincenter)
            prediction.SetBinContent(bin, content*centralfactor)

            maxdiff = 0
            for i in range(len(self.__fitfunctions)):
                if i==0: continue
                diff = abs(self.__fitfunctions[0].Eval(bincenter) - self.__fitfunctions[i].Eval(bincenter))
                if diff > maxdiff:
                    maxdiff = diff
            syserror = content*maxdiff
            totalerror = sqrt( (error*centralfactor)*(error*centralfactor) + syserror*syserror )
            prediction.SetBinError(bin,totalerror)
        return prediction
