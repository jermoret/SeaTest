#!/usr/bin/python

import sys, getopt
from dateutil import parser
from datetime import timedelta
import git
import csv

def getModifiedLines(commit_hash, previous_commit_hash, filename, g):
    diff = g.diff('--unified=0', previous_commit_hash, commit_hash, filename)
    modifiedLines = []
    for line in diff.encode('utf8').split('\n'):
        if line.startswith("@@"): # Only interested by header diff lines
            minus = line.find("-")
            comma = line.find(",")
            if (comma != -1): # Multiple or zero line(s) to add
                noLine = int(line[minus + 1: comma])
                nbLine = int(line[comma + 1: comma + 2])
                while nbLine != 0:
                    modifiedLines.append(noLine)
                    nbLine = nbLine - 1
                    noLine = noLine + 1
            else: # Juste one line
                modifiedLines.append(int(line[minus + 1: line.find("+") - 1]))
    return modifiedLines

def computeChunks(commit_hash, previous_commit_hash, filename, author_name, date, daysDelta, g):
    if previous_commit_hash == "":
        return 0
    chunkLines = 0
    modifiedLines = getModifiedLines(commit_hash, previous_commit_hash, filename, g)
    for line in modifiedLines:
        blame = g.blame('-L' + str(line) + ',+1', previous_commit_hash, '--', filename).encode('utf8')
        author_pos = blame.find(author_name)
        if author_pos != -1: # Same author
            date_pos = author_pos + len(author_name) + 1
            modif_dt = parser.parse(blame[date_pos : date_pos + len(date)])
            dt = parser.parse(date)
            delta = dt - modif_dt
            if delta < timedelta(days=daysDelta):
                chunkLines += 1
    return chunkLines

def main(argv):
   inputfile = ''
   outputfile = 'dataset.csv'
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'usage : -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'usage : -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

   g = git.Git(inputfile)
   loginfo = g.log('--pretty=format:%h%x09%s%x09%ae%x09%an%x09%ai', '--numstat', '--reverse')

   ofile = open(outputfile, "wb")
   writer = csv.writer(ofile, quoting=csv.QUOTE_NONNUMERIC)
   writer.writerow(('commit_hash', 'commit_name', 'author_name', 'author_email', 'commit_date', 'filename', 'additions',
                    'deletions', 'chunk'))
   headerLine = True
   previous_commit_hash = ""
   for line in loginfo.split('\n'):
       chunks = line.encode('utf8').split('\t')
       if headerLine:  # Header commit line
           commit_hash = chunks[0]
           commit_name = chunks[1]
           author_email = chunks[2]
           author_name = chunks[3]
           commit_date = chunks[4]
           headerLine = False
       elif len(chunks) != 1:  # File line
           additions = int(chunks[0])
           deletions = int(chunks[1])
           filename = chunks[2]
           chunks = 0
           if deletions != 0:
               chunks = computeChunks(commit_hash, previous_commit_hash, filename, author_name, commit_date, 21, g)
           writer.writerow(
               (commit_hash, commit_name, author_name, author_email, commit_date, filename, additions, deletions,
                chunks))
       else:  # Empty line (separation between commits)
           previous_commit_hash = commit_hash
           headerLine = True

   ofile.close()


if __name__ == "__main__":
   main(sys.argv[1:])
