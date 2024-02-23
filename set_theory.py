from manim import *
config.background_color = WHITE
MuTeX = TexTemplate().add_to_preamble(r"\usepackage{musicography}")

# Constants

BROWN = "#603917"
CB_COLORS = [BLUE_E, "#ff8000", "#08ff40", "#e6f219",
             "#33ffff", "#ff3300", "#e64dff", BROWN]


# Functions
def rotate_list(pc_set, n=1):
    n = n % len(pc_set)
    res = pc_set[slice(n, len(pc_set))]
    new_tail = pc_set[slice(0, n)]
    for item in new_tail:
        res.append(item)
    return res


def start_zero(pc_set, edo=12, zero_index=0):
    pc_set = np.array(pc_set)
    return np.sort(((pc_set % edo) - pc_set[zero_index]) % edo)


def tn_prime(pc_set, edo=12):
    # Returns a np.array. set can be a list or np.array
    pc_set.sort()
    card = len(pc_set)
    modes = np.zeros((card, card))

    for i in range(card):
        modes[i] = start_zero(pc_set, edo, i)

    # Added these lines 20231015 to deal with problems with inputs like (0, 4, 6, 10)
    modes = np.unique(modes, axis=0)

    if len(modes) == 1:
        return modes.flatten()

    card = modes.shape[0]

    preferred_mode = list(range(card))
    for i in reversed(range(card)):
        preferred_mode = np.argwhere(modes[:, i] == np.amin(modes[preferred_mode, i]))
        if len(preferred_mode) < 2:
            break

    if len(preferred_mode) > 1:
        preferred_mode = preferred_mode[0]

    return modes[preferred_mode].flatten()


def prime_form(pc_set, edo=12):
    # Returns a np.array. set can be a list or np.array
    card = len(pc_set)

    if card == 0:
        return np.array(0)
    if card == 1:
        return np.array([0])

    strange_set = tn_prime(pc_set, edo)
    charm_set = tn_prime(np.repeat(edo, card) - np.array(pc_set), edo)
    set_comparison = charm_set - strange_set
    differences = np.nonzero(set_comparison)

    if len(differences[0]) < 1:
        return strange_set

    orientation = set_comparison[np.amax(differences)]
    if orientation < 0:
        return charm_set
    else:
        return strange_set


# Objects
class Clockface(VMobject):
    CONFIG = {
        "edo": 12,
        "clockface_color": BLACK,
        "clockface_radius": 2,
        "digit_ratio": 0.75,
        "digit_size": 1,
        "digit_color": BLACK,
        "note_color": BLUE_E,
        "note_radius": 0.3,
        "letter_names": False,
        "sub_doubles": False
    }

    def __init__(self,
                 edo=12,
                 clockface_color=BLACK,
                 clockface_radius=2,
                 digit_ratio=0.75,
                 digit_size=1,
                 digit_color=BLACK,
                 note_color=BLUE_E,
                 note_radius=0.35,
                 letter_names=False,
                 sub_doubles=False,
                 **kwargs):

        VMobject.__init__(self, **kwargs)
        self.edo = edo
        self.clockface_color = clockface_color
        self.clockface_radius = clockface_radius
        self.digit_ratio = digit_ratio
        self.digit_size = digit_size
        self.digit_color = digit_color
        self.note_color = note_color
        self.note_radius = note_radius
        self.letter_names = letter_names
        self.sub_doubles = sub_doubles

        if self.letter_names is True:
            self.edo = 12

        self.get_clockface()

    def get_clockface(self):
        # oc for "o'clock":
        oc = []
        pc_letters = ["C", "C\\sh", "D", "E\\fl", "E", "F", "F\\sh", "G", "A\\fl", "A", "B\\fl", "B"]
        double_subs = ["T", "E", "W", "R", "U", "I", "X", "V", "G", "N", "Y"]
        digits = VGroup()

        for pc in range(self.edo):
            position = self.rotate_vec(-TAU * pc / self.edo, (UP * self.clockface_radius * self.digit_ratio))
            oc.append(position)
            if self.letter_names is False:
                digit = Text(str(pc), color=self.digit_color, font="Gentium Book Basic")
                if self.sub_doubles is True and pc > 9:
                    digit = Text(double_subs[pc-10], color=self.digit_color, font="Gentium Book Basic")
            else:
                digit = Tex(pc_letters[pc], tex_template=MuTeX, color=self.digit_color)
            digit.scale(self.digit_size)
            digit.move_to(position)
            digits.add(digit)

        rim = Circle(radius=self.clockface_radius, color=self.clockface_color)

        # clockface = VGroup(*digits,rim)
        # self.add(clockface)
        self.add(digits)
        self.add(rim)

    def digit(self, number):
        return self[0][number]

    def get_pcset(self, pitch_classes, **kwargs):
        if "color" not in kwargs:
            kwargs["color"] = self.note_color

        if "radius" not in kwargs:
            kwargs["radius"] = self.note_radius

        circles = VGroup()
        circles.host = self

        for pc in pitch_classes:
            new_circle = Circle(**kwargs)
            new_circle.move_to(self.n2p(pc))
            circles.add(new_circle)

        # self.add(circles)
        return circles

    def get_arc(self, start, stop, radius_scale=1, **kwargs):
        result_arc = self[1].copy()
        result_arc.host = self
        if stop - start > 0:
            result_arc.reverse_points()

        result_arc.rotate((TAU/4) - self.p2a(Dot().move_to(self.n2p(start))))
        start_point = 0
        end_point = (abs(stop - start)/self.edo) % 1
        result_arc.pointwise_become_partial(result_arc, start_point, end_point)
        result_arc.set_style(**kwargs)
        result_arc.scale_about_point(radius_scale, self[1].get_center())
        # self.add(result_arc)
        return result_arc

    def number_to_point(self, number):
        noon = self.digit(0).get_center() - self[1].get_center()
        hand_position = self.rotate_vec(TAU * (-number / self.edo), noon)
        return hand_position + self[1].get_center()

    def point_to_number(self, point):
        # This takes the "note circle" as the point argument
        coords = point.get_center() - self[1].get_center()
        x_coord = coords[0]
        y_coord = coords[1]

        if y_coord > 0:
            theta = np.arctan(x_coord/y_coord)
        elif y_coord < 0:
            theta = PI + np.arctan(x_coord/y_coord)
        else:
            theta = (PI/2) * np.sign(x_coord)

        return (self.edo * theta/TAU) % self.edo

    def point_to_angle(self, point):
        # This takes the "note circle" as the point argument
        coords = point.get_center() - self[1].get_center()
        x_coord = coords[0]
        y_coord = coords[1]

        if y_coord > 0:
            theta = np.arctan(x_coord/y_coord)
        elif y_coord < 0:
            theta = PI + np.arctan(x_coord/y_coord)
        else:
            theta = (PI/2) * np.sign(x_coord)

        return theta

    def n2p(self, number):
        """Abbreviation for number_to_point"""
        return self.number_to_point(number)

    def p2n(self, point):
        return self.point_to_number(point)

    def p2a(self, point):
        return self.point_to_angle(point)

    def get_edo(self):
        return self.edo

    @staticmethod
    def rotate_vec(angle, vector):
        cos = np.cos(angle)
        sin = np.sin(angle)
        rotation_matrix = np.array(((cos, -sin, 0), (sin, cos, 0), (0, 0, 0)))
        out_vec = rotation_matrix.dot(vector)
        return out_vec


class Tonnetz(VMobject):
    CONFIG = {
        "edo": 12,
        "node_color": BLACK,
        "line_color": BLACK,
        "node_radius": 0.35,
        "node_fill": WHITE,
        "letter_names": True,
        "horiz_angle": 0,
        "horiz_dist": 1,
        "horiz_interval": 7,
        "horiz_radius": 6,
        "diag_angle": TAU/6,
        "diag_dist": 1,
        "diag_interval": 4,
        "diag_radius": 3,
        "dashed_boundary": True,
        "all_sharps": False
    }

    def __init__(self,
                 edo=12,
                 node_color=BLACK,
                 line_color=BLACK,
                 node_radius=0.35,
                 node_fill=WHITE,
                 letter_names=True,
                 horiz_angle=0,
                 horiz_dist=1,
                 horiz_interval=7,
                 horiz_radius=6,
                 diag_angle=TAU/6,
                 diag_interval=4,
                 diag_dist=1,
                 diag_radius=3,
                 dashed_boundary=True,
                 all_sharps=False,
                 **kwargs):
        VMobject.__init__(self, **kwargs)

        self.edo = edo
        self.node_color = node_color
        self.line_color = line_color
        self.node_radius = node_radius
        self.node_fill = node_fill
        self.letter_names = letter_names
        self.horiz_angle = horiz_angle
        self.horiz_dist = horiz_dist
        self.horiz_interval = horiz_interval
        self.horiz_radius = horiz_radius
        self.diag_angle = diag_angle
        self.diag_dist = diag_dist
        self.diag_interval = diag_interval
        self.diag_radius = diag_radius
        self.dashed_boundary = dashed_boundary
        self.all_sharps = all_sharps

        self.horiz_vector = np.array([self.horiz_dist * np.cos(self.horiz_angle),
                                     self.horiz_dist * np.sin(self.horiz_angle),
                                     0])
        self.diag_vector = np.array([self.diag_dist * np.cos(self.diag_angle),
                                     self.diag_dist * np.sin(self.diag_angle),
                                     0])

        if self.letter_names is True:
            self.edo = 12
        self.get_nodes()
        self.get_lines()

        self.nodes = self[0]
        self.lines = self[1]

    def get_nodes(self, **kwargs):

        pc_letters = ["C", "C\\sh", "D", "E\\fl", "E", "F", "F\\sh", "G", "A\\fl", "A", "B\\fl", "B"]
        if self.all_sharps is True:
            pc_letters = ["C", "C\\sh", "D", "D\\sh", "E", "F", "F\\sh", "G", "G\\sh", "A", "A\\sh", "B"]
        nodes = VGroup()

        for j in range(-self.horiz_radius, self.horiz_radius+1):
            for i in range(-self.diag_radius, self.diag_radius+1):
                position = ORIGIN + (i * self.diag_vector) + (j * self.horiz_vector)
                pitch_class_integer = (i*self.diag_interval + j*self.horiz_interval) % self.edo

                if self.letter_names is False:
                    digit = Tex(str(pitch_class_integer), color=self.node_color)
                else:
                    digit = Tex(pc_letters[pitch_class_integer], tex_template=MuTeX,
                                color=self.node_color)
                digit.move_to(position)
                digit_circle = Circle(radius=self.node_radius,
                                      color=self.node_color,
                                      # fill_color=self.node_fill, fill_opacity=1,
                                      **kwargs).move_to(position)
                node = VGroup(digit_circle, digit)
                nodes.add(node)

        self.add(nodes)

    def get_lines(self, **kwargs):
        lattice = VGroup()
        # for i in range(-self.diag_radius, self.diag_radius):
        #     for j in range(-self.horiz_radius, self.horiz_radius):
        for y in range(-self.horiz_radius, self.horiz_radius):
            for x in range(-self.diag_radius, self.diag_radius):
                lattice.add(Line(start=self.grid(x, y).get_center(), end=self.grid(x, y+1).get_center(),
                                 buff=self.node_radius, color=self.line_color, **kwargs))
                lattice.add(Line(start=self.grid(x, y).get_center(), end=self.grid(x+1, y).get_center(),
                                 buff=self.node_radius, color=self.line_color, **kwargs))
                lattice.add(Line(start=self.grid(x+1, y).get_center(), end=self.grid(x, y+1).get_center(),
                                 buff=self.node_radius, color=self.line_color, **kwargs))
        for x in range(-self.diag_radius, self.diag_radius):
            lattice.add(Line(start=self.grid(x, self.horiz_radius).get_center(), end=self.grid(x+1, self.horiz_radius).get_center(),
                             buff=self.node_radius, color=self.line_color, **kwargs))
        for x in range(self.horiz_radius-1, -self.horiz_radius-1, -1):
            lattice.add(Line(start=self.grid(self.diag_radius, x).get_center(), end=self.grid(self.diag_radius, x+1).get_center(),
                             buff=self.node_radius, color=self.line_color, **kwargs))
        self.add(lattice)

    def grid(self, i, j):
        # Note that I've chosen to index positions like a matrix: row then column.
        # This is opposite your intuitions for how a Cartesian plane would work.
        modulus = (2*self.diag_radius) + 1
        central_point = (modulus * self.horiz_radius) + self.diag_radius
        return self[0][central_point + (j * modulus) + i]


