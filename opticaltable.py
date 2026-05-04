import cairo
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import math

allowed_ids = ('laser', 'mirror', 'box')

allowed_modes = ('r', 't')

allowed_rel_pos = ('above', 'below', 'left', 'right', 'inside')

class Tools:

    def get_midpoint(start, end):
        """Get midpoint of a line"""
        midpoint_x = 0.5*(start[0] + end[0])
        midpoint_y = 0.5*(start[1] + end[1])
        return midpoint_x, midpoint_y
    
    def draw_arrow(tbl,start, end):
        xmid, ymid = Tools.get_midpoint(start, end)

        #Check if not vertical
        if(end[0] - start[0] != 0):
            slope = (end[1] - start[1]) / (end[0] - start[0])
            #downward/leftward
            if(end[1] > start[1] | end[0] < start[0]):
                slopeAngle = Tools.rad_to_deg(math.atan(slope)) + 180
            #upward/rightward
            else:
                slopeAngle = Tools.rad_to_deg(math.atan(slope))
        #Edgecases for vertical up/down
        elif(end[1] - start[1] > 0):
            slope = -1
            slopeAngle = 90
        else:
            slope = 1
            slopeAngle = -90

        angle = 135 + slopeAngle
        length = 6
        arrowStartX = xmid + length * Tools.cosd(angle)
        arrowStartY = ymid + length * Tools.sind(angle)
        arrowEndX = xmid + length * Tools.cosd(angle+90)
        arrowEndY = ymid + length * Tools.sind(angle+90)

        tbl.set_line_width(0.75)
        tbl.set_dash([1,0])
        tbl.move_to(arrowStartX,arrowStartY)
        tbl.line_to(xmid, ymid)
        tbl.line_to(arrowEndX, arrowEndY)
        tbl.stroke()

    def text(tbl, string, x, y, theta = 0.0, fontsize=5):
        tbl.save()

        tbl.select_font_face("Monospace")
        tbl.set_font_size(fontsize)
        fascent, fdescent, fheight, fxadvance, fyadvance = tbl.font_extents()
        x_off, y_off, tw, th = tbl.text_extents(string)[:4]
        nx = -tw/2.0
        ny = th/2.5

        tbl.translate(x, y)
        tbl.rotate(theta)
        tbl.translate(nx, ny)
        tbl.move_to(0,0)
        tbl.show_text(string)
        tbl.restore()

    def get_corners(x,y,width,height,rot=0):
        tl = ( (x - ((width/2) * Tools.cosd(rot)) + ((height/2) * Tools.sind(rot))), (y - ((width/2) * Tools.sind(rot)) - ((height/2) * Tools.cosd(rot))) )
        tr = ( (x + ((width/2) * Tools.cosd(rot)) + ((height/2) * Tools.sind(rot))), (y + ((width/2) * Tools.sind(rot)) - ((height/2) * Tools.cosd(rot))) )
        bl = ( (x - ((width/2) * Tools.cosd(rot)) - ((height/2) * Tools.sind(rot))), (y - ((width/2) * Tools.sind(rot)) + ((height/2) * Tools.cosd(rot))) )
        br = ( (x + ((width/2) * Tools.cosd(rot)) - ((height/2) * Tools.sind(rot))), (y + ((width/2) * Tools.sind(rot)) + ((height/2) * Tools.cosd(rot))) )

        return bl,tl,tr,br


    def deg_to_rad(x):
        """Convert degrees to radians."""
        return x * (np.pi/180)
    
    def rad_to_deg(x):
        return x * (180/np.pi)

    def sind(x):
        """Return sine of an angle in degrees."""
        return np.sin(Tools.deg_to_rad(x))

    def cosd(x):
        """Return cosine of an angle in degrees."""
        return np.cos(Tools.deg_to_rad(x))

