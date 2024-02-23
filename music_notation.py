from manim import *

class Staff(VGroup):
    # The idea here is to make initializing a staff define some parameters for the scene
    # like get_start to figure out the x coordinate that's as close as proper to the key sig
    """
    This class makes a few assumptions about how your staff is formatted as an SVG file:
    - Its lowest layer (viewed in Illustrator) is a background rectangle.
      That rectangle should be the same size for all score objects you want to animate together.
    - All staff lines are the first objects above the background rectangle.
      The staff lines should be ordered in a peculiar way: staves from top to bottom, but lines from bottom to top
      within a staff. Thus, in a piano grand staff, the treble E should be line 0 and bass A should be line 9.
    - There should be no objects to the right of the 'signature' group (e.g. tempo indication, clef, key sig, etc.)
    """
    def __init__(self, file, num_staves=1, scale_factor=1, **kwargs):
        self.staff = SVGMobject(file, stroke_width=0, color=BLACK)
        self.remove_background(self.staff, scale_factor)
        self.group_lines(self.staff, num_staves)
        self.group_remainder(self.staff, num_staves)

        VGroup.__init__(self, *[self.line, self.remainder], **kwargs)

    def remove_background(self, object, scale_factor):
        object.remove(object[0])
        object.scale(scale_factor)

    def group_lines(self, object, num_staves):
        self.line = VGroup()
        for line in range(5 * num_staves):
            new_line = object[line]
            self.line.add(new_line)

    def group_remainder(self, object, num_staves):
        self.remainder = VGroup()
        for i in range(5 * num_staves, len(object.submobjects)):
            symbol = object[i]
            self.remainder.add(symbol)
            # VGroup().get_y

    def get_space(self):
        return self.line[1].get_y() - self.line[0].get_y()