# Animations
class Transpose(Succession):
    def __init__(self, pc_set, distance,
                 show_label=True,
                 remove_label=True,
                 first_arrow_only=True,
                 match_note_color=True,
                 scalar_offset=0,
                 place_label_inside=False,
                 label_color=BLACK,
                 default_arrow_scale=0.55,
                 **kwargs):

        self.show_label = show_label
        self.remove_label = remove_label
        self.first_arrow_only = first_arrow_only
        self.match_note_color = match_note_color
        self.scalar_offset = scalar_offset
        self.place_label_inside = place_label_inside
        self.label_color = label_color
        self.default_arrow_scale = default_arrow_scale

        if "label_text" not in kwargs:
            self.label_text = ["T_{", str(distance), "}"]
        else:
            self.label_text = kwargs["label_text"]

        self.arrows = VGroup()
        self.arrow_radius = self.default_arrow_scale * pc_set.host[1].get_width()
        self.arrow_center = pc_set.host[1].get_arc_center()
        creation_animations = []
        fade_animations = []
        host = pc_set.host

        if self.first_arrow_only:
            run_over = pc_set[0]
        else:
            run_over = pc_set

        if self.place_label_inside:
            radius_scalars = np.linspace(.3, .5, len(run_over)) + self.scalar_offset
        else:
            radius_scalars = np.linspace(1.3, 1.1, len(run_over)) + self.scalar_offset

        for note, scalar in zip(run_over, radius_scalars):
            note.host = host
            creation_animations.append(Create(self.get_arrow(note, distance, scalar), **kwargs))

        tn_label = self.get_tn_label(self.arrows[0])

        main_rotation = self.get_rotation(pc_set, distance, **kwargs)

        animations = list([])
        animations.append(main_rotation)

        if self.show_label:
            animations.remove(main_rotation)
            animations.append(AnimationGroup(Write(tn_label), *creation_animations, main_rotation,
                                             lag_ratio=0.1, rate_func=linear))
            pc_set.host.add(tn_label)
            pc_set.host.add(self.arrows)
            fade_animations.append(FadeOut(tn_label))
            for arrow in self.arrows:
                fade_animations.append(FadeOut(arrow, **kwargs))

        if self.show_label and self.remove_label:
            pc_set.host.remove(tn_label)
            pc_set.host.remove(self.arrows)
            animations.append(AnimationGroup(*fade_animations))

        super().__init__(*animations, **kwargs)

    def get_rotation(self, pc_set, distance, **kwargs):
        center = pc_set.host[1].get_arc_center()
        rotate_by = TAU*(distance/pc_set.host.edo)
        return Rotate(pc_set, angle=rotate_by, axis=IN, about_point=center, **kwargs)

    def get_arrow(self, note, distance, radius_scalar):
        arrow = note.host[1].copy()
        if distance > 0:
            arrow.reverse_points()

        arrow.rotate((TAU/4) - note.host.p2a(note))
        start_point = 0
        end_point = (abs(distance)/note.host.edo) % 1
        arrow.pointwise_become_partial(arrow, start_point, end_point)
        arrow.scale(radius_scalar)

        if distance != 0:
            arrow.move_arc_center_to(self.arrow_center)
        else:
            arrow.next_to(note, note.get_center()-self.arrow_center)

        if self.match_note_color:
            arrow.set_color(note.get_color())
        else:
            arrow.set_color(self.label_color)

        self.arrows.add(arrow)
        return arrow

    def get_tn_label(self, arrow):
        tn_label = MathTex(*self.label_text)
        tn_label.set_color(arrow.get_color())
        direction = arrow.get_start() - self.arrow_center
        if self.place_label_inside:
            tn_label.move_to(self.arrow_center)
        else:
            tn_label.next_to(arrow.get_start(), direction, buff=SMALL_BUFF)

        return tn_label


