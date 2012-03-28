from droop.rules.scotland import Rule as ScotlandRule
import droop
class BCSTVRule(ScotlandRule):
    """
    TODO: Chris must edit this to say that the Scottish Rules are close enough
    to BCSTV, the only difference is the precision.

    Proposed Rules:
      British Columbia Citizen's Assembly Technical Report
      http://www.citizensassembly.bc.ca/resources/TechReport(full).pdf
    
    Description:
      These rules have been proposed for the Province of British Columbia.
      This is a straightforward implementation of STV and recommended to
      organizations using STV for the first time.  See the Help menu for a
      more detailed description.  For an alternative description of the
      rules see
      http://www.fairvote.org/library/statutes/choice_voting.htm.
  
    Rules:
      The Scottish Local Government Elections Order 2007
      http://www.opsi.gov.uk/legislation/scotland/ssi2007/ssi_20070042_en.pdf

    Description:
      Scotland enacted the STV rules for local elections in 2007. This is a
      straightforward implementation of STV and recommended to
      organizations using STV for the first time.  Previous users of
      British Columbia STV should now use Scottish STV, as the only
      difference between the two sets of rules is that Scottish STV
      carries out computations to five decimal points rather than six.
    """
    name = 'bcstv'
    def options(self):
        ScotlandRule.options(self)
        self.E.options.setopt('precision', default=6, force=True)
        self.E.options.setopt('display', default=6, force=True)

    def info(self):
        return "BC STV"

# This is important to register this rule with Droop!
#with BCSTVRule as rule:
droop.ruleClasses.append(BCSTVRule)
droop.ruleByName[BCSTVRule.name] = BCSTVRule

from droop.rules.electionrule import ElectionRule

class SNTVRule(ElectionRule):
    name = method = 'sntv'

    @classmethod
    def ruleNames(cls):
        "return supported rule name or names"
        return cls.name

    @classmethod
    def helps(cls, helps, name):
        "provide help string for SNTV"
        h = "SNTV is the classic most votes rule.\n"
        h += "\nThere are no options.\n"
        helps[name] = h

    def __init__(self, E):
        "initialize rule"
        self.E = E

    def options(self):
        "initialize election parameters"
        self.E.options.setopt('arithmetic', default='rational', force=True)
        self.E.options.setopt('precision', default=0, force=True)
        self.E.options.setopt('display', default=0, force=True)

    def info(self):
        "return an info string for the election report"
        return "SNTV"

    def tag(self):
        "return a tag string for unit tests"
        return self.name

    #########################
    #
    #   Main Election Counter
    #
    #########################
    def count(self):
        E = self.E  # election object
        C = E.C     # candidates

        E.logAction('begin', 'Begin Count')

        # Take the leading candidate from each ballot
        for b in E.ballots:
            b.topCand.vote += b.vote

        # Fill any remaining seats
        while E.seatsLeftToFill():
            ordered_candidates = C.hopeful(order='vote', reverse=True)
            #print "Cands=",len(ordered_candidates)
            if len(ordered_candidates) > 0:
                ordered_candidates[0].elect()
            else:
                break

        # Defeat remaining hopeful candidates for reporting purposes
        for c in C.hopeful():
            c.defeat(msg='Defeat remaining candidates')

# This is important to register this rule with Droop!
#droop.ruleClasses.append(SNTVRule)
#droop.ruleByName[SNTVRule.name] = SNTVRule

# vim: et ft=python:
