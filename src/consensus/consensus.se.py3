import expiringEvents as EXPIRING
import reporting as REPORTING
import fxpFunctions as FXP
import events as EVENTS
import makeReports as REPORTS

data proportionCorrect[]
# normalize lazily if you don't do it next send you get docked

#Use consistent 1 and 2 fixed point numbers as min and max for close market, make market, make event, buy/sell shares, and consensus on binary events - really, just use base 64 fixed point everywhere

#if .5 due to catch param push back once (as .5 outcome), if same on next consensus no more push backs, that’s the final outcome

#if event gets pushed back due to 65% thing make so people can still buy / sell

def penalizeWrong(event):
	if(notDoneForEvent)
	p = self.getProportionCorrect(event)
	outcome = EVENTS.getOutcome(event)
	for all reporters:
		# wrong
		if(reportValue > outcome+.01 or reportValue < outcome-.01):
			if(scalar or categorical):
				p = -(abs(reportValue - EVENTS.getMedian(event))) + 1.5
			newRep = oldRep*(2*p -1)
		# right
		else:
			if(scalar or categorical):
				p = -(abs(reportValue - EVENTS.getMedian(event))) + 1.5
			newRep = 1 + oldRep*(2*(1-p)**2 / p)
		smoothedRep = oldRep*.8 + newRep*.2
	normalize(smoothedRep)
	# must add up to repreported on event or less
	for all reporters:
		updateRepValues();

macro abs($a):
	if($a<0):
		$a = -$a
	$a

def proportionCorrect(event):
	# p is proportion of correct responses
	p = 0
	# real answer is outcome
	outcome = EVENTS.getOutcome(event)
	if(outcome!=0):
		# binary
		if(EVENTS.getNumOutcomes(event)==2 and 2**64*EVENTS.getMaxValue(event)==2**65):
			avgOutcome = EVENTS.getUncaughtOutcome(event)
			# say we have outcome of 0, avg is .4, what is p?
			# p is .6 or 60%
			if(outcome == 2**64):
				p = 1 - avgOutcome
			# say we have outcome of 1, avg is .8, what is p (proportion correct)?
				# p is .8 or 80%
			if(outcome == 2 * 2**64):
				p = avgOutcome
			# say we have outcome of .5, avg is .55, what is p?
			if(outcome == 3 * 2**63):
	return(p)

def getProportionCorrect(event):
	return(self.proportionCorrect[event])

# rep claiming similar to fee claiming
# person didn't report enough
def collectPenaltyRep(branch, votePeriod):
	# if reported not enough for this period, don't allow collection
	numEvents = REPORTS.getNumEventsToReportOn(branch, votePeriod)
	if(numEvents < 30*2**64):
        numEvents = 30*2**64
    if(numEvents/(2*2**64) > REPORTS.getNumReportsActual(branch, votePeriod)):
    	return(-1)
    if(hasntDoneRRForLazyEventsAndWrongAnsForPast+CurrentPeriods):
        doIt()
        self.RRDone = true
    lastPeriod = BRANCHES.getVotePeriod(branch)-1
    repReported = EXPEVENTS.getTotalRepReported(branch, lastPeriod)
    if(penaltyNotAlreadyCollected && periodOver && hasReported)
    	rep = fixed_multiply(REPORTING.getInitialRep(branch, lastPeriod), REPORTING.getReputation(msg.sender)*2**64/repReported)
    	REPORTING.addRep(branch, REPORTING.repIDToIndex(branch, tx.origin), rep)
		REPORTING.subtractRep(branch, REPORTING.repIDToIndex(branch, branch), rep)
	return(1)

