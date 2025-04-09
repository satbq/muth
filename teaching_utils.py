from manim import *

class Timeline(NumberLine):
    def __init__(self, start_date=1800, end_date=2000, tick_dist=100, number_scale=1,
                 color=BLACK, length=12, **kwargs):

        NumberLine.__init__(self, x_range = [start_date, end_date, tick_dist], length=length,
                            decimal_number_config={"group_with_commas": False,
                                                   "num_decimal_places": 0},
                            include_tip=True, include_numbers=True, **kwargs)
        self.set_style(stroke_color=color, fill_color=color)
        for number in self.numbers:
            number.scale(scale_factor=number_scale).set_style(fill_color=MAROON_E)

    def get_brace(self, start_date, end_date, text=None,
                  text_scale=.5, direction=DOWN):
        new_brace = BraceBetweenPoints(self.n2p(start_date), self.n2p(end_date), direction=direction).set_color(BLACK)
        res = VGroup(new_brace)

        if text is not None:
            new_text = Text(text).set_color(BLACK).scale(text_scale).next_to(new_brace, direction=direction, buff=SMALL_BUFF)
            res.add(new_text)

        return res

    def get_arrow(self, date, text=None, text_scale=.5, arrow_scale=1.5, direction=UP, **kwargs):
        if 'tip_length' not in kwargs:
            my_tip_length = .2
        else:
            my_tip_length = kwargs.pop('tip_length')
        new_arrow = Arrow(start=arrow_scale*direction, end=ORIGIN, tip_length=my_tip_length, **kwargs)
        new_arrow.set_color(BLACK).set_x(self.n2p(date)[0])
        res = VGroup(new_arrow)

        if text is not None:
            new_text = Text(text).set_color(BLACK).scale(text_scale).next_to(new_arrow, direction=direction, buff=SMALL_BUFF)
            res.add(new_text)

        return(res)



# class LectureTitle(Scene):
#     #"#EEEEEE"
#
#     # Note that each heading in the outline should be no more than 50 characters long
#     # Should have no more than 5 topics in the outline
#
#     def __init__(self, course=None, date=None, topic=None, outline=None):
#         config.background_color = WHITE
#         if course is None:
#             self.course = "Default Class"
#         if date is None:
#             self.date = "January 27, 1756"
#         if topic is None:
#             self.topic = "Music Theory is Good"
#
#         border = Rectangle(width=10,height=3,color=BLACK)
#         class_title = Text(self.course)
#         class_title.set_color(MAROON_E)
#         date_subtitle = Text(self.date)
#         date_subtitle.set_color(BLACK)
#         date_subtitle.scale(0.8)
#         Title_1 = VGroup(class_title, date_subtitle)
#         Title_1.arrange(DOWN)
#         topic_subtitle = Text(self.topic)
#         topic_subtitle.set_color(MAROON_E)
#         self.class_title = class_title
#         self.date_subtitle = date_subtitle
#         self.topic_subtitle = topic_subtitle
#         self.border = border
#
#         self.wait()
#         self.play(AnimationGroup(Write(class_title), Write(date_subtitle), Create(border), lag_ratio=0.5))
#         self.wait(2)
#         self.play(FadeOut(Title_1))
#         self.play(Write(topic_subtitle, run_time=1))
#         self.wait(4)
#
#         if self.outline is not None:
#             outline_list = VGroup()
#             for topic in self.outline:
#                 topic_text = Text("- ", topic)
#                 topic_text.set_color(BLACK)
#                 outline_list.add(topic_text)
#             outline_list.arrange(DOWN, buff=MED_LARGE_BUFF)
#
#             for topic in outline_list:
#                 topic.align_to(outline_list, LEFT)
#
#             self.outline_list = outline_list
#
#             topic_subtitle.generate_target()
#             topic_subtitle.target.to_edge(UP, buff=LARGE_BUFF)
#             self.play(AnimationGroup(FadeOut(border), MoveToTarget(topic_subtitle), lag_ratio=.5))
#             self.wait()
#
#             for topic in outline_list:
#                 self.play(Write(topic))
#                 self.wait()
#
#         else:
#             self.play(FadeOut(topic_subtitle), FadeOut(border))
#
#         self.wait()

