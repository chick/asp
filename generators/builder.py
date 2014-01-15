__author__ = 'chick'

import os
import inspect
import shutil

import sys
from mako.template import Template

class Builder:
    def __init__(self,template_family,target_base,**kwargs):
        self.target_base = target_base
        self.template_family = template_family

    def build(self,template_dir,target_dir,depth=0):
        """
        walks the template_dir
        each directory founds is created in associated target_dir
        each *.mako file is processed as a template and created without .mako
        other files are copied as is
        """

        def iprint( s ):
            print ( ' ' * depth ) + s

        if template_dir == None:
            a = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            b = 'templates'
            c = self.template_family

            template_dir = os.path.join(a,b,c) #
            #    os.path.abspath(inspect.getfile(inspect.currentframe())),
            #    'templates',
            #    self.command_name,
            #)
            target_dir = self.target_base

        iprint( "template dir is %s" % template_dir )
        iprint( "target dir is %s" % target_dir )

        try:
            os.makedirs(target_dir)
        except OSError as exception:
            print "Unable to create %s error (%d) %s" % \
                (template_dir,exception.errno,exception.strerror)
            exit(1)

        files = os.listdir( template_dir )
        iprint( "files " + ",".join(files) )
        for file in files:
            source_file = os.path.join( template_dir, file )
            target_file = os.path.join( target_dir, file )

            if os.path.isfile( source_file ):
                if source_file.endswith(".mako"):
                    template = Template(filename=source_file)
                    file_name = target_file[:-5]

                    f1=open(file_name,'w+')
                    iprint( "Rendering %s" % file_name )
                    iprint( template.render(specializer_name=self.target_base) )
                    print >>f1, template.render(specializer_name=self.target_base)
                    f1.close()
                else:
                    iprint( "processing ordinary file %s" % source_file )
                    shutil.copyfile( source_file, target_file )
            elif os.path.isdir(source_file):
                iprint( "processing directory %s" % file )
                self.build(source_file,target_file,depth+1)




