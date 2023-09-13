# -*- coding: utf-8 -*-

def main():
    args = parseArgs()
    
    LUNAS_CRISPOR_tool(args.input_file_name, args.PAM, args.spacer_length, args.search_range, args.spacer_orientation, args.interspace_range)

def parseArgs():
    """ parse command line options into args """
    import argparse
    parser = argparse.ArgumentParser(usage="""LUNAS_CRISPOR_tool.py [options] inputFile

Command line add-on tool for selecting LUNAS guide pairs based on the list of candidate 
guides generated by the CRISPOR command line tool (Maximilian Haeussler, https://doi.org/10.1093/nar/gky354).
Output comma separated file (.csv) is saved in same directory as inputFile, named <input_file_name>_LUNAS_pairs.csv

    inputFile = tab-sep file (.tsv) generated by crispor.py, one row per guide

    Examples:
    LUNAS_CRISPOR_tool.py SARS-CoV-2_Orf1a_guides.tsv
    LUNAS_CRISPOR_tool.py SARS-CoV-2_Orf1a_guides.tsv --search_range 100 400
    """)

    parser.add_argument("input_file_name", \
        help="path to input .tsv file generated by CRISPOR.py commandline tool")
    parser.add_argument("--spacer_orientation", dest="spacer_orientation", default='><', choices=['><','<>','>>','<<'], \
        help="Orientation of spacers: '><' = PAMs proximal, '<>' = PAMs distal, '>>' = PAMs to the right, '<<' = PAMs to the left, default: '><'")
    parser.add_argument("--interspace_range", dest="interspace_range", nargs=2, default=[30, 50], type=int, \
        help="Range of distance between indices (PAM-proximal end positions) of candidate spacer pairs, usage: min max, default: (30, 50)")
    parser.add_argument("--PAM", default="NGG", dest="PAM", \
        help="PAM sequence used in CRISPOR.py for generating input.tsv file, default: 'NGG'")
    parser.add_argument("--spacer_length", type=int, default=int(20), dest="spacer_length", \
        help="Spacer length used in CRISPOR.py for generating input.tsv file, default: 20")
    parser.add_argument("--search_range", type=int, nargs=2, default=[], dest="search_range", \
        help="Search range, usage: min_index max_index, default: full range") 

    args = parser.parse_args()
    
    if args.spacer_orientation == '><': min_interspace = len(args.PAM)*2
    elif args.spacer_orientation == '>>' or args.spacer_orientation == '<<' : 
        min_interspace = len(args.PAM) + args.spacer_length
    elif args.spacer_orientation == '<>': min_interspace = 2*args.spacer_length

    if args.interspace_range[0] < min_interspace:
        raise ValueError('Spacers may overlap using current settings, increase the minimal interspace length!')

    return args

def LUNAS_CRISPOR_tool(input_file_name, PAM, spacer_length, search_range, spacer_orientation = '><', interspace_range = (30,50)):
    FOR, REV = data_read(input_file_name, PAM)
    Sort_Candidates_Pairs(input_file_name, FOR, REV, spacer_length, spacer_orientation, interspace_range, search_range, PAM)

def data_read(input_file_name, PAM):
    """Function that reads guide candidate info from CRISPOR-generated .tsv file."""
    lstFOR = []
    lstREV = []
    with open(input_file_name, 'r') as input_file:
        header_line = input_file.readline() #Skip the header line
        for line in input_file:
            a = line.strip()
            a = a.split('\t')
            MMScore = a[8]
            Doench16Score = a[7]
            if MMScore != 'NotEnoughFlankSeq':
                MMScore = float(MMScore)
            if Doench16Score != 'NotEnoughFlankSeq':
                Doench16Score = float(Doench16Score)
            
            if 'rev' in a[1]:
                i = int(a[1].strip('rev'))+len(PAM) #Adjust index to match PAM-proximal end of protospacer
                lstREV.append((a[2], int(i), float(a[3]), float(a[4]), Doench16Score, MMScore))
            if 'forw' in a[1]:
                i = int(a[1].strip('forw'))-1 #Adjust index to match PAM-proximal end of protospacer
                lstFOR.append((a[2], int(i), float(a[3]), float(a[4]), Doench16Score, MMScore))
    lstFOR.sort(key = lambda x: x[1]) # Sort the list based on the index i of a spacer sequence, purely for determining default max index at line 78
    lstREV.sort(key = lambda x: x[1])
    return (lstFOR, lstREV)