#Q: Can we do lazy eval claiming of trading fees?
#A: Yes:
#      if(addrWasInThisConsensusPeriod):
#          send them cash of amount equal to fees from that period * rep owned by addr in that period / total #rep in that period
# payout function (lazily evaluate it)
def collectFees(branch):
	# if reported not enough for this period, don't allow collection
	numEvents = REPORTS.getNumEventsToReportOn(branch, votePeriod)
	if(numEvents < 30*2**64):
        numEvents = 30*2**64
    if(numEvents/(2*2**64) > REPORTS.getNumReportsActual(branch, votePeriod)):
    	return(-1)
	# - need to loop through rep holders and distribute 50% of branch fees to
	# except instead, do it on a per report basis
    # reporters' cashcoin addresses
    if(hasntDoneRRForLazyEventsAndWrongAnsForPast+CurrentPeriods):
        doIt()
        self.RRDone = true
    lastPeriod = BRANCHES.getVotePeriod(branch)-1
    repReported = EXPEVENTS.getTotalRepReported(branch, lastPeriod)
    if(feesNotAlreadyCollected && periodOver && hasReported)
		cash = fixed_multiply(BRANCHES.getInitialBalance(branch, lastPeriod), REPORTING.getReputation(msg.sender)*2^64/repReported)
		CASH.addCash(msg.sender, cash)
		CASH.subtractCash(branch, cash)
	return(1)

#essentially anyone can pay a bond to have an event put up for reporting on again, but this time by all reporters.  If the second round returns the same result, the bond is lost.  If the previous decision is overruled, then whoever posted the bond would get double the bond back.  To not have to deal with conversion issues, it’s simplest to keep the bond as a rep bond.  The rep to reward the bonded challenger would come from the people who reported wrong in level 1.  
# The easiest way to set the bond would be to make a flat cost, say.. 100 rep.  There can’t be an extremely low minimum (i.e. 5 cents) because then you could spam the system by paying to put a bunch of events up for re-adjudication cheaply and repeatedly.  100 is large enough not to get spammed, and small enough that people could create a dominant assurance contract to put something up for re-adjudication if no one with >100 rep is willing to step up.  
#We can’t simply pay out 2x though, since there theoretically may not be that much rep which reported on an event, so the easiest way to code things is probably to a) return the bond and b) reward the bonded challenger with whatever rep would normally be taken from the liars up to 2x the bond, then beyond that the people who originally reported whatever the actual truth was would get the rest.  
def roundTwoBond():

#Essentially, we could allow anyone to pay some amount significantly greater than the bond amount to force a branching event, splitting rep into two classes.*  In one class the reported outcome for whatever event was the cause of dispute is said to be right, and rep would be redistributed accordingly.  In the other class/branch, the other outcome would be considered right and rep would be redistributed accordingly.  Whichever outcome was truly the correct one would determine which branch had rep that actually held value.  This would be akin to a Bitcoin hard fork scenario.  The winning fork, of course, would be the one with the most voluminous markets.  Market makers should then be able to move their market to whichever fork they want, if they fail to act, it'd go to the most voluminous fork by default after a couple weeks.

#We should probably still have an option to pay to resolve in case something somehow goes wrong here.  This also doesn't work for scalar markets (although it does for categorical).  
# "On the fork where the chosen answer is equal to the original voted answer, the alarm raiser loses their rep bond. On the other form, the alarm raiser gets back a reward of 2x the deposit, paid out from incorrect voters’ deposits. Additionally, the rewards for all other answerers are made more extreme: “correct” answerers get 5*P and “incorrect” answerers lose 10*P."
def fork():


#  only resolve ones that had odds <99% for one of the outcomes. 
# We should probably still have an option to pay to resolve in case something somehow goes wrong here.  This also doesn't work for scalar markets (although it does for categorical).  




# 3b) if .5 due to catch param push back once (as .5 outcome), if same on next consensus no more push backs, # that's the outcome (or we could audit here or do certainty based audits) - not done yet
#    3c) detect b via a "times voted on" var - not done yet





def incrementPeriodAfterReporting():
	# do this after reporting is finished
	if(reportingPeriodOver/finished):
		BRANCHES.incrementPeriod(branch)
		return(1)
	else:
		return(0)

# Proportional distance from zero (fixed-point input)
macro normalize($a):
    with $len = len($a):
        with $total = 0:
            with $i = 0:
                while $i < $len:
                    $total += $a[$i]
                    $i += 1
                with $wt = array($len):
                    with $i = 0:
                        while $i < $len:
                            $wt[$i] = $a[$i] * 2^64 / $total
                            $i += 1
                        $wt

# Sum elements of array
macro sum($a):
    with $len = len($a):
        with $total = 0:
            with $i = 0:
                while $i < $len:
                    $total += $a[$i]
                    $i += 1
                $total