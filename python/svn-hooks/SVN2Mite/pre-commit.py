#!/usr/bin/python
import sys
import subprocess

def hookSVN2Mite(repository, author, message):
    import SVN2Mite
    mite = SVN2Mite('75e781252a82fe9', 'https://tspycher.mite.yo.lk')
    mite.hook(repository, author, message)
    return 0

def main(args):
    errors = 0
    svnlookbin = "/usr/bin/svnlook"
    repoPath = args[0]
    txn = args[1]
        
    repoName = str(repoPath).split('/')[-1]
    message = svnLook(log_cmd = '%s log -t "%s" "%s"' % (svnlookbin, txn, repoPath)) #`$SVNLOOK log -t "$TXN" "$REPOS"`
    author = svnLook(log_cmd = '%s author -t "%s" "%s"' % (svnlookbin, txn, repoPath)) #`$SVNLOOK author -t "$TXN" "$REPOS"`
    
    sys.stderr.write("Reponame: %s" % repoName)
    sys.stderr.write("Message: %s" % message)
    sys.stderr.write("Author: %s" % author)

    errors += hookSVN2Mite(repoName, message,author)
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