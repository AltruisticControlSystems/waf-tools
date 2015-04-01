#! /usr/bin/env python
# Kenneth Wells, 2015

from waflib.TaskGen import before, feature
from waflib import Task

class qdbus_adapter(Task.Task):
    def __init__(self,*k,**kw):
        Task.Task.__init__(self,*k,**kw)
        self.build_done = 0

    def runnable_status(self):
        if self.build_done:
            return Task.Task.runnable_status(self)
        else:
            for t in self.run_after:
                if not t.hasrun:
                    return Task.ASK_LATER
            self.build_adapter()
            return Task.Task.runnable_status(self)

    def build_adapter(self):
        cmd = [self.env.QDBUSXML2CPP[0]]
        for header in self.env.DBUS_INCLUDES:
            cmd += ['-i',header]
        cmd += ['-l',
            self.env.BUSINESS_LOGIC,
            '-a',
            '%s:%s' % (self.outputs[0].path_from(self.cwd),
                self.outputs[1].path_from(self.cwd)),
            self.inputs[0].path_from(self.cwd)]
        self.exec_command(cmd, cwd=self.cwd.abspath())

@feature('qdbus_adapter')
@before('process_source')
@before('apply_incpath')
def process_qdbus_adapter(self):
    outputs = []

    output_path = self.path.get_bld().make_node(['DBus'])

    h_file= '%s.h'%self.env.INTERFACE_NAME
    source_file = '%s.cpp'%self.env.INTERFACE_NAME

    h_node = output_path.find_or_declare(h_file)
    source_node = output_path.find_or_declare(source_file)

    moc_node = output_path.find_or_declare(
        h_file.replace('.','_') + '_%d_moc.cpp'%self.idx
        )

    self.create_task('moc',h_node,moc_node)

    outputs += [h_node,source_node]

    task = self.create_task(
        'qdbus_adapter',
        self.env.INTROSPECT_FILE,
        outputs
        )

    task.cwd = output_path

    self.includes = self.to_incnodes(getattr(self,'includes',[]))
    self.includes.append(h_node.parent)

    self.export_includes = self.to_incnodes(getattr(self,'export_includes',[]))
    self.export_includes.append(h_node.parent)

    self.source = self.to_list(getattr(self,'source',[]))
    self.source.append(source_node)
    self.source.append(moc_node)
