class PlotlyFig:
    def __init__(self, fig):
        self.fig = fig
        self.traces_names = [f['name'] for f in self.fig['data']]

    def remove_element_from_figure_data(self, essential_elements):
        new_figure_data = []
        for f in self.fig['data']:
            if f['name'] in essential_elements:
                new_figure_data.append(f)
        new_figure_data = tuple(new_figure_data)
        self.fig['data'] = new_figure_data
        print(self.fig['data'])
        return self.fig
