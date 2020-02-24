# OntoGapDetection

APE folder : https://github.com/Attempto/APE

Clex : https://github.com/Attempto/Clex

ACE_to_DRS_and_Rules.py reads the ACE_in.txt file and runs the APE software on it, then outputs the resulting DRS to DRS.txt (you'll need to run make install in the APE folder once to install it after adding Clex). After the DRS is saved to a file it runs Dapylog to do reasoning and allow modification of instruction rules/facts if needed.

# Dayplog

https://github.com/aaronEberhart/Dapylog

Integrated custom datalog reasoner for rules and facts extracted from instructions - can check for rule coverage **gaps**. Works but is repurposed from the link above. Will modify to suit this task at a later time.

# Fuseki 

https://jena.apache.org/documentation/fuseki2/

Will initialize this process after parsing the input file so that data can be loaded into it. Then Fuseki will allow queries and interaction with the ontology it has read. Currently it is not hooked up but the configuration is in progress

## TODO: Improve README