class OpticalTable:

    def __init__(self, width, height, filename, border=True):
        self.width = width
        self.height = height
        self.filename = filename
        self.border = border
        self.surface = cairo.SVGSurface(self.filename, self.width, self.height)
        self.tbl = cairo.Context(self.surface)

        self.tbl.set_source_rgb(0,0,0)
        self.tbl.set_line_width(1)
        self.tbl.scale(1,1)
        self.tbl.set_dash([1,0])
        self.tbl.save()
        
        #List of Elements
        self.elements = []

        #Draw border
        if(self.border):
            self.tbl.scale(1, 1)
            self.tbl.rectangle(0,0, self.width, self.height)
            self.tbl.stroke()

    def draw_elements(self):

        #Draw Elements
        for i in self.elements:
            i.draw(self.tbl)
            if(i.label):
                i.add_label(self.tbl, i.xpos, i.ypos, i.label, i.label_pos, i.labelpad)

        #Finalize  
        self.surface.finish()
        self.surface.flush()

    
    def mirror(self, x, y, angle, scale=1, label=None, label_pos='above', labelpad=0, labelsize=5, fliplabel=False):

        aspect_ratio = self.width / self.height
        #dX = (length/2) * Tools.cosd(angle) * aspect_ratio
        #dY = (length/2) * Tools.sind(angle) * aspect_ratio  
        width = 10 * scale
        height = 2 * scale

        mirror = Mirror(x,y,width,height,label, label_pos,'r', element_id="mirror", rot=angle, labelpad=labelpad, labelsize=labelsize, fliplabel=fliplabel)
        self.elements.append(mirror)

        return mirror
    
    def genericBox(self, x, y, width, height, rot, color=(0,0,0), scale=1, fill=None, fillcolor=(0,0,0), label='', label_pos='inside', labelpad=0, labelsize=5, fliplabel=False):
        
        box = GenericBox(x,y,width,height,rot,color,fill, fillcolor, scale=scale, label=label, label_pos=label_pos, labelpad=labelpad, labelsize=labelsize, fliplabel=fliplabel)
        self.elements.append(box)

        return box

    def pathObject(self,x,y):
        po = PathObject(x,y)
        return po

    def beam(self, beampath, color, size=1, fiber=False, arrows=False):
        j = 0
        for i in beampath:
            self.tbl.set_source_rgb(color[0],color[1],color[2])
            self.tbl.set_line_width(1)
            if(fiber):
                self.tbl.set_dash([1,0])
            else:
                self.tbl.set_dash([1,1])
            if j < (len(beampath)-1):
                self.tbl.move_to(i.xpos, i.ypos)
                self.tbl.line_to(beampath[j+1].xpos, beampath[j+1].ypos)
                self.tbl.stroke()
                if(arrows):
                    Tools.draw_arrow(self.tbl, (i.xpos, i.ypos),(beampath[j+1].xpos, beampath[j+1].ypos))
                j += 1


class OpticalElement:

    def __init__(self, xpos, ypos, mode='r', scale=1, rot=None, element_id=None, label=None, label_pos='above', labelpad=0, labelsize=5, fliplabel=False):
        self.element_id = element_id
        self.xpos = xpos
        self.ypos = ypos
        self.scale = scale
        self.rot = rot
        self.mode = mode
        self.label = label
        self.label_pos = label_pos
        self.labelpad = labelpad
        self.labelsize = labelsize
        self.fliplabel = fliplabel

