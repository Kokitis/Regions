import math
import random
import matplotlib.pyplot as plt

class RegionPlot:
    def __init__(self, *other, **kwargs):
        plt.style.use('fivethirtyeight')
        self.fig, self.ax = self._createPlot()
        self._colormap = dict()
        self._alphamap = dict()
        self._stylemap = dict()
        self._is_formatted = False
        if len(other) > 0:
            self._plotSeries(other, **kwargs)
        


    def formatPlot(self, template):
        if not self._is_formatted:
            self._setPlotOrigins(template)
            self._addPlotLabels(template)
            #self._formatTickLabels(self.ax.get_xticklabels())
            self._addSignature(template)
            self._generateLegend()
            self._is_formatted = True
    def _addSignature(self, template, kind = 'grey'):
        """ Adds text to the bottom of the graph with information about
            the agency and report the data comes from.

            Parameters
            ----------
                template: Series
                    A Series object to use as a template for the series labels.

                kind: {'grey', 'transparent'}
                    Changes how the bottom label is implemented.

        """
        # The signature bar

        # Remove the label of the x-axis
        self.ax.xaxis.label.set_visible(False)
        
        #plot_size = self.fig.get_size_inches() * self.fig.dpi
        left = template.report.name
        right = template.report.agency.name
        
        _padding = 200 - (len(left) - len(right))
        signature_text = "{}{}{}".format(left, " " * _padding, right)
        
        #x_pos = [i.x for i in template]
        #y_pos = [i.y for i in template]
        #x_bounds = min(x_pos) - 3.5
        #y_bounds = -500
        #_color_cast = lambda s: "{:>02X}".format(int(255 * s))
        x_bounds = -0.05
        y_bounds = -0.1
        if kind == 'transparent':
            #_backgroundcolor = "".join(_color_cast(i) for i in self.ax.get_facecolor())
            _backgroundcolor = self.ax.get_facecolor()
            color = 'grey'
            self.ax.text(
                x = x_bounds,
                y = y_bounds,
                s = "_" * _padding,
                fontsize = 14,
                color = color,
                backgroundcolor = _backgroundcolor,
                transform = self.ax.transAxes
            )
        else:
            color = '#F0F0F0'
            _backgroundcolor = "grey"

        self.ax.text(
            x = x_bounds,
            y = y_bounds,
            s = signature_text,
            fontsize = 14,
            color = color,
            backgroundcolor = _backgroundcolor,
            transform = self.ax.transAxes
        )
        #self.ax.text(x = min(template).x, y = .5, s = "(100, 100)")
        
    def _setPlotOrigins(self, template):
        
        # Generate a bolded horizontal line at y = 0 
        self.ax.axhline(y = 0, color = 'black', linewidth = 1.3, alpha = .7)
        x_lims = (min(template.x), max(template.x))
        self.ax.set_xlim(left = min(x_lims) - 1, right = max(x_lims) + 1)
    @staticmethod
    def _createPlot():
        fig, ax = plt.subplots(figsize = (20, 10))
        #ax.tick_params(axis = 'both', which = 'major', labelsize = 18)
        return fig, ax
    def _generateLegend(self):
        """ Generates a legend to indicate what each color, linestyle, and transparency
            applied to each line indicates.
        """
        _colors = list()
        _styles = list()
        for _region_name, _region_color in self._colormap.items():
            line, = plt.plot([1,2,3], c = _region_color, label = _region_name)
            _colors.append(line)
        for _subject_name, _subject_style in self._stylemap.items():
            line, = plt.plot([1,2,3], c = 'k', linestyle = _subject_style, label = _subject_name)
            _styles.append(line)
        handles = _colors + _styles
        self.ax.legend(handles = handles)
        
        
    def _getAlpha(self, string):
        alpha = self._alphamap.get(string)
        if alpha is None:
            index = len(self._alphamap)
            alpha = (100 - (30 * index)) / 100
            self._alphamap[string] = alpha
        return alpha
    
    def _getColor(self, string):
        _default_colors = [
            '#008fd5', '#fc4f30', '#e5ae38',
            '#6d904f', '#8b8b8b', '#810f7c'
        ]
        
        color = self._colormap.get(string)
        if color is None:
            index = len(self._colormap)
            if index < len(_default_colors):
                color = _default_colors[index]
            else:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                color = "#{:>02X}{:>02X}{:>02X}".format(r, g, b)
            self._colormap[string] = color
        return color
    
    def _getStyle(self, string, style = None):
        """
        [‘solid’ | ‘dashed’, ‘dashdot’, ‘dotted’ | (offset, on-off-dash-seq) | '-' | '--' | '-.' | ':' | 'None' | ' ' | '']

        """
        _default_styles = ['-', '--',':', '-.', 'None',' ',  '']
        if style is not None:
            self._stylemap[string] = style
        else:
            style = self._stylemap.get(string)
        if style is None:
            
            index = len(self._stylemap)
            style = _default_styles[index%len(_default_styles)]
            self._stylemap[string] = style
        return style

    @staticmethod
    def _formatTickLabels(labels):
        
        float_labels = list()
        for l in labels:
            try:
                n = float(l.get_text())
                float_labels.append(n)
            except Exception as exception:
                message = "Should add a specific class of exception"
                print(message)
                raise exception
        magnitude = max(float_labels)

        magnitude = math.pow(10, int(math.log10(magnitude)))
        return magnitude
        
    
    def _addPlotLabels(self, template):
        """ Add labels to the x-axis, y-axis, and add a title.

            Parameters
            ----------
                template: Series
                    A series to extract relevant information from.  
        """
        
        self.ax.tick_params(axis = 'both', which = 'major', labelsize = 18)
        self.ax.set_title(template.name)
        self.ax.set_ylabel("{}".format(template.unit))
        self.ax.set_xlabel('Year')    
    
    def _plotSeries(self, other, **kwargs):
                 
        for other_series in other:
            if len(other_series.x) == 0:
                print("Empty Series: ", other_series)
                continue
            
            self.addSeries(other_series, **kwargs)
        
        self.ax.legend()

        
    
    def addSeries(self, series, **kwargs):
        """ Adds a series to the plot.

            Parameters
            ----------
                series: Series
                    The series to plot. The colors, style, transparency,
                    and label will be added automatically.
            
            Keyword Arguments
            -----------------
            color
            linestyle
            alpha
            label
            
        """
       # _current_label = "{} {}".format(series.region.name, series.code)
        _current_label = series.region.name

        kwargs['label'] = kwargs.get('label', _current_label)
        _color = kwargs.get('color')
        _style = kwargs.get('style')
        _alpha = kwargs.get('alpha')
        if _color is None:
            _color = self._getColor(series.region.name)
        if _style is None:
            _style = self._getStyle("{}|{}".format(series.name, series.code), _style)
        if _alpha is None:
            _alpha = self._getAlpha(series.report.name)

        kwargs['color'] = _color
        kwargs['linestyle'] = _style 
        kwargs['alpha'] = _alpha
        kwargs['marker'] = '.'
        kwargs['markersize'] = 10
        result = self.ax.plot(series.x, series.y, **kwargs)
        #result = self.ax.scatter(series.x, series.y, color = kwargs['color'])

        self.formatPlot(series)
        return result

class ProjectionPlot(RegionPlot):
    """ A version of the regionplot specialized for population projections."""

    def addRegion(self, region, report):
        """ Adds all series for a region from the provided report.
        """

        all_series = region.getSeries(report)

        highest_series = max(all_series, lambda s: max(s.y))
        lowest_series  = min([i for i in all_series if i != highest_series], lambda s: min(s.y))

        other_series = [i for i in all_series if (i != highest_series and i != lowest_series)]



