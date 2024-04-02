# CRISPOR for LUNAS gRNA search on WSL Ubuntu

First install Ubuntu through WSL on your Windows computer and setup miniconda:
1. Press Windows key + R, enter cmd and press cntrl + shift + enter to start command prompt in administrator mode.
2. Enter `wsl --install` to install WSL on your system and automatically install Ubuntu as default distribution. If WSL is already installed, you can use `wsl --install -d ubuntu`  instead to install Ubuntu. 

You have to provide a username and password. After successful installation you can start Ubuntu from the Windows search tool or by simply entering `wsl` in cmd. 

Your Ubuntu filesystem can now be accessed from within your Windows file explorer by going to `\\wsl.localhost\Ubuntu`

3. Download latest version of miniconda by entering below command:
`wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`

4. Install it:
`bash Miniconda3-latest-Linux-x86_64.sh`

5. Remove installation file:
`rm Miniconda3-latest-Linux-x86_64.sh`

6. Create a new conda environment for the CRISPOR tool and install python 3.9:
`conda create --name CRISPOR python==3.9`

7. To activate the environment you just made, enter:
`conda activate CRISPOR`  
You should now see `(base)` at the start of your command line turn into `(CRISPOR)`. To use the tools we are installing, you should always work from this environment.

## Setup CRISPOR and LUNAS_CRISPOR_tool
In general, check https://github.com/maximilianh/crisporWebsite/blob/master/INSTALL.md for most recent instructions for local installation of the CRISPOR tool and related information on usage. Below is what I did to install it on 12/09/2023 in WSL.

1. Go to https://github.com/maximilianh/crisporWebsite and download the ZIP file with all CRISPOR code (Last version I successfully used was from 28/08/2023, github commit fd9929f4a843b4998ebaf0e808a67e8e94b5421f). Unzip in a new directory ‘CRISPOR’ in your Ubuntu home directory, so you get a path like this: \home\<USER>\CRISPOR\crisporWebsite-master.

2. Install BWA and other required basic python modules:  
`sudo add-apt-repository ppa:deadsnakes/ppa`  
`sudo apt-get install bwa python-pip python-matplotlib`

3. Install required python packages:
`pip install biopython numpy scikit-learn==1.1.1 pandas twobitreader xlwt h5py rs3 pytabix matplotlib lmdbm`

4. Fix some package version issues that can give errors (also why scikit-learn version 1.1.1 needs to be installed specifically in previous step):  
Downgrade lightgbm to version 3.3.3:
`pip install lightgbm==3.3.3`

5. Move to the directory where the crispor.py script is, i.e.:
`cd ~/CRISPOR/crisporWebsite-master`
6. If you now run the crispor.py script by entering python crispor.py, it should show the usage message: 
>Usage: crispor.py [options] org fastaInFile guideOutFile   
>
>Command line interface for the Crispor tool.  
>
>    org          = genome identifier, like hg19 or ensHumSap  
>    fastaInFile  = Fasta file  
>    guideOutFile = tab-sep file, one row per guide  
>
>    Use "noGenome" if you only want efficiency scoring (a LOT faster). This option   
>    will use BWA only to match the sequence to the genome, extend it and obtain  
>    efficiency scores.  
>
>    If many guides have to be scored in batch: Add GGG to them to make them valid  
>    guides, separate these sequences by at least one "N" character and supply as a single  
>    fasta sequence, a few dozen to ~100 per file.  
>    
>
>Options:  
>  -h, --help            show this help message and exit  
>  -d, --debug           show debug messages, do not delete temp directory  
>  -t, --test            run internal tests  
>  -p PAM, --pam=PAM     PAM-motif to use, default NGG. TTTN triggers special  
>                        Cpf1 behavior: no scores anymore + the PAM is assumed  
>                        to be 5' of the guide. Common PAMs are:  
>                        NGG,TTTN,NGA,NGCG,NNAGAA,NGGNG,NNGRRT,NNNNGMTT,NNNNACA  
>  -o OFFTARGETFNAME, --offtargets=OFFTARGETFNAME  
>                        write offtarget info to this filename  
>  -m MAXOCC, --maxOcc=MAXOCC  
>                        MAXOCC parameter, guides with more matches are  
>                        excluded  
>  --mm=MISMATCHES       maximum number of mismatches, default 4  
>  --bowtie              new: use bowtie as the aligner. Do not use. Bowtie  
>                        misses many off-targets.  
>  --skipAlign           do not align the input sequence. The on-target will be  
>                        a random match with 0 mismatches.  
>  --noEffScores         do not calculate the efficiency scores  
>  --minAltPamScore=MINALTPAMSCORE  
>                        minimum MIT off-target score for alternative PAMs, default  
>                        1.0  
>  --worker              Run as worker process: watches job queue and runs jobs  
>  --clear               clear the worker job table and exit  
>  -g GENOMEDIR, --genomeDir=GENOMEDIR  
>                        directory with genomes, default ./genomes  