class TheoryStaff(Staff):
    # Need to implement "cluster"
    # rework melody to use *args taking tuples (like chords), not strings of positions and accidentals
    def __init__(self, scale_factor=1, contract_factor=1, **kwargs):
        super().__init__(file="TS_theorystaff", scale_factor=scale_factor, **kwargs)
        self.contract(contract_factor)
        self.notehead = self.remainder[2]
        self.notehead_y = self.notehead.get_y() - self.line[0].get_y()
        self.sharp = self.remainder[3]
        self.sharp_y = self.sharp.get_y() - self.line[0].get_y()
        self.flat = self.remainder[4]
        self.flat_y = self.flat.get_y() - self.line[0].get_y()
        self.cluster = self.remainder[5]
        self.cluster_y = self.cluster.get_y() - self.line[0].get_y()
        self.ledger = self.remainder[6]
        self.bb = self.remainder[7]
        self.bb_y = self.bb.get_y() - self.line[0].get_y()
        self.x = self.remainder[8]
        self.x_y = self.x.get_y() - self.line[0].get_y()
        self.natural = self.remainder[9]
        self.natural_y = self.natural.get_y() - self.line[0].get_y()

        self.notewidth = self.notehead.get_width()
        self.note_buff = (self.notehead.get_critical_point(LEFT) - self.remainder[0].get_critical_point(RIGHT))[0]

        self.misc = VGroup()

        for i in range(8):
            self.misc.add(self.remainder[-1])
            self.remainder.remove(self.remainder[-1])

    def note(self, position, accidental):
        # 0 = none, -1 = flat, +1 = sharp; +3 is natural; +/-2 are doubles; -3 and -4 create a step cluster.
        # bottom line is position 0
        new_note = VGroup(self.notehead.copy())
        new_note.set_y(self.line[0].get_y()+self.notehead_y)
        new_note.shift(UP * .5 * self.get_space() * position)
        new_note.set_x(self.remainder[0].get_critical_point(RIGHT)[0] + self.note_buff)
        if position < -1:
            new_note.add(self.lower_ledger(new_note, position))
        if position > 9:
            new_note.add(self.upper_ledger(new_note, position))

        if accidental == 3:
            # add natural sign
            new_accy = self.natural.copy()
            new_accy.set_y(self.line[0].get_y() + self.natural_y)
            new_accy.shift(.5 * UP * self.get_space() * ((position / 1) - 2))
            new_accy.set_x(new_note.get_x() - self.notewidth)
        if accidental == 1:
            # add sharp
            new_accy = self.sharp.copy()
            new_accy.set_y(self.line[0].get_y() + self.sharp_y)
            new_accy.shift(.5 * UP * self.get_space() * ((position/1) - 1))
            new_accy.set_x(new_note.get_x() - self.notewidth)
        if accidental == -1:
            # add flat
            new_accy = self.flat.copy()
            new_accy.set_y(self.line[0].get_y() + self.flat_y)
            new_accy.shift(.5 * UP * self.get_space() * ((position/1) - 2))
            new_accy.set_x(new_note.get_x() - self.notewidth)
        if accidental == 2:
            # add double sharp
            new_accy = self.x.copy()
            new_accy.set_y(self.line[0].get_y() + self.x_y)
            new_accy.shift(.5 * UP * self.get_space() * ((position / 1) - 1))
            new_accy.set_x(new_note.get_x() - self.notewidth)
        if accidental == -2:
            # add double flat
            new_accy = self.bb.copy()
            new_accy.set_y(self.line[0].get_y() + self.bb_y)
            new_accy.shift(.5 * UP * self.get_space() * ((position / 1) - 2))
            new_accy.set_x(new_note.get_x() - self.notewidth)
        if accidental == -3:
            # add cluster note below & to left
            # Remember that "chords" will align notes to the RIGHT of your original note, so choose -3 or -4 based on
            # what you want to align to. -3 means you want the odd note out to be lower-left, -4 means odd note out
            # is upper-right.
            new_accy = self.cluster.copy()
            new_accy.align_to(new_note, UP)
            new_accy.align_to(new_note, RIGHT)
        if accidental == -4:
            new_accy = self.cluster.copy()
            new_accy.align_to(new_note, DOWN)
            new_accy.align_to(new_note, LEFT)
        if abs(accidental) > 0:
            new_note.add(new_accy)

        return new_note

    def melody(self, positions, accidentals):
        new_melody = VGroup()
        for i, (position, accidental) in enumerate(zip(positions, accidentals)):
            new_note = self.note(position, accidental)
            if i > 0:
                new_note.set_x(new_melody[-1].get_x() + self.note_buff)
                if accidentals[i-1] == 0:
                    new_note.shift(LEFT * .5 * self.sharp.get_width())
            # new_note.shift(RIGHT * self.note_buff * i)
            new_melody.add(new_note)
        # start = new_melody[0].get_x()
        # x_dist_avg = (new_melody[-1].get_x() - start)/len(new_melody)
        # for i, note in enumerate(new_melody):
        #     note.set_x(start + i*x_dist_avg)
        return new_melody

    def chords(self, base_melody, *args, **kwargs):
        # Each arg is a 3-tuple including: the position & accidental of a new note, and then which note in the melody
        # it should align to
        all_chords = VGroup()
        for note in base_melody:
            all_chords.add(VGroup())
        for tuple in args:
            if len(tuple) < 3:
                tuple = [tuple[0], None, tuple[1]]
            new_note = self.note(tuple[0], tuple[1])
            new_note.align_to(base_melody[tuple[2]][0], RIGHT)
            all_chords[tuple[2]].add(new_note)
        for i, note in enumerate(base_melody):
            all_chords[i].add(note)

        return all_chords

    def lower_ledger(self, note, position):
        num_lines_needed = int(abs(np.ceil(position/2)))
        ledger_group = VGroup()

        for i in range(num_lines_needed):
            new_line = self.ledger.copy()
            new_line.set_y(self.line[0].get_y() - (i+1) * self.get_space())
            new_line.match_x(note[0])
            ledger_group.add(new_line)

        return ledger_group

    def upper_ledger(self, note, position):
        num_lines_needed = int(abs(np.floor((position-8)/2)))
        ledger_group = VGroup()

        for i in range(num_lines_needed):
            new_line = self.ledger.copy()
            new_line.set_y(self.line[4].get_y() + (i+1) * self.get_space())
            new_line.match_x(note[0])
            ledger_group.add(new_line)

        return ledger_group

    def contract(self, factor=1/2):
        anchor = self.line[0].copy()
        self.line.stretch(factor, 0)
        self.line.align_to(anchor, LEFT)
        self.remainder[1].align_to(self.line, RIGHT)
        return self


class MusicTitle(VGroup):
    def __init__(self, composer, title, supplement=None, **kwargs):
        all_text = Tex("\\textbf{ " + composer + " }", title).set_color(BLACK)
        # composer_text = TextMobject("\\textbf{ " + composer + " }").set_color(BLACK)
        # title_text = TextMobject(title).set_color(BLACK)

        outline_list = VGroup(all_text[0], all_text[1])
        outline_list.center()

        outline_list[0].align_to(LEFT/2, RIGHT)
        outline_list[1].align_to(RIGHT/2, LEFT)

        if supplement is not None:
            for line in supplement:
                new_line = Tex(line).set_color(DARK_GRAY).scale(.8)
                new_line.next_to(outline_list[-1], DOWN, buff=SMALL_BUFF)
                new_line.align_to(outline_list[1], LEFT)
                outline_list.add(new_line)

        VGroup.__init__(self, *[item for item in outline_list], **kwargs)