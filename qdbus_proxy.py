#! /usr/bin/env python
# Kenneth Wells, 2015

from waflib.TaskGen import before, feature
from waflib import Task

class qdbus_proxy(Task.Task):
    def __init__(self,*k,**kw):
        Task.Task.__init__(self,*k,**kw)
        self.build_done = False

    def runnable_status(self):
        if self.build_done:
            return Task.Task.runnable_status(self)
        else:
            for t in self.run_after:
                if not t.hasrun:
                    return Task.ASK_LATER
            self.build_proxy()
            return Task.Task.runnable_status(self)

    def build_proxy(self):
        cmd = [self.env.QDBUSXML2CPP[0]]
        for header in self.env.DBUS_INCLUDES:
            cmd += ['-i',header]
        cmd += ['-p',
            '%s:%s' % (self.outputs[0].path_from(self.cwd),
                self.outputs[1].path_from(self.cwd)),
            self.inputs[0].path_from(self.cwd)]
        self.exec_command(cmd, cwd=self.cwd.abspath())

        self.build_done = True

@feature('qdbus_proxy')
@before('process_source')
def process_qdbus_proxy(self):
    outputs = []

    output_path = self.path.get_bld().make_node(['DBus'])

    h_file= '%s_proxy.h'%self.env.INTERFACE_NAME
    source_file = '%s_proxy.cpp'%self.env.INTERFACE_NAME

    h_node = output_path.find_or_declare(h_file)
    source_node = output_path.find_or_declare(source_file)

    moc_node = output_path.find_or_declare(
        h_file.replace('.','_') + '_%d_moc.cpp'%self.idx
        )

    self.create_task('moc',h_node,moc_node)

    outputs += [h_node,source_node]

    task = self.create_task(
        'qdbus_proxy',
        self.env.INTROSPECT_FILE,
        outputs
        )

    task.cwd = output_path

    self.includes = self.to_incnodes(getattr(self,'includes',[]))
    self.includes.append(h_node.parent)
    self.includes.append(output_path)

    self.export_includes = self.to_incnodes(getattr(self,'export_includes',[]))
    self.export_includes.append(h_node.parent)
    self.export_includes.append(output_path)
    print self.export_includes

    self.source = self.to_list(getattr(self,'source',[]))
    self.source.append(source_node)
    self.source.append(moc_node)
