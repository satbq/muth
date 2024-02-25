from manim import *
from set_theory import rotate_list
from set_theory import start_zero
import networkx as nx

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


def modecompare(pc_set, reference, rounder=10):
    difference = np.round(np.array(pc_set)-np.array(reference), decimals=rounder)
    res = np.sum(np.unique(np.sign(difference)))
    return res.astype(int)


def brightness_comps(pc_set, edo=12, rounder=10):
    card = len(pc_set)
    res = np.zeros([card, card])
    modes = scalar_interval_matrix(pc_set, edo=edo)
    for i in range(card):
        for j in range(card):
            res[i, j] = modecompare(modes[:, i], modes[:, j], rounder=rounder)
    return res


class BrightnessGraph(VMobject):
    def __init__(self, pc_set, position_matrix=None, node_names=None,
                 edo=12, arrow_stroke_width=3, arrow_tip_length=.2,
                 pc_scale=.35, pc_color=BLACK, v_buff=0.8, h_buff=.7,
                 rn_scale=.5, rn_color=BLACK,
                 sum_scale=.4, sum_color=BLACK,
                 **kwargs):
        VMobject.__init__(self, **kwargs)

        card = len(pc_set)
        current_SIM = scalar_interval_matrix(pc_set, edo=edo)
        SIM_row_sums = current_SIM.sum(axis=0)

        mode_labels = VGroup(*[Tex(ROMAN_NUMERALS[i]).set_color(rn_color).scale(rn_scale) for i in range(1, card+1)])
        if node_names is not None:
            for i, name in enumerate(node_names):
                if name is not None:
                    mode_labels[i] = Tex(name).set_color(rn_color).scale(rn_scale)

        mode_pcs = Matrix(current_SIM.transpose(), v_buff=v_buff, h_buff=h_buff).set_color(pc_color).scale(pc_scale)
        for bracket in mode_pcs.get_brackets():
            mode_pcs.remove(bracket)

        mode_sums = VGroup(*[Tex("(", mode_sum, ")").set_color(sum_color).scale(sum_scale) for mode_sum in SIM_row_sums])
        nodes = VGroup()

        for i in range(card):
            new_node = VGroup(mode_labels[i], mode_sums[i], mode_pcs.get_rows()[i])
            new_node[1].next_to(new_node[0], RIGHT)
            new_node[0].align_to(new_node[1], UP)
            new_node[2].next_to(new_node[0], DOWN, buff=SMALL_BUFF).match_x(VGroup(new_node[0], new_node[1]))
            nodes.add(new_node)

        unreduced_matrix = brightness_comps(pc_set=pc_set, edo=edo)
        unreduced_matrix[unreduced_matrix > 0] = 0
        unreduced_graph = nx.from_numpy_array(unreduced_matrix, create_using=nx.DiGraph)
        reduced_graph = nx.transitive_reduction(unreduced_graph)
        reduced_matrix = nx.adjacency_matrix(reduced_graph)
        reduced_matrix = reduced_matrix.todense()

        # nodes.arrange_in_grid(cols=2, buff=LARGE_BUFF)

        if len(np.shape(position_matrix)) == 1:
            brightest_mode = nodes[np.argmax(SIM_row_sums)]
            darkest_mode = nodes[np.argmin(SIM_row_sums)]
            brightest_mode.to_edge(UP)
            darkest_mode.to_edge(DOWN)
            step_size = (brightest_mode.get_y() - darkest_mode.get_y())/(np.max(SIM_row_sums)-np.min(SIM_row_sums))
            sizes_above_darkest = SIM_row_sums - np.min(SIM_row_sums)
            heights = np.zeros(card)
            for i, size in zip(range(card), sizes_above_darkest):
                heights[i] = (step_size * size) + darkest_mode.get_y()
            new_position_matrix = np.zeros((card, 3))
            for i, width, height in zip(range(card), position_matrix, heights):
                new_position_matrix[i, :] = np.array([width, height, 0])
            position_matrix = new_position_matrix

        for row, node in zip(position_matrix, nodes):
            node.move_to(row)

        arrows = VGroup()
        for i in range(card):
            for j in range(card):
                if reduced_matrix[i, j] > 0:
                    arrows.add(Arrow(nodes[i].get_top(),
                                     nodes[j].get_bottom(),
                                     stroke_width=arrow_stroke_width, tip_length=arrow_tip_length,
                                     max_stroke_width_to_length_ratio=10,
                                     max_tip_length_to_length_ratio=.5,
                                     buff=SMALL_BUFF).set_color(BLACK))

        # self.add(mode_labels)
        # self.add(mode_pcs)
        # self.add(mode_sums)
        self.node = nodes
        self.arrow = arrows
        self.add(nodes)
        self.add(arrows)
        # self.add(arrows)
