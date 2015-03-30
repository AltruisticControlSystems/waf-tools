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
        files = []
        for output in self.outputs:
            files += [self.cwd.find_or_declare(output)]
        cmd = [self.env.QDBUSXML2CPP]
        for header in self.env.DBUS_INCLUDES:
            cmd += ['-i',header]
        cmd = ['-l',
            self.env.BUSINESS_LOGIC,
            '-a',
            '%s:%s' % (files[0].path_from(self.cwd),files[1].path_from(self.cwd)),
            self.inputs[0].path_from(self.cwd),
            self.env.INTERFACE_NAME]
        self.exec_command(cmd, cwd=self.cwd.abspath())

@feature('qdbus_adapter')
@before('process_source')
@before('apply_incpath')
def process_qdbus_adapter(self):
    outputs = []

    base_output_path = self.path.get_bld().make_node(['%d'%self.idx])
    output_path = base_output_path.make_node(self.env.INTERFACE_NAME)

    h_file= '%s.h'%self.env.INTERFACE_NAME
    source_file = '%s.cpp'%self.env.INTERFACE_NAME

    h_node = output_path.find_or_declare(h_file)
    source_node = output_path.find_or_declare(source_file)

    outputs += [h_node,source_node]

    self.create_task(
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

def configure(conf):
    conf.find_program('qdbusxml2cpp',var='QDBUSXML2CPP')

