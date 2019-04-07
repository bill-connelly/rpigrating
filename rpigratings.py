
import time as t
import os, sys
from collections import namedtuple

GratPerfRec = namedtuple("GratingPerformanceRecord",["mean_FPS","slowest_frame_FPS","start_time"])

GRAY = (127,127,127)
BLACK = (0,0,0)
WHITE = (255,255,255)
SINE = 1
SQUARE = 0

# We wish to import _rpigratings from its
# relative path /build/lib.linux-armv7l-3.4
# but we must not have the "-" character in
# our import command, so 
#    >>> import build.lib.linux-armv7l-3.4._rpigratings
# is an illegal command.
# Therefore we will use sys.path to modify the lookup
# path for modules to include the relevant directory.

PATH = os.getcwd() + "/build/lib.linux-armv7l-3.4"
sys.path.append(PATH)
import _rpigratings as rpy


def draw_grating(filename,spac_freq,temp_freq,
                 angle=0, resolution = (1280,720)):
    """
    Create a raw animation file of a drifting grating called filename.
    The grating's angle of propogation is measured counterclockwise
      from the x-axis and defaults to zero.
    The spacial frequency of the grating is in cycles per degree of
      visual angle.
    The temporal frequency is in cycles per second.
    The resolution paramater is formatted as (width, height) and
      must match the resolution of any Screen object used to display
      the grating.
    For smooth propogation of the grating, the pixels-per-frame speed
      is truncated to the nearest interger; low resolutions combined with
      a low temporal frequency:spacial frequency ratio may result in incorrect
      speeds of propogation or even static, unmoving gratings. This also means
      that the temp_freq is approximate only.
    """
    rpy.draw_grating(filename,angle,spac_freq,temp_freq,
                     resolution[0],resolution[1])
    


class Screen:
    def __init__(self, resolution=(1280,720)):
        """
        A class encapsulating the raspberry pi's framebuffer,
          with methods to display drifting gratings and solid colors to
          the screen.
          
        ONLY ONE INSTANCE OF THIS OBJECT SHOULD EXIST AT ANY ONE TIME.
          Otherwise both objects will be attempting to manipulate the memory
          assosiated with the linux framebuffer. If a resolution change is desired
          first clean up the old instance of this class with the close() method
          and then create the new instance.
          
        The resolution of this screen object does NOT need to match the actual
          resolution of the physical display; the linux framebuffer device is
          automatically scaled up to fit the physical display.
          
        The resolution of this object MUST match the resolution of any
          grating animation files created by draw_grating; if the resolution
          of the animation is smaller pixels will simply be misaligned, but
          if the animation is larger then attempting to play it will cause a
          segmentation fault.
        
        :param resolution: a tuple of the desired width of the display
          resolution as (width, height). Defaults to (1280,720).
         """
        self.capsule = rpy.init(resolution[0],resolution[1])
        self.grating = None

    def load_grating(self,filename):
        """
        Load a raw grating file called filename into local memory. Once loaded
        in this way, display_grating() can be called to display the loaded file
        to the screen.
        """
        if self.grating != None:
            self.close()
            raise FileError("Only one grating may be loaded into"
                            + " local memory. Call unload_grating() first.")
        try: self.grating = rpy.load_grating(self.capsule,filename)
        except:
            self.close()
            raise
    def unload_grating(self):
        """
        Clear the loaded grating from memory so another grating can
        be loaded.
        """
        try:
            rpy.unload_grating(self.grating)
            del self.grating
            self.grating = None
        except:
            self.close()
            raise
    def display_grating(self, cleanup=True):
        """
        Display the currently loaded grating (grating files are created with
        the draw_grating function and loaded with the Screen.load_grating
        method). Also automatically unloads the currently loaded grating
        after displaying it unless cleanup is set to False.

        Returns a namedtuple (from the collections module) with the fields
        mean_FPS, slowest_frame_FPS,
        and start_time; these refer respectively to the average FPS, the inverse
        of the time of the slowest frame, and the time the
        grating began to play (in Unix Time).
        """
        if self.grating==None:
            self.close()
            raise NameError("Attempted to display a grating without "
                            +"first loading a grating file with load_grating()")
        else:
            try:
                rawtuple = rpy.display_grating(self.capsule, self.grating)
                if cleanup: self.unload_grating()
                return GratPerfRec(*rawtuple)
            except:
                self.close()
                raise
            
    def display_color(self,color):
        """
        Fill the screen with a solid color until something else is
                displayed to the screen. Calling display_color(GRAY) will
                display mid-gray.
        :param color: 3-tuple of the rgb color value eg (255,0,0) for red.
                Available macros are WHITE, BLACK, and GRAY.
        :rtype None:
        """
        for value in color:
            if (value<0 or value>255):
                self.close()
                raise ValueError("Color must be a tuple of RBG values"
                                 + "each between 0 and 255.")
        try: rpy.display_color(self.capsule,color[0],color[1],color[2])
        except:
            self.close()
            raise
    def close(self):
        """
        Destroy this object, cleaning up its memory and restoring previous
        screen settings.
        :rtype None:
        """
        rpy.close_display(self.capsule)
        del self

