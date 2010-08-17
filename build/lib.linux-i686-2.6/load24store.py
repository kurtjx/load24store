#!/usr/bin/env python
# encoding: utf-8
'''
Created on Aug 17, 2010

@author: kurtjx
'''

import sys,os
import shutil
import getopt
from HTTP4Store import HTTP4Store


help_message = '''
Usage: load24store [OPTIONS...] ENDPOINT GRAPH PATH_TO_RDF
  -k, --kill-all        empty graph before writing to 4Store
  -s, --silent          print no information
'''

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg



class Loader():
    def __init__(self, endpoint, graph, path, kill=False, verbose=False):
        self.store = self.connect(endpoint)
        self.graph = graph
        self.path = path
        self.verbose = verbose
        if kill:
            self.kill()
    
    def connect(self,endpoint):
        if endpoint.endswith('sparql'):
            endpoint = endpoint.split('sparql')[0]
        return HTTP4Store(endpoint)
    
    def kill(self):
        if raw_input('really kill contents of %s? (y/n)' % self.graph)=='y':
            self.store.del_graph(self.graph)

    def load_files(self):
        donepath = os.path.join(self.path, 'done_rdf')
        if not os.path.exists(donepath):
            os.mkdir(donepath)
            
        if self.verbose:
            print "loading files"
        for idx, f in enumerate(os.listdir(self.path)):
            if f.endswith('.ntriples') or f.endswith('.nt') or f.endswith('.rdf') or f.endswith('.ttl') or f.endswith('.n3'):
                if self.verbose:
                    print "loading %s" % f
                rdf = open(os.path.join(self.path,f),'r').read()
                self.store.append_graph(self.graph, rdf)
                shutil.move(os.path.join(self.path,f), os.path.join(donepath,f))
        if self.verbose:
            print "loaded %i files" %idx+1
            print "loaded files moved to %s" % donepath

            

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hks", ["help", "kill-all", "silent"])
        except getopt.error, msg:
            raise Usage(msg)

        kill = False
        verbose = True
        # option processing
        for option, value in opts: #@UnusedVariable
            if option == "-s":
                verbose = False
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-k", "--kill-all"):
                kill = True
        try:
            endpoint = args[0]
        except IndexError:
            raise Usage('must provide 4store endpoint as first argument - '+help_message)
        try:
            graph = args[1]
        except IndexError:
            raise Usage('must provide named graph as 2nd argument - '+help_message)
        try:
            path = args[2]
        except IndexError:
            raise Usage('must provide path to RDF directory as 3rd argument - '+help_message)
        else:
            Loader(endpoint,graph, path, kill, verbose)

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())