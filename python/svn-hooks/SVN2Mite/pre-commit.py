#!/usr/bin/python
import sys
import subprocess
import re

def hookSVN2Mite(repository, txn, author, message):
    from SVN2Mite import SVN2Mite
    mite = SVN2Mite('APIKEY', 'https://URL.mite.yo.lk')
    mite.hook(repository, author, "Subversion commit with ID %s from %s in Repository %s and Message: %s" % (txn, author, repository, message) )
    return 0

def hookCommitWithTracker(message):
    regex = re.compile('(?<=#)[0-9]{1,}')
    match = regex.search(message)
    if not match:
        sys.stderr.write("No Tracker ID has been provided.")
        return 1
    return 0

def main(args):
    errors = 0
    svnlookbin = "/usr/bin/svnlook"
    repoPath = args[0]
    txn = args[1]
        
    repoName = str(repoPath).split('/')[-1]
    message = svnLook('%s log -t "%s" "%s"' % (svnlookbin, txn, repoPath))
    author = svnLook('%s author -t "%s" "%s"' % (svnlookbin, txn, repoPath))

    errors += hookCommitWithTracker(message)
    errors += hookSVN2Mite(repoName, txn, author, message)
    return errors

def svnLook(log_cmd):
    p = subprocess.Popen(log_cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    p.stderr.close()
    p.stdin.close()

    return str(p.stdout.read().rstrip('\n'))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))