7.	Now to use the tool for finding gRNAs for targeting within a certain sequence, we need to first load the corresponding genome in CRISPOR. For this, you can use the tool crisporAddGenome in the tools subdirectory. To get this tool to work, first create a genomes directory:
`mkdir ~/CRISPOR/crisporWebsite-master/genomes`

8. Install the tool gffread by installing cufflinks:
`apt-get install cufflinks`

9. Create a personal bin directory:
`mkdir ~/bin`

10. The other tools we need are located in the subdirectory `/tools/usrLocalBin`, move them to the newly created `/home/<username>/bin` folder:
`cp -a ~/CRISPOR/crisporWebsite-master/tools/usrLocalBin/. ~/bin`

Alternatively, you can move them to the /usr/local/bin directory. This can result in permission errors. If you get a ‘permission denied’ error, make your Ubuntu user account the owner of the `/usr/local/bin` directory by applying:
`chown -R <username> /usr/local/bin`

The tools may still need to be made executable binaries (you can check permissions by `ls -l ~/bin`) by applying:
`chmod -R 755 ~/bin/.`

Also, to be able to add future genomes and output files to the `~/CRISPOR` directory, we need to make this directory editable:
`chmod -R 755 ~/CRISPOR`

11. For Ubuntu 18.04 and up, we need to install libpng12 using an alternative PPA: 
`sudo add-apt-repository ppa:linuxuprising/libpng12`
`sudo apt update`
`sudo apt install libpng12-0`

12. Now we need to make a small modification to the crisporAddGenome script to avoid an error (already done in the version that is bundled with this manual), open the file in a text editor and change the penultimate line (1196) as follows:
`cmd = "cd ~/CRISPOR/crisporWebsite-master/genomes && ~/CRISPOR/crisporWebsite-master/makeGenomeInfo"`
`#cmd = "cd /data/www/crispor && ./makeGenomeInfo"`

Additionally, change the default genomes directory location in line 31 of the code:
`crisprGenomeDir = os.path.expanduser('~/CRISPOR/crisporWebsite-master/genomes')`
`#crisprGenomeDir = "/data/www/crispor"`

13. Now, to add a genome, you can either use a fasta file (this also allows you to use a custom genome fasta) or let the tool auto-download the genome from Ensembl, UCSC or NCBI. Take a look at the help info for how to use the tool:
`cd ~/CRISPOR/crisporWebsite-master/tools`
`python crisporAddGenome –help`

For example, to add the SARS-CoV-2 genome for which you placed the fasta in folder `/home/<username>/CRISPOR`: 
`python crisporAddGenome fasta ~/CRISPOR/SARS-CoV-2.fasta --desc 'SARSCoV2|Severe Acute Respiratory Coronavirus 2|SARS-CoV-2|NC_045512.2, isolate Wuhan-Hu-1'`

The four |-split values for the `--desc` option are: internalDatabaseName, scientificName, commonOrDisplayName, VersionNameOfAssembly

Make sure that internalDatabaseName does not include special characters, spaces etc. as it is used as a directory name. 

14. Now that we have a genome available in CRISPOR, we can do a test run. Again, move to the directory where the crispor.py script is, i.e.:
`cd ~/CRISPOR/crisporWebsite-master`

15. Perform a run where we are looking for gRNAs in the full SARS-CoV-2 genome (i.e. we provide the SARS-CoV-2 fasta file as input, and use the SARS-CoV-2 genome we previously loaded into CRISPOR for specificity checking):
`python crispor.py SARSCoV2 ~/CRISPOR/SARS-CoV-2.fasta ~/CRISPOR/scoreGuides.tsv`

16. If the run was successful, the tab-separated scoreGuides.tsv file should be located in your `/home/<username>/CRISPOR` folder. 
17.	Now, to easily find all potential LUNAS gRNA pairs from this list, you can use the LUNAS_CRISPOR_tool.py script (see https://github.com/harmveer/LUNAS_CRISPOR_tool or the version that comes bundled with this manual). Place this script in the /home/<username>/CRISPOR folder. Checkout the help description to find out how the tool is used:
`cd ~/CRISPOR`
`python LUNAS_CRISPOR_tool.py –help`


For example, to process the scoreGuides.tsv file that the CRISPOR tool generated in step 14 with default settings, perform:
python LUNAS_CRISPOR_tool.py scoreGuides.tsv

You should get a comma-separated file scoreGuides_LUNAS_pairs.csv in the same working directory that contains all suitable LUNAS gRNA pairs including their guide scores and other details. To analyse this csv file, import it in MS Excel. This also allows you to filter/sort based on e.g. interspace length of the guide pair.
