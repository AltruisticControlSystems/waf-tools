#! /usr/bin/env python
# Kenneth Wells, 2015

import glob
import os
import sys
import string
from xml.dom import minidom

from waflib.TaskGen import before, feature
from waflib import Utils

def safe_file_name(name):
    safe_chars = '_-()' + string.digits + string.ascii_letters
    safe_name = ""
    for x in name:
        if x in safe_chars:
            safe_name += x
        else:
            safe_name += '_'
    return safe_name

def process_moc_list(self,mocList):
    for header in mocList:
        header_node = self.to_nodes(header)
        moc_node = self.path.find_or_declare(
            header.replace('.','_') + '_%d_moc.cpp'%self.idx
            )

        self.create_task('moc',header_node,moc_node)
        self.source = Utils.to_list(getattr(self,'source',[]))
        self.source.append(moc_node)

        print self.source

def process_introspect(self,introspectList):
    if len(introspectList) > 1:
        self.fatal("Please use one introspect per package")

    if len(introspectList) < 1:
        pass
    else:
        self.env.INTROSPECT_FILE = self.path.find_resource(introspectList[0])
        doc = minidom.parse(self.env.INTROSPECT_FILE.abspath())

        for interface in doc.getElementsByTagName('interface'):
            interfaceName = str(interface.getAttribute('name'))

            self.env.INTERFACE_NAME = safe_file_name(interfaceName)

def process_business_logic(self,businessLogicList):
    if len(businessLogicList) > 1:
        self.fatal("Please only list one business logic class per package")

    if len(businessLogicList) < 1:
        pass
    else:
        for businessLogic in businessLogicList:
            self.env.BUSINESS_LOGIC = businessLogic

@feature('package')
@before('process_source')
def package_reader(self):
    if not getattr(self,'manifest', None):
        pass
    else:
        self.source = []
        self.include = []
        self.moc_list = []
        self.env.DBUS_INCLUDES = []
        packageFile = self.path.find_resource(self.manifest)

        doc = minidom.parse(packageFile.abspath())

        for manifest in doc.getElementsByTagName("manifest"):
            self.include += [str(include.getAttribute("path")) for include in manifest.getElementsByTagName("include")]
            self.source += [str(source.getAttribute("path")) for source in manifest.getElementsByTagName("source")]
            self.env.DBUS_INCLUDES += [str(source.getAttribute("path")) for source in manifest.getElementsByTagName("dbusInclude")]

            process_moc_list(
                self,
                [str(moc.getAttribute("path")) for moc in manifest.getElementsByTagName("moc")]
                )
            process_introspect(
                self,
                [str(introspect.getAttribute("path")) for introspect in manifest.getElementsByTagName("introspect")]
                )
            process_introspect(
                self,
                [str(bL.getAttribute("class")) for bL in manifest.getElementsByTagName("businessLogic")]
                )

        self.source = self.to_nodes(self.source)

        print self.source