class Invert(Succession):
    def __init__(self, pc_set, index,
                 show_axis=True,
                 remove_axis=True,
                 label_color=BLACK,
                 **kwargs):

        self.show_axis = show_axis
        self.remove_axis = remove_axis
        self.label_color = label_color

        if "label_text" not in kwargs:
            self.label_text = ["T_{", str(index), "}I"]
        else:
            self.label_text = kwargs["label_text"]

        self.digit_ratio = pc_set.host.digit_ratio
        self.center = pc_set.host[1].get_center()
        tritone = pc_set.host.edo / 2
        self.point_1 = pc_set.host.n2p(index/2)
        self.point_2 = pc_set.host.n2p((index/2) + tritone)
        self.tni_axis = self.point_2 - self.point_1

        visible_axis = self.create_axis()
        axis_appear = Write(visible_axis, run_time=1)
        inversion = self.animate_inversion(pc_set, **kwargs)
        axis_disappear = FadeOut(visible_axis)

        animations = []
        if self.show_axis:
            animations.append(axis_appear)
            pc_set.host.add(visible_axis)

        animations.append(inversion)

        if self.show_axis and self.remove_axis:
            animations.append(axis_disappear)
            pc_set.host.remove(visible_axis)

        super().__init__(*animations, **kwargs)

    def animate_inversion(self, pc_set, **kwargs):
        return Rotate(pc_set, angle=PI, axis=self.tni_axis, about_point=self.center, **kwargs)

    def create_axis(self):
        label_text = self.label_text
        visible_axis = DashedLine(start=self.point_1, end=self.point_2)
        visible_axis.scale((2/self.digit_ratio)-1)
        visible_axis.set_color(self.label_color)
        tni_label = MathTex(*label_text)
        tni_label.set_color(self.label_color)
        tni_label.next_to(visible_axis, -self.tni_axis, buff=SMALL_BUFF)
        visible_axis.add(tni_label)
        return visible_axis

class VoiceLead(AnimationGroup):
    def __init__(self, pc_set, voice_leading, **kwargs):
        if "show_label" not in kwargs:
            kwargs["show_label"] = False

        animations = []
        host = pc_set.host

        for note, motion in zip(pc_set, voice_leading):
            note.host = host
            animation = Transpose(note, motion, **kwargs)
            animations.append(animation)

        super().__init__(*animations, **kwargs)


class RotateClock(AnimationGroup):
    # This rotates anticlockwise, because math. Maybe that's counterintuitive b/c it's applied to a clock...
    def __init__(self, clock, theta, **kwargs):
        step_angle = -TAU/clock.edo

        basic_arc = Arc(angle=theta,
                        radius=clock.clockface_radius * clock.digit_ratio).rotate((TAU/4)-clock.p2a(clock.digit(0)))
        basic_arc.move_arc_center_to(clock[1].get_center())

        animations = []
        for i, digit in enumerate(clock[0]):
            new_arc = basic_arc.copy().rotate(i * step_angle, about_point=clock[1].get_center())
            animations.append(MoveAlongPath(digit, new_arc))

        super().__init__(*animations, **kwargs)

