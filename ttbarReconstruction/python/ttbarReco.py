"""
This is a ttbar reconstruction class
"""


import ROOT,os,sys
from math                                import sqrt


class ttbarReco:
    def __init__(self, lepton, met, jets):
        self.__lepton = lepton
        self.__met = met
        self.__jets = jets
        self.__mode = "normal"
        self.all_hypotheses = []
        self.best_hypothesis = None
        self.minimax = None
        if len(self.__jets)<4:
            print "[Error]: TTbar reconstruction needs at least 4 jets!"
            sys.exit(1)
        
            
            
    def changeMode(self, mode):
        self.__mode = mode
        
        
    # Calculate chi2 from all reconstructed objects
    def __calculate_chi2(self, toplep, tophad, Whad, mode):
        Mtlep_mean   = 171.
        Mtlep_sigma  =  16.
        Mthad_mean   = 171.
        Mthad_sigma  =  17.
        MWhad_mean   =  83.
        MWhad_sigma  =  11.
        Mtdiff_sigma = sqrt(pow(Mtlep_sigma,2)+pow(Mthad_sigma,2))
        b_disc_mean  = 1.0
        b_disc_sigma = 0.4
        toplepterm  = pow((toplep.M()-Mtlep_mean)/Mtlep_sigma,2)
        tophadterm  = pow((tophad.M()-Mthad_mean)/Mthad_sigma,2)
        Whadterm    = pow((  Whad.M()-MWhad_mean)/MWhad_sigma,2)
        topdiffterm = pow((toplep.M()-tophad.M())/Mtdiff_sigma,2)
        if mode=="topdiff":
            chi2 = topdiffterm+Whadterm
        else:
            chi2 = toplepterm+tophadterm+Whadterm
        return chi2        

    # Construct all hypotheses from reconstructed neutrinos, lepton and
    # all possible jet permutations
    def __constructHypotheses(self, lepton, neutrinos, jet_permutations):
        hypotheses = []
        for neutrino in neutrinos:
            for (blep,bhad,Wdecay1,Wdecay2) in jet_permutations:
                hypo = {}
                # decay products from lep top
                hypo['lepton']       = lepton
                hypo['neutrino']     = neutrino
                hypo['blep']         = blep
                # decay products from had top
                hypo['bhad']         = bhad
                hypo['WhadDecay1']   = Wdecay1
                hypo['WhadDecay2']   = Wdecay2
                # tops and Ws
                hypo['toplep']       = lepton + neutrino + blep
                hypo['Wlep']         = neutrino + blep
                hypo['tophad']       = bhad + Wdecay1 + Wdecay2
                hypo['Whad']         = Wdecay1 + Wdecay2

                hypo['chi2']         = self.__calculate_chi2(hypo['toplep'],hypo['tophad'],hypo['Whad'],"normal")
                hypotheses.append(hypo)
        return hypotheses

    # Get all possible jet permutations:
    def __getGetPermutations(self, jets):
        # Set maximum number of jets
        Njetsmax = len(jets)
        # Find all possible solutions for the 4 missing jets
        # (blep,bhad,Wdecay1,Wdecay2)
        jet_permutations = []
        for i in range(Njetsmax):
            for j in range(Njetsmax):
                if j == i:
                    continue
                for k in range(Njetsmax):
                    if k==i or k==j:
                        continue
                    for l in range(Njetsmax):
                        if l==i or l==j or l==k:
                            continue
                        jet_i = jets[i]
                        jet_j = jets[j]
                        jet_k = jets[k]
                        jet_l = jets[l]
                        jet_permutations.append( (jet_i, jet_j, jet_k, jet_l) )
        return jet_permutations



    # Get the neutrino 
    def __reconstructNeutrino(self, lepton, met):
        Wlep = ROOT.TLorentzVector()    
        # get relevant observables and constants
        lepton_pT = ROOT.TVector3(lepton.Px(), lepton.Py(), 0)
        neutrino_pT = ROOT.TVector3(met.Px(), met.Py(), 0)
        mass_w = 80.399
        
        # construct variables for solving the system
        mu = mass_w * mass_w / 2 + lepton_pT * neutrino_pT
        A = - (lepton_pT * lepton_pT)
        B = mu * lepton.Pz()
        C = mu * mu - lepton.E() * lepton.E() * (neutrino_pT * neutrino_pT)
        discriminant = B * B - A * C
        
        # Now get all neutrino solutions
        neutrinos = []
        if discriminant <= 0:
            # Take only real part of the solution for pz:
            neutrino = ROOT.TLorentzVector()
            neutrino.SetPxPyPzE(met.Px(),met.Py(),-B / A,0)
            neutrino.SetE(neutrino.P())
            neutrinos.append(neutrino)
        else:
            discriminant = sqrt(discriminant)
            neutrino1 = ROOT.TLorentzVector()
            neutrino1.SetPxPyPzE(met.Px(),met.Py(),(-B - discriminant) / A,0)
            neutrino1.SetE(neutrino1.P())
            neutrino2 = ROOT.TLorentzVector()
            neutrino2.SetPxPyPzE(met.Px(),met.Py(),(-B + discriminant) / A,0)
            neutrino2.SetE(neutrino2.P())
            if neutrino1.E() > neutrino2.E():
                neutrinos.append(neutrino1)
                neutrinos.append(neutrino2)
            else:
                neutrinos.append(neutrino2)
                neutrinos.append(neutrino1)

        # there is either one solution or two 
        return neutrinos


    # minimax variable is contructed as follows:
    # min[ max(mhad1, mlep1), max(mhad2, mlep2), ...]
    # the number indicates the index of the hypothesis 
    def __calculateMinimax(self, hypotheses):
        minMass = 100000 
        for hypo in hypotheses:
            toplep = hypo['toplep']
            tophad = hypo['tophad']
            maxMass = toplep.M() if toplep.M() > tophad.M() else tophad.M()
            if maxMass < minMass:
                minMass = maxMass
        return minMass

    def reconstruct(self):
        # get neutrino solutions
        neutrinos = self.__reconstructNeutrino(self.__lepton, self.__met)
        # get jet permutations
        jet_permutations = self.__getGetPermutations(self.__jets)
        # get all possible ttbar hypotheses
        self.all_hypotheses = self.__constructHypotheses(self.__lepton, neutrinos, jet_permutations)
        # find best hypothesis
        chi2min = 1000000
        for hypo in self.all_hypotheses:
            if hypo['chi2'] < chi2min:
                chi2min = hypo['chi2']
                self.best_hypothesis = hypo 
        # calculate minimax observable
        self.minimax = self.__calculateMinimax(self.all_hypotheses)   
        
                
                
