#! /usr/bin/env python
# Kenneth Wells, 2015

import glob
import os
import sys
from xml.dom import minidom

from waflib.TaskGen import before, feature
from waflib import Utils

@feature('package')
@before('process_source')
def package_reader(self):
    if not getattr(self,'manifest', None):
        pass
    else:
        self.source = []
        packageFile = self.path.find_resource(self.manifest)

        doc = minidom.parse(packageFile.abspath())

        for manifest in doc.getElementsByTagName("manifest"):
            self.source += [source.getAttribute("path").encode('ascii', 'ignore') for source in manifest.getElementsByTagName("source")]
            self.source += [include.getAttribute("path").encode('ascii', 'ignore') for include in manifest.getElementsByTagName("include")]
            self.source += [moc.getAttribute("path").encode('ascii', 'ignore') for moc in manifest.getElementsByTagName("moc")]

        self.source = self.to_nodes(self.source)

        print self.source
