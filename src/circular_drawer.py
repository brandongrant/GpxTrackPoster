# Copyright 2016-2017 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import calendar
import datetime
import math
import svgwrite
from . import utils


class TracksDrawer:
    def __init__(self):
        self.poster = None

    def draw(self, poster, d, w, h, offset_x, offset_y):
        self.poster = poster

        tracks_by_date = {}
        for track in self.poster.tracks:
            if not self.poster.years.contains(track.start_time):
                continue
            text_date = track.start_time.strftime("%Y-%m-%d")
            if text_date in tracks_by_date:
                tracks_by_date[text_date].append(track)
            else:
                tracks_by_date[text_date] = [track]
        max_length = 0
        for tracks in tracks_by_date.values():
            length = sum([t.length for t in tracks])
            if length > max_length:
                max_length = length
        if max_length == 0:
            return

        years = self.poster.years.count()
        _, (count_x, count_y) = utils.compute_grid(years, w, h)
        x, y = 0, 0
        ww, hh = w / count_x, h / count_y
        margin_x, margin_y = 4, 4
        if count_x <= 1:
            margin_x = 0
        if count_y <= 1:
            margin_y = 0
        www = ww - 2 * margin_x
        hhh = hh - 2 * margin_y
        for year in range(self.poster.years.from_year, self.poster.years.to_year + 1):
            self.__draw(d,
                www, hhh,
                offset_x + ww * x + margin_x, offset_y + hh * y + margin_y,
                year, max_length, tracks_by_date)
            x += 1
            if x >= count_x:
                x = 0
                y += 1

    def __draw(self, d, w, h, offset_x, offset_y, year, max_length, tracks_by_date):
        outer_radius = 0.5 * min(w, h) - 6
        inner_radius = 0.25 * outer_radius
        c_x = offset_x + 0.5 * w
        c_y = offset_y + 0.5 * h

        year_style = 'font-size:{}px; font-family:Arial;'.format(min(w, h) * 4.0 / 80.0)
        month_style = 'font-size:{}px; font-family:Arial;'.format(min(w, h) * 3.0 / 80.0)

        d.add(d.text('{}'.format(year), insert=(c_x, c_y), fill=self.poster.colors['text'], text_anchor="middle", alignment_baseline="middle", style=year_style))
        df = 360.0 / (366 if calendar.isleap(year) else 365)
        day = 0
        date = datetime.date(year, 1, 1)
        while date.year == year:
            text_date = date.strftime("%Y-%m-%d")
            a1 = math.radians(day * df)
            a2 = math.radians((day + 1) * df)
            if date.day == 1:
                (_, last_day) = calendar.monthrange(date.year, date.month)
                a3 = math.radians((day + last_day - 1) * df)
                r1 = outer_radius + 1
                r2 = outer_radius + 6
                r3 = outer_radius + 2
                d.add(d.line(
                    start=(c_x + r1 * math.sin(a1), c_y - r1 * math.cos(a1)),
                    end=(c_x + r2 * math.sin(a1), c_y - r2 * math.cos(a1)),
                    stroke=self.poster.colors['text'],
                    stroke_width=0.3))
                path = d.path(d=('M', c_x + r3 * math.sin(a1), c_y - r3 * math.cos(a1)), fill='none', stroke='none')
                path.push('a{},{} 0 0,1 {},{}'.format(
                    r3, r3,
                    r3 * (math.sin(a3) - math.sin(a1)),
                    r3 * (math.cos(a1) - math.cos(a3))))
                d.add(path)
                tpath = svgwrite.text.TextPath(path, date.strftime("%B"), startOffset=(0.5 * r3 * (a3 - a1)))
                text = d.text("", fill=self.poster.colors['text'], text_anchor="middle", style=month_style)
                text.add(tpath)
                d.add(text)
            if text_date in tracks_by_date:
                tracks = tracks_by_date[text_date]
                special = [t for t in tracks if t.special]
                length = sum([t.length for t in tracks])
                color = self.poster.colors['special'] if special else self.poster.colors['track']
                r1 = inner_radius
                r2 = inner_radius + (outer_radius-inner_radius) * length / max_length
                path = d.path(d=('M', c_x + r1 * math.sin(a1), c_y - r1 * math.cos(a1)), fill=color, stroke='none')
                path.push('l', (r2 - r1) * math.sin(a1), (r1 - r2) * math.cos(a1))
                path.push('a{},{} 0 0,0 {},{}'.format(r2, r2, r2 * (math.sin(a2) - math.sin(a1)), r2 * (math.cos(a1) - math.cos(a2))))
                path.push('l', (r1 - r2) * math.sin(a2), (r2 - r1) * math.cos(a2))
                d.add(path)

            day += 1
            date += datetime.timedelta(1)
