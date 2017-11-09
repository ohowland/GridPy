#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk

class Application(tk.Frame):
    def __init__(self, system):
        self.root = tk.Tk()
        super().__init__(self.root)
        self.pack()
        self.create_widgets()
        self.create_tree(system)

    def create_widgets(self):
        self.quit = tk.Button(self, text='STOP', fg='red', command=self.root.destroy)
        self.quit.pack(side='bottom')

    def create_tree(self, system):
        self.tree = ttk.Treeview(self.root)
        self.tree['columns'] = ('val','units')
        self.tree.column("val", width=100)
        self.tree.column("units", width=100)
        self.tree.heading("val", text="Tag Value")
        self.tree.heading("units", text="Units")

        for asset_name in system.assets.keys():
            self.tree.insert("", 1, asset_name, text=asset_name)
            self.tree.insert(asset_name, 1, asset_name + '_status', text='status')
            self.tree.insert(asset_name, 1, asset_name + '_ctrl', text='control')
            self.tree.insert(asset_name, 1, asset_name + '_config', text='configuration')

            for tag in system.assets[asset_name].status.keys():
                tag_category = asset_name + '_status'
                self.tree.insert(tag_category, 0, asset_name + '_' + tag, text=tag, value=["0"])

            for tag in system.assets[asset_name].ctrl.keys():
                tag_category = asset_name + '_ctrl'
                self.tree.insert(tag_category, 0, asset_name + '_' + tag, text=tag, value=["0"])

            for tag in system.assets[asset_name].config.keys():
                tag_category = asset_name + '_config'
                self.tree.insert(tag_category, 0, asset_name + '_' + tag, text=tag, value=["0"])

        self.tree.pack(side="top")

    def update_tree(self, system):

        for asset_name in system.assets.keys():
            for tag in system.assets[asset_name].status.keys():
                tag_val = system.read(asset_name + '_' + tag)
                self.tree.set(asset_name + '_' + tag, 'val', tag_val)

            for tag in system.assets[asset_name].ctrl.keys():
                tag_val = system.read(asset_name + '_' + tag)
                self.tree.set(asset_name + '_' + tag, 'val', tag_val)

            for tag in system.assets[asset_name].config.keys():
                tag_val = system.read(asset_name + '_' + tag)
                self.tree.set(asset_name + '_' + tag, 'val', tag_val)
