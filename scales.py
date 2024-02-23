from manim import *
from set_theory import rotate_list
from set_theory import start_zero

ROMAN_NUMERALS = ["N", "I", "II", "III", "IV", "V", "VI",
                  "VII", "VIII", "IX", "X", "XI", "XII", "XIII",
                  "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
                  "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII",
                  "XXVIII", "XXIX", "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV"]

def scalar_interval_matrix(pc_set, edo=12):
    res = np.vstack([*[rotate_list(pc_set, i) for i in range(len(pc_set))]])
    res = np.apply_along_axis(start_zero, 1, res, edo=edo)
    res = res.transpose()
    return res


class BrightnessGraph(VMobject):
    def __init__(self, pc_set, position_matrix=None, adjacency_matrix=None,
                 edo=12,
                 pc_scale=.5, pc_color=BLACK,
                 rn_scale=1, rn_color=BLACK,
                 sum_scale=.8, sum_color=BLACK,
                 **kwargs):
        VMobject.__init__(self, **kwargs)

        card = len(pc_set)
        current_SIM = scalar_interval_matrix(pc_set, edo=edo)
        SIM_row_sums = current_SIM.sum(axis=0)

        mode_labels = VGroup(*[Tex(ROMAN_NUMERALS[i]).set_color(rn_color).scale(rn_scale) for i in range(1, card+1)])
        mode_pcs = Matrix(current_SIM.transpose()).set_color(pc_color).scale(pc_scale)
        mode_sums = VGroup(*[Tex("(", mode_sum, ")").set_color(sum_color).scale(sum_scale) for mode_sum in SIM_row_sums])
        nodes = VGroup()

        for i in range(card):
            new_node = VGroup(mode_labels[i], mode_sums[i], mode_pcs.get_rows()[i])
            new_node[1].next_to(new_node[0], RIGHT)
            new_node[0].align_to(new_node[1], UP)
            new_node[2].next_to(new_node[0], DOWN).match_x(VGroup(new_node[0], new_node[1]))
            nodes.add(new_node)

        self.add(mode_labels)
        self.add(mode_pcs)
        self.node = nodes