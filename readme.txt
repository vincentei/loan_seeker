

+### GENEREAL INTRODUCTION
People participate in various crowsfunding projects. So they extend loans to small companies (i.e. they invest).
They do this on platforms like: 
www.fundingcircle.com
www.collincrowdfund.nl/
ww.kapitaalopmaat.nl/

For now assume the investor is active on one platform (i.e. fundingcircle)

In return of the investment the investor will get a monthly payment from the small company (mostly annuity payment).
The investor will bear the risk that the loan will default (he loses his investment). 
In return for this risk he gets a return on his capital invested.
The payment is also referred as the cashflow (cf) below.
The investor can make different loans on each platform.

Everything I say here is from the perspective of the investor (i.e. the person who gives the loan to the crowfunding project)

Website of J aggregates the loans(investments) people have on different platforms.

There is new legislation. This is PSD2. 
PSD2 allows APP builders to access your back account statement (with your consent of course)
See also:
https://transferwise.com/gb/blog/what-is-psd2

Website J will access bank account statement of investors. He will retrieve: 
1. info about the investments they have made on the different crowfunding platforms
2. He will also retrieve the monthly cashflow the investor receives from the platform. Note that per platform the monthly cashflow is aggregated.  

With this info our model will the have to figure out:
1. which loan is in default yes/no
2. What interest has each loan (i.e. 5% or 10%)
3. What is the maturity of each loan.


########## MORE INTRODUCTION

Goal of code is to figure out which set of loans (lots of columns) best fit the observed cashflow (1 column).

loans are divded into subloans. example:
1_1 is subloan 1 of loan 1
1_2 is subloan 2 of loan 1

The subloans are made because we do not know exactly what kind of loans there are.  

We only know the number of loans and the total investment of the loan. 
AND we know the TOTAL monthly cashflow the investor receives on his bank account each month.

So we have to guess:

the interest payment i.e. the monthly cashflow
the lenght of the loans i.e. 2 years, 3 years.
Whether the loan is in default yes/no
(and some other stuff that will come later)

We have some idea what the interest payment could be (mostly between 5% and 15%).
Also the length of the loan is mostly 6,12,24,36 months.
Knowing this. For each loan we could formulate a set of subloans (or candidate loans).

The real loan is then one of the subloans.

The task of the solver is then to figure out which set of subloans best matches the observed cashflow

#### DESCRIPTION OF INPUT FILES

loan_data_wide.csv
This contains the expected cashlows for each subloans for every time step t in the past. 
headers: step; 0_0; 0_1; 0_2...

act_cf.csv
This contains the actual cashflow observed on the bank account of the investor. 



