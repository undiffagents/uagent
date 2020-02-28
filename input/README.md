# Input

APE folder : https://github.com/Attempto/APE

Clex : https://github.com/Attempto/Clex

ACE_to_DRS_and_Rules.py reads the ACE_in.txt file and runs the APE software on it, then outputs the resulting DRS to DRS.txt (you'll need to run make install in the APE folder once to install it after adding Clex). After the DRS is saved to a file it runs Dapylog to do reasoning.

Must install SWI-prolog to run this.

# Dayplog

https://github.com/aaronEberhart/Dapylog

Integrated custom datalog reasoner for rules and facts extracted from instructions - can check for rule coverage **gaps**. Works but is repurposed from the link above. Will modify to suit this task at a later time.

## TODO: Improve README
