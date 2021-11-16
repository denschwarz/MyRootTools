"""
Simple class to use the ABCD method for background estimation.
Just set histograms for control regions A, B, C and let the class return D.
Transfer factor is calculated from simulation in A and B, and then applied
to the data histogram C in order to get a predcition for D.
"""

import ROOT
from math import sqrt

class BackgroundABCD:
    def __init__(self):
        self.__histA = ROOT.TH1F()
        self.__histB = ROOT.TH1F()
        self.__histC = ROOT.TH1F()
        self.__histA_exists = False
        self.__histB_exists = False
        self.__histC_exists = False
        self.__UncertaintiesA = ROOT.TH1F()
        self.__UncertaintiesB = ROOT.TH1F()

    ############################################################################
    ## Get difference of central to up/down (average)
    def __calculateUncertainty(self, central, up, down):
        Nbins = central.GetSize()-2
        uncert = central.Clone()
        uncert.Reset()
        for i in range(Nbins):
            bin = i+1
            diff_up = abs(central.GetBinContent(bin)-up.GetBinContent(bin))
            diff_down = abs(central.GetBinContent(bin)-down.GetBinContent(bin))
            diff = (diff_up+diff_down)/2
            uncert.SetBinContent(bin, diff)
        return uncert

    ############################################################################
    ## Quadratically add two histograms that contain uncertainties as bin content
    def __addUncertainties(self, uncert1, uncert2):
        Nbins = uncert1.GetSize()-2
        uncert = uncert1.Clone()
        uncert.Reset()
        for i in range(Nbins):
            bin = i+1
            u1 = uncert1.GetBinContent(bin)
            u2 = uncert2.GetBinContent(bin)
            uncert.SetBinContent(bin, sqrt(u1*u1+u2*u2))
        return uncert

    ############################################################################
    ## Set histogram A, use BinError for uncertainty
    def setSampleRegionA(self, hist):
        self.__histA = hist.Clone()
        self.__UncertaintiesA = hist.Clone()
        self.__UncertaintiesA.Reset()
        Nbins = hist.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            self.__UncertaintiesA.SetBinContent(bin, hist.GetBinError(bin))
        self.__histA_exists = True

    ############################################################################
    ## Set histogram B, use BinError for uncertainty
    def setSampleRegionB(self, hist):
        self.__histB = hist.Clone()
        self.__UncertaintiesB = hist.Clone()
        self.__UncertaintiesB.Reset()
        Nbins = hist.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            self.__UncertaintiesB.SetBinContent(bin, hist.GetBinError(bin))
        self.__histB_exists = True

    ############################################################################
    ## Add up/down variations to histogram A
    def addUncertaintyRegionA(self, up, down):
        if not self.__histA_exists:
            print "[Error]: Histogram A is not set but needed to add uncertainties."
            sys.exit(1)
        diff = self.__calculateUncertainty(self, self.__histA, up, down)
        self.__UncertaintiesA = self.__addUncertainties(self.__UncertaintiesA, diff)

    ############################################################################
    ## Add up/down variations to histogram B
    def addUncertaintyRegionB(self, up, down):
        if not self.__histB_exists:
            print "[Error]: Histogram B is not set but needed to add uncertainties."
            sys.exit(1)
        diff = self.__calculateUncertainty(self, self.__histB, up, down)
        self.__UncertaintiesB = self.__addUncertainties(self.__UncertaintiesB, diff)

    ############################################################################
    ## Set the sample for region C (this should be data)
    def setSampleRegionC(self, hist):
        self.__histC = hist.Clone()
        self.__histC_exists = True

    ############################################################################
    ## Add backgrounds that are subtracted from histogram C
    def addBackgroundRegionC(self, hist):
        self.__histC.Add(hist, -1)

    ############################################################################
    ## Error propagation for a ratio (c1+-e1)/(c2+-e2)
    def __doErrorProgagationRatio(self, c1, e1, c2, e2):
        error = 0.
        ratio = 0.
        if c2 != 0:
            ratio = c1/c2
            error = sqrt(e1/c2 * e1/c2 + c1*e2/(c2*c2) * c1*e2/(c2*c2))
        return ratio, error

    ############################################################################
    ## Error propagation for a product (c1+-e1)*(c2+-e2)
    def __doErrorProgagationProduct(self, c1, e1, c2, e2):
        error = sqrt(e1*e1*c2*c2 + e2*e2*c1*c1)
        return c1*c2, error

    ############################################################################
    ## Get TF from histograms A and B
    def getTransferFactor(self):
        if not self.__histA_exists:
            print "[Error]: Histogram A is not set but needed for TF."
            sys.exit(1)
        if not self.__histB_exists:
            print "[Error]: Histogram B is not set but needed for TF."
            sys.exit(1)
        tf = self.__histB.Clone()
        tf.Reset()
        Nbins = tf.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            c1 = self.__histB.GetBinContent(bin)
            e1 = self.__UncertaintiesB.GetBinContent(bin)
            c2 = self.__histA.GetBinContent(bin)
            e2 = self.__UncertaintiesA.GetBinContent(bin)
            ratio, error = self.__doErrorProgagationRatio(c1, e1, c2, e2)
            tf.SetBinContent(bin, ratio)
            tf.SetBinError(bin, error)
        return tf

    ############################################################################
    ## Multiply TF with data driven background from region C
    ## (after subtracting backgrounds)
    def getBackgroundPrediction(self):
        if not self.__histC_exists:
            print "[Error]: Histogram C is not set but needed for prediction."
            sys.exit(1)

        # Calculate TF from hists A and B
        tf = self.getTransferFactor()

        # Multiply histogram C with TF
        prediction = self.__histC.Clone()
        prediction_up = self.__histC.Clone()
        prediction_down = self.__histC.Clone()
        prediction.Reset()
        prediction_up.Reset()
        prediction_down.Reset()
        Nbins = tf.GetSize()-2
        for i in range(Nbins):
            bin = i+1
            c1 = tf.GetBinContent(bin)
            e1 = tf.GetBinError(bin)
            c2 = self.__histC.GetBinContent(bin)
            e2 = self.__histC.GetBinError(bin)
            product, error = self.__doErrorProgagationProduct(c1, e1, c2, e2)
            prediction.SetBinContent(bin,product)
            prediction_up.SetBinContent(bin,product+error)
            prediction_down.SetBinContent(bin,product-error)
        return prediction, prediction_up, prediction_down
