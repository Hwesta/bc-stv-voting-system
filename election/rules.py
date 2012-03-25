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
