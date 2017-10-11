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

        for tag in system.tagbus.tags.keys():
            name_components = tag.split('_')
            tag_category = '_'.join(name_components[0:2])
            tag_name = '_'.join(name_components[2:])
            self.tree.insert(tag_category, 0, tag, text=tag_name, value=["0"])

        self.tree.pack(side="top")

        """   
        for tag in system.tagbus.items():

            self.tree.insert("asset1", 0, "asset1_tag1",  # Insert Under Parent
                             text="Tag1", values=("0", "kW"))

        # tree.insert(pos, child, **kw)
        self.tree.insert("", 1, "asset1", text="GridIntertie1")   # Parent in tree
        self.tree.insert("asset1", 0, "asset1_tag1",              # Insert Under Parent
                         text="Tag1", values=("0","kW"))

        self.tree.insert("", 1, "asset2", text="EnergyStorage1")
        self.tree.insert("asset2", 0, "asset2_tag1",
                         text="Tag1", values=("0", "kW"))

        self.tree.insert("", 1, "asset3", text="Feeder1")
        self.tree.insert("asset3", 0, "asset3_tag1",
                         text="Tag1", values=("0", "kW"))

        self.status = ttk.Treeview()
        self.tree.pack(side="top")
        """