class Mirror(OpticalElement):
    
    def __init__(self, xpos, ypos, dX, dY, label, label_pos, mode='r', scale=1, rot=None, element_id=None, labelpad=0, labelsize=5, fliplabel=False):
        super().__init__(xpos, ypos, mode, scale, rot, element_id, label, label_pos, labelpad, labelsize, fliplabel)
        self.dX = dX
        self.dY = dY

    def draw(self, tbl):
        #tbl.move_to(self.xpos-self.dX, self.ypos-self.dY)
        #tbl.line_to(self.xpos+self.dX, self.ypos+self.dY)
        bl,tl,tr,br = Tools.get_corners(self.xpos, self.ypos, self.dX, self.dY, self.rot)
        midA = Tools.get_midpoint(bl,tl) 
        midB = Tools.get_midpoint(br,tr)

        pattern = cairo.LinearGradient(midA[0], midA[1], midB[0], midB[1])
        pattern.add_color_stop_rgb(0, 0.54, 0.8, 1)
        pattern.add_color_stop_rgb(0.5, 1,1,1)
        pattern.add_color_stop_rgb(1, 0.54, 0.8, 1)
        tbl.set_source(pattern)

        tbl.move_to(bl[0],bl[1])
        tbl.line_to(tl[0],tl[1])
        tbl.line_to(tr[0],tr[1])
        tbl.line_to(br[0],br[1])
        tbl.line_to(bl[0],bl[1])
        tbl.line_to(tl[0],tl[1])

        tbl.fill_preserve()
        tbl.set_line_width(1)
        tbl.set_source_rgb(0,0,0)
        tbl.stroke()

    def add_label(self,tbl, x, y, text, label_pos, labelpad):
        if label_pos not in allowed_rel_pos:
            raise AttributeError("Invalid label position, use 'left', 'right', 'below' or 'above'")

        offset=10
        tbl.select_font_face("Monospace")
        tbl.set_font_size(self.labelsize)
        tbl.set_source_rgb(0,0,0)
        xcor = len(text) / 2 + self.labelsize
        match label_pos:
            case 'above': 
                tbl.move_to(x-xcor, y-offset-labelpad)
                tbl.show_text(text)
                tbl.stroke()
            case 'below': 
                tbl.move_to(x-xcor, y+offset+3+labelpad)
                tbl.show_text(text)
                tbl.stroke()
            case 'left':
                tbl.move_to(x-offset-labelpad, y)
                tbl.show_text(text)
                tbl.stroke()
            case 'right':
                tbl.move_to(x+offset+labelpad, y)
                tbl.show_text(text)
                tbl.stroke()
            case 'inside':
                if(self.fliplabel):
                    Tools.text(tbl, self.label, x, y, Tools.deg_to_rad(self.rot + 180), fontsize=self.labelsize)
                else:
                    Tools.text(tbl, self.label, x, y, Tools.deg_to_rad(self.rot), fontsize=self.labelsize)
                

class GenericBox(OpticalElement):

    def __init__(self, xpos, ypos, width, height, rot=0, color=(0,0,0), fill=None, fillcolor=(0,0,0), mode='r', scale=1, element_id=None, label=None, label_pos='inside', labelpad=0, labelsize=5, fliplabel=False):
        super().__init__(xpos, ypos, mode, scale, rot, element_id, label, label_pos, labelpad, labelsize, fliplabel)
        self.width = width
        self.height = height
        self.color = color
        self.fill = fill
        self.fillcolor = fillcolor

    def draw(self, tbl):
        #rotated corner coordinates
        bl, tl, tr, br = Tools.get_corners(self.xpos, self.ypos, self.width, self.height, self.rot)
        
        tbl.set_source_rgb(self.color[0], self.color[1], self.color[2])
        tbl.set_line_width(self.scale)
        tbl.move_to(bl[0],bl[1])
        tbl.line_to(tl[0],tl[1])
        tbl.line_to(tr[0],tr[1])
        tbl.line_to(br[0],br[1])
        tbl.line_to(bl[0],bl[1])
        tbl.line_to(tl[0],tl[1])

        if(self.fill):
            tbl.set_source_rgb(self.fillcolor[0], self.fillcolor[1], self.fillcolor[2])
            tbl.fill_preserve()
            tbl.set_source_rgb(self.color[0], self.color[1], self.color[2])
            tbl.stroke()
        else:
            tbl.stroke()

    def add_label(self,tbl, x, y, text, label_pos, labelpad):
        if label_pos not in allowed_rel_pos:
            raise AttributeError("Invalid label position, use 'left', 'right', 'below' or 'above'")

        offset=15
        tbl.select_font_face("Monospace")
        tbl.set_font_size(self.labelsize)
        tbl.set_source_rgb(0,0,0)
        xcor = len(text) / 2 + self.labelsize
        match label_pos:
            case 'above':
                tbl.move_to(x-xcor, y-offset-labelpad)
                tbl.show_text(self.label)
            case 'below': 
                tbl.move_to(x-xcor, y+offset+3+labelpad)
                tbl.show_text(self.label)
            case 'left': 
                tbl.move_to(x-offset-labelpad, y)
                tbl.show_text(self.label)
            case 'right':
                tbl.move_to(x+offset+labelpad, y)
                tbl.show_text(self.label)
            case 'inside':
                if(self.fliplabel):
                    Tools.text(tbl, self.label, x, y, Tools.deg_to_rad(self.rot + 180), fontsize=self.labelsize)
                else:
                    Tools.text(tbl, self.label, x, y, Tools.deg_to_rad(self.rot), fontsize=self.labelsize)
        
        
        tbl.stroke()
    
class PathObject:

    def __init__(self, x,y):
        self.xpos = x
        self.ypos = y

    def draw():
        return





        