def Sort_Candidates_Pairs(input_file_name, FOR, REV, spacer_length, spacer_orientation, interspace_range, search_range, PAM):
    """Function that pairs guide candidates and filters candidate pairs based on orientation, interspace and position (index)"""
    # If the target sequence subsection search range is not set, set values to 0 and end of target sequence
    if search_range == []:
        min_index = 0
        max_index = max(FOR[-1][1] + 2, REV[-1][1] + spacer_length + 2 )
    else:
        min_index = search_range[0]
        max_index = search_range[1]

        
    # Check if candidate sequences are within the search range, else remove them
    for item in FOR[:]: #FOR[:] instead of simply FOR directly, as otherwise we remove from the same list we iterate on!
        if (not item[1] - spacer_length >= min_index) or (not item[1] + len(PAM) < max_index):
            FOR.remove(item)
    for item in REV[:]:
        if (not item[1] - len(PAM) >= min_index) or (not item[1] + spacer_length < max_index):
            REV.remove(item)
            
    if spacer_orientation == "<>":
        spacerL = REV
        spacerR = FOR
        const = -1
    elif spacer_orientation == "><":
        spacerL = FOR
        spacerR = REV
        const = 1
    elif spacer_orientation == ">>":
        spacerL = FOR
        spacerR = FOR
        const = 0
    elif spacer_orientation == "<<": 
        spacerL = REV
        spacerR = REV
        const = 0

    pair_list = []
    min_interspace_len = interspace_range[0]
    max_interspace_len = interspace_range[1]
    
    for leftSpacer in spacerL:
        for rightSpacer in spacerR:
            interspace_len = rightSpacer[1] - (leftSpacer[1] + const)
            # If the spacer length is in between the min and max value, add
            # the combination of rightSpacer and leftSpacer to the pair list
            if min_interspace_len <= interspace_len <= max_interspace_len:
                # Determine the average score
                pair_scoreMIT = (leftSpacer[2] + rightSpacer[2]) / 2 #mitSpecScore for the pair
                pair_scoreCFD =  (leftSpacer[3] + rightSpacer[3]) / 2 #CFDSpecScore for the pair
                if leftSpacer[4] == 'NotEnoughFlankSeq' or rightSpacer[4] == 'NotEnoughFlankSeq':
                    pair_scoreDoench16 = 'NotEnoughFlankSeq'
                else: pair_scoreDoench16 =  (leftSpacer[4] + rightSpacer[4]) / 2 #Doench '16 activity score for the pair
                if leftSpacer[5] == 'NotEnoughFlankSeq' or rightSpacer[5] == 'NotEnoughFlankSeq':
                    pair_scoreMM = 'NotEnoughFlankSeq'
                else: 
                    pair_scoreMM =  (leftSpacer[5] + rightSpacer[5]) / 2 # Moreno-Mateos activity score for the pair
                pair_scores = (interspace_len, pair_scoreMIT, pair_scoreCFD, pair_scoreDoench16, pair_scoreMM)
                pair_list.append((leftSpacer + rightSpacer + pair_scores))
                
    # Write the list of spacer pairs to a csv file.
    import csv
    OutFileName = str(input_file_name).replace(".tsv","_LUNAS_pairs.csv")
    header = ['Guide1_TargetSeq', 'Guide1_Index', 'Guide1_MIT-SpecScore', 'Guide1_CFD-SpecScore', 'Guide1_Doench16-Score', 'Guide1_Moreno-Mateos-Score', 'Guide2_TargetSeq', 'Guide2_Index', 'Guide2_MIT-SpecScore', 'Guide2_CFD-SpecScore', 'Guide2_Doench16-Score', 'Guide2_Moreno-Mateos-Score', 'Interspace_(nt)', 'Mean_MIT-SpecScore', 'Mean_CFD-SpecScore', 'Mean_Doench16-Score', 'Mean_Moreno-Mateos-Score' ]
    with open(OutFileName, 'w') as OutFile: # for Python 2 compatibility
        writer = csv.writer(OutFile)
        writer.writerow(header)
        writer.writerows(pair_list)
    
       
    
if __name__=="__main__":
    main